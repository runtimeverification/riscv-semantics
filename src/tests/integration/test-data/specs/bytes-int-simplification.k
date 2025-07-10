module BYTES-INT-SIMPLIFICATION
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1 |-> ((Bytes2Int(OP0, LE, Unsigned) &Int 255) <<Int 8 &Int 4294967295 |Int 96 => Bytes2Int(b"`" +Bytes OP0, LE, Unsigned))
     2 |-> (Bool2Word(239 ==Int Bytes2Int(b"`" +Bytes OP0, LE, Unsigned)) => 0)
     3 |-> (Bool2Word(239 ==Int Bytes2Int(b"a" +Bytes substrBytes(OP1, 0, 1), LE, Unsigned)) => 0)
    </regs>
    <haltCond> ADDRESS(0) </haltCond>
    requires lengthBytes(OP0) ==Int 1 andBool lengthBytes(OP1) ==Int 2
endmodule
