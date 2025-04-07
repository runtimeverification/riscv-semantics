from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kdist import kdist
from pyk.kllvm import importer

from .tools import Tools

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

importer.import_kllvm(kdist.get('riscv-semantics.kllvm'))

runtime: Final = importer.import_runtime(kdist.get('riscv-semantics.kllvm-runtime'))


def semantics(*, temp_dir: Path | None = None) -> Tools:
    return Tools(definition_dir=kdist.get('riscv-semantics.llvm'), temp_dir=temp_dir)
