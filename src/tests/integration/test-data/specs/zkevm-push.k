module ZKEVM-PUSH
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1 |-> ((Bytes2Int(OP0, LE, Unsigned) &Int 255) <<Int 8 &Int 4294967295 |Int 96 => Bytes2Int(b"`" +Bytes OP0, LE, Unsigned))
    </regs>
    <haltCond> ADDRESS(0) </haltCond>
    requires lengthBytes(OP0) ==Int 1
endmodule
