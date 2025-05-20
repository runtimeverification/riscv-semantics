requires "riscv-semantics/riscv.md"

module BYTES-INT
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <regs>
     8  |-> (W(Bytes2Int(replaceAtBytes (W0 +Bytes W3 +Bytes b"\x00\x00\x00\x00" , 64 , b"\x02" ), LE, Unsigned)) => W(Bytes2Int ( W0:Bytes +Bytes W3:Bytes +Bytes b"\x02\x00\x00\x00" , LE , Unsigned )))
     9  |-> (W(Bytes2Int(replaceAtBytes (b"\x00\x00", 0, b"\x01\x02"), LE, Unsigned)) => W(513))
     10 |-> (W(Bytes2Int(replaceAtBytes (W1, 2, b"\x01\x02"), LE, Unsigned)) => W(Bytes2Int(substrBytes ( W1:Bytes , 0 , 2 ) +Bytes b"\x01\x02", LE, Unsigned)))
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 32
 andBool lengthBytes(W1) ==Int 4
 andBool lengthBytes(W3) ==Int 32
endmodule