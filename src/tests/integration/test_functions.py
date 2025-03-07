from __future__ import annotations

from itertools import count
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


def config(kitem: Pattern) -> App:
    return generated_top(
        (
            k(kseq((kitem,))),
            generated_counter(int_dv(0)),
        ),
    )


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


def disassemble(n: int) -> App:
    return App('Lbldisassemble', (), (int_dv(n),))


def is_32bit(x: int) -> bool:
    return 0 <= x < 0x100000000


def chop(x: int) -> int:
    return x & 0xFFFFFFFF


def signed(x: int) -> int:
    assert is_32bit(x)
    return x if x < 0x80000000 else x - 0x100000000


MUL_TEST_DATA: Final = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
    (0xFFFFFFFF, 1),
    (0xFFFFFFFF, 12),
    (0xFFFFFFFF, 0xFFFFFFFF),
    (0xFFFF8765, 0xFFF01234),
    (0xFFFF8765, 12),
)


assert all(is_32bit(op1) and is_32bit(op2) for op1, op2 in MUL_TEST_DATA)


@pytest.mark.parametrize('op1,op2', MUL_TEST_DATA, ids=count())
def test_mul(definition_dir: Path, op1: int, op2: int) -> None:
    # Given
    init = config(inj(SortApp('SortWord'), SORT_K_ITEM, App('LblmulWord', (), (w(op1), w(op2)))))
    res = chop(op1 * op2)
    expected = config(inj(SortApp('SortWord'), SORT_K_ITEM, w(res)))

    # When
    actual = llvm_interpret(definition_dir, init)

    # Then
    assert actual == expected


def w(x: int) -> App:
    return App('LblW', (), (int_dv(x),))
