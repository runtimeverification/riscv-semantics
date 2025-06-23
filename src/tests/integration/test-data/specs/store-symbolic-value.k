module STORE-SYMBOLIC-VALUE
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> 0 </pc>
    <mem>
    storeBytes(
        0, 
        X:Int,
        4,
        #bytes ( b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" ) .SparseBytes
    ) =>
    #bytes ( Int2Bytes ( 4 , X , LE ) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00" ) .SparseBytes
    </mem>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires lengthBytes(W0) ==Int 4
endmodule
