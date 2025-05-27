from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kriscv.symtools import SymTools

if TYPE_CHECKING:
    from pytest import FixtureRequest, Parser

    from kriscv.tools import Tools


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        '--save-final-config',
        action='store_true',
        default=False,
        help='Save the final configuration for each simple test',
    )
    parser.addoption(
        '--temp-dir',
        type=Path,
        help='Directory to save temporary files',
    )


@pytest.fixture
def save_final_config(request: FixtureRequest) -> bool:
    return request.config.getoption('--save-final-config')


@pytest.fixture
def temp_dir(request: FixtureRequest, tmp_path: Path) -> Path:
    temp_dir = request.config.getoption('--temp-dir')
    if temp_dir is not None:
        return temp_dir
    return tmp_path


@pytest.fixture
def tools(temp_dir: Path) -> Tools:
    from kriscv import build

    return build.semantics(temp_dir=temp_dir)


@pytest.fixture
def symtools(temp_dir: Path) -> SymTools:
    return SymTools.default(proof_dir=temp_dir, bug_report=temp_dir / 'bug-reports')
