from __future__ import annotations

import logging
import os
import shutil
from importlib.metadata import version
from typing import TYPE_CHECKING

import riscof.utils as utils  # type: ignore
from riscof.pluginTemplate import pluginTemplate  # type: ignore

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger()


class sail_cSim(pluginTemplate):  # noqa N801
    __model__ = 'sail_cSim'
    __version__ = version('kriscv')

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        config = kwargs.get('config')
        if config is None:
            logger.error('Config node for sail_cSim missing.')
            raise SystemExit(1)
        self.num_jobs = str(config['jobs'] if 'jobs' in config else 1)
        self.pluginpath = os.path.abspath(config['pluginpath'])
        path = config['PATH'] if 'PATH' in config else ''

        self.sail_exe = {'32': os.path.join(path, 'riscv_sim_RV32'), '64': os.path.join(path, 'riscv_sim_RV64')}
        self.isa_spec = os.path.abspath(config['ispec']) if 'ispec' in config else ''
        self.platform_spec = os.path.abspath(config['pspec']) if 'ispec' in config else ''
        self.make = config['make'] if 'make' in config else 'make'
        logger.debug('SAIL CSim plugin initialised using the following configuration.')
        for entry in config:
            logger.debug(entry + ' : ' + config[entry])

    def initialise(self, suite: str, workdir: str, env: str) -> None:
        self.suite = suite
        self.workdir = workdir
        self.objdump_cmd = 'riscv64-unknown-elf-objdump -D {0} > {1};'
        self.env = env
        self.compile_cmd = 'riscv64-unknown-elf-gcc -march={0} \
         -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles'
        self.compile_cmd += (
            ' -T '
            + self.pluginpath
            + '/env/link.ld\
            -I '
            + self.pluginpath
            + '/env/\
            -I '
            + env
        )

    def build(self, isa_yaml: str, platform_yaml: str) -> None:
        ispec = utils.load_yaml(isa_yaml)['hart0']
        self.xlen = '64' if 64 in ispec['supported_xlen'] else '32'
        self.isa = 'rv' + self.xlen
        if '64I' in ispec['ISA']:
            self.compile_cmd = self.compile_cmd + ' -mabi=' + 'lp64 '
        elif '32I' in ispec['ISA']:
            self.compile_cmd = self.compile_cmd + ' -mabi=' + 'ilp32 '
        elif '32E' in ispec['ISA']:
            self.compile_cmd = self.compile_cmd + ' -mabi=' + 'ilp32e '
        if 'I' in ispec['ISA']:
            self.isa += 'i'
        if 'E' in ispec['ISA']:
            self.isa += 'e'
        if 'M' in ispec['ISA']:
            self.isa += 'm'
        if 'C' in ispec['ISA']:
            self.isa += 'c'
        if 'F' in ispec['ISA']:
            self.isa += 'f'
        if 'D' in ispec['ISA']:
            self.isa += 'd'
        objdump = 'riscv64-unknown-elf-objdump'
        if shutil.which(objdump) is None:
            logger.error(objdump + ': executable not found. Please check environment setup.')
            raise SystemExit(1)
        compiler = 'riscv64-unknown-elf-gcc'
        if shutil.which(compiler) is None:
            logger.error(compiler + ': executable not found. Please check environment setup.')
            raise SystemExit(1)
        if shutil.which(self.sail_exe[self.xlen]) is None:
            logger.error(self.sail_exe[self.xlen] + ': executable not found. Please check environment setup.')
            raise SystemExit(1)
        if shutil.which(self.make) is None:
            logger.error(self.make + ': executable not found. Please check environment setup.')
            raise SystemExit(1)

    def runTests(self, testlist: dict[str, dict[str, Any]]) -> None:  # noqa N802
        make = utils.makeUtil(makefilePath=os.path.join(self.workdir, 'Makefile.' + self.name[:-1]))
        make.makeCommand = self.make + ' -j' + self.num_jobs
        for file in testlist:
            testentry = testlist[file]
            test = testentry['test_path']
            test_dir = testentry['work_dir']
            test_name = test.rsplit('/', 1)[1][:-2]
            sig_file = self.name[:-1] + '.signature'
            elf = 'ref.elf'
            execute = '@cd ' + test_dir + ';'

            cmd = self.compile_cmd.format(testentry['isa'].lower()) + ' ' + test + ' -o ' + elf
            compile_cmd = cmd + ' -D' + ' -D'.join(testentry['macros'])
            execute += compile_cmd + ';'

            execute += self.objdump_cmd.format(elf, 'ref.disass')

            if 'c' not in self.isa:
                cmd = self.sail_exe[self.xlen] + ' -C'
            else:
                cmd = self.sail_exe[self.xlen]
            execute += cmd + f' --test-signature={sig_file} {elf} > {test_name}.log 2>&1;'

            make.add_target(execute, tname=test_name)

            make.execute_all(self.workdir)
