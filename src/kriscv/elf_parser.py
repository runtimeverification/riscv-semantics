from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.prelude.bytes import bytesToken
from pyk.prelude.collections import rangemap_of
from pyk.prelude.kint import intToken

if TYPE_CHECKING:
    from elftools.elf.elffile import ELFFile  # type: ignore
    from pyk.kast.inner import KInner


def _memory_rangemap(elf: ELFFile) -> KInner:
    segments: dict[tuple[KInner, KInner], KInner] = {}
    for seg in elf.iter_segments():
        if seg['p_type'] == 'PT_LOAD':
            start = seg['p_vaddr']
            file_size = seg['p_filesz']
            data = seg.data() + b'\0' * (seg['p_memsz'] - file_size)
            segments[(intToken(start), intToken(start + file_size))] = bytesToken(data)
    return rangemap_of(segments)


def _entry_point(elf: ELFFile) -> KInner:
    return intToken(elf.header['e_entry'])


def config_vars(elf: ELFFile) -> dict[str, KInner]:
    memory = _memory_rangemap(elf)
    pc = _entry_point(elf)
    return {'$MEM': memory, '$PC': pc}
