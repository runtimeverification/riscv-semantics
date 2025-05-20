requires "riscv-semantics/riscv.md"

module BYTES-INT
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <regs>
     1 |-> (W(Bytes2Int (b"\x12\x34\x56\x78", LE, Unsigned) &Int 65280) => W(13312))
     2 |-> (W(b"\x12\x34\x56\x78" [ 1 ] <<Int 8) => W(13312))
     3 |-> (W(Bytes2Int (substrBytes(W0, 0, 4), LE, Unsigned ) &Int 65280) => W(W0 [ 1 ] <<Int 8))
     4 |-> (W(Bytes2Int(substrBytes(b"\x01\x02", 0, 1), LE, Unsigned) &Int 65280) => W(0))
     5 |-> (W(Bytes2Int(substrBytes(W0, 0, 1), LE, Unsigned) &Int 65280) => W(0))
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 32
endmodule