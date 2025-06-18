module XX
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1 |-> (Bool2Word(Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned)) &Int 4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned)) => Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned))))
     2 |-> (Bool2Word(Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) <=Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned))) => 1)
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires lengthBytes(W0) ==Int 32
 andBool lengthBytes(W1) ==Int 4
 andBool lengthBytes(W3) ==Int 32
 andBool 0 <=Int X andBool 0 <=Int Y andBool 0 <=Int Z
endmodule
