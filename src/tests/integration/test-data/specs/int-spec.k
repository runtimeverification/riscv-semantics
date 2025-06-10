module INT-SPEC
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1  |-> ((12 <<Int 8 <<Int 8) => 786432)
     2  |-> ((12 <<Int 16) => 786432)
     3  |-> ((W0 <<Int 8 <<Int 8) => W0 <<Int 16)
     4  |-> ((W1 &Int 4294967295) => W1)
     5  |-> ((W2 <<Int 16 &Int 4294967295) => W2 <<Int 16)
     6  |-> ((b"\x12"[0] <<Int 16 &Int 4294967295) => 1179648)
     7  |-> ((Bytes2Int(b"\x00\x00\x12", LE, Unsigned)) => 1179648)
     8  |-> ((Bytes2Int(W3, LE, Unsigned) &Int 4294967295) => Bytes2Int(W3, LE, Unsigned))
     9  |-> ((W3[0] <<Int 16 &Int 4294967295) => Bytes2Int(b"\x00\x00" +Bytes substrBytes(W3, 0, 1 ), LE, Unsigned))
     10 |-> ((Bytes2Int(b"\x12\x34\x56\x78", LE, Unsigned) >>Int 8) => 7886388)
     11 |-> ((Bytes2Int(b"\x34\x56\x78", LE, Unsigned)) => 7886388)
     12 |-> ((Bytes2Int(substrBytes(W3, 4, 8), LE, Unsigned) >>Int 8) => Bytes2Int(substrBytes(W3, 5, 8), LE, Unsigned))
     13 |-> ((Bytes2Int(b"\x00" +Bytes substrBytes(W3, 5, 6), LE, Unsigned) <<Int 8 &Int 4294967295) => Bytes2Int(b"\x00\x00" +Bytes substrBytes(W3, 5 , 6 ), LE, Unsigned))
     14 |-> ((Bytes2Int(b"\x00\x12", LE, Unsigned) |Int Bytes2Int(b"\x34", LE, Unsigned)) => 4660)
     15 |-> ((Bytes2Int(reverseBytes(b"\x12\x34"), LE, Unsigned)) => 4660)
     16 |-> ((Bytes2Int(b"\x00" +Bytes substrBytes(W3, 6, 7), LE, Unsigned) |Int Bytes2Int(substrBytes(W3, 7, 8), LE, Unsigned)) => Bytes2Int(reverseBytes(substrBytes(W3, 6, 8)), LE, Unsigned))
     17 |-> ((Bytes2Int(b"\x00\x00\x00" +Bytes substrBytes(W3, 4, 8), LE, Unsigned) |Int Bytes2Int(b"\x00\x00" +Bytes substrBytes(W3, 5, 6), LE, Unsigned) |Int Bytes2Int(substrBytes(W3, 6, 7) +Bytes substrBytes(W3, 7, 8), LE, Unsigned)) => Bytes2Int(substrBytes(W3, 6, 7) +Bytes substrBytes(W3, 7, 8) +Bytes substrBytes(W3, 5, 6) +Bytes substrBytes(W3, 4, 8), LE, Unsigned))
     18 |-> ((W1 &Int 255) &Int 4294967295 => W1 &Int 255)
     19 |-> (((W1 &Int 255) +Int W2) &Int 255 => (W1 +Int W2) &Int 255)
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires 0 <=Int W1 andBool W1 <Int 4294967296
 andBool 0 <=Int W2 andBool W2 <Int 256
 andBool lengthBytes(W3) ==Int 32
endmodule
