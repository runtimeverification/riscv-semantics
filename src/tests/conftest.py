from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest import FixtureRequest, Parser


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        '--update-expected-output',
        action='store_true',
        default=False,
        help='Write expected output files for simple tests',
    )


@pytest.fixture
def update_expected_output(request: FixtureRequest) -> bool:
    return request.config.getoption('--update-expected-output')