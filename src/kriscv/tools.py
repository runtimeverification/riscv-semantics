from __future__ import annotations

from typing import TYPE_CHECKING

from elftools.elf.elffile import ELFFile  # type: ignore
from pyk.kast.inner import Subst
from pyk.ktool.krun import KRun
from pyk.prelude.k import GENERATED_TOP_CELL

from kriscv import elf_parser, term_builder

if TYPE_CHECKING:
    from pathlib import Path

    from pyk.kast.inner import KInner
    from pyk.kllvm.runtime import Runtime
    from pyk.ktool.kprint import KPrint


class Tools:
    __krun: KRun
    __runtime: Runtime

    def __init__(
        self,
        definition_dir: Path,
        runtime: Runtime,
    ) -> None:
        self.__krun = KRun(definition_dir)
        self.__runtime = runtime

    @property
    def krun(self) -> KRun:
        return self.__krun

    @property
    def kprint(self) -> KPrint:
        return self.__krun

    @property
    def runtime(self) -> Runtime:
        return self.__runtime

    def init_config(self, config_vars: dict[str, KInner]) -> KInner:
        conf = self.krun.definition.init_config(sort=GENERATED_TOP_CELL)
        return Subst(config_vars)(conf)

    def run_config(self, config: KInner) -> KInner:
        config_kore = self.krun.kast_to_kore(config, sort=GENERATED_TOP_CELL)
        final_config_kore = self.krun.run_pattern(config_kore)
        return self.krun.kore_to_kast(final_config_kore)

    def run_elf(self, elf_file: Path, *, end_symbol: str | None = None) -> KInner:
        with open(elf_file, 'rb') as f:
            elf = ELFFile(f)
            if end_symbol is not None:
                end_values = elf_parser.read_symbol(elf, end_symbol)
                if len(end_values) == 0:
                    raise AssertionError(f'Cannot find end symbol {end_symbol!r}: {elf_file}')
                if len(end_values) > 1:
                    raise AssertionError(
                        f'End symbol {end_symbol!r} should be unique, but found multiple instances: {elf_file}'
                    )
                halt_cond = term_builder.halt_at_address(term_builder.word(end_values[0]))
            else:
                halt_cond = term_builder.halt_never()
            config_vars = {
                '$MEM': elf_parser.memory_map(elf),
                '$PC': elf_parser.entry_point(elf),
                '$HALT': halt_cond,
            }
            return self.run_config(self.init_config(config_vars))
