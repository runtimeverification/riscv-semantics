# Tests
This directory contains the input RISC-V files for various tests.

## Contents

### failing.txt
A list of tests that are known to fail under the current implementation. Each line consists of a single path to a failing test file. Paths are given relative to the `riscv-semantics/tests` directory.

### riscv-arch-test(-compiled)
The official RISC-V Architectural Test Suite. These are exercised in `src/tests/integration/test_conformance.py` as part of `make test-integration`.

The test source files can be found under `riscv-arch-test/riscv-test-suite` and are compiled by calling `make tests/riscv-arch-test-compiled` from the repository root. This will populate the `riscv-arch-test-compiled` directory with the following contents:
- `database.yaml`
  - A database of all tests in the suite with associated information pulled from `RVTEST` macros
- `test_list.yaml`
  - A list of selected tests to run based on the supported ISA and platform in `kriscv_isa_checked.yaml` and `kriscv_platform_checked.yaml`
- `kriscv_isa_checked.yaml`
  - Completion of `src/tests/integration/riscof/kriscv/kriscv_isa.yaml`, checked for well-formedness and with all defaults made explicit
- `kriscv_platform_checked.yaml`
  - Completion of `src/tests/integration/riscof/kriscv/kriscv_platform.yaml`, checked for well-formedness with all defaults made explicit
- `Makefile.DUT-kriscv`
  - The generated Makefile which was used to compile the test suite
- `rv(32|64)(i|e)_...`
  - The actual compiled test files for input to `kriscv`
  - The directory structure mirrors `riscv-arch-test/riscv-test-suite`, but with each `<test_name>.S` test file replaced by a directory of the same name containing:
      - `<test_name>.s`, the pre-linking RISC-V ASM
      - `<test_name>.elf`, the fully compiled object file
      - `<test_name>.disass`, the disassembly of the compiled object file

### simple
A suite of handwritten RISC-V tests. These are exercised in `src/tests/integration/test_integration.py` as part of `make test-simple` or `make test-integration`.

Each test consists of an input RISC-V ASM file `test.S` and a corresponding assertion file `test.S.assert`.

The input is compiled with
```
riscv64-unknown-elf-gcc -nostdlib -nostartfiles -static -march=rv32e -mabi=ilp32e -mno-relax -mlittle-endian -Xassembler -mno-arch-attr test.S
```
and must define global symbols `_start` and `_halt`. See the convenience macros defined in `simple.h`.

The assertion file must be in YAML format and may contain the following entries:
- `regs`, a dictionary of entries `i: val` asserting that register `xi` has value `val`
  - `i` must be in the range `[0, 15]`
  - `val` must be a 32-bit integer, either signed or unsigned
- `mem`, a dictionary of entries `offset: val` asserting that memory address `_mem + offset` has value `val`
  - `offset` must be an unsigned integer
  - `val` must be an 8-bit integer, either signed or unsigned

The test is executed with the PC initially set to `_start` and will halt when the PC reaches `_halt`. The final configuration is then checked against each of entries in the assertion file.
