module BYTES-CONCAT-CONSECUTIVE
  imports RISCV

  claim [id]:
    <instrs> #CHECK_HALT => #HALT </instrs>
    <pc> 0 </pc>
    <mem>
      #bytes(b"\x00\x00\x00\x00" +Bytes substrBytes(reverseBytes(VALUE), 0, 4) +Bytes substrBytes(reverseBytes(VALUE), 4, 8) +Bytes substrBytes(reverseBytes(VALUE), 8, 12) +Bytes substrBytes(reverseBytes(VALUE), 12, 16) +Bytes substrBytes(reverseBytes(VALUE), 16, 20) +Bytes substrBytes(reverseBytes(VALUE), 20, 24) +Bytes substrBytes(reverseBytes(VALUE), 24, 28) +Bytes substrBytes(reverseBytes(VALUE), 28, 32) +Bytes b"\x00\x00\x00\x00" ) .SparseBytes 
    =>
    #bytes(b"\x00\x00\x00\x00" +Bytes reverseBytes(VALUE) +Bytes b"\x00\x00\x00\x00" ) .SparseBytes
    </mem>
    <haltCond> ADDRESS ( 0 ) </haltCond>
    requires lengthBytes(VALUE) ==Int 32
endmodule
