module ZKEVM-SLOAD
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1 |-> ((Bytes2Int(b"\x00\x00" +Bytes reverseBytes(substrBytes(KEY, 16, 18)), LE, Unsigned) |Int Bytes2Int(reverseBytes(substrBytes(KEY, 18, 20)) +Bytes b"\x00\x00", LE, Unsigned)) &Int 4294967295 => Bytes2Int(reverseBytes(substrBytes(KEY, 16, 20)), LE, Unsigned))
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires lengthBytes(KEY) ==Int 32
endmodule
