module ZKEVM-MSTORE-0
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1  |-> (Bool2Word(0 <Int (0 -Int Bool2Word(4294967295 <Int X)) &Int 4294967295 |Int X &Int 4294967295) => 1)
     2  |-> (Bool2Word(0 <=Int Bytes2Int ( OFFSET:Bytes +Bytes b"\x00\x00\x00" , LE , Unsigned )) => 1)
     3  |-> (Bool2Word(0 <Int Bytes2Int ( OFFSET:Bytes +Bytes b"\x00\x00\x00" , LE , Unsigned ) +Int 32) => 1)
     4  |-> (Bool2Word(0 <Int 0 -Int Bool2Word ( 4294967295 <Int Bytes2Int ( OFFSET:Bytes +Bytes b"\x00\x00\x00" , LE , Unsigned ) +Int 32 ) &Int 4294967295 |Int Bytes2Int ( OFFSET:Bytes +Bytes b"\x00\x00\x00" , LE , Unsigned ) +Int 32 &Int 4294967295) => 1)
     // 5  |-> (Bool2Word(4294967295 <Int Bytes2Int ( OFFSET:Bytes +Bytes b"\x00\x00\x00" , LE , Unsigned ) +Int 32) => 0)
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires 0 <Int X andBool 0 <=Int Y andBool 0 <Int Z
     andBool lengthBytes(OFFSET) ==Int 1
endmodule
