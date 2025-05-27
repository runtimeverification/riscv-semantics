requires "riscv-semantics/riscv.md"

module SW-SPEC
  imports RISCV

  claim [id]:
    <instrs> (.K => #HALT) ~> #EXECUTE ... </instrs>
    <regs>
      1 |-> W(12)
      2 |-> W(24)
      3 |-> W(28)
      4 |-> W(4)
    </regs>
    <pc> W ( 0 => 8 ) </pc>
    <mem>
      #bytes ( b"\x23\xa0\x40\x00\x23\x20\x41\x00" )  // sw x4, 0(x1) ; sw x4, 0(x3)
      #empty ( 4 )
      (#bytes ( (b"\x00\x00\x00\x00" +Bytes X) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") =>
       #bytes ( b"\x04\x00\x00\x00" +Bytes X +Bytes b"\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00"))
      .SparseBytes
    </mem>
    <haltCond> ADDRESS ( W ( 8 ) ) </haltCond>
    requires lengthBytes(X) ==Int 4
endmodule
