from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from pyk.proof import ProofStatus
from pyk.proof.show import APRProofShow

from kriscv.symtools import SymTools

from .utils import TEST_DATA_DIR

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final


SPEC_DIR: Final = TEST_DATA_DIR / 'specs'
SPEC_TESTS: Final = list(SPEC_DIR.glob('*.k'))
DEBUG_DIR: Final = TEST_DATA_DIR / 'debug'
BUG_REPORT: Final = TEST_DATA_DIR / 'debug' / 'bug-reports'


@dataclass
class SpecLoader:
    temp_dir: Path

    def __call__(self, file_name: str) -> Path:
        import shutil

        res = self.temp_dir / file_name
        shutil.copy(SPEC_DIR / file_name, res)
        return res


@pytest.fixture
def load_spec(tmp_path: Path, debug_mode: bool) -> SpecLoader:
    """Fixture to load spec files.
    In debug mode, uses DEBUG_DIR for persistent debugging.
    In normal mode, uses tmp_path for clean test isolation.
    """
    temp_dir = DEBUG_DIR if debug_mode else tmp_path
    temp_dir.mkdir(parents=True, exist_ok=True)
    return SpecLoader(temp_dir=temp_dir)


@pytest.fixture
def symtools(tmp_path: Path, debug_mode: bool) -> SymTools:
    """Fixture to create SymTools instance.
    In debug mode, uses DEBUG_DIR for persistent debugging.
    In normal mode, uses tmp_path for clean test isolation.
    """
    temp_dir = DEBUG_DIR if debug_mode else tmp_path
    temp_dir.mkdir(parents=True, exist_ok=True)
    return SymTools.default(proof_dir=temp_dir, bug_report=BUG_REPORT if debug_mode else None)


@pytest.mark.parametrize(
    'spec_file',
    SPEC_TESTS,
    ids=[str(test.relative_to(SPEC_DIR)) for test in SPEC_TESTS],
)
def test_specs(
    load_spec: SpecLoader,
    symtools: SymTools,
    debug_mode: bool,
    spec_file: Path,
) -> None:
    # Given
    spec_file = load_spec(spec_file.name)
    max_depth = 1 if debug_mode else 1000

    # When
    proof = symtools.prove(
        spec_file=spec_file,
        spec_module=spec_file.stem.upper(),
        claim_id=f'{spec_file.stem.upper()}.id',
        max_depth=max_depth,
    )

    if debug_mode:
        with open(DEBUG_DIR / f'{spec_file.stem}-proof.txt', 'w') as f:
            f.write('\n'.join(APRProofShow(symtools.kprove).show(proof, nodes=[node.id for node in proof.kcfg.nodes])))

    # Then

    assert proof.status == ProofStatus.PASSED, f'Proof failed: {proof.failure_info}'
