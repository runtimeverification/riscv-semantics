from __future__ import annotations

from typing import TYPE_CHECKING

from kriscv.term_builder import sparse_bytes, word

if TYPE_CHECKING:
    from elftools.elf.elffile import ELFFile  # type: ignore
    from pyk.kast.inner import KInner


def _memory_segments(elf: ELFFile) -> dict[int, bytes]:
    segments: dict[int, bytes] = {}
    for seg in elf.iter_segments():
        if seg['p_type'] == 'PT_LOAD':
            start = seg['p_vaddr']
            file_size = seg['p_filesz']
            mem_size = seg['p_memsz']
            data = seg.data() + b'\0' * (mem_size - file_size)
            segments[start] = data
    return segments


def memory(elf: ELFFile) -> KInner:
    return sparse_bytes(_memory_segments(elf))


def entry_point(elf: ELFFile) -> KInner:
    return word(elf.header['e_entry'])


def read_unique_symbol(elf: ELFFile, symbol: str, *, error_loc: str | None) -> int:
    values = read_symbol(elf, symbol)
    error_loc = error_loc if error_loc else ''
    if len(values) == 0:
        raise AssertionError(f'{error_loc}: Cannot find symbol {symbol!r}.')
    if len(values) > 1:
        raise AssertionError(f'{error_loc}: Symbol {symbol!r} should be unique, but found multiple instances.')
    return values[0]


def read_symbol(elf: ELFFile, symbol: str) -> list[int]:
    symtab = elf.get_section_by_name('.symtab')
    if symtab is None:
        return []
    syms = symtab.get_symbol_by_name(symbol)
    if syms is None:
        return []
    return [sym['st_value'] for sym in syms]


def read_symbols(elf: ELFFile) -> dict[str, list[tuple[int, int]]]:
    from elftools.elf.sections import SymbolTableSection

    symtab = elf.get_section_by_name('.symtab')
    if not symtab:
        return {}

    assert isinstance(symtab, SymbolTableSection)

    res = {}
    for sym in symtab.iter_symbols():
        res.setdefault(sym.name, []). append((sym['st_value'], sym['st_size']))
    return res
