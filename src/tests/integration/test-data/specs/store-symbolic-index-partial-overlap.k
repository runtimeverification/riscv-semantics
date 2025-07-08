module STORE-SYMBOLIC-INDEX-PARTIAL-OVERLAP
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> 0 </pc>
    <mem>
    // Partial overlapping writes - only part of the writes overlap
    storeBytes(I0, V1, 2,
    storeBytes(I1, V0, 2, #bytes ( b"\x00\x00\x00\x00" ) .SparseBytes))
    => 
    // Ordering is preserved
    #WB(true, I0, V1, 2, 
    #WB(true, I1, V0, 2, #bytes ( b"\x00\x00\x00\x00" ) .SparseBytes))
    </mem>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires // Partial overlapping case: I0 starts 1 byte after I1, so they overlap by 1 byte
        I0 ==Int I1 +Int 1 // I1 writes [I1, I1+2), I0 writes [I1+1, I1+3), overlap at [I1+1, I1+2)
endmodule 