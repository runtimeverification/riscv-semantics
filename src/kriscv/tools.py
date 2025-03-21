from __future__ import annotations

from pathlib import Path
from subprocess import CalledProcessError
from typing import TYPE_CHECKING

from elftools.elf.elffile import ELFFile  # type: ignore
from pyk.kast.inner import KSort, Subst
from pyk.kast.manip import split_config_from
from pyk.kore.match import kore_int
from pyk.ktool.krun import KRun
from pyk.prelude.collections import map_empty
from pyk.prelude.k import GENERATED_TOP_CELL

from kriscv import elf_parser, term_builder
from kriscv.term_manip import kore_sparse_bytes, kore_word, match_map

if TYPE_CHECKING:

    from pyk.kast.inner import KInner
    from pyk.kllvm.runtime import Runtime
    from pyk.ktool.kprint import KPrint


class Tools:
    __krun: KRun
    __runtime: Runtime

    def __init__(self, definition_dir: Path, runtime: Runtime, *, temp_dir: Path | None = None) -> None:
        self.__krun = KRun(definition_dir, use_directory=temp_dir)
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
        try:
            final_config_kore = self.krun.run_pattern(config_kore, check=True)
        except CalledProcessError as e:
            path = Path.cwd()
            stdout_path = path / 'krun_stdout.txt'
            stderr_path = path / 'krun_stderr.txt'
            input_path = path / 'krun_input.txt'

            stdout_path.write_text(e.stdout)
            stderr_path.write_text(e.stderr)
            input_path.write_text(config_kore.text)

            print('Generated debug files:')
            print(f'- {stdout_path.resolve()}: KRun standard output')
            print(f'- {stderr_path.resolve()}: KRun error output')
            print(f'- {input_path.resolve()}: Input configuration in Kore format')
            raise
        return self.krun.kore_to_kast(final_config_kore)

    def run_elf(self, elf_file: Path, *, end_symbol: str | None = None) -> KInner:
        with open(elf_file, 'rb') as f:
            elf = ELFFile(f)
            if end_symbol is not None:
                end_addr = elf_parser.read_unique_symbol(elf, end_symbol, error_loc=str(elf_file))
                halt_cond = term_builder.halt_at_address(term_builder.word(end_addr))
            else:
                halt_cond = term_builder.halt_never()
            config_vars = {
                '$REGS': map_empty(),
                '$MEM': elf_parser.memory(elf),
                '$PC': elf_parser.entry_point(elf),
                '$HALT': halt_cond,
            }
            return self.run_config(self.init_config(config_vars))

    def get_registers(self, config: KInner) -> dict[int, int]:
        _, cells = split_config_from(config)
        regs_kore = self.krun.kast_to_kore(cells['REGS_CELL'], sort=KSort('Map'))
        regs = {}
        for reg, val in match_map(regs_kore):
            regs[kore_int(reg)] = kore_word(val)
        if 0 not in regs:
            regs[0] = 0
        return regs

    def get_memory(self, config: KInner) -> dict[int, int]:
        _, cells = split_config_from(config)
        mem_kore = self.krun.kast_to_kore(cells['MEM_CELL'], sort=KSort('SparseBytes'))
        mem = {}
        for addr, data in kore_sparse_bytes(mem_kore).items():
            for idx, val in enumerate(data):
                mem[addr + idx] = val
        return mem
