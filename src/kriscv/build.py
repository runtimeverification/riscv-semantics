from pyk.kdist import kdist

from .tools import Tools


def semantics() -> Tools:
    return Tools(definition_dir=kdist.get('riscv-semantics.llvm'))
