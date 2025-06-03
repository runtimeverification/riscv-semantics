from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm.symbolic import CTermSymbolic
from pyk.kcfg.explore import KCFGExplore
from pyk.ktool.kprove import KProve
from pyk.proof.reachability import APRProof
from pyk.proof.show import APRProofShow

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from pyk.kast import KInner
    from pyk.kcfg.kcfg import NodeIdLike
    from pyk.kcfg.show import KCFGShow
    from pyk.ktool.kprint import KPrint
    from pyk.utils import BugReport


@dataclass
class SymTools:
    haskell_dir: Path
    llvm_lib_dir: Path
    proof_dir: Path
    bug_report: BugReport | None

    @staticmethod
    def default(*, proof_dir: Path, bug_report: str | Path | None = None) -> SymTools:
        from pyk.kdist import kdist

        return SymTools(
            haskell_dir=kdist.get('riscv-semantics.haskell'),
            llvm_lib_dir=kdist.get('riscv-semantics.llvm-lib'),
            proof_dir=proof_dir,
            bug_report=bug_report_arg(bug_report) if bug_report else None,
        )

    @cached_property
    def kprove(self) -> KProve:
        return KProve(definition_dir=self.haskell_dir, use_directory=self.proof_dir, bug_report=self.bug_report)

    @cached_property
    def proof_show(self) -> APRProofShow:
        return _APRProofShow(self.kprove)

    @contextmanager
    def explore(self, *, id: str) -> Iterator[KCFGExplore]:
        from pyk.kore.rpc import BoosterServer, KoreClient

        with BoosterServer(
            {
                'kompiled_dir': self.haskell_dir,
                'llvm_kompiled_dir': self.llvm_lib_dir,
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
        include_dirs = [Path(include) for include in includes] if includes else []

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


class _APRProofShow(APRProofShow):
    kprint: KPrint

    def __init__(self, kprint: KPrint):
        self.kprint = kprint

    def show(
        self,
        proof: APRProof,
        nodes: Iterable[NodeIdLike] = (),
        node_deltas: Iterable[tuple[NodeIdLike, NodeIdLike]] = (),
        to_module: bool = False,
        minimize: bool = False,
        omit_cells: Iterable[str] = (),
    ) -> list[str]:
        if node_deltas or to_module or minimize or omit_cells:
            # These potentially produce ill-typed terms that kore-print cannot handle
            raise ValueError('Unsupported feature')

        return super().show(
            proof=proof,
            nodes=nodes,
            node_deltas=node_deltas,
            to_module=to_module,
            minimize=minimize,
            omit_cells=omit_cells,
        )

    @cached_property
    def kcfg_show(self) -> KCFGShow:  # type: ignore [override]
        from types import SimpleNamespace

        from pyk.cterm.show import CTermShow
        from pyk.kcfg.show import KCFGShow, NodePrinter

        res = KCFGShow(
            defn=self.kprint.definition,
            node_printer=NodePrinter(
                cterm_show=CTermShow(
                    printer=self._print,
                    minimize=False,
                    break_cell_collections=False,
                ),
                full_printer=False,
            ),
        )

        # Patch res.pretty_printer
        res.pretty_printer = SimpleNamespace(
            definition=self.kprint.definition,
            print=self._print,
        )  # type: ignore [assignment]

        return res

    def _print(self, kast: KInner) -> str:
        from . import utils

        return utils.kast_print(kast, kprint=self.kprint)
