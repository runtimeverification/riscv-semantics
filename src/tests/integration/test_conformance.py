from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml

from ..utils import FAILING_TESTS, REPO_ROOT

if TYPE_CHECKING:
    from typing import Any, Final

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'

RISCOF: Final = Path(__file__).parent / 'riscof'

ARCH_SUITE_DIR: Final = REPO_ROOT / 'tests' / 'riscv-arch-test' / 'riscv-test-suite'
ARCH_TEST_COMPILED_DIR: Final = REPO_ROOT / 'tests' / 'riscv-arch-test-compiled'
TEST_LIST: Final = ARCH_TEST_COMPILED_DIR / 'test_list.yaml'
ALL_ARCH_TESTS: Final = tuple(yaml.safe_load(TEST_LIST.read_text()).values())
ARCH_TESTS: Final = tuple(test for test in ALL_ARCH_TESTS if test['test_path'] not in FAILING_TESTS)
REST_ARCH_TESTS: Final = tuple(test for test in ALL_ARCH_TESTS if test['test_path'] in FAILING_TESTS)


def _test(test_dir: Path, name: str, isa: str) -> None:
    asm = test_dir / f'{name}.s'
    elf = test_dir / f'{name}.elf'
    disass = test_dir / f'{name}.disass'

    assert asm.exists()
    assert elf.exists()
    assert disass.exists()


@pytest.mark.parametrize(
    'test_entry',
    ARCH_TESTS,
    ids=[str(Path(test['test_path']).relative_to(ARCH_SUITE_DIR)) for test in ARCH_TESTS],
)
def test_arch(test_entry: dict[str, Any]) -> None:
    _test(
        Path(test_entry['work_dir']) / 'dut',
        Path(test_entry['test_path']).relative_to(ARCH_SUITE_DIR).stem,
        test_entry['isa'].lower(),
    )


@pytest.mark.skip(reason='failing arch tests')
@pytest.mark.parametrize(
    'test_entry',
    REST_ARCH_TESTS,
    ids=[str(Path(test['test_path']).relative_to(ARCH_SUITE_DIR)) for test in REST_ARCH_TESTS],
)
def test_rest_arch(test_entry: dict[str, Any]) -> None:
    _test(
        Path(test_entry['work_dir']) / 'dut',
        Path(test_entry['test_path']).relative_to(ARCH_SUITE_DIR).stem,
        test_entry['isa'].lower(),
    )
