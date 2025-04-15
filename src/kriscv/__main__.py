from __future__ import annotations

import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from elftools.elf.elffile import ELFFile  # type: ignore

from kriscv import elf_parser
from kriscv.build import semantics

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class KRISCVOpts:
    temp_dir: Path | None


@dataclass
class RunOpts(KRISCVOpts):
    input_file: Path
    end_symbol: str | None
    zero_init: bool | None


@dataclass
class RunArchTestOpts(KRISCVOpts):
    input_file: Path
    output_file: Path | None


def kriscv(args: Sequence[str]) -> None:
    opts = _parse_args(args)
    match opts:
        case RunOpts():
            _kriscv_run(opts)
        case RunArchTestOpts():
            _kriscv_run_arch_test(opts)
        case _:
            raise AssertionError()


def _parse_args(args: Sequence[str]) -> KRISCVOpts:
    ns = _arg_parser().parse_args(args)

    if ns.temp_dir is not None:
        ns.temp_dir = ns.temp_dir.resolve(strict=True)

    match ns.command:
        case 'run':
            return RunOpts(
                temp_dir=ns.temp_dir,
                input_file=ns.input_file.resolve(strict=True),
                end_symbol=ns.end_symbol,
                zero_init=ns.zero_init,
            )
        case 'run-arch-test':
            return RunArchTestOpts(
                temp_dir=ns.temp_dir,
                input_file=ns.input_file.resolve(strict=True),
                output_file=ns.output_file,
            )
        case _:
            raise AssertionError()


def _kriscv_run(opts: RunOpts) -> None:
    tools = semantics(temp_dir=opts.temp_dir)
    regs = dict.fromkeys(range(32), 0) if opts.zero_init else {}
    final_conf = tools.run_elf(opts.input_file, regs=regs, end_symbol=opts.end_symbol)
    print(tools.kprint.pretty_print(final_conf, sort_collections=True))


def _kriscv_run_arch_test(opts: RunArchTestOpts) -> None:
    input = opts.input_file
    tools = semantics(temp_dir=opts.temp_dir)
    final_conf = tools.run_elf(input, end_symbol='_halt')
    memory = tools.get_memory(final_conf)

    with open(input, 'rb') as f:
        elf = ELFFile(f)
        begin_sig_addr = elf_parser.read_unique_symbol(elf, 'begin_signature', error_loc=str(input))
        end_sig_addr = elf_parser.read_unique_symbol(elf, 'end_signature', error_loc=str(input))

    if begin_sig_addr % 4 != 0:
        raise AssertionError(
            'Signature region must begin at an XLEN-bit boundary, but begins at address 0x{begin_sig_addr:08X}.'
        )
    if (end_sig_addr - begin_sig_addr) % 4 != 0:
        raise AssertionError(
            'Signature region must contain a series 32-bit words, but spans addresses 0x{begin_sig_addr:08X}-0x{end_sig_addr:08X}.'
        )

    def _addr_to_hex(addr: int) -> str:
        if addr not in memory:
            return '--'
        byte = memory[addr]
        assert 0 <= byte <= 0xFF
        return f'{byte:02x}'

    merged_sig = [_addr_to_hex(addr) for addr in range(begin_sig_addr, end_sig_addr)]
    signature = [''.join(reversed(merged_sig[i : i + 4])) for i in range(0, len(merged_sig), 4)]

    if opts.output_file is None:
        for word in signature:
            print(word)
        return

    with open(opts.output_file, 'w') as out:
        for word in signature:
            out.write(word + '\n')


def _arg_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kriscv')

    command_parser = parser.add_subparsers(dest='command', required=True)

    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument('--temp-dir', type=Path, help='directory where temporary files should be saved')

    run_parser = command_parser.add_parser('run', help='execute a RISC-V ELF file', parents=[common_parser])
    run_parser.add_argument('input_file', type=Path, metavar='FILE', help='RISC-V ELF file to run')
    run_parser.add_argument('--end-symbol', type=str, help='symbol marking the address which terminates execution')
    run_parser.add_argument('-z', '--zero-init', action='store_true', help='initialize registers to zero')

    run_arch_test_parser = command_parser.add_parser(
        'run-arch-test',
        help='execute a RISC-V Architectural Test ELF file and dump the test signature',
        parents=[common_parser],
    )
    run_arch_test_parser.add_argument(
        'input_file', type=Path, metavar='FILE', help='RISC-V Architectural Test ELF file to run'
    )
    run_arch_test_parser.add_argument(
        '-o', '--output', dest='output_file', type=Path, help='output file for the test signature'
    )

    return parser


def main() -> None:
    kriscv(sys.argv[1:])
