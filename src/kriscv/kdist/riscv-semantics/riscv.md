```k
requires "riscv-disassemble.md"
requires "riscv-instructions.md"

module RISCV
  imports RISCV-DISASSEMBLE
  imports RISCV-INSTRUCTIONS
  imports BYTES
  imports INT
  imports RANGEMAP

  configuration
    <mem> $MEM:RangeMap </mem>
    <pc> $PC:Int </pc>
endmodule
```
