from __future__ import annotations

import logging
import os
from importlib.metadata import version
from typing import TYPE_CHECKING

from riscof.pluginTemplate import pluginTemplate  # type: ignore

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger()


class kriscv(pluginTemplate):  # noqa N801
    __model__ = 'kriscv'
    __version__ = version('kriscv')

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        config = kwargs.get('config')
        if config is None:
            print('Please enter input file paths in configuration.')
            raise SystemExit(1)
        self.num_jobs = str(config['jobs'] if 'jobs' in config else 1)
        self.pluginpath = os.path.abspath(config['pluginpath'])
        self.isa_spec = os.path.abspath(config['ispec'])
        self.platform_spec = os.path.abspath(config['pspec'])
        self.target_run = ('target_run' not in config) or config['target_run'] == '1'

    def initialise(self, suite: str, workdir: str, env: str) -> None:
        pass

    def build(self, isa_yaml: str, platform_yaml: str) -> None:
        pass

    def runTests(self, testlist: dict[str, dict[str, Any]]) -> None:  # noqa N802
        pass
