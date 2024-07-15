from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kdist import kdist
from pyk.kllvm import importer

from .tools import Tools

if TYPE_CHECKING:
    from typing import Final

importer.import_kllvm(kdist.get('riscv-semantics.kllvm'))

runtime: Final = importer.import_runtime(kdist.get('riscv-semantics.kllvm-runtime'))


def semantics() -> Tools:
    return Tools(definition_dir=kdist.get('riscv-semantics.llvm'), runtime=runtime)
