from __future__ import annotations

import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from kriscv.build import semantics

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class KRISCVOpts: ...


@dataclass
class RunOpts(KRISCVOpts):
    input_file: Path
    end_symbol: str | None


def kriscv(args: Sequence[str]) -> None:
    opts = _parse_args(args)
    match opts:
        case RunOpts():
            _kriscv_run(opts)
        case _:
            raise AssertionError()


def _parse_args(args: Sequence[str]) -> KRISCVOpts:
    ns = _arg_parser().parse_args(args)

    match ns.command:
        case 'run':
            return RunOpts(input_file=Path(ns.input_file).resolve(strict=True), end_symbol=ns.end_symbol)
        case _:
            raise AssertionError()


def _kriscv_run(opts: RunOpts) -> None:
    tools = semantics()
    final_conf = tools.run_elf(opts.input_file, end_symbol=opts.end_symbol)
    print(tools.kprint.pretty_print(final_conf, sort_collections=True))


def _arg_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kriscv')

    command_parser = parser.add_subparsers(dest='command', required=True)

    run_parser = command_parser.add_parser('run', help='execute RISC-V ELF files programs')
    run_parser.add_argument('input_file', metavar='FILE', help='RISC-V ELF file to run')
    run_parser.add_argument('--end-symbol', type=str, help='Symbol marking the address which terminates execution')
    return parser


def main() -> None:
    kriscv(sys.argv[1:])
