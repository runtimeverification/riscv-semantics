module XX
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
    // 25 |-> (Bytes2Int(Int2Bytes(1, (Bytes2Int(substrBytes(reverseBytes(W3), 8, 12), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 8, 12), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned))) &Int 4294967295) >>Int 8, LE), LE, Unsigned) => ( Bytes2Int ( substrBytes ( reverseBytes ( W3:Bytes ) , 8 , 12 ) , LE , Unsigned ) +Int Bytes2Int ( substrBytes ( reverseBytes ( W0:Bytes ) , 8 , 12 ) , LE , Unsigned ) +Int Bool2Word ( 4294967295 <Int Bytes2Int ( substrBytes ( reverseBytes ( W3:Bytes ) , 4 , 8 ) , LE , Unsigned ) +Int Bytes2Int ( substrBytes ( reverseBytes ( W0:Bytes ) , 4 , 8 ) , LE , Unsigned ) +Int Bool2Word ( 4294967295 <Int Bytes2Int ( substrBytes ( reverseBytes ( W3:Bytes ) , 0 , 4 ) , LE , Unsigned ) +Int Bytes2Int ( substrBytes ( reverseBytes ( W0:Bytes ) , 0 , 4 ) , LE , Unsigned ) ) ) &Int 4294967295 ) >>Int 8 &Int 255)
     26 |-> (Bytes2Int(Int2Bytes(1, (X +Int Y +Int Z &Int 4294967295) >>Int 8, LE), LE, Unsigned) => (X +Int Y +Int Z &Int 4294967295 ) >>Int 8 &Int 255)
     27 |-> (Bytes2Int(Int2Bytes(1, (Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 4294967295) >>Int 8, LE), LE, Unsigned) => (Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 4294967295 ) >>Int 8 &Int 255)
     28 |-> (Bool2Word(0 <=Int Bytes2Int(substrBytes(reverseBytes(W3), 8, 12), LE, Unsigned)) => 1)
     // 26 |-> (Bool2Word(0 <=Int Bytes2Int(substrBytes(reverseBytes(W3), 8, 12), LE, Unsigned)) => 1)
     // 27 |-> (Bool2Word(0 <=Int Bytes2Int(substrBytes(reverseBytes(W0), 8, 12), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W3), 8, 12), LE, Unsigned)) => 1)
     // 28 |-> ((Bool2Word(0 <=Int Bytes2Int(substrBytes(reverseBytes(W3), 8, 12), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 8, 12), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned))))) => 1)
     // 29 |-> (Bool2Word(0 <=Int (Bytes2Int(substrBytes(reverseBytes(W3), 8, 12), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 8, 12), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned))) &Int 4294967295)) => 1)
     // 30 |-> (Bool2Word(0 <=Int X >>Int 8) => 1)
     // 31 |-> (Bool2Word(0 <=Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned)))) => 1)
     // 32 |-> (Bool2Word(0 <=Int (X +Int Y +Int Z &Int 4294967295) >>Int 8) => 1)
     // 33 |-> ((Bool2Word(0 <=Int Bytes2Int(substrBytes(reverseBytes(W3), 8, 12), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 8, 12), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned))) &Int 4294967295) >>Int 8) => 1)
     // 31 |-> (Bool2Word(0 <=Int (Bytes2Int(substrBytes(reverseBytes(W3), 8, 12), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 8, 12), LE, Unsigned) +Int Z &Int 4294967295) >>Int 8) => 1)
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires lengthBytes(W0) ==Int 32
 andBool lengthBytes(W1) ==Int 4
 andBool lengthBytes(W3) ==Int 32
 andBool 0 <=Int X andBool 0 <=Int Y andBool 0 <=Int Z
 // andBool 0 <=Int Bool2Word(0 <=Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 4, 8), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 4, 8), LE, Unsigned) +Int Bool2Word(4294967295 <Int Bytes2Int(substrBytes(reverseBytes(W3), 0, 4), LE, Unsigned) +Int Bytes2Int(substrBytes(reverseBytes(W0), 0, 4), LE, Unsigned))))
endmodule
