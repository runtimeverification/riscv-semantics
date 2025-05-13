from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

    from pyk.kast import KInner
    from pyk.proof.reachability import APRProof

    from .api import Config, Init, Show


def init_from_claims(config: Config, spec_file: Path, claim_id: str) -> APRProof:
    from pyk.ktool.claim_loader import ClaimLoader
    from pyk.proof.reachability import APRProof

    spec_module, claim_label = claim_id.split('.', 1)
    include_dirs = config.dist.source_dirs

    claims = ClaimLoader(config.kprove).load_claims(
        spec_file=spec_file,
        spec_module_name=spec_module,
        claim_labels=[claim_label],
        include_dirs=include_dirs,
    )
    (claim,) = claims

    proof = APRProof.from_claim(
        config.kprove.definition,
        claim=claim,
        logs={},
        proof_dir=config.proof_dir,
    )
    return proof


def show_pretty_term(config: Config, term: KInner) -> str:
    from pyk.konvert import kast_to_kore
    from pyk.kore.tools import kore_print

    kore = kast_to_kore(config.definition, term)
    text = kore_print(kore, definition_dir=config.dist.haskell_dir)
    return text


# Check signatures
_default_init: Final[Init] = init_from_claims
_default_show: Final[Show] = show_pretty_term
