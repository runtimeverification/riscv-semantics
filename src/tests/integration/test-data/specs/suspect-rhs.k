module SUSPECT-RHS
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <regs>
     1 |-> (Bytes2Int(Int2Bytes(1, (Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 4294967295) >>Int 8, LE), LE, Unsigned) => (Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 4294967295 ) >>Int 8 &Int 255) // fail
     2 |-> (Bytes2Int(Int2Bytes(1, (Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 4294967295), LE), LE, Unsigned) => (Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 255 )) // pass
     // check if >>Int 8 > 0
     3 |-> (Bool2Word(0 <=Int (Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 4294967295) >>Int 8) => 1) // fail
     4 |-> (Bool2Word(0 <=Int X >>Int 8) => 1) // pass
     5 |-> (Bool2Word(0 <=Int Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 4294967295) => 1) // pass
     6 |-> (-1 &Int 255 => 255) // 
    </regs>
    <haltCond> ADDRESS ( 0 ) </haltCond>
requires lengthBytes(W0) ==Int 32
 andBool lengthBytes(W1) ==Int 4
 andBool lengthBytes(W3) ==Int 32
 andBool 0 <=Int X andBool 0 <=Int Y andBool 0 <=Int Z
 // andBool 0 <=Int (Bytes2Int(substrBytes(W3, 8, 12), LE, Unsigned) +Int Y +Int Z &Int 4294967295) >>Int 8
 
endmodule
