from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.kbuild.utils import k_version
from pyk.kdist.api import Target
from pyk.kllvm.compiler import compile_kllvm, compile_runtime
from pyk.ktool.kompile import kompile

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from typing import Any, Final


class SourceTarget(Target):
    SRC_DIR: Final = Path(__file__).parent

    def build(self, output_dir: Path, deps: dict[str, Path], args: dict[str, Any], verbose: bool) -> None:
        shutil.copytree(self.SRC_DIR / 'riscv-semantics', output_dir / 'riscv-semantics')

    def source(self) -> tuple[Path, ...]:
        return (self.SRC_DIR,)


class KompileTarget(Target):
    _kompile_args: Callable[[Path], Mapping[str, Any]]

    def __init__(self, kompile_args: Callable[[Path], Mapping[str, Any]]):
        self._kompile_args = kompile_args

    def build(self, output_dir: Path, deps: dict[str, Path], args: dict[str, Any], verbose: bool) -> None:
        kompile_args = self._kompile_args(deps['riscv-semantics.source'])
        kompile(output_dir=output_dir, verbose=verbose, **kompile_args)

    def context(self) -> dict[str, str]:
        return {'k-version': k_version().text}

    def deps(self) -> tuple[str]:
        return ('riscv-semantics.source',)


class KLLVMTarget(Target):
    def build(self, output_dir: Path, deps: dict[str, Path], args: dict[str, Any], verbose: bool) -> None:
        compile_kllvm(output_dir, verbose=verbose)

    def context(self) -> dict[str, str]:
        return {
            'k-version': k_version().text,
            'python-path': sys.executable,
            'python-version': sys.version,
        }


class KLLVMRuntimeTarget(Target):
    def build(self, output_dir: Path, deps: dict[str, Path], args: dict[str, Any], verbose: bool) -> None:
        compile_runtime(
            definition_dir=deps['riscv-semantics.llvm'],
            target_dir=output_dir,
            verbose=verbose,
        )

    def deps(self) -> tuple[str, ...]:
        return ('riscv-semantics.llvm',)

    def context(self) -> dict[str, str]:
        return {
            'k-version': k_version().text,
            'python-path': sys.executable,
            'python-version': sys.version,
        }


__TARGETS__: Final = {
    'source': SourceTarget(),
    'llvm': KompileTarget(
        lambda src_dir: {
            'main_file': src_dir / 'riscv-semantics/riscv.md',
            'syntax_module': 'RISCV',
            'include_dirs': [src_dir],
            'md_selector': 'k',
            'warnings_to_errors': True,
        },
    ),
    'kllvm': KLLVMTarget(),
    'kllvm-runtime': KLLVMRuntimeTarget(),
}
