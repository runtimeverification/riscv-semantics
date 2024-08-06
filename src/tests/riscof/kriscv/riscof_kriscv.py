from __future__ import annotations

import logging
import os
import shutil
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

import riscof.utils as utils  # type: ignore
from riscof.pluginTemplate import pluginTemplate  # type: ignore

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger()


class kriscv(pluginTemplate):  # noqa N801
    __model__ = 'kriscv'
    __version__ = version('kriscv')

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        config = kwargs.get('config')
        if config is None:
            logger.error('Config for kriscv is missing.')
            raise SystemExit
        self.num_jobs = str(config['jobs'] if 'jobs' in config else 1)
        self.pluginpath = os.path.abspath(config['pluginpath'])
        self.isa_spec = os.path.abspath(config['ispec'])
        self.platform_spec = os.path.abspath(config['pspec'])
        self.target_run = ('target_run' not in config) or config['target_run'] == '1'

    def initialise(self, suite: str, workdir: str, env: str) -> None:
        self.suite = suite
        self.workdir = workdir
        self.compile_cmd = 'riscv64-unknown-elf-gcc -march={march} -mabi={mabi} -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles'
        self.compile_cmd += f' -T {self.pluginpath}/env/link.ld -I {self.pluginpath}/env/ -I {env}'
        self.compile_cmd += ' {flags} {input} {output}'
        self.objdump_cmd = 'riscv64-unknown-elf-objdump --no-addresses --no-show-raw-insn -D {input} > {output}'

    def build(self, isa_yaml: str, platform_yaml: str) -> None:
        ispec = utils.load_yaml(isa_yaml)['hart0']
        self.mabi = _mabi(ispec['ISA'])
        _check_exec_exists('kriscv')
        _check_exec_exists('riscv64-unknown-elf-gcc')
        _check_exec_exists('riscv64-unknown-elf-objdump')
        _check_exec_exists('make')

    def runTests(self, testlist: dict[str, dict[str, Any]]) -> None:  # noqa N802
        name = self.name[:-1]  # riscof includes an extra : on the end of the name for some reason
        make = utils.makeUtil(makefilePath=os.path.join(self.workdir, f'Makefile.{name}'))
        make.makeCommand = f'make -j {self.num_jobs}'
        for entry in testlist.values():
            test_path = entry['test_path']
            march = entry['isa'].lower()
            macro_flags = ' '.join(f'-D{macro}' for macro in entry['macros'])
            test_name = Path(test_path).stem
            compile_asm_cmd = self.compile_cmd.format(
                march=march, mabi=self.mabi, flags=macro_flags + ' -S', input=test_path, output=f'> {test_name}.s'
            )
            compile_elf_cmd = self.compile_cmd.format(
                march=march,
                mabi=self.mabi,
                flags=macro_flags,
                input=test_path,
                output=f'-o {test_name}.elf',
            )
            objdump_cmd = self.objdump_cmd.format(
                input=f'{test_name}.elf',
                output=f'{test_name}.disass',
            )
            work_dir = Path(entry['work_dir']).resolve(strict=True)
            sig_file = work_dir / (name + '.signature')
            execute_cmd = (
                f'kriscv run-arch-test {test_name}.elf --output {sig_file}' if self.target_run else 'echo "NO RUN"'
            )
            execute = f'@cd {work_dir}; {compile_asm_cmd}; {compile_elf_cmd}; {objdump_cmd}; {execute_cmd}'
            make.add_target(execute, tname=test_name)
        make.execute_all(self.workdir)
        if not self.target_run:
            raise SystemExit


def _mabi(spec_isa: str) -> str:
    if '64I' in spec_isa:
        return 'lp64'
    if '64E' in spec_isa:
        return 'lp64e'
    if '32I' in spec_isa:
        return 'ilp32'
    if '32E' in spec_isa:
        return 'ilp32e'
    logger.error(f'Bad ISA string in ISA YAML: {spec_isa}')
    raise SystemExit


def _check_exec_exists(executable: str) -> None:
    if shutil.which(executable) is None:
        logger.error(f'{executable}: executable not found. Please check environment setup.')
        raise SystemExit
