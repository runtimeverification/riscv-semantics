from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


REPO_ROOT: Final = Path(__file__).parents[2].resolve(strict=True)
TESTS_DIR: Final = (REPO_ROOT / 'tests').resolve(strict=True)


def _failing_tests() -> set[Path]:
    return {
        (TESTS_DIR / test_path).resolve(strict=True)
        for test_path in (TESTS_DIR / 'failing.txt').read_text().splitlines()
    }


FAILING_TESTS: Final = _failing_tests()
