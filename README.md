# KRISC-V: Semantics of RISC-V in K
This repository presents an executable formal semantics of the [RISC-V ISA](https://riscv.org/) using the [K framework](https://kframework.org/). It is currently under construction.

Presently, we support the [unprivileged RV32E base ISA](https://github.com/riscv/riscv-isa-manual/releases/tag/20240411) under the following assumptions:
- Memory is little-endian.
- There is a single hart with access to all of physical memory.
- All memory is readable, writeable, and executable.
- Instruction fetch is the only implicit memory access.
- Instruction memory is always coherent with main memory.

## Repository Structure
The following files constitute the KRISC-V semantics:
- [word.md](src/kriscv/kdist/riscv-semantics/word.md) provides a `Word` datatype representing `XLEN`-bit values, along with associated numeric operations.
- [riscv-instructions.md](src/kriscv/kdist/riscv-semantics/riscv-instructions.md) defines the syntax of disassembled instructions.
- [riscv-disassemble.md](src/kriscv/kdist/riscv-semantics/riscv-disassemble.md) implements the disassembler.
- [riscv.md](src/kriscv/kdist/riscv-semantics/riscv.md) is the main KRISC-V semantics, defining the configuration and transition rules to fetch and execute instructions.

## Installation
Prerequsites: `python >= 3.10`, `pip >= 20.0.2`, `poetry >= 1.3.2`.

```bash
poetry install
make kdist-build
```
## Usage
Execute a compiled RISC-V ELF file with the following command:
```bash
poetry -C kriscv run test.elf
```
The output shows the final K configuration, including the state of memory, all registers, and any encountered errors. Execution can also be halted at a particular global symbol by providing the `--end-symbol` flag.

## For Developers
Use `make` to run common tasks (see the [Makefile](Makefile) for a complete list of available targets).

* `make build`: Build wheel
* `make check`: Check code style
* `make format`: Format code
* `make test-unit`: Run unit tests
* `make test-integration`: Run integration tests

For interactive use, spawn a shell with `poetry shell` (after `poetry install`), then run an interpreter.
