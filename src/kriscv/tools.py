from __future__ import annotations

from pathlib import Path
from subprocess import CalledProcessError
from typing import TYPE_CHECKING

from pyk.kast.inner import KSort, KVariable, Subst
from pyk.kast.manip import split_config_from
from pyk.kast.prelude.k import GENERATED_TOP_CELL
from pyk.kore.match import kore_int
from pyk.ktool.krun import KRun

from kriscv import term_builder
from kriscv.term_builder import word
from kriscv.term_manip import kore_sparse_bytes, kore_word, match_map

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyk.kast import KInner
    from pyk.ktool.kprint import KPrint

    from .elf_parser import ELF


class Tools:
    __krun: KRun

    def __init__(self, definition_dir: Path, *, temp_dir: Path | None = None) -> None:
        self.__krun = KRun(definition_dir, use_directory=temp_dir)

    @property
    def krun(self) -> KRun:
        return self.__krun

    @property
    def kprint(self) -> KPrint:
        return self.__krun

    def config(self, *, regs: KInner, mem: KInner, pc: KInner, halt: KInner) -> KInner:
        config_vars = {
            '$REGS': regs,
            '$MEM': mem,
            '$PC': pc,
            '$HALT': halt,
        }
        config = self.krun.definition.init_config(sort=GENERATED_TOP_CELL)
        return Subst(config_vars)(config)

    def config_from_elf(
        self,
        elf: str | Path | ELF,
        *,
        regs: dict[int, int] | None = None,
        end_symbol: str | None = None,
        symbolic_names: Iterable[str] | None = None,
    ) -> KInner:
        from pyk.kast.prelude.ml import mlAnd

        from .elf_parser import ELF
        from .sparse_bytes import SparseBytes, SymBytes

        if not isinstance(elf, ELF):
            elf = ELF.load(elf)

        def _symdata(symbolic_names: Iterable[str]) -> dict[int, SymBytes]:
            res = {}
            for name in symbolic_names:
                symbol = elf.unique_symbol(name)
                var = KVariable(name.upper(), 'Bytes')
                res[symbol.addr] = SymBytes(var, symbol.size)
            return res

        symdata = _symdata(symbolic_names) if symbolic_names else {}
        mem, cnstrs = SparseBytes.from_data(data=elf.memory, symdata=symdata).to_k()

        _regs = term_builder.regs(regs or {})
        pc = word(elf.entry_point)

        halt: KInner
        if end_symbol is not None:
            end_addr = elf.unique_symbol(end_symbol).addr
            halt = term_builder.halt_at_address(term_builder.word(end_addr))
        else:
            halt = term_builder.halt_never()

        config = self.config(regs=_regs, mem=mem, pc=pc, halt=halt)
        config = mlAnd([config] + cnstrs)
        return config

    def run_config(self, config: KInner, *, depth: int | None = None) -> KInner:
        config_kore = self.krun.kast_to_kore(config, sort=GENERATED_TOP_CELL)
        try:
            final_config_kore = self.krun.run_pattern(config_kore, depth=depth, check=True)
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
