from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest import Config, FixtureRequest, Parser
    from xdist import WorkerController  # type: ignore


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        '--update-expected-output',
        action='store_true',
        default=False,
        help='Write expected output files for simple tests',
    )
    parser.addoption(
        '--temp-dir',
        type=Path,
        help='Directory to save temporary files',
    )


@pytest.fixture
def update_expected_output(request: FixtureRequest) -> bool:
    return request.config.getoption('--update-expected-output')


@pytest.fixture
def temp_dir(request: FixtureRequest) -> Path:
    if is_master(request.config):
        return Path(request.config.temp_dir)  # type: ignore[attr-defined]
    else:
        return Path(request.config.workerinput['temp_dir'])  # type: ignore[attr-defined]


def pytest_configure(config: Config) -> None:
    if is_master(config):
        temp_dir = config.getoption('--temp-dir')
        if temp_dir is None:
            temp_dir = Path(tempfile.mkdtemp())
        else:
            temp_dir.mkdir(parents=True, exist_ok=True)
        config.temp_dir = str(temp_dir.resolve(strict=True))  # type: ignore[attr-defined]


def pytest_configure_node(node: WorkerController) -> None:
    node.workerinput['temp_dir'] = node.config.temp_dir


def pytest_unconfigure(config: Config) -> None:
    if is_master(config) and config.getoption('--temp-dir') is None:
        shutil.rmtree(config.temp_dir)  # type: ignore[attr-defined]


def is_master(config: Config) -> bool:
    return not hasattr(config, 'workerinput')
