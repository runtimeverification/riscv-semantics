from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from pyk.proof import ProofStatus

from kriscv.symtools import SymTools

from .utils import TEST_DATA_DIR

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final


SPEC_DIR: Final = TEST_DATA_DIR / 'specs'
SPEC_TESTS: Final = list(SPEC_DIR.glob('*.k'))


@dataclass
class SpecLoader:
    temp_dir: Path

    def __call__(self, file_name: str) -> Path:
        import shutil

        res = self.temp_dir / file_name
        shutil.copy(SPEC_DIR / file_name, res)
        return res


@pytest.fixture
def load_spec(tmp_path: Path) -> SpecLoader:
    return SpecLoader(temp_dir=tmp_path)


@pytest.fixture
def symtools(tmp_path: Path) -> SymTools:
    return SymTools.default(proof_dir=tmp_path)


@pytest.mark.parametrize(
    'spec_file',
    SPEC_TESTS,
    ids=[str(test.relative_to(SPEC_DIR)) for test in SPEC_TESTS],
)
def test_specs(
    load_spec: SpecLoader,
    symtools: SymTools,
    spec_file: Path,
) -> None:
    # Given
    spec_file = load_spec(spec_file.name)

    # When
    proof = symtools.prove(
        spec_file=spec_file,
        spec_module=spec_file.stem.upper(),
        claim_id=f'{spec_file.stem.upper()}.id',
    )

    # Then
    assert proof.status == ProofStatus.PASSED, f'Proof failed: {proof.failure_info}'
