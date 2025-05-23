from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, final

from pyk.utils import FrozenDict, check_file_path

from kriscv.term_builder import word

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from elftools.elf.elffile import ELFFile
    from pyk.kast.inner import KInner


class Symbol(NamedTuple):
    addr: int
    size: int


@final
@dataclass(frozen=True)
class ELF:
    entry_point: int
    memory: FrozenDict[int, bytes]
    symbols: FrozenDict[str, tuple[Symbol, ...]]

    def __init__(
        self,
        *,
        entry_point: int,
        memory: Mapping[int, bytes],
        symbols: Mapping[str, Iterable[tuple[int, int]]],
    ):
        memory = FrozenDict(memory)
        symbols = FrozenDict((name, tuple(Symbol(*symbol) for symbol in symbols)) for name, symbols in symbols.items())
        object.__setattr__(self, 'entry_point', entry_point)
        object.__setattr__(self, 'memory', memory)
        object.__setattr__(self, 'symbols', symbols)

    @staticmethod
    def load(file: str | Path) -> ELF:
        from elftools.elf.elffile import ELFFile

        file = Path(file)
        check_file_path(file)

        with file.open('rb') as f:
            elf = ELFFile(f)
            return ELF(
                entry_point=ELF._entry_point(elf),
                memory=ELF._memory(elf),
                symbols=ELF._symbols(elf),
            )

    @staticmethod
    def _entry_point(elf: ELFFile) -> int:
        return elf.header['e_entry']

    @staticmethod
    def _memory(elf: ELFFile) -> dict[int, bytes]:
        res: dict[int, bytes] = {}
        for seg in elf.iter_segments():
            if seg['p_type'] == 'PT_LOAD':
                start = seg['p_vaddr']
                file_size = seg['p_filesz']
                mem_size = seg['p_memsz']
                data = seg.data() + b'\0' * (mem_size - file_size)
                res[start] = data
        return res

    @staticmethod
    def _symbols(elf: ELFFile) -> dict[str, list[Symbol]]:
        from elftools.elf.sections import SymbolTableSection

        symtab = elf.get_section_by_name('.symtab')
        if not symtab:
            return {}

        assert isinstance(symtab, SymbolTableSection)

        res: dict[str, list[Symbol]] = {}
        for sym in symtab.iter_symbols():
            res.setdefault(sym.name, []).append(
                Symbol(
                    addr=sym['st_value'],
                    size=sym['st_size'],
                )
            )
        return res

    def unique_symbol(self, name: str, *, error_loc: str | None = None) -> Symbol:
        error_loc = f'{error_loc}: ' if error_loc else ''
        symbols = self.symbols.get(name, ())
        if not symbols:
            raise AssertionError(f'{error_loc}Cannot find symbol: {name!r}')
        if len(symbols) > 1:
            raise AssertionError(f'{error_loc}Symbol not unique: {name!r}')
        return symbols[0]


def entry_point(elf: ELF) -> KInner:
    return word(elf.entry_point)
