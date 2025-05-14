requires "riscv-semantics/riscv.md"

module BYTES-INT
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> W ( 0 ) </pc>
    <regs>
     4 |-> (W(Bytes2Int(substrBytes( W0 +Bytes b"\x12\x34\x56\x78", 0, 4), LE, Unsigned)) => W(Bytes2Int(substrBytes( W0, 0, 4), LE, Unsigned)))
     5 |-> (W(Bytes2Int(substrBytes( W0 +Bytes b"\x01\x00\x00\x00", 32, 36), LE, Unsigned)) => W(1))
    </regs>
    <test>
      <haltCond> ADDRESS ( W ( 0 ) ) </haltCond>
    </test>
requires lengthBytes(W0) ==Int 32
endmodule