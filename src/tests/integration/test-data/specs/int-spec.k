requires "riscv-semantics/riscv.md"

module INT-SPEC
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <regs>
     1  |-> (W(12 <<Int 8 <<Int 8) => W(786432))
     2  |-> (W(12 <<Int 16) => W(786432))
     3  |-> (W(W0 <<Int 8 <<Int 8) => W(W0 <<Int 16))
     4  |-> (W(W1 &Int 4294967295) => W(W1))
     5  |-> (W(W2 <<Int 16 &Int 4294967295) => W(W2 <<Int 16))
     6  |-> (W(b"\x12"[0] <<Int 16 &Int 4294967295) => W(1179648))
     7  |-> (W(Bytes2Int(b"\x00\x00\x12", LE, Unsigned)) => W(1179648))
     8  |-> (W(Bytes2Int(W3, LE, Unsigned) &Int 4294967295) => W(Bytes2Int(W3, LE, Unsigned)))
     9  |-> (W(W3[0] <<Int 16 &Int 4294967295) => W(Bytes2Int(b"\x00\x00" +Bytes substrBytes(W3, 0, 1 ), LE, Unsigned)))
     10 |-> (W(Bytes2Int(b"\x12\x34\x56\x78", LE, Unsigned) >>Int 8) => W(7886388))
     11 |-> (W(Bytes2Int(b"\x34\x56\x78", LE, Unsigned)) => W(7886388))
     12 |-> (W(Bytes2Int(substrBytes(W3, 4, 8), LE, Unsigned) >>Int 8) => W(Bytes2Int(substrBytes(W3, 5, 8), LE, Unsigned)))
     13 |-> (W(Bytes2Int(b"\x00" +Bytes substrBytes(W3, 5, 6), LE, Unsigned) <<Int 8 &Int 4294967295) => W(Bytes2Int(b"\x00\x00" +Bytes substrBytes(W3, 5 , 6 ), LE, Unsigned)))
     14 |-> (W(Bytes2Int(b"\x00\x12", LE, Unsigned) |Int Bytes2Int(b"\x34", LE, Unsigned)) => W(4660))
     15 |-> (W(Bytes2Int(reverseBytes(b"\x12\x34"), LE, Unsigned)) => W(4660))
     16 |-> (W(Bytes2Int(b"\x00" +Bytes substrBytes(W3, 6, 7), LE, Unsigned) |Int Bytes2Int(substrBytes(W3, 7, 8), LE, Unsigned)) => W(Bytes2Int(substrBytes(W3, 7, 8) +Bytes substrBytes(W3, 6, 7), LE, Unsigned)))
     17 |-> (W(Bytes2Int(b"\x00\x00\x00" +Bytes substrBytes(W3, 4, 8), LE, Unsigned) |Int Bytes2Int(b"\x00\x00" +Bytes substrBytes(W3, 5, 6), LE, Unsigned) |Int Bytes2Int(substrBytes(W3, 7, 8) +Bytes substrBytes(W3, 6, 7), LE, Unsigned)) => W(Bytes2Int(substrBytes(W3, 7, 8) +Bytes substrBytes(W3, 6, 7) +Bytes substrBytes(W3, 5, 6) +Bytes substrBytes(W3, 4, 8), LE, Unsigned)))
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires 0 <=Int W1 andBool W1 <Int 4294967296
 andBool 0 <=Int W2 andBool W2 <Int 256
 andBool lengthBytes(W3) ==Int 32
endmodule