requires "riscv-semantics/riscv.md"

module LW-SPEC
  imports RISCV

  claim [id]:
    <instrs> (.K => #HALT) ~> #EXECUTE ... </instrs>
    <regs>
      1 |-> (W(16) => W(1))
      2 |-> (W(24) => signExtend ( ... bits: Bytes2Int ( substrBytes ( Y:Bytes , 0 , 4 ) , LE , Unsigned ) , signBitIdx: 32 ))
      3 |-> (W(28) => W(2))
    </regs>
    <pc> W ( 0 => 12 ) </pc>
    <mem>
      #bytes ( b"\x83\xa0\x00\x00\x03\x21\x01\x00\x83\xa1\x01\x00" )  // lw x1, 0(x1) ; lw x2, 0(x2) ; lw x3, 0(x3)
      #empty ( 4 )
      #bytes ( b"\x01\x00\x00\x00" +Bytes X +Bytes Y +Bytes b"\x02\x00\x00\x00")
      .SparseBytes
    </mem>
    <test>
      <haltCond> ADDRESS ( W ( 12 ) ) </haltCond>
    </test>
    requires lengthBytes(X) ==Int 4 andBool lengthBytes(Y) ==Int 4
endmodule