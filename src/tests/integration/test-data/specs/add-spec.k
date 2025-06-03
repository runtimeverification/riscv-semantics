module ADD-SPEC
  imports RISCV

  claim [id]:
    <instrs> (.K => #HALT) ~> #EXECUTE ... </instrs>
    <regs>
      1 |-> X
      2 |-> Y
      3 |-> (_ => Y +Word X)
    </regs>
    <pc> 0 => 4 </pc>
    <mem>
      #bytes ( b"\xb3\x01\x11\x00" )  // add x3, x2, x1
      .SparseBytes
    </mem>
    <haltCond> ADDRESS ( 4 ) </haltCond>
endmodule
