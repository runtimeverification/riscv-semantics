from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, NamedTuple, Protocol, final

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from pathlib import Path

    from pyk.kast import KInner
    from pyk.kast.outer import KDefinition
    from pyk.kcfg.explore import KCFGExplore
    from pyk.ktool.kprove import KProve
    from pyk.proof.reachability import APRProof
    from pyk.utils import BugReport


@final
class Dist(NamedTuple):
    haskell_dir: Path
    llvm_lib_dir: Path
    source_dirs: tuple[Path, ...]


@final
@dataclass(frozen=True)
class Config:
    dist: Dist
    proof_dir: Path
    bug_report: BugReport | None

    def __init__(self, *, dist: Dist, proof_dir: Path, bug_report: BugReport | None):
        object.__setattr__(self, 'dist', dist)
        object.__setattr__(self, 'proof_dir', proof_dir)
        object.__setattr__(self, 'bug_report', bug_report)

    @cached_property
    def kprove(self) -> KProve:
        from pyk.ktool.kprove import KProve

        return KProve(
            definition_dir=self.dist.haskell_dir,
            use_directory=self.proof_dir,
            bug_report=self.bug_report,
        )

    @property
    def definition(self) -> KDefinition:
        return self.kprove.definition

    @contextmanager
    def explore(self, *, id: str) -> Iterator[KCFGExplore]:
        from pyk.cterm.symbolic import CTermSymbolic
        from pyk.kcfg.explore import KCFGExplore
        from pyk.kore.rpc import BoosterServer, KoreClient

        with BoosterServer(
            {
                'kompiled_dir': self.dist.haskell_dir,
                'llvm_kompiled_dir': self.dist.llvm_lib_dir,
                'module_name': self.kprove.main_module,
                'bug_report': self.bug_report,
            }
        ) as server:
            with KoreClient('localhost', server.port, bug_report=self.bug_report, bug_report_id=id) as client:
                cterm_symbolic = CTermSymbolic(
                    kore_client=client,
                    definition=self.kprove.definition,
                )
                yield KCFGExplore(
                    id=id,
                    cterm_symbolic=cterm_symbolic,
                )


class Init(Protocol):
    def __call__(self, config: Config, spec_file: Path, claim_id: str) -> APRProof: ...


class Show(Protocol):
    def __call__(self, config: Config, term: KInner) -> str: ...


class Plugin(ABC):
    @abstractmethod
    def dist(self) -> Dist: ...

    def inits(self) -> Mapping[str, Init]:
        return {}

    def shows(self) -> Mapping[str, Show]:
        return {}
