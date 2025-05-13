from __future__ import annotations

import importlib
import logging
import re
from typing import TYPE_CHECKING

from pyk.utils import FrozenDict

from .api import Plugin

if TYPE_CHECKING:
    from importlib.metadata import EntryPoint
    from typing import Final


_LOGGER: Final = logging.getLogger(__name__)


def _load_plugins() -> FrozenDict[str, Plugin]:
    entry_points = importlib.metadata.entry_points(group='kprovex')
    plugins: FrozenDict[str, Plugin] = FrozenDict(
        (entry_point.name, plugin) for entry_point in entry_points if (plugin := _load_plugin(entry_point)) is not None
    )
    return plugins


def _load_plugin(entry_point: EntryPoint) -> Plugin | None:
    if not _valid_id(entry_point.name):
        _LOGGER.warning(f'Invalid entry point name, skipping: {entry_point.name}')
        return None

    _LOGGER.info(f'Loading entry point: {entry_point.name}')
    try:
        module_name, class_name = entry_point.value.split(':')
    except ValueError:
        _LOGGER.error(f'Invalid entry point value: {entry_point.value}', exc_info=True)
        return None

    try:
        _LOGGER.info(f'Importing module: {module_name}')
        module = importlib.import_module(module_name)
    except Exception:
        _LOGGER.error(f'Module {module_name} cannot be imported', exc_info=True)
        return None

    try:
        _LOGGER.info(f'Loading plugin: {class_name}')
        cls = getattr(module, class_name)
    except AttributeError:
        _LOGGER.error(f'Class {class_name} not found in module {module_name}', exc_info=True)
        return None

    if not issubclass(cls, Plugin):
        _LOGGER.error(f'Class {class_name} is not a Plugin', exc_info=True)
        return None

    try:
        _LOGGER.info(f'Instantiating plugin: {class_name}')
        plugin = cls()
    except TypeError:
        _LOGGER.error(f'Cannot instantiate plugin {class_name}', exc_info=True)
        return None

    return plugin


_ID_PATTERN = re.compile('[a-z0-9]+(-[a-z0-9]+)*')


def _valid_id(s: str) -> bool:
    return _ID_PATTERN.fullmatch(s) is not None


PLUGINS: Final = _load_plugins()
