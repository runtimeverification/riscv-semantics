module READ-SYMBOLIC-INDEX-VALUE
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <regs>
    // read from #bytes
        1 |-> (readBytes(4, 4, 
          #WB(true, I1, V0, 2,
          #WB(true, I1, V1, 4,
          #WB(true, I0, V2, 4,
          #WB(true, I2, V3, 4, 
          #bytes (b"\x00\x00\x00\x00" +Bytes Int2Bytes(4, V4, LE) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00") .SparseBytes)))))
          => V4)
    // read I2 with same number of bytes
        2 |-> (readBytes(I2, 4,
          #WB(true, I1, V0, 2,
          #WB(true, I1, V1, 4,
          #WB(true, I0, V2, 4,
          #WB(true, I2, V3, 4, 
          #bytes (Int2Bytes(4, V4, LE) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00") .SparseBytes)))))
          => V3)
    // read I2 with smaller number of bytes
        3 |-> (readBytes(I2, 2,
          #WB(true, I1, V0, 2,
          #WB(true, I1, V1, 4,
          #WB(true, I0, V2, 4,
          #WB(true, I2, V3, 4, 
          #bytes (Int2Bytes(4, V4, LE) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00") .SparseBytes)))))
          => V3 &Int 65535)
    // DISALLOWED: read with more number of bytes (8 bytes, but only 4 stored) 
    // read I1 with 2 bytes
        4 |-> (readBytes(I1, 2,
          #WB(true, I1, V0, 2,
          #WB(true, I1, V1, 4,
          #WB(true, I0, V2, 4,
          #WB(true, I2, V3, 4, 
          #bytes (Int2Bytes(4, V4, LE) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00") .SparseBytes)))))
          => V0 &Int 65535)
    // read I1 with 4 bytes
        5 |-> (readBytes(I1, 4,
          #WB(true, I1, V0, 2,
          #WB(true, I1, V1, 4,
          #WB(true, I0, V2, 4,
          #WB(true, I2, V3, 4, 
          #bytes (Int2Bytes(4, V4, LE) +Bytes b"\x00\x00\x00\x00\x00\x00\x00\x00") .SparseBytes)))))
          => Bytes2Int(Int2Bytes(2, V0, LE) +Bytes Int2Bytes(2, V1 >>Int 16, LE), LE, Unsigned))
    </regs>
    <pc> 0 </pc>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    // index not equal to 0
    requires 4 =/=Int I0 andBool 4 =/=Int I1 andBool 4 =/=Int I2
    // different indices
    andBool  I0 =/=Int I1 andBool I0 =/=Int I2 andBool  I1 =/=Int I2
    // values are within range
    andBool  0 <=Int V0 andBool V0 <=Int 65535
    andBool  0 <=Int V1 andBool V1 <=Int 4294967295
    andBool  0 <=Int V2 andBool V2 <=Int 4294967295
    andBool  0 <=Int V3 andBool V3 <=Int 4294967295
    andBool  0 <=Int V4 andBool V4 <=Int 4294967295
endmodule

