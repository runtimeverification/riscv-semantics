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


def _test_function(definition_dir: Path, app: Pattern, res: Pattern) -> None:
    # Given
    init = config(app)
    expected = config(res)

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
    def disassemble(n: int) -> App:
        return App('Lbldisassemble', (), (int_dv(n),))

    n = int.from_bytes(code, byteorder='big')
    app = inj(SortApp('SortInstruction'), SORT_K_ITEM, disassemble(n))
    res = inj(sort, SORT_K_ITEM, pattern)
    _test_function(definition_dir=definition_dir, app=app, res=res)


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


def _test_binary_op(
    definition_dir: Path,
    symbol: str,
    op1: int,
    op2: int,
    res: int,
) -> None:
    _test_function(
        definition_dir=definition_dir,
        app=inj(SortApp('SortInt'), SORT_K_ITEM, App(symbol, (), (int_dv(op1), int_dv(op2)))),
        res=inj(SortApp('SortInt'), SORT_K_ITEM, int_dv(res)),
    )


@pytest.mark.parametrize('op1,op2', MUL_TEST_DATA, ids=count())
def test_mul(definition_dir: Path, op1: int, op2: int) -> None:
    _test_binary_op(
        definition_dir=definition_dir,
        symbol='LblmulWord',
        op1=op1,
        op2=op2,
        res=chop(op1 * op2),
    )


@pytest.mark.parametrize('op1,op2', MUL_TEST_DATA, ids=count())
def test_mulh(definition_dir: Path, op1: int, op2: int) -> None:
    _test_binary_op(
        definition_dir=definition_dir,
        symbol='LblmulhWord',
        op1=op1,
        op2=op2,
        res=chop((signed(op1) * signed(op2)) >> 32),
    )


@pytest.mark.parametrize('op1,op2', MUL_TEST_DATA, ids=count())
def test_mulhu(definition_dir: Path, op1: int, op2: int) -> None:
    _test_binary_op(
        definition_dir=definition_dir,
        symbol='LblmulhuWord',
        op1=op1,
        op2=op2,
        res=chop((op1 * op2) >> 32),
    )


@pytest.mark.parametrize('op1,op2', MUL_TEST_DATA, ids=count())
def test_mulhsu(definition_dir: Path, op1: int, op2: int) -> None:
    _test_binary_op(
        definition_dir=definition_dir,
        symbol='LblmulhsuWord',
        op1=op1,
        op2=op2,
        res=chop((signed(op1) * op2) >> 32),
    )


DIV_TEST_DATA: Final = (
    # Normal division cases
    (10, 3),
    (100, 7),
    (0xFFFFFFFF, 1),  # -1 / 1 = -1
    (0xFFFFFFFE, 2),  # -2 / 2 = -1
    (0x80000000, 2),  # -2^31 / 2 = -2^30
    (15, 4),
    (0x7FFFFFFF, 3),  # 2^31-1 / 3
    # Division by zero cases
    (0, 0),
    (1, 0),
    (0xFFFFFFFF, 0),  # -1 / 0
    (0x80000000, 0),  # -2^31 / 0
    (0x7FFFFFFF, 0),  # 2^31-1 / 0
    # Signed overflow case: -2^31 / -1
    (0x80000000, 0xFFFFFFFF),  # -2^31 / -1 should return -2^31
    # Additional edge cases
    (0x80000001, 0xFFFFFFFF),  # (-2^31+1) / -1 = 2^31-1
    (0x7FFFFFFF, 0xFFFFFFFF),  # (2^31-1) / -1 = -(2^31-1)
)


assert all(is_32bit(op1) and is_32bit(op2) for op1, op2 in DIV_TEST_DATA)


def div_expected(op1: int, op2: int) -> int:
    # Calculate expected result according to RISC-V specification
    if op2 == 0:
        # Division by zero returns -1 (all bits set)
        expected = 0xFFFFFFFF
    elif op1 == 0x80000000 and op2 == 0xFFFFFFFF:
        # Signed overflow: -2^31 / -1 returns the dividend (-2^31)
        expected = 0x80000000
    else:
        # Normal signed division with truncation towards zero
        expected = chop(signed(op1) // signed(op2))
    return expected


@pytest.mark.parametrize('op1,op2', DIV_TEST_DATA, ids=count())
def test_div(definition_dir: Path, op1: int, op2: int) -> None:
    _test_binary_op(
        definition_dir=definition_dir,
        symbol='LbldivWord',
        op1=op1,
        op2=op2,
        res=div_expected(op1, op2),
    )


def divu_expected(op1: int, op2: int) -> int:
    # Calculate expected result according to RISC-V specification
    if op2 == 0:
        # Division by zero returns 2^32 - 1 (all bits set)
        expected = 0xFFFFFFFF
    else:
        # Normal unsigned division with truncation towards zero
        expected = op1 // op2
    return expected


@pytest.mark.parametrize('op1,op2', DIV_TEST_DATA, ids=count())
def test_divu(definition_dir: Path, op1: int, op2: int) -> None:
    _test_binary_op(
        definition_dir=definition_dir,
        symbol='LbldivuWord',
        op1=op1,
        op2=op2,
        res=divu_expected(op1, op2),
    )


def rem_expected(op1: int, op2: int) -> int:
    # Calculate expected result according to RISC-V specification for signed remainder
    if op2 == 0:
        # Division by zero returns the dividend
        expected = op1
    elif op1 == 0x80000000 and op2 == 0xFFFFFFFF:
        # Signed overflow: -2^31 % -1 returns 0
        expected = 0
    else:
        # Normal signed remainder with truncation towards zero
        expected = chop(signed(op1) % signed(op2))
    return expected


@pytest.mark.parametrize('op1,op2', DIV_TEST_DATA, ids=count())
def test_rem(definition_dir: Path, op1: int, op2: int) -> None:
    _test_binary_op(
        definition_dir=definition_dir,
        symbol='LblremWord',
        op1=op1,
        op2=op2,
        res=rem_expected(op1, op2),
    )


def remu_expected(op1: int, op2: int) -> int:
    # Calculate expected result according to RISC-V specification for unsigned remainder
    if op2 == 0:
        # Division by zero returns the dividend
        expected = op1
    else:
        # Normal unsigned remainder with truncation towards zero
        expected = op1 % op2
    return expected


@pytest.mark.parametrize('op1,op2', DIV_TEST_DATA, ids=count())
def test_remu(definition_dir: Path, op1: int, op2: int) -> None:
    _test_binary_op(
        definition_dir=definition_dir,
        symbol='LblremuWord',
        op1=op1,
        op2=op2,
        res=remu_expected(op1, op2),
    )
