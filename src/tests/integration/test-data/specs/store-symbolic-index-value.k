module STORE-SYMBOLIC-INDEX-VALUE
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> 0 </pc>
    <mem>
    storeBytes(0 , V6, 4,
    storeBytes(I2, V5, 4,
    storeBytes(I1, V4, 2,
    storeBytes(I0, V3, 4,
    storeBytes(I2, V2, 2,
    storeBytes(I1, V1, 4,
    storeBytes(I0, V0, 4, #bytes ( b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" ) .SparseBytes)))))))
    => // No way to simplify this without any information about the index. Just eliminate the writes on the same index.
    #WB(true, I1, V4, 2,
    #WB(true, I1, V1, 4,
    #WB(true, I0, V3, 4,
    #WB(true, I2, V5, 4, 
    #bytes (Int2Bytes(4, V6, LE) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00") .SparseBytes))))
    </mem>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    //  requires 0 =/=Int I0 andBool 0 =/=Int I1 andBool 0 =/=Int I2
endmodule
