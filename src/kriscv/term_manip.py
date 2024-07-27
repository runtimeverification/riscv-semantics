from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kore.match import kore_int, match_app, match_symbol
from pyk.kore.syntax import App

if TYPE_CHECKING:
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
