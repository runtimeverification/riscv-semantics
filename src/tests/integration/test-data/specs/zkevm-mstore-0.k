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
     6  |-> (Bool2Word(Y <=Int Z) => 0)
     7  |-> (Bool2Word(Z <=Int 4294967295) => 1)
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires 0 <Int X 
     andBool lengthBytes(OFFSET) ==Int 1
     andBool notBool (Y <=Int Z)
     andBool notBool (Bool2Word(Z <=Int 4294967295) ==Int 0)
endmodule
