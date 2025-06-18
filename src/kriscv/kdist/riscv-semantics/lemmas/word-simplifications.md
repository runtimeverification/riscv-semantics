# Word Simplifications

## Preliminaries

```k
requires "../word.md"
module WORD-SIMPLIFICATIONS
  imports WORD
```

## SignExtend

```k
  rule signExtend ( Bytes2Int ( B , LE , Unsigned ) , NumBits ) => Bytes2Int ( B , LE , Unsigned )
    requires NumBits ==Int lengthBytes(B) *Int 8 [simplification(45), preserves-definedness]
```

## Bool2Word

```k
  rule [bool2word-non-neg]: 0 <=Int Bool2Word(_) => true [simplification]
```

```k
endmodule
```