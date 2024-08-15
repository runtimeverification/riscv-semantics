from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml
from elftools.elf.elffile import ELFFile  # type: ignore

from kriscv import elf_parser
from kriscv.build import semantics

from ..utils import TESTS_DIR

if TYPE_CHECKING:
    from typing import Final

    from kriscv.tools import Tools

SIMPLE_DIR: Final = TESTS_DIR / 'simple'
SIMPLE_TESTS: Final = tuple(asm_file for asm_file in SIMPLE_DIR.rglob('*.S'))


def _as_unsigned(val: int, bits: int) -> int | None:
    if 0 <= val and val < 2**bits:
        return val
    if -(2 ** (bits - 1)) <= val and val < 0:
        return val + 2**bits
    return None


def _check_regs_entry(assert_file: Path, registers: dict[int, int], reg: int, val: int) -> None:
    if not (0 <= reg and reg < 16):
        raise AssertionError(
            f"{assert_file}: Invalid register {reg} found in 'regs'. Registers must be in the range [0, 15]."
        )
    expect = _as_unsigned(val, 32)
    if expect is None:
        val_str = f'{val} (0x{val:08X})' if val >= 0 else f'{val}'
        raise AssertionError(
            f'{assert_file}: expected value {val_str} for x{reg} is not a 32-bit integer. Value must be in the range [-2147483648, 2147483647] or [0, 4294967295] ([0, 0xFFFFFFFF]).'
        )
    err_msg = f'Expected x{reg} to contain {val} (0x{expect:08X}), but '
    if reg not in registers:
        raise AssertionError(err_msg + f'x{reg} was never written to.')
    actual = registers[reg]
    if actual != expect:
        raise AssertionError(err_msg + f'found {actual} (0x{actual:08X}).')


def _check_mem_entry(assert_file: Path, mem_symbol: int, memory: dict[int, int], offset: int, val: int) -> None:
    addr = mem_symbol + offset
    mem_str = f'{mem_symbol} (0x{mem_symbol:08X})'
    offset_str = f'{offset} (0x{offset:08X})'
    addr_str = f'{addr} (0x{addr:08X})'
    if not (0 <= addr and addr < 2**32):
        raise AssertionError(
            f"{assert_file}: Invalid memory offset {offset_str} found in 'mem'. Symbol '_mem' is at address {mem_str}, so the absolute address {addr_str} corresponding to this offset is outside the allowed range [0, 4294967295] ([0, 0xFFFFFFFF])."
        )
    expect = _as_unsigned(val, 8)
    if expect is None:
        val_str = f'{val} (0x{val:02X})' if val >= 0 else f'{val}'
        raise AssertionError(
            f'{assert_file}: expected value {val_str} for memory offset {offset_str} is not an 8-bit integer. Value must be in the range [-128, 127] or [0, 255] ([0, 0xFF]).'
        )
    err_msg = (
        f'Expected memory offset {offset_str} to contain {val} (0x{expect:02X}), but '
        + '{reason}'
        + f". Symbol '_mem' is at address {mem_str}, so this offset corresponds to absolute address {addr_str}."
    )
    if addr not in memory:
        raise AssertionError(err_msg.format(reason='this location was never written to'))
    actual = memory[addr]
    if actual != expect:
        raise AssertionError(err_msg.format(reason=f'found {actual} (0x{actual:02X})'))


def _test_simple(tools: Tools, elf_file: Path, assert_file: Path, final_config_output: Path | None) -> None:
    final_config = tools.run_elf(elf_file, end_symbol='_halt')

    if final_config_output is not None:
        final_config_output.touch()
        pretty_config = tools.kprint.pretty_print(final_config, sort_collections=True)
        final_config_output.write_text(pretty_config)

    registers = tools.get_registers(final_config)
    memory = tools.get_memory(final_config)

    assert_file = assert_file.resolve(strict=True)
    asserts = yaml.safe_load(assert_file.read_bytes())

    if asserts is None:
        return
    if not (set(asserts.keys()) <= {'regs', 'mem'}):
        raise AssertionError(f"{assert_file}: Unexpected keys {asserts.keys()}. Expected only 'regs' or 'mem'.")

    for reg, val in asserts.get('regs', {}).items():
        if not isinstance(reg, int):
            raise AssertionError(f"{assert_file}: Unexpected key {reg} in 'regs'. Expected an integer register number.")
        if not isinstance(val, int):
            raise AssertionError(f"{assert_file}: Unexpected value {val} in 'regs'. Expected a 32-bit integer.")
        _check_regs_entry(assert_file, registers, reg, val)

    if 'mem' not in asserts:
        return

    with open(elf_file, 'rb') as f:
        mem_symbol_vals = elf_parser.read_symbol(ELFFile(f), '_mem')

    if len(mem_symbol_vals) == 0:
        raise AssertionError(
            f"{assert_file}: Found 'mem' assertion entry, but test file does not contain '_mem' symbol."
        )
    if len(mem_symbol_vals) > 1:
        raise AssertionError(
            f"{assert_file}: Found 'mem' assertion entry, but test file contains multiple instances of '_mem' symbol."
        )
    mem_symbol = mem_symbol_vals[0]
    for addr, val in asserts.get('mem', {}).items():
        if not isinstance(addr, int):
            raise AssertionError(f"{assert_file}: Unexpected key {reg} in 'mem'. Expected an integer address.")
        if not isinstance(val, int):
            raise AssertionError(f"{assert_file}: Unexpected value {val} in 'mem'. Expected an 8-bit integer.")
        _check_mem_entry(assert_file, mem_symbol, memory, addr, val)


@pytest.mark.parametrize(
    'asm_file',
    SIMPLE_TESTS,
    ids=[str(test.relative_to(SIMPLE_DIR)) for test in SIMPLE_TESTS],
)
def test_simple(asm_file: Path, save_final_config: bool, temp_dir: Path) -> None:
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
        f'-I {SIMPLE_DIR}',
        str(asm_file),
        '-o',
        str(elf_file),
    ]
    subprocess.run(compile_cmd, check=True)
    assert elf_file.exists()
    assert_file = Path(str(asm_file) + '.assert')
    final_config_output = (Path(temp_dir) / (asm_file.name + '.out')) if save_final_config else None
    _test_simple(semantics(temp_dir=temp_dir), elf_file, assert_file, final_config_output)
