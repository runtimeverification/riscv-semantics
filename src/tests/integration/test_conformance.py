from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml
from filelock import FileLock

from ..utils import REPO_ROOT

if TYPE_CHECKING:
    from typing import Any, Final

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'

RISCOF: Final = Path(__file__).parent / 'riscof'


def _skipped_tests() -> set[Path]:
    return {REPO_ROOT / test_path for test_path in (REPO_ROOT / 'tests' / 'failing.txt').read_text().splitlines()}


# Failing tests pulled from tests/riscof/failing.txt
SKIPPED_TESTS: Final = _skipped_tests()

ARCH_SUITE_DIR: Final = REPO_ROOT / 'tests' / 'riscv-arch-test' / 'riscv-test-suite'


def _mod_time(path: Path) -> float:
    """Get the modification time of a directory, accounting for all its recursive contents."""
    if path.is_file():
        return os.path.getmtime(path)
    return max(
        os.path.getmtime(entry)
        for root, _, files in os.walk(path)
        for entry in [os.path.join(root, name) for name in files] + [root]
    )


def _test_list() -> Path:
    """Get the path to test_list.yaml, regenerating if needed."""
    work_dir = RISCOF / 'work'
    test_list = work_dir / 'test_list.yaml'
    config = RISCOF / 'config.ini'
    # Lock file to avoid every worker trying to regenerate the test list when using pytest-xdist
    with FileLock(RISCOF / 'work.lock'):
        if not test_list.exists() or _mod_time(test_list) < max(_mod_time(ARCH_SUITE_DIR), _mod_time(config)):
            if work_dir.exists():
                shutil.rmtree(work_dir)
            subprocess.run(
                [
                    'riscof',
                    'testlist',
                    f'--suite={ARCH_SUITE_DIR}',
                    f'--env={ARCH_SUITE_DIR / "env"}',
                    f'--config={config}',
                    f'--work-dir={work_dir}',
                ],
                check=True,
            )
    assert test_list.exists()
    return test_list


TEST_LIST: Final = _test_list()
ALL_ARCH_TESTS: Final = tuple(yaml.safe_load(TEST_LIST.read_text()).values())
ARCH_TESTS: Final = tuple(test for test in ALL_ARCH_TESTS if test['test_path'] not in SKIPPED_TESTS)
REST_ARCH_TESTS: Final = tuple(test for test in ALL_ARCH_TESTS if test['test_path'] in SKIPPED_TESTS)


def _isa_spec() -> dict[str, Any]:
    isa_yaml = RISCOF / 'kriscv' / 'kriscv_isa.yaml'
    return yaml.safe_load(isa_yaml.read_text())['hart0']


ISA_SPEC: Final = _isa_spec()


def _mabi() -> str:
    spec_isa = ISA_SPEC['ISA']
    if '64I' in spec_isa:
        return 'lp64'
    if '64E' in spec_isa:
        return 'lp64e'
    if '32I' in spec_isa:
        return 'ilp32'
    if '32E' in spec_isa:
        return 'ilp32e'
    raise AssertionError(f'Bad ISA spec: {spec_isa}')


def _compile_test(test: dict[str, Any]) -> Path:
    """Compile the test for the given test entry from test_list.yaml.

    Produces the compiled <test>.elf file and returns the path to its disassembly <test>.diss."
    """
    test_file = Path(test['test_path'])
    _LOGGER.info(f'Running test: {test_file}')
    march = test['isa'].lower()
    plugin_env = RISCOF / 'kriscv' / 'env'
    plugin_link = plugin_env / 'link.ld'
    suite_env = ARCH_SUITE_DIR / 'env'
    work_dir = Path(test['work_dir'])
    elf_output = work_dir / (work_dir.stem + '.elf')
    diss_output = work_dir / (work_dir.stem + '.diss')
    compile_cmd = [
        'riscv64-unknown-elf-gcc',
        f'-march={march}',
        f'-mabi={_mabi()}',
        '-static',
        '-mcmodel=medany',
        '-fvisibility=hidden',
        '-nostdlib',
        '-nostartfiles',
        '-T',
        f'{plugin_link}',
        '-I',
        f'{plugin_env}',
        '-I',
        f'{suite_env}',
        f'{test_file}',
        '-o',
        f'{elf_output}',
    ]
    compile_cmd += [f'-D{macro}' for macro in test['macros']]
    subprocess.run(
        compile_cmd,
        check=True,
    )
    assert elf_output.exists()
    with open(diss_output, 'w') as out:
        subprocess.run(
            ['riscv64-unknown-elf-objdump', '--no-addresses', '--no-show-raw-insn', '-D', elf_output], stdout=out
        )
    return diss_output


def _test(diss_file: Path) -> None:
    """Execute a compiled test given its disassembled ELF file."""


@pytest.mark.parametrize(
    'test_entry',
    ARCH_TESTS,
    ids=[str(Path(test['test_path']).relative_to(ARCH_SUITE_DIR)) for test in ARCH_TESTS],
)
def test_arch(test_entry: dict[str, Any]) -> None:
    diss_file = _compile_test(test_entry)
    _test(diss_file)


@pytest.mark.skip(reason='failing arch tests')
@pytest.mark.parametrize(
    'test_entry',
    REST_ARCH_TESTS,
    ids=[str(Path(test['test_path']).relative_to(ARCH_SUITE_DIR)) for test in REST_ARCH_TESTS],
)
def test_rest_arch(test_entry: dict[str, Any]) -> None:
    diss_file = _compile_test(test_entry)
    _test(diss_file)
