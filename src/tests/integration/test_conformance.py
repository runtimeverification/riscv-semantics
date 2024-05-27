from __future__ import annotations

import logging
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

RISCOF: Final = REPO_ROOT / 'tests' / 'riscof'


def _skipped_tests() -> set[Path]:
    return {REPO_ROOT / test_path for test_path in (RISCOF / 'failing.txt').read_text().splitlines()}


SKIPPED_TESTS: Final = _skipped_tests()

ARCH_SUITE_DIR: Final = RISCOF / 'riscv-arch-test' / 'riscv-test-suite'


def _test_list() -> Path:
    work_dir = RISCOF / 'work'
    test_list = work_dir / 'test_list.yaml'
    with FileLock(RISCOF / 'work.lock'):
        if not test_list.exists():
            if work_dir.exists():
                shutil.rmtree(work_dir)
            subprocess.run(
                [
                    'riscof',
                    'testlist',
                    f'--suite={ARCH_SUITE_DIR}',
                    f'--env={ARCH_SUITE_DIR / "env"}',
                    f'--config={RISCOF / "config.ini"}',
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


def _test(test: dict[str, Any]) -> None:
    test_file = Path(test['test_path'])
    _LOGGER.info(f'Running test: {test_file}')


@pytest.mark.parametrize(
    'test_entry',
    ARCH_TESTS,
    ids=[str(Path(test['test_path']).relative_to(ARCH_SUITE_DIR)) for test in ARCH_TESTS],
)
def test_arch(test_entry: dict[str, Any]) -> None:
    _test(test_entry)


@pytest.mark.skip(reason='failing arch tests')
@pytest.mark.parametrize(
    'test_entry',
    REST_ARCH_TESTS,
    ids=[str(Path(test['test_path']).relative_to(ARCH_SUITE_DIR)) for test in REST_ARCH_TESTS],
)
def test_rest_arch(test_entry: dict[str, Any]) -> None:
    _test(test_entry)
