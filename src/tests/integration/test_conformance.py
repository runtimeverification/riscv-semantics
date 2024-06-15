from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml

from ..utils import REPO_ROOT

if TYPE_CHECKING:
    from typing import Any, Final

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'

RISCOF: Final = Path(__file__).parent / 'riscof'


def _skipped_tests() -> set[Path]:
    return {REPO_ROOT / test_path for test_path in (REPO_ROOT / 'tests' / 'failing.txt').read_text().splitlines()}


SKIPPED_TESTS: Final = _skipped_tests()

ARCH_SUITE_DIR: Final = REPO_ROOT / 'tests' / 'riscv-arch-test' / 'riscv-test-suite'
ARCH_TEST_COMPILED_DIR: Final = REPO_ROOT / 'tests' / 'riscv-arch-test-compiled'
TEST_LIST: Final = ARCH_TEST_COMPILED_DIR / 'test_list.yaml'
ALL_ARCH_TESTS: Final = tuple(yaml.safe_load(TEST_LIST.read_text()).values())
ARCH_TESTS: Final = tuple(test for test in ALL_ARCH_TESTS if test['test_path'] not in SKIPPED_TESTS)
REST_ARCH_TESTS: Final = tuple(test for test in ALL_ARCH_TESTS if test['test_path'] in SKIPPED_TESTS)


def _test(test_dir: Path, isa: str) -> None:
    pass


@pytest.mark.parametrize(
    'test_entry',
    ARCH_TESTS,
    ids=[str(Path(test['test_path']).relative_to(ARCH_SUITE_DIR)) for test in ARCH_TESTS],
)
def test_arch(test_entry: dict[str, Any]) -> None:
    _test(Path(test_entry['work_dir']), test_entry['isa'].lower())


@pytest.mark.skip(reason='failing arch tests')
@pytest.mark.parametrize(
    'test_entry',
    REST_ARCH_TESTS,
    ids=[str(Path(test['test_path']).relative_to(ARCH_SUITE_DIR)) for test in REST_ARCH_TESTS],
)
def test_rest_arch(test_entry: dict[str, Any]) -> None:
    _test(Path(test_entry['work_dir']), test_entry['isa'].lower())
