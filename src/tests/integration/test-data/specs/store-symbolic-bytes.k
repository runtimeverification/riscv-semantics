module STORE-SYMBOLIC-BYTES
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> 0 </pc>
    <mem>
    storeBytes(
        #bytes ( b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" ) .SparseBytes, 
        0, 
        X:Int,
        4
    ) =>
    #bytes ( Int2Bytes ( 4 , X , LE ) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00" ) .SparseBytes
    </mem>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires lengthBytes(W0) ==Int 4
endmodule
