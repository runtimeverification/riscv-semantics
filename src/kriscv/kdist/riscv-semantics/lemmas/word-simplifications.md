# Word Simplifications

## Preliminaries

```k
requires "../word.md"
module WORD-SIMPLIFICATIONS
  imports WORD
```

## SignExtend

```k
  rule signExtend ( Bytes2Int ( B , LE , Unsigned ) , NumBits ) => W(Bytes2Int ( B , LE , Unsigned ))
    requires NumBits ==Int lengthBytes(B) *Int 8 [simplification(45), preserves-definedness]
```

```k
endmodule
```