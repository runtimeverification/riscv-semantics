```k
module RISCV
imports BYTES
imports INT
imports RANGEMAP

configuration
  <mem> $MEM:RangeMap </mem>
  <pc> $PC:Int </pc>
endmodule
```
