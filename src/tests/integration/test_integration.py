from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kriscv.build import semantics

from ..utils import TESTS_DIR

if TYPE_CHECKING:
    from typing import Final


SIMPLE_DIR: Final = TESTS_DIR / 'simple'
SIMPLE_TESTS: Final = tuple(asm_file for asm_file in SIMPLE_DIR.rglob('*.S'))


def _test_simple(elf_file: Path, expected_file: Path, update: bool) -> None:
    tools = semantics()
    actual = tools.kprint.pretty_print(tools.run_elf(elf_file, end_symbol='_halt'), sort_collections=True)

    if update:
        expected_file.touch()
        expected_file.write_text(actual)
        return

    expected_file = expected_file.resolve(strict=True)
    expected = expected_file.read_text()
    assert actual == expected


@pytest.mark.parametrize(
    'asm_file',
    SIMPLE_TESTS,
    ids=[str(test.relative_to(SIMPLE_DIR)) for test in SIMPLE_TESTS],
)
def test_simple(asm_file: Path, update_expected_output: bool, temp_dir: Path) -> None:
    elf_file = Path(temp_dir) / (asm_file.stem + '.elf')
    compile_cmd = [
        'riscv64-unknown-elf-gcc',
        '-nostdlib',
        '-nostartfiles',
        '-static',
        '-march=rv32e',
        '-mabi=ilp32e',
        '-mno-relax',
        '-mlittle-endian',
        '-Xassembler',
        '-mno-arch-attr',
        str(asm_file),
        '-o',
        str(elf_file),
    ]
    subprocess.run(compile_cmd, check=True)
    assert elf_file.exists()
    expected_file = Path(str(asm_file) + '.out')
    _test_simple(elf_file, expected_file, update_expected_output)
