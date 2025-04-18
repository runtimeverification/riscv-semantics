from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

from pyk.kast.inner import KInner
from pyk.prelude.kint import eqInt, intToken
from pyk.prelude.ml import mlEqualsTrue

from .term_builder import (
    add_bytes,
    bytesToken,
    dot_sb,
    length_bytes,
    normalize_memory,
    sb_bytes,
    sb_bytes_cons,
    sb_empty,
    sb_empty_cons,
)


def _size(data: bytes | int | SymBytes) -> int:
    if isinstance(data, bytes):
        return len(data)
    elif isinstance(data, int):
        return 1
    else:
        return data.size


def _split(
    data: bytes | int | SymBytes, offset: int
) -> tuple[bytes | int | SymBytes | None, bytes | int | SymBytes | None]:
    if isinstance(data, bytes):
        return data[:offset], data[offset:]
    elif isinstance(data, int):
        return offset, data - offset
    elif isinstance(data, SymBytes):
        if offset == 0:
            return None, data
        elif offset == data.size:
            return data, None
        else:
            raise NotImplementedError("Splitting symbolic bytes is not implemented")
    else:
        raise ValueError(f"Unexpected item type: {type(data)}")


@dataclass
class SymBytes:
    data: KInner
    size: int

    def constraint(self) -> KInner:
        return mlEqualsTrue(eqInt(length_bytes(self.data), intToken(self.size)))


@dataclass
class SparseBytes:
    """
    Python binding for `SparseBytes` in sparse-bytes.md

    Invariants:
    - No consecutive bytes/integers
    - Ascending address order
    """

    data: list[bytes | int | SymBytes]

    @staticmethod
    def from_concrete(data: dict[int, bytes]) -> SparseBytes:
        """Create a SparseBytes from a {address: bytes} dictionary"""
        clean_data: list[tuple[int, int | bytes]] = sorted(normalize_memory(data).items())

        if len(clean_data) == 0:
            return dot_sb()

        # Collect all empty gaps between segements
        gaps: list[tuple[int, int | bytes]] = []
        start = clean_data[0][0]
        if start != 0:
            gaps.append((0, start))
        for (start1, val1), (start2, _) in pairwise(clean_data):
            end1 = start1 + len(val1)
            # normalize_memory should already have merged consecutive segments
            assert end1 < start2
            gaps.append((end1, start2 - end1))

        # Merge segments and gaps into a list of sparse bytes items
        return SparseBytes([gap_or_val for _, gap_or_val in sorted(clean_data + gaps)])

    @staticmethod
    def from_data(data: dict[int, bytes | SymBytes]) -> SparseBytes:
        """Create a SparseBytes from a {address: bytes | SymBytes} dictionary"""
        concrete_data = {k: v for k, v in data.items() if isinstance(v, bytes)}
        symbolic_data = {k: v for k, v in data.items() if isinstance(v, SymBytes)}
        result = SparseBytes.from_concrete(concrete_data)
        for addr, sym in symbolic_data.items():
            result[addr : addr + sym.size] = sym
        return result

    @staticmethod
    def from_k(sparse_bytes: KInner, constraints: list[KInner]) -> SparseBytes:
        # > This will introduce more codes that make it hard to review.
        # > I want to implement in the next PR.
        pass

    def to_k(self) -> tuple[KInner, list[KInner]]:
        result = dot_sb()
        processed: list[KInner | int] = []

        # Merge consecutive byte-like items
        for item in self.data:
            if isinstance(item, (bytes, KInner)):
                token = bytesToken(item) if isinstance(item, bytes) else item
                if processed and isinstance(processed[-1], KInner):
                    processed[-1] = add_bytes(processed[-1], token)
                else:
                    processed.append(token)
            else:  # int
                processed.append(item)

        # Build term right-to-left
        for item in reversed(processed):
            if isinstance(item, int):
                result = sb_empty_cons(sb_empty(intToken(item)), result)
            else:
                result = sb_bytes_cons(sb_bytes(item), result)

        return result, [item.constraint() for item in self.data if isinstance(item, SymBytes)]

    def which_data(self, addr: int) -> tuple[int, int]:
        """Return the index and offset of the data item that contains the address"""
        current_addr = 0
        for i, item in enumerate(self.data):
            if addr < current_addr + _size(item):
                return i, addr - current_addr
            current_addr += _size(item)
        raise ValueError(f"Address {addr} is out of bounds")

    def which_data_slice(self, start: int, end: int) -> tuple[tuple[int, int], tuple[int, int]]:
        """Return the start and end index of the data item that contains the address"""
        return self.which_data(start), self.which_data(end)

    def split(self, addr: int) -> tuple[SparseBytes, SparseBytes]:
        """Split the SparseBytes at the address"""
        idx, offset = self.which_data(addr)
        left_item, right_item = _split(self.data[idx], offset)
        left_data = list(self.data[:idx]) if left_item is None else list(self.data[:idx]) + [left_item]
        right_data = list(self.data[idx + 1 :]) if right_item is None else [right_item] + list(self.data[idx + 1 :])
        return SparseBytes(left_data), SparseBytes(right_data)

    def __setitem__(self, addr: int, value: bytes | int | SymBytes) -> None:
        """Set one byte from the address"""
        self.__setitem__(slice(addr, addr + 1), SparseBytes([value]))

    def __setitem__(self, addr: slice, value: SparseBytes) -> None:
        """Set a sub-bytes from the address"""
        assert len(value) == addr.stop - addr.start, f"Expected length {addr.stop - addr.start}, got {value}"
        self.data = self.split(addr.start)[0].data + value.data + self.split(addr.stop)[1].data

    def __getitem__(self, addr: int) -> bytes | int | SymBytes:
        """Return one byte from the address"""
        return self.__getitem__(slice(addr, addr + 1))

    def __getitem__(self, addr: slice) -> SparseBytes:
        """Return a sub-bytes from the address"""
        _, result = self.split(addr.start)
        result, _ = result.split(addr.stop - addr.start)
        return result

    def __add__(self, other: SparseBytes) -> SparseBytes:
        """Concatenate two SparseBytes"""
        if isinstance(self.data[-1], int) and isinstance(other.data[0], int):
            self.data[-1] += other.data[0]
            return SparseBytes(self.data + other.data[1:])
        elif isinstance(self.data[-1], bytes) and isinstance(other.data[0], bytes):
            return SparseBytes(self.data[:-1] + [self.data[-1] + other.data[0]] + other.data[1:])
        else:
            return SparseBytes(self.data + other.data)

    def __len__(self) -> int:
        """Return the length of the SparseBytes"""
        return sum(_size(item) for item in self.data)
