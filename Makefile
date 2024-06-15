POETRY     := poetry
POETRY_RUN := $(POETRY) run


default: check test-unit

all: check cov

.PHONY: clean
clean:
	rm -rf dist .coverage cov-* .mypy_cache .pytest_cache
	find -type d -name __pycache__ -prune -exec rm -rf {} \;

.PHONY: build
build:
	$(POETRY) build

.PHONY: poetry-install
poetry-install:
	$(POETRY) install


# Semantics

kdist-build: poetry-install
	$(POETRY) run kdist -v build riscv-semantics.llvm

kdist-clean: poetry-install
	$(POETRY) run kdist clean


# Tests

TEST_ARGS :=

test: test-all

test-all: poetry-install
	$(POETRY_RUN) pytest src/tests --maxfail=1 --verbose --durations=0 --numprocesses=4 --dist=worksteal $(TEST_ARGS)

test-unit: poetry-install
	$(POETRY_RUN) pytest src/tests/unit --maxfail=1 --verbose $(TEST_ARGS)

test-integration: poetry-install
	$(POETRY_RUN) pytest src/tests/integration --maxfail=1 --verbose --durations=0 --numprocesses=4 --dist=worksteal $(TEST_ARGS)

RISCOF_DIRS = $(shell find src/tests/integration/riscof -type d)
RISCOF_FILES = $(shell find src/tests/integration/riscof -type f -name '*')

tests/riscv-arch-test-compiled: tests/riscv-arch-test $(RISCOF_DIRS) $(RISCOF_FILES)
	$(POETRY_RUN) riscof run --suite tests/riscv-arch-test/riscv-test-suite --env tests/riscv-arch-test/riscv-test-suite/env --config src/tests/integration/riscof/config.ini --work-dir tests/riscv-arch-test-compiled --no-ref-run

# Coverage

COV_ARGS :=

cov: cov-all

cov-%: TEST_ARGS += --cov=kriscv --no-cov-on-fail --cov-branch --cov-report=term

cov-all: TEST_ARGS += --cov-report=html:cov-all-html $(COV_ARGS)
cov-all: test-all

cov-unit: TEST_ARGS += --cov-report=html:cov-unit-html $(COV_ARGS)
cov-unit: test-unit

cov-integration: TEST_ARGS += --cov-report=html:cov-integration-html $(COV_ARGS)
cov-integration: test-integration


# Checks and formatting

format: autoflake isort black
check: check-flake8 check-mypy check-autoflake check-isort check-black

check-flake8: poetry-install
	$(POETRY_RUN) flake8 src

check-mypy: poetry-install
	$(POETRY_RUN) mypy src

autoflake: poetry-install
	$(POETRY_RUN) autoflake --quiet --in-place src

check-autoflake: poetry-install
	$(POETRY_RUN) autoflake --quiet --check src

isort: poetry-install
	$(POETRY_RUN) isort src

check-isort: poetry-install
	$(POETRY_RUN) isort --check src

black: poetry-install
	$(POETRY_RUN) black src

check-black: poetry-install
	$(POETRY_RUN) black --check src


# Optional tools

SRC_FILES := $(shell find src -type f -name '*.py')

pyupgrade: poetry-install
	$(POETRY_RUN) pyupgrade --py310-plus $(SRC_FILES)
