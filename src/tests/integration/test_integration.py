from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kriscv.hello import hello

from ..utils import TESTS_DIR

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final


def test_hello() -> None:
    assert hello('World') == 'Hello, World!'


SIMPLE_DIR: Final = TESTS_DIR / 'simple'
SIMPLE_TESTS: Final = tuple(asm_file for asm_file in SIMPLE_DIR.rglob('*.S'))


@pytest.mark.parametrize(
    'asm_file',
    SIMPLE_TESTS,
    ids=[str(test.relative_to(SIMPLE_DIR)) for test in SIMPLE_TESTS],
)
def test_simple(asm_file: Path) -> None:
    print(asm_file)
