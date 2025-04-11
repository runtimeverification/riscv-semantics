from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cterm.symbolic import CTermSymbolic, cterm_symbolic
from pyk.kcfg.explore import KCFGExplore
from pyk.ktool.kprove import KProve
from pyk.proof.reachability import APRProof
from pyk.utils import BugReport
from pyk.cli.utils import bug_report_arg

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


@dataclass
class SymTools:
    haskell_dir: Path
    llvm_lib_dir: Path
    proof_dir: Path
    source_dirs: tuple[Path, ...]
    bug_report: BugReport | None

    @staticmethod
    def default(*, proof_dir: Path, bug_report: BugReport | None = None) -> SymTools:
        from pyk.kdist import kdist

        return SymTools(
            haskell_dir=kdist.get('riscv-semantics.haskell'),
            llvm_lib_dir=kdist.get('riscv-semantics.llvm-lib'),
            source_dirs=(kdist.get('riscv-semantics.source'),),
            proof_dir=proof_dir,
            bug_report= bug_report_arg(bug_report) if bug_report is not None else None,
        )

    @cached_property
    def kprove(self) -> KProve:
        return KProve(definition_dir=self.haskell_dir, use_directory=self.proof_dir, bug_report=self.bug_report)

    @contextmanager
    def explore(self, *, id: str) -> Iterator[KCFGExplore]:
        from pyk.kore.rpc import BoosterServer, KoreClient
        
        with cterm_symbolic(
            self.kprove.definition,
            self.haskell_dir,
            llvm_definition_dir=self.llvm_lib_dir,
            bug_report=self.bug_report,
            id=id if self.bug_report is None else None,
        ) as cts:
            yield KCFGExplore(cts, id=id)

    def prove(
        self,
        *,
        spec_file: str | Path,
        spec_module: str,
        claim_id: str,
        reinit: bool | None = None,
        max_depth: int | None = None,
        max_iterations: int | None = None,
        includes: Iterable[str | Path] | None = None,
    ) -> APRProof:
        from pyk.ktool.claim_loader import ClaimLoader
        from pyk.proof.reachability import APRProver

        spec_file = Path(spec_file)
        include_dirs = self.source_dirs + (tuple(Path(include) for include in includes) if includes is not None else ())

        claims = ClaimLoader(self.kprove).load_claims(
            spec_file=spec_file,
            spec_module_name=spec_module,
            claim_labels=[claim_id],
            include_dirs=include_dirs,
        )
        (claim,) = claims
        spec_label = f'{spec_module}.{claim_id}'

        if not reinit and APRProof.proof_data_exists(spec_label, self.proof_dir):
            # load an existing proof (to continue work on it)
            proof = APRProof.read_proof_data(proof_dir=self.proof_dir, id=f'{spec_module}.{claim_id}')
        else:
            # ignore existing proof data and reinitialize it from a claim
            proof = APRProof.from_claim(self.kprove.definition, claim=claim, logs={}, proof_dir=self.proof_dir)

        with self.explore(id=spec_label) as kcfg_explore:
            prover = APRProver(
                kcfg_explore=kcfg_explore,
                execute_depth=max_depth,
            )
            prover.advance_proof(proof, max_iterations=max_iterations)

        return proof
