module STORE-SYMBOLIC-INDEX-OVERLAP-COUNTER
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
        .Map
    </regs>
    <pc> 0 </pc>
    <mem>
    // Perfect overlapping writes - I0's write completely covers I1's write
    storeBytes(I0, V1, 2,
    storeBytes(I1, V0, 1, #bytes ( b"\x00\x00" ) .SparseBytes))
    => 
    // Only I0's write remains since it completely covers I1's write
    #WB(true, I0, V1, 2, #bytes ( b"\x00\x00" ) .SparseBytes)
    </mem>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires // Perfect overlapping case: I1 is completely within I0's write range
        I0 <=Int I1 andBool I1 +Int 1 <=Int I0 +Int 2 // I1's write [I1, I1+1) is within I0's write [I0, I0+2)
endmodule 