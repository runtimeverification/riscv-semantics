requires "riscv-semantics/riscv.md"

module STORE-SYMBOLIC-BYTES
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> W ( 0 ) </pc>
    <mem>
    storeBytes(
        #bytes ( b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" ) .SparseBytes, 
        W(0), 
        X:Int,
        4
    ) =>
    #bytes ( Int2Bytes ( 1 , X:Int &Int 255 , LE ) +Bytes Int2Bytes ( 1 , X:Int >>Int 8 &Int 255 , LE ) +Bytes Int2Bytes ( 1 , X:Int >>Int 8 >>Int 8 &Int 255 , LE ) +Bytes Int2Bytes ( 1 , X:Int >>Int 8 >>Int 8 >>Int 8 , LE ) +Bytes b"\x00\x00\x00\x00" ) .SparseBytes
    </mem>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 4
endmodule
