from __future__ import annotations

from typing import TYPE_CHECKING

from elftools.elf.elffile import ELFFile  # type: ignore
from pyk.kast.inner import Subst
from pyk.ktool.krun import KRun
from pyk.prelude.k import GENERATED_TOP_CELL

from kriscv import elf_parser

if TYPE_CHECKING:
    from pathlib import Path

    from pyk.kast.inner import KInner
    from pyk.ktool.kprint import KPrint


class Tools:
    __krun: KRun

    def __init__(
        self,
        definition_dir: Path,
    ) -> None:
        self.__krun = KRun(definition_dir)

    @property
    def krun(self) -> KRun:
        return self.__krun

    @property
    def kprint(self) -> KPrint:
        return self.__krun

    def init_config(self, config_vars: dict[str, KInner]) -> KInner:
        conf = self.krun.definition.init_config(sort=GENERATED_TOP_CELL)
        return Subst(config_vars)(conf)

    def run_config(self, config: KInner) -> KInner:
        config_kore = self.krun.kast_to_kore(config, sort=GENERATED_TOP_CELL)
        final_config_kore = self.krun.run_pattern(config_kore)
        return self.krun.kore_to_kast(final_config_kore)

    def run_elf(self, elf_file: Path) -> KInner:
        with open(elf_file, 'rb') as f:
            return self.run_config(self.init_config(elf_parser.config_vars(ELFFile(f))))
