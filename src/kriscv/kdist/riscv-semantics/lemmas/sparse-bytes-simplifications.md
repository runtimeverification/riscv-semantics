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
  rule pickFront(#bytes(substrBytes(B, I, J) +Bytes _) _ , J0) => substrBytes(substrBytes(B, I, J), 0, J0)
    requires 0 <=Int I andBool I <=Int J andBool J <=Int lengthBytes(B)
     andBool J0 <=Int lengthBytes(substrBytes(B, I, J))
  [simplification(44), preserves-definedness]
  rule pickFront(#bytes(B +Bytes _) _ , I) => substrBytes(B, 0, I)
    requires I >Int 0 andBool I <=Int lengthBytes(B)    [simplification(45), preserves-definedness]
  rule pickFront(#bytes(B +Bytes BS) EF, I) => B +Bytes pickFront(#bytes(BS) EF, I -Int lengthBytes(B))
    requires I >Int lengthBytes(B)                      [simplification(45), preserves-definedness]

  rule dropFront(#bytes(B +Bytes BS) EF , I) => dropFront(#bytes(substrBytes(B, I, lengthBytes(B)) +Bytes BS) EF, 0) 
    requires I >Int 0 andBool I <Int lengthBytes(B)     [simplification(45), preserves-definedness]
  rule dropFront(#bytes(B +Bytes BS) EF, I) => dropFront(#bytes(BS) EF, I -Int lengthBytes(B)) 
    requires I >=Int lengthBytes(B)                     [simplification(45), preserves-definedness]
```


## writeByteBF

To write a byte to a symbolic sparse byte region, we need to:

```k
  rule writeBytesBF(#bytes(B +Bytes BS) EF, I, V, NUM) => #bytes(replaceAtBytes(B, I, Int2Bytes(NUM, V, LE)) +Bytes BS) EF
    requires I >=Int 0 andBool I +Int NUM <=Int lengthBytes(B)  [simplification(45)]
  rule writeBytesBF(#bytes(B +Bytes BS) EF, I, V, NUM) => prepend(substrBytes(B, 0, I) +Bytes Int2Bytes(NUM, V, LE), dropFront(#bytes(BS) EF, I +Int NUM -Int lengthBytes(B)))
    requires I <Int lengthBytes(B) andBool I +Int NUM >Int lengthBytes(B)    [simplification(45)]
  rule writeBytesBF(#bytes(B +Bytes BS) EF, I, V, NUM) => prepend(B, writeBytesBF(#bytes(BS) EF, I -Int lengthBytes(B), V, NUM))
    requires I >=Int lengthBytes(B)                             [simplification(45)]
```

```k
endmodule
```
