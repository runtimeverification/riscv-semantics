requires "riscv-semantics/riscv.md"

module ADD-SPEC
  imports RISCV

  claim [add]:
    <instrs> (.K => #HALT) ~> #EXECUTE ... </instrs>
    <regs>
      1 |-> X
      2 |-> Y
      3 |-> (_ => Y +Word X)
    </regs>
    <pc> W ( 0 => 4 ) </pc>
    <mem>
      #bytes ( b"\xb3\x01\x11\x00" )  // add x3, x2, x1
      .SparseBytes
    </mem>
    <test>
      <haltCond> ADDRESS ( W ( 4 ) ) </haltCond>
    </test>
endmodule
