module XX
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1  |-> (Bool2Word(0 <Int 0 -Int Bool2Word ( 4294967295 <Int Bytes2Int ( OFFSET:Bytes +Bytes b"\x00\x00\x00" , LE , Unsigned ) +Int 32 ) &Int 4294967295 |Int Bytes2Int ( OFFSET:Bytes +Bytes b"\x00\x00\x00" , LE , Unsigned ) +Int 32 &Int 4294967295) => 0)
     2  |-> (Bool2Word(0 <Int 0 -Int Bool2Word ( 4294967295 <Int X ) &Int 4294967295 |Int X &Int 4294967295) => 0)
     3  |-> (Bool2Word(0 <Int 0 -Int Z &Int 4294967295) => 0)
     4  |-> (Bool2Word(0 <=Int Z &Int 4294967295) => 1)
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires 0 <=Int X andBool 0 <=Int Y
endmodule

0 <Int (
  (0 -Int Bool2Word(4294967295 <Int (Bytes2Int(OFFSET:Bytes +Bytes b"\x00\x00\x00", LE, Unsigned) +Int 32))) &Int 4294967295
  |Int 
  (Bytes2Int(OFFSET:Bytes +Bytes b"\x00\x00\x00", LE, Unsigned) +Int 32) &Int 4294967295
)