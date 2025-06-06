from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, final

from pyk.proof.reachability import APRProof, APRProver

from .api import Config

if TYPE_CHECKING:
    from pyk.proof import ProofStatus
    from pyk.proof.show import APRProofNodePrinter
    from pyk.utils import BugReport

    from .api import Init, Plugin, Show


def create_prover(plugin_id: str, proof_dir: str | Path, *, bug_report: BugReport | None = None) -> KProveX:
    from ._loader import PLUGINS

    if plugin_id not in PLUGINS:
        raise ValueError(f'Unknown plugin: {plugin_id}')

    plugin = PLUGINS[plugin_id]
    proof_dir = Path(proof_dir)

    return KProveX(
        plugin=plugin,
        proof_dir=proof_dir,
        bug_report=bug_report,
    )


@final
@dataclass
class KProveX:
    plugin: Plugin
    proof_dir: Path
    bug_report: BugReport | None

    def __init__(
        self,
        plugin: Plugin,
        proof_dir: Path,
        *,
        bug_report: BugReport | None = None,
    ):
        self.plugin = plugin
        self.proof_dir = proof_dir
        self.bug_report = bug_report

        proof_dir.mkdir(parents=True, exist_ok=True)

    @cached_property
    def config(self) -> Config:
        return Config(
            dist=self.plugin.dist(),
            proof_dir=self.proof_dir,
            bug_report=self.bug_report,
        )

    def init_proof(
        self,
        spec_file: str | Path,
        claim_id: str,
        *,
        init_id: str | None = None,
        exist_ok: bool = False,
    ) -> str:
        spec_file = Path(spec_file)
        init = self._load_init(init_id=init_id)
        proof = init(config=self.config, spec_file=spec_file, claim_id=claim_id)
        if not exist_ok and APRProof.proof_data_exists(proof.id, self.proof_dir):
            raise ValueError(f'Proof with id already exists: {proof.id}')

        proof.write_proof_data()
        return proof.id

    def list_proofs(self) -> list[str]:
        raise ValueError('TODO')

    def list_nodes(self, proof_id: str) -> list[int]:
        proof = self._load_proof(proof_id)
        return [node.id for node in proof.kcfg.nodes]

    def advance_proof(
        self,
        proof_id: str,
        *,
        max_depth: int | None = None,
        max_iterations: int | None = None,
    ) -> ProofStatus:
        proof = self._load_proof(proof_id)

        with self.config.explore(id=proof_id) as kcfg_explore:
            prover = APRProver(
                kcfg_explore=kcfg_explore,
                execute_depth=max_depth,
            )
            prover.advance_proof(proof, max_iterations=max_iterations)

        return proof.status

    def show_proof(
        self,
        proof_id: str,
        *,
        show_id: str | None = None,
        truncate: bool = False,
    ) -> str:
        from pyk.proof.show import APRProofShow

        proof = self._load_proof(proof_id)
        node_printer = self._proof_node_printer(proof, show_id=show_id, full_printer=False)
        proof_show = APRProofShow(self.config.definition, node_printer=node_printer)
        lines = proof_show.show(proof)
        if truncate:
            lines = [_truncate(line, 120) for line in lines]
        return '\n'.join(lines)

    def view_proof(
        self,
        proof_id: str,
        *,
        show_id: str | None = None,
    ) -> None:
        from pyk.proof.tui import APRProofViewer

        proof = self._load_proof(proof_id)
        node_printer = self._proof_node_printer(proof, show_id=show_id, full_printer=False)
        viewer = APRProofViewer(proof, self.config.kprove, node_printer=node_printer)
        viewer.run()

    def prune_node(self, proof_id: str, node_id: str) -> list[int]:
        proof = self._load_proof(proof_id)
        res = proof.prune(node_id)
        proof.write_proof_data()
        return res

    def show_node(
        self,
        proof_id: str,
        node_id: str,
        *,
        show_id: str | None = None,
        truncate: bool = False,
    ) -> str:
        proof = self._load_proof(proof_id)
        node_printer = self._proof_node_printer(proof, show_id=show_id, full_printer=True)
        kcfg = proof.kcfg
        node = kcfg.node(node_id)
        lines = node_printer.print_node(kcfg, node)
        if truncate:
            lines = [_truncate(line, 120) for line in lines]
        return '\n'.join(lines)

    # Private helpers

    def _load_proof(self, proof_id: str) -> APRProof:
        return APRProof.read_proof_data(proof_dir=self.proof_dir, id=proof_id)

    def _load_init(self, *, init_id: str | None) -> Init:
        if init_id is None:
            from . import _default

            return _default.init_from_claims

        inits = self.plugin.inits()
        if init_id not in inits:
            raise ValueError(f'Unknown init function: {init_id}')

        return inits[init_id]

    def _load_show(self, *, show_id: str | None) -> Show:
        if show_id is None:
            from . import _default

            return _default.show_pretty_term

        shows = self.plugin.shows()
        if show_id not in shows:
            raise ValueError(f'Unknown show function: {show_id}')

        return shows[show_id]

    def _proof_node_printer(
        self,
        proof: APRProof,
        *,
        show_id: str | None = None,
        full_printer: bool = False,
    ) -> APRProofNodePrinter:
        from pyk.cterm.show import CTermShow
        from pyk.proof.show import APRProofNodePrinter

        show = self._load_show(show_id=show_id)
        printer = lambda kast: show(self.config, kast)
        return APRProofNodePrinter(
            proof=proof,
            cterm_show=CTermShow(
                printer=printer,
                minimize=False,
                break_cell_collections=False,
            ),
            full_printer=full_printer,
        )


def _truncate(line: str, n: int) -> str:
    if len(line) <= n:
        return line
    return line[: n - 3] + '...'
