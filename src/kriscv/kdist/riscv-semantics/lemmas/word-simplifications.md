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
  rule [bool2word-eq-0]: Bool2Word(B) ==Int 0 => notBool B [simplification]
  rule [bool2word-eq-1]: Bool2Word(B) ==Int 1 => B [simplification]


  rule [int-bool2word-or-ineq]: 0 <Int (0 -Int Bool2Word(4294967295 <Int X)) &Int 4294967295 |Int X &Int 4294967295 => true 
    requires 0 <Int X [simplification(45)]
```

```k
endmodule
```