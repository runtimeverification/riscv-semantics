requires "riscv-semantics/riscv.md"

module BYTES-INT
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <regs>
     1  |-> (W(Bytes2Int (b"\x12\x34\x56\x78", LE, Unsigned) &Int 65280) => W(13312))
     2  |-> (W(b"\x12\x34\x56\x78" [ 1 ] <<Int 8) => W(13312))
     3  |-> (W(Bytes2Int (substrBytes(W0, 0, 4), LE, Unsigned ) &Int 65280) => W(W0 [ 1 ] <<Int 8))
     4  |-> (W(Bytes2Int(substrBytes(b"\x01\x02", 0, 1), LE, Unsigned) &Int 65280) => W(0))
     5  |-> (W(Bytes2Int(substrBytes(W0, 0, 1), LE, Unsigned) &Int 65280) => W(0))
     6  |-> (W(Bytes2Int(substrBytes( W0 +Bytes b"\x12\x34\x56\x78", 0, 4), LE, Unsigned)) => W(Bytes2Int(substrBytes( W0, 0, 4), LE, Unsigned)))
     7  |-> (W(Bytes2Int(substrBytes( W0 +Bytes b"\x01\x00\x00\x00", 32, 36), LE, Unsigned)) => W(1))
     8  |-> (W(Bytes2Int(replaceAtBytes (W0 +Bytes W3 +Bytes b"\x00\x00\x00\x00" , 64 , b"\x02" ), LE, Unsigned)) => W(Bytes2Int ( W0:Bytes +Bytes W3:Bytes +Bytes b"\x02\x00\x00\x00" , LE , Unsigned )))
     9  |-> (W(Bytes2Int(replaceAtBytes (b"\x00\x00", 0, b"\x01\x02"), LE, Unsigned)) => W(513))
     10 |-> (W(Bytes2Int(replaceAtBytes (W1, 2, b"\x01\x02"), LE, Unsigned)) => W(Bytes2Int(substrBytes ( W1:Bytes , 0 , 2 ) +Bytes b"\x01\x02", LE, Unsigned)))
     11 |-> (W(Bytes2Int(substrBytes(b"\x00", 1, 1), LE, Unsigned)) => W(0))
     12 |-> (W(Bytes2Int(Int2Bytes ( 4 , Bytes2Int (W1, LE, Unsigned), LE ), LE, Unsigned)) => W(Bytes2Int(W1, LE, Unsigned)))
     13 |-> (W(Bytes2Int(Int2Bytes ( 4 , Bytes2Int ( substrBytes ( W0:Bytes , 31 , 32 ) +Bytes substrBytes ( W0:Bytes , 30 , 31 ) +Bytes substrBytes ( W0:Bytes , 29 , 30 ) +Bytes substrBytes ( W0:Bytes , 28 , 32 ) , LE , Unsigned ) , LE ), LE, Unsigned)) => W(Bytes2Int(substrBytes ( W0:Bytes , 31 , 32 ) +Bytes substrBytes ( W0:Bytes , 30 , 31 ) +Bytes substrBytes ( W0:Bytes , 29 , 30 ) +Bytes substrBytes ( W0:Bytes , 28 , 29), LE, Unsigned)))
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 32
 andBool lengthBytes(W1) ==Int 4
 andBool lengthBytes(W3) ==Int 32
endmodule