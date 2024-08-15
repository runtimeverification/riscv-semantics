# RISC-V Architectural Tests
This directory contains the configuration for the `riscof` tool used to execute the RISC-V Architectural Test Suite.

## Contents
### config.ini
The [riscof configuration file](https://riscof.readthedocs.io/en/1.24.0/inputs.html?highlight=config.ini#config-ini-syntax) specifying the paths to our DUT and golden reference plugins.

### krsicv
The [DUT (Design Under Test) plugin](https://riscof.readthedocs.io/en/1.24.0/plugins.html) which builds and executes the test suite for our RISC-V implementation. Consists of
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
   - The actual plugin implementation for initializing, building, and running the test suite with riscof.

### sail_cSim
The [reference plugin](https://riscof.readthedocs.io/en/1.24.0/plugins.html) against which our RISC-V implementation is compared. Both plugins execute the test suite, then the results are compared by `riscof`. Based on [https://gitlab.com/incoresemi/riscof-plugins/-/tree/master/sail_cSim](https://gitlab.com/incoresemi/riscof-plugins/-/tree/master/sail_cSim).

## Running the Tests
Execute the tests with `make test-architectural`.
