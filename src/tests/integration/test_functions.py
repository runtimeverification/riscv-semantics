from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pyk.kdist import kdist
from pyk.kore.prelude import INT, SORT_K_ITEM, generated_counter, generated_top, inj, int_dv, k, kseq
from pyk.kore.syntax import App, SortApp
from pyk.ktool.krun import llvm_interpret

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

    from pyk.kore.syntax import Pattern


@pytest.fixture(scope='module')
def definition_dir() -> Path:
    return kdist.get('riscv-semantics.func-test')


def sw(rs2: int, imm: int, rs1: int) -> App:
    return App(
        'LblRegImmRegInstr',
        (),
        (
            App('LblSW'),
            reg(rs2),
            int_dv(imm),
            reg(rs1),
        ),
    )


def reg(x: int) -> App:
    return inj(INT, SortApp('SortRegister'), int_dv(x))


DISASSEMBLE_TEST_DATA: Final = (
    ('sw s0,296(sp)', b'\x12\x81\x24\x23', SortApp('SortRegImmRegInstr'), sw(8, 296, 2)),
    ('sw s1,292(sp)', b'\x12\x91\x22\x23', SortApp('SortRegImmRegInstr'), sw(9, 292, 2)),
)


@pytest.mark.parametrize(
    'test_id,code,sort,pattern',
    DISASSEMBLE_TEST_DATA,
    ids=[test_id for test_id, *_ in DISASSEMBLE_TEST_DATA],
)
def test_disassemble(definition_dir: Path, test_id: str, code: bytes, sort: SortApp, pattern: Pattern) -> None:
    # Given
    n = int.from_bytes(code, byteorder='big')
    init = config(inj(SortApp('SortInstruction'), SORT_K_ITEM, disassemble(n)))
    expected = config(inj(sort, SORT_K_ITEM, pattern))

    # When
    actual = llvm_interpret(definition_dir, init)

    # Then
    assert actual == expected


def config(kitem: Pattern) -> App:
    return generated_top(
        (
            k(kseq((kitem,))),
            generated_counter(int_dv(0)),
        ),
    )


def disassemble(n: int) -> App:
    return App('Lbldisassemble', (), (int_dv(n),))
