from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
from pyk.kast.inner import KToken, KVariable
from pyk.prelude.kint import eqInt, intToken
from pyk.prelude.ml import mlEqualsTrue

import kriscv.term_builder as tb
from kriscv.sparse_bytes import SparseBytes, SymBytes

if TYPE_CHECKING:
    from pyk.kast.inner import KInner

SYMBOLIC_MEMORY_TEST_DATA: Final = (
    (
        'empty-bytes-2-3',
        {2: b'\x7f\x7f\x7f\x7f\x7f'},
        {3: SymBytes(KVariable('W0', 'Bytes'), 1), 2: SymBytes(KVariable('W1', 'Bytes'), 1)},
        SparseBytes([2, SymBytes(KVariable('W1', 'Bytes'), 1), SymBytes(KVariable('W0', 'Bytes'), 1), b'\x7f\x7f\x7f']),
        # #empty(2) #bytes(W1 +Bytes +W0 +Bytes b'\x7f\x7f\x7f')
        tb.sb_empty_cons(
            tb.sb_empty(intToken(2)),
            tb.sb_bytes_cons(
                tb.sb_bytes(
                    tb.add_bytes(
                        tb.add_bytes(KVariable('W1', 'Bytes'), KVariable('W0', 'Bytes')),
                        KToken('b"\\x7f\\x7f\\x7f"', 'Bytes'),
                    )
                ),
                tb.dot_sb(),
            ),
        ),
        [
            mlEqualsTrue(eqInt(tb.length_bytes(KVariable('W1', 'Bytes')), intToken(1))),
            mlEqualsTrue(eqInt(tb.length_bytes(KVariable('W0', 'Bytes')), intToken(1))),
        ],
    ),
    (
        'empty-bytes-6',
        {2: b'\x7f\x7f', 12: b'\x7f\x7f\x7f'},
        {14: SymBytes(KVariable('W0', 'Bytes'), 1)},
        SparseBytes([2, b'\x7f\x7f', 8, b'\x7f\x7f', SymBytes(KVariable('W0', 'Bytes'), 1)]),
        # #empty(2) #bytes(b'\x7f\x7f') #empty(8) #bytes(b'\x7f\x7f' +Bytes +W0)
        tb.sb_empty_cons(
            tb.sb_empty(intToken(2)),
            tb.sb_bytes_cons(
                tb.sb_bytes(KToken('b"\\x7f\\x7f"', 'Bytes')),
                tb.sb_empty_cons(
                    tb.sb_empty(intToken(8)),
                    tb.sb_bytes_cons(
                        tb.sb_bytes(tb.add_bytes(KToken('b"\\x7f\\x7f"', 'Bytes'), KVariable('W0', 'Bytes'))),
                        tb.dot_sb(),
                    ),
                ),
            ),
        ),
        [mlEqualsTrue(eqInt(tb.length_bytes(KVariable('W0', 'Bytes')), intToken(1)))],
    ),
)


def test_from_concrete() -> None:
    assert SparseBytes.from_concrete({0: b'\xab', 2: b'\xcd'}) == SparseBytes([b'\xab', 1, b'\xcd'])


@pytest.mark.parametrize(
    'data,symdata,expected',
    [(data, symdata, expected) for (_, data, symdata, expected, _, _) in SYMBOLIC_MEMORY_TEST_DATA],
    ids=[test_id for test_id, *_ in SYMBOLIC_MEMORY_TEST_DATA],
)
def test_from_data(data: dict[int, bytes], symdata: dict[int, SymBytes], expected: SparseBytes) -> None:
    assert SparseBytes.from_data(data, symdata) == expected


@pytest.mark.parametrize(
    'symbytes,expected',
    [(symbytes, (expected0, expected1)) for (_, _, _, symbytes, expected0, expected1) in SYMBOLIC_MEMORY_TEST_DATA],
    ids=[test_id for test_id, *_ in SYMBOLIC_MEMORY_TEST_DATA],
)
def test_to_k(symbytes: SparseBytes, expected: tuple[KInner, list[KInner]]) -> None:
    assert symbytes.to_k() == expected


def test_which_data() -> None:
    sb = SparseBytes([b'\xab\xab', 3, b'\xcd\xcd'])
    assert sb.which_data(0) == (0, 0)
    assert sb.which_data(1) == (0, 1)
    assert sb.which_data(2) == (1, 0)
    assert sb.which_data(3) == (1, 1)
    assert sb.which_data(4) == (1, 2)
    assert sb.which_data(5) == (2, 0)
    assert sb.which_data(6) == (2, 1)
    assert sb.which_data(7) == (2, 2)
    with pytest.raises(ValueError):
        sb.which_data(8)


def test_split() -> None:
    sb = SparseBytes([b'\xab\xab', 3, b'\xcd\xcd'])
    assert sb.split(0) == (SparseBytes([]), SparseBytes([b'\xab\xab', 3, b'\xcd\xcd']))
    assert sb.split(1) == (SparseBytes([b'\xab']), SparseBytes([b'\xab', 3, b'\xcd\xcd']))
    assert sb.split(2) == (SparseBytes([b'\xab\xab']), SparseBytes([3, b'\xcd\xcd']))
    assert sb.split(3) == (SparseBytes([b'\xab\xab', 1]), SparseBytes([2, b'\xcd\xcd']))
    assert sb.split(4) == (SparseBytes([b'\xab\xab', 2]), SparseBytes([1, b'\xcd\xcd']))
    assert sb.split(5) == (SparseBytes([b'\xab\xab', 3]), SparseBytes([b'\xcd\xcd']))
    assert sb.split(6) == (SparseBytes([b'\xab\xab', 3, b'\xcd']), SparseBytes([b'\xcd']))
    assert sb.split(7) == (SparseBytes([b'\xab\xab', 3, b'\xcd\xcd']), SparseBytes([]))


def test_setitem() -> None:
    sb = SparseBytes([b'\xab\xab', 3, b'\xcd\xcd'])
    sb[0:2] = SparseBytes([b'\xde\xde'])
    assert sb == SparseBytes([b'\xde\xde', 3, b'\xcd\xcd'])
    sb[2:3] = SparseBytes([b'\xef'])
    assert sb == SparseBytes([b'\xde\xde\xef', 2, b'\xcd\xcd'])
    sb[3:4] = SparseBytes([SymBytes(KVariable('W0', 'Bytes'), 1)])
    assert sb == SparseBytes([b'\xde\xde\xef', SymBytes(KVariable('W0', 'Bytes'), 1), 1, b'\xcd\xcd'])
    sb[3:4] = SparseBytes([SymBytes(KVariable('W1', 'Bytes'), 1)])
    assert sb == SparseBytes([b'\xde\xde\xef', SymBytes(KVariable('W1', 'Bytes'), 1), 1, b'\xcd\xcd'])
    sb[3:5] = SparseBytes([SymBytes(KVariable('W3', 'Bytes'), 2)])
    assert sb == SparseBytes([b'\xde\xde\xef', SymBytes(KVariable('W3', 'Bytes'), 2), b'\xcd\xcd'])
    with pytest.raises(NotImplementedError):
        sb[3:4] = SparseBytes([SymBytes(KVariable('W4', 'Bytes'), 1)])


def test_getitem() -> None:
    sb = SparseBytes([b'\xab\xab', 3, b'\xcd\xef'])
    assert sb[0:2] == SparseBytes([b'\xab\xab'])
    assert sb[1:6] == SparseBytes([b'\xab', 3, b'\xcd'])
    assert sb[6:7] == SparseBytes([b'\xef'])


def test_add() -> None:
    sb = SparseBytes([b'\xab\xab', 3, b'\xcd\xcd'])
    sb2 = SparseBytes([b'\xef\xef'])
    assert sb + sb2 == SparseBytes([b'\xab\xab', 3, b'\xcd\xcd\xef\xef'])
    sb3 = SparseBytes([4])
    assert sb + sb3 == SparseBytes([b'\xab\xab', 3, b'\xcd\xcd', 4])
    sb4 = SparseBytes([SymBytes(KVariable('W0', 'Bytes'), 1)])
    assert sb + sb4 == SparseBytes([b'\xab\xab', 3, b'\xcd\xcd', SymBytes(KVariable('W0', 'Bytes'), 1)])
    sb5 = SparseBytes([])
    assert sb + sb5 == SparseBytes([b'\xab\xab', 3, b'\xcd\xcd'])
    assert sb5 + sb == SparseBytes([b'\xab\xab', 3, b'\xcd\xcd'])


def test_len() -> None:
    sb = SparseBytes([b'\xab\xab', 3, b'\xcd\xcd'])
    assert len(sb) == 7
    sb = SparseBytes([b'\xab\xab', 3, b'\xcd\xcd', SymBytes(KVariable('W0', 'Bytes'), 1), b'\xef\xef'])
    assert len(sb) == 10
