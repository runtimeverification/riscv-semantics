# RISC-V Architectural Tests
This directory contains the RISC-V Architectural Test Suite and associated configuration.

## Contents
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
   - Currently only supports compiling but not executing the tests.

## Running the Tests
### PyTest
These tests are run as part of `make test-integration` under `src/tests/integration/test_conformance.py`. Tests are selected based on the riscof-generated `test_list.yaml`. Failing tests under `failing.txt` will automatically be skipped.

### riscof
The full riscof DUT plugin is still under construction, so execution with riscof is currently unsupported.
