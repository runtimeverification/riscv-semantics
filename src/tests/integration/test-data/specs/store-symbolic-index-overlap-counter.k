module STORE-SYMBOLIC-INDEX-OVERLAP-COUNTER
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> 0 </pc>
    <mem>
    // Overlapping writes - should preserve original order when indices overlap
    storeBytes(I0, V1, 2,
    storeBytes(I1, V0, 1, #bytes ( b"\x00\x00" ) .SparseBytes))
    => 
    // Keep original order when overlapping - no simplification
    #WB(true, I0, V1, 2, 
    #WB(true, I1, V0, 1, #bytes ( b"\x00\x00" ) .SparseBytes))
    </mem>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires // Overlapping case: I0 [I0, I0+2) overlaps with I1 [I1, I1+1)
        I0 <=Int I1 andBool I1 <Int I0 +Int 2 // I1 is within the range of I0's write
endmodule 