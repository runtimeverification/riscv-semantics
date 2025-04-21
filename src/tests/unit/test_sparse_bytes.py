from __future__ import annotations

from typing import Final

import pytest
from pyk.kast.inner import KToken, KVariable
from pyk.prelude.kint import intToken

import kriscv.term_builder as tb
from kriscv.sparse_bytes import SparseBytes, SymBytes

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
    ),
)


def test_from_concrete() -> None:
    assert SparseBytes.from_concrete({0: b'\xab', 2: b'\xcd'}) == SparseBytes([b'\xab', 1, b'\xcd'])


def test_which_data() -> None:
    sb = SparseBytes([b'\xab\xab', 3, b'\xcd\xcd'])
    assert sb.which_data(0) == (0, 0)
    assert sb.which_data(1) == (0, 1)
    assert sb.which_data(2) == (1, 0)
    assert sb.which_data(3) == (1, 1)
    assert sb.which_data(4) == (1, 2)
    assert sb.which_data(5) == (2, 0)
    assert sb.which_data(6) == (2, 1)
    with pytest.raises(ValueError):
        sb.which_data(7)


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


@pytest.mark.parametrize(
    'data,symdata,expected',
    [(data, symdata, expected) for (_, data, symdata, expected, _) in SYMBOLIC_MEMORY_TEST_DATA],
    ids=[test_id for test_id, *_ in SYMBOLIC_MEMORY_TEST_DATA],
)
def test_from_data(data: dict[int, bytes], symdata: dict[int, SymBytes], expected: SparseBytes) -> None:
    assert SparseBytes.from_data(data, symdata) == expected
