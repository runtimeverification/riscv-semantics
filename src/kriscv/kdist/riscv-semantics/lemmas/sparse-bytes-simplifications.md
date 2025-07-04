# Sparse Bytes Simplifications

This module contains lemmas specific to sparse bytes in `sparse-bytes.md`. If you want to reuse sparse bytes to build your own semantics' memory model, you can use this module to ease your symbolic execution.

## Preliminaries

```k
requires "../sparse-bytes.md"
module SPARSE-BYTES-SIMPLIFICATIONS
  imports SPARSE-BYTES
```

## pickFront and dropFront

For symbolic execution, we need to tackle the patterns of `#bytes(B +Bytes _) _` and `#bytes(B +Bytes BS) EF` to obtain as exact as possible values for `pickFront`.

```k
  rule pickFront(J0, #bytes(substrBytes(B, I, J) +Bytes _) _) => substrBytes(substrBytes(B, I, J), 0, J0)
    requires 0 <=Int I andBool I <=Int J andBool J <=Int lengthBytes(B)
     andBool J0 <=Int lengthBytes(substrBytes(B, I, J))
  [simplification(44), preserves-definedness]
  rule pickFront(I, #bytes(B +Bytes _) _) => substrBytes(B, 0, I)
    requires I >Int 0 andBool I <=Int lengthBytes(B)    [simplification(45), preserves-definedness]
  rule pickFront(I, #bytes(B +Bytes BS) EF) => B +Bytes pickFront(I -Int lengthBytes(B), #bytes(BS) EF)
    requires I >Int lengthBytes(B)                      [simplification(45), preserves-definedness]

  rule dropFront(I, #bytes(B +Bytes BS) EF) => dropFront(0, #bytes(substrBytes(B, I, lengthBytes(B)) +Bytes BS) EF) 
    requires I >Int 0 andBool I <Int lengthBytes(B)     [simplification(45), preserves-definedness]
  rule dropFront(I, #bytes(B +Bytes BS) EF) => dropFront(I -Int lengthBytes(B), #bytes(BS) EF) 
    requires I >=Int lengthBytes(B)                     [simplification(45), preserves-definedness]
```


## writeByteBF

To write a byte to a symbolic sparse byte region, we need to:

```k
  rule writeBytesBF(I, V, NUM, #bytes(B +Bytes BS) EF) => #bytes(replaceAtBytes(B, I, Int2Bytes(NUM, V, LE)) +Bytes BS) EF
    requires I >=Int 0 andBool I +Int NUM <=Int lengthBytes(B)  [simplification(45)]
  rule writeBytesBF(I, V, NUM, #bytes(B +Bytes BS) EF) => prepend(substrBytes(B, 0, I) +Bytes Int2Bytes(NUM, V, LE), dropFront(I +Int NUM -Int lengthBytes(B), #bytes(BS) EF))
    requires I <Int lengthBytes(B) andBool I +Int NUM >Int lengthBytes(B)    [simplification(45)]
  rule writeBytesBF(I, V, NUM, #bytes(B +Bytes BS) EF) => prepend(B, writeBytesBF(I -Int lengthBytes(B), V, NUM, #bytes(BS) EF))
    requires I >=Int lengthBytes(B)                             [simplification(45)]
```

```k
endmodule
```
