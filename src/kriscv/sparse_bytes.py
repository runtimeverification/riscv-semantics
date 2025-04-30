from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise
from typing import NamedTuple

from pyk.kast.inner import KInner
from pyk.kast.prelude.kint import eqInt, intToken
from pyk.kast.prelude.ml import mlEqualsTrue

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
        return data
    else:
        return data.size


def _split(
    data: bytes | int | SymBytes, offset: int
) -> tuple[bytes | int | SymBytes | None, bytes | int | SymBytes | None]:
    size = _size(data)
    if offset == 0:
        return None, data
    if offset == size:
        return data, None
    if 0 < offset < size:
        match data:
            case bytes():
                return data[:offset], data[offset:]
            case int():
                return offset, size - offset
            case SymBytes():
                raise NotImplementedError('Splitting symbolic bytes is not implemented')
            case _:
                raise ValueError(f'Unexpected item type: {type(data)}')
    raise ValueError(f'Offset {offset} is out of bounds for size {size}')


class SymBytes(NamedTuple):
    data: KInner
    size: int

    def constraint(self) -> KInner:
        return mlEqualsTrue(eqInt(length_bytes(self.data), intToken(self.size)))


@dataclass
class SparseBytes:
    """
    Python representation for ``SparseBytes`` in sparse-bytes.md

    Invariants:
    - No consecutive bytes/integers
    - Ascending address order
    """

    data: list[bytes | int | SymBytes]

    def __init__(self, data: list[bytes | int | SymBytes]) -> None:
        self.data = list(data)

    @staticmethod
    def from_concrete(data: dict[int, bytes]) -> SparseBytes:
        """Create a SparseBytes from a {address: bytes} dictionary"""
        clean_data: list[tuple[int, int | bytes]] = sorted(normalize_memory(data).items())

        if not clean_data:
            return SparseBytes([])

        # Collect all empty gaps between segements
        gaps: list[tuple[int, int | bytes]] = []
        start = clean_data[0][0]
        if start != 0:
            gaps.append((0, start))
        for (start1, val1), (start2, _) in pairwise(clean_data):
            end1 = start1 + _size(val1)
            # normalize_memory should already have merged consecutive segments
            assert end1 < start2
            gaps.append((end1, start2 - end1))

        # Merge segments and gaps into a list of sparse bytes items
        return SparseBytes([gap_or_val for _, gap_or_val in sorted(clean_data + gaps)])

    @staticmethod
    def from_data(data: dict[int, bytes], symdata: dict[int, SymBytes]) -> SparseBytes:
        """Create a SparseBytes from a {address: bytes} dictionary and a {address: SymBytes} dictionary"""
        result = SparseBytes.from_concrete(data)
        for addr, sym in symdata.items():
            result[addr : addr + sym.size] = SparseBytes([sym])
        return result

    @staticmethod
    def from_k(sparse_bytes: KInner, constraints: list[KInner]) -> SparseBytes:
        # > This will introduce more codes that make it hard to review.
        # > I want to implement in the next PR.
        raise NotImplementedError('TODO')

    def to_k(self) -> tuple[KInner, list[KInner]]:
        """Generate a KInner and a list of constraints from a SparseBytes"""
        result = dot_sb()
        processed: list[KInner | int] = []

        # Merge consecutive byte-like items
        for item in self.data:
            if isinstance(item, (bytes, SymBytes)):
                token = bytesToken(item) if isinstance(item, bytes) else item.data
                if processed and isinstance(processed[-1], KInner):
                    processed[-1] = add_bytes(processed[-1], token)
                else:
                    processed.append(token)
            elif isinstance(item, int):
                processed.append(item)
            else:
                raise ValueError(f'Unexpected item type: {type(item)}')

        # Build term right-to-left
        for data in reversed(processed):
            if isinstance(data, int):
                result = sb_empty_cons(sb_empty(intToken(data)), result)
            else:
                result = sb_bytes_cons(sb_bytes(data), result)

        return result, [item.constraint() for item in self.data if isinstance(item, SymBytes)]

    def which_data(self, addr: int) -> tuple[int, int]:
        """Return the index and offset of the data item that contains the address"""
        current_addr = 0
        for i, item in enumerate(self.data):
            if addr < current_addr + _size(item):
                return i, addr - current_addr
            current_addr += _size(item)
        if current_addr == addr:
            return len(self.data) - 1, _size(self.data[-1])
        raise ValueError(f'Address {addr} is out of bounds')

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

    def __setitem__(self, addr: slice, value: SparseBytes) -> None:
        """Set a sub-bytes from the address"""
        if len(value) != addr.stop - addr.start:
            raise ValueError(f'Expected length {addr.stop - addr.start}, got {len(value)}')
        self.data = (self.split(addr.start)[0] + value + self.split(addr.stop)[1]).data

    def __getitem__(self, addr: slice) -> SparseBytes:
        """Return a sub-bytes from the address"""
        _, result = self.split(addr.start)
        result, _ = result.split(addr.stop - addr.start)
        return result

    def __add__(self, other: SparseBytes) -> SparseBytes:
        """Concatenate two SparseBytes"""
        if self.data == []:
            return SparseBytes(other.data)
        if other.data == []:
            return SparseBytes(self.data)
        if isinstance(self.data[-1], int) and isinstance(other.data[0], int):
            self.data[-1] += other.data[0]
            return SparseBytes(self.data + other.data[1:])
        if isinstance(self.data[-1], bytes) and isinstance(other.data[0], bytes):
            return SparseBytes(self.data[:-1] + [self.data[-1] + other.data[0]] + other.data[1:])
        return SparseBytes(self.data + other.data)

    def __len__(self) -> int:
        """Return the length of the SparseBytes"""
        return sum(_size(item) for item in self.data)
