from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kore.match import kore_bytes, kore_int, match_app, match_symbol
from pyk.kore.syntax import App, SortApp

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyk.kore.syntax import Pattern


def kore_word(word: Pattern) -> int:
    return kore_int(match_app(word, 'LblW').args[0])


def strip_inj(pattern: Pattern) -> Pattern:
    if isinstance(pattern, App) and pattern.symbol == 'inj':
        return pattern.args[0]
    return pattern


def match_map(pattern: Pattern) -> tuple[tuple[Pattern, Pattern], ...]:
    # Same as match_map from pyk.kore.match, but not using LeftAssoc and stripping injections
    stop_symbol = "Lbl'Stop'Map"
    cons_symbol = "Lbl'Unds'Map'Unds'"
    item_symbol = "Lbl'UndsPipe'-'-GT-Unds'"

    app = match_app(pattern)
    if app.symbol == stop_symbol:
        return ()

    if app.symbol == item_symbol:
        return ((strip_inj(app.args[0]), strip_inj(app.args[1])),)

    match_symbol(app.symbol, cons_symbol)
    return match_map(app.args[0]) + match_map(app.args[1])


def match_sparse_bytes(pattern: Pattern) -> tuple[Pattern, ...]:
    app = match_app(pattern)
    if app.symbol == 'inj' and (
        app.sorts == (SortApp('SortSparseBytesEF'), SortApp('SortSparseBytes'))
        or app.sorts == (SortApp('SortSparseBytesBF'), SortApp('SortSparseBytes'))
    ):
        app = match_app(app.args[0])
    if app.symbol == "LblSparseBytes'Coln'EmptyCons" or app.symbol == "LblSparseBytes'Coln'BytesCons":
        return (app.args[0],) + match_sparse_bytes(app.args[1])
    match_symbol(app.symbol, "Lbl'Stop'SparseBytes")
    return ()


def kore_sb_empty(empty: Pattern) -> int:
    return kore_int(match_app(empty, "LblSparseBytes'ColnHash'empty").args[0])


def kore_sb_bytes(bs: Pattern) -> bytes:
    return kore_bytes(match_app(bs, "LblSparseBytes'ColnHash'bytes").args[0])


def kore_sparse_bytes(sb: Pattern) -> dict[int, bytes]:
    sparse_items: list[int | bytes] = []
    is_bytes = True
    for sb_item in reversed(match_sparse_bytes(sb)):
        if is_bytes:
            sparse_items.append(kore_sb_bytes(sb_item))
        else:
            sparse_items.append(kore_sb_empty(sb_item))
        is_bytes = not is_bytes

    sparse_dict = {}
    addr = 0
    for gap_or_val in reversed(sparse_items):
        if isinstance(gap_or_val, int):
            addr += gap_or_val
        elif isinstance(gap_or_val, bytes):
            sparse_dict[addr] = gap_or_val
            addr += len(gap_or_val)
        else:
            raise AssertionError()
    return sparse_dict


def normalize_memory(memory: Mapping[int, bytes]) -> dict[int, bytes]:
    # normalize sparse bytes data by merging contiguous segments
    raw_memory = sorted(memory.items())
    merged_memory: dict[int, bytes] = {}
    seg_idx = 0
    while seg_idx < len(raw_memory):
        start, val = raw_memory[seg_idx]
        seg_idx += 1
        while seg_idx < len(raw_memory):
            start_next, val_next = raw_memory[seg_idx]
            end_curr = start + len(val)
            assert end_curr <= start_next
            if end_curr == start_next:
                val += val_next
                seg_idx += 1
            else:
                break
        merged_memory[start] = val
    return merged_memory
