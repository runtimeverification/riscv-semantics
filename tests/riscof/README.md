# RISC-V Architectural Tests
This directory contains the RISC-V Architectural Test Suite and associated configuration.

## Contents
### riscv-arch-test
The submodule containing the actual test files under `riscv-arch-test/riscv-test-suite`.

### failing.txt
A list of tests that are known to fail with the current implementation. Each line gives the path to a failing test file relative to the `riscv-semantics` repo root.

### config.ini
The [riscof configuration file](https://riscof.readthedocs.io/en/1.24.0/inputs.html?highlight=config.ini#config-ini-syntax) specifying the paths to our DUT and golden reference plugins. 

### krsicv
The [DUT plugin](https://riscof.readthedocs.io/en/1.24.0/plugins.html) for our RISC-V implementation. Consists of
- env
  - link.ld
     - Linker script used when compiling each test. 
     - Unmodified from the riscof model template.
   - model_test.h
     - Definition of macros used in the test suite.
     - Unmodified from the riscof model template, except that `RVMODEL_HALT` uses `t2` rather than `t5` because `t5` does not exist for the `rv32e` and `rv64e` ISAs.
- kriscv_isa.yaml
  - Specification of the supported ISA and extensions as described in [https://riscv-config.readthedocs.io/en/3.3.1/yaml-specs.html#isa-yaml-spec](https://riscv-config.readthedocs.io/en/3.3.1/yaml-specs.html#isa-yaml-spec)
- kriscv_platform.yaml
   - Specification of the platform as described in [https://riscv-config.readthedocs.io/en/3.3.1/yaml-specs.html#platform-yaml-spec](https://riscv-config.readthedocs.io/en/3.3.1/yaml-specs.html#platform-yaml-spec)
- riscof_kriscv.py
   - The actual plugin implementation for initializing, building, and running the test suite  with riscof.
   - Currently under construction.

### sail_cSim
Analogous to `kriscv`, but for the golden reference [Sail RISC-V model](https://github.com/riscv/sail-riscv). Taken from [https://gitlab.com/incoresemi/riscof-plugins/-/tree/master/sail_cSim](https://gitlab.com/incoresemi/riscof-plugins/-/tree/master/sail_cSim)

### work
The test working directory generated during a test run. After a test run, this will contain:
 - kriscv_isa_checked.yaml
   - Completion of `kriscv_isa.yaml` with all defaults made explicit.
 - kriscv_platform_checked.yaml
   - Completion of `kriscv_platform.yaml` with all defaults made explicit.  
 - database.yaml
    -  A database of all tests in the test suite and their associated info pulled from the various `RVTEST` macros.
- test_list.yaml
   - The list of supported tests to run based on the `kriscv` ISA and platform specs.
- rv(32|64)_(i|e)...
   - The working directory for each individual test.
   - Follows the same directory structure as the tests in `riscv-arch-test/riscv-test-suite`, but each `.S` file is replaced by a directory of the same name containing the compiled `.elf` and disassembled `.diss` files.

### work.lock
A lock file used to control concurrent accesses to the `work` directory by different test workers.

## Running the Tests
### PyTest
These tests are run as part of `make test-integration` under `src/tests/integration/test_conformance.py`. Tests are selected based on the riscof-generated `test_list.yaml`. Failing tests under `failing.txt` will automatically be skipped.

### riscof
The full riscof DUT plugin is still under construction, so execution with riscof is currently unsupported.

