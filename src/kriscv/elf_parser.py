from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.prelude.collections import map_of
from pyk.prelude.kint import intToken

if TYPE_CHECKING:
    from elftools.elf.elffile import ELFFile  # type: ignore
    from pyk.kast.inner import KInner


def _memory_segments(elf: ELFFile) -> dict[tuple[int, int], bytes]:
    segments: dict[tuple[int, int], bytes] = {}
    for seg in elf.iter_segments():
        if seg['p_type'] == 'PT_LOAD':
            start = seg['p_vaddr']
            file_size = seg['p_filesz']
            data = seg.data() + b'\0' * (seg['p_memsz'] - file_size)
            segments[(start, start + file_size)] = data
    return segments


def memory_map(elf: ELFFile) -> KInner:
    mem_map: dict[KInner, KInner] = {}
    for addr_range, data in _memory_segments(elf).items():
        start, end = addr_range
        for addr in range(start, end):
            mem_map[intToken(addr)] = intToken(data[addr - start])
    return map_of(mem_map)


def entry_point(elf: ELFFile) -> KInner:
    return intToken(elf.header['e_entry'])


def read_symbol(elf: ELFFile, symbol: str) -> list[int]:
    symtab = elf.get_section_by_name('.symtab')
    if symtab is None:
        return []
    syms = symtab.get_symbol_by_name(symbol)
    if syms is None:
        return []
    return [sym['st_value'] for sym in syms]
