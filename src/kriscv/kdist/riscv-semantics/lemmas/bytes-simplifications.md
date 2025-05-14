# Bytes Simplifications

## Preliminaries

```k
module BYTES-SIMPLIFICATIONS [symbolic]
  imports BYTES
  imports INT
  imports K-EQUAL
  imports BOOL
```

## Bytes Equality Lemmas

```k
  rule [bytes-not-equal-length]:
    BA1:Bytes ==K BA2:Bytes => false
    requires lengthBytes(BA1) =/=Int lengthBytes(BA2)
    [simplification]
    
```

## Bytes Concatenation Lemmas

```k
    rule [bytes-equal-concat-split-k]:
      A:Bytes +Bytes B:Bytes ==K C:Bytes +Bytes D:Bytes => A ==K C andBool B ==K D
      requires lengthBytes(A) ==Int lengthBytes(C)
        orBool lengthBytes(B) ==Int lengthBytes(D)
      [simplification]

    rule [bytes-equal-concat-split-ml]:
      { A:Bytes +Bytes B:Bytes #Equals C:Bytes +Bytes D:Bytes } => { A #Equals C } #And { B #Equals D }
      requires lengthBytes(A) ==Int lengthBytes(C)
        orBool lengthBytes(B) ==Int lengthBytes(D)
      [simplification]

    rule [bytes-concat-empty-right]: B:Bytes +Bytes .Bytes  => B [simplification]
    rule [bytes-concat-empty-left]:   .Bytes +Bytes B:Bytes => B [simplification]
    rule [bytes-concat-concrete-empty-right]: B:Bytes +Bytes b"" => B [simplification]
    rule [bytes-concat-concrete-empty-left]:   b"" +Bytes B:Bytes => B [simplification]

    rule [bytes-concat-right-assoc-symb-l]: (B1:Bytes +Bytes B2:Bytes) +Bytes B3:Bytes => B1 +Bytes (B2 +Bytes B3) [symbolic(B1), simplification(40)]
    rule [bytes-concat-right-assoc-symb-r]: (B1:Bytes +Bytes B2:Bytes) +Bytes B3:Bytes => B1 +Bytes (B2 +Bytes B3) [symbolic(B2), simplification(40)]
    rule [bytes-concat-left-assoc-conc]:    B1:Bytes +Bytes (B2:Bytes +Bytes B3:Bytes) => (B1 +Bytes B2) +Bytes B3 [concrete(B1, B2), symbolic(B3), simplification(40)]
```

## Bytes Update Lemmas

```k
  rule [bytes-update-symbolic-value]:
    B:Bytes [I <- V] => substrBytes(B, 0, I) +Bytes Int2Bytes(1, V, LE) +Bytes substrBytes(B, I +Int 1, lengthBytes(B) -Int I -Int 1)
    requires I <Int lengthBytes(B)
    [simplification, concrete(B, I), symbolic(V), preserves-definedness]
  
  rule [multiple-bytes-update-symbolic-value]:
    replaceAtBytes(B, I, V) => substrBytes(B, 0, I) +Bytes V +Bytes substrBytes(B, I +Int lengthBytes(V), lengthBytes(B))
    requires I +Int lengthBytes(V) <Int lengthBytes(B)
    [simplification, concrete(B, I), symbolic(V), preserves-definedness]
```


## Bytes Length Lemmas

```k
  rule [bytes-length-int2bytes]: lengthBytes(Int2Bytes(N, _:Int, _:Endianness)) => N [simplification]
  rule [bytes-length-substr]: lengthBytes(substrBytes(_, I, N)) => N -Int I [simplification, preserves-definedness]
  rule [bytes-length-concat]: lengthBytes(A +Bytes B) => lengthBytes(A) +Int lengthBytes(B) [simplification]
```

## Bytes Substr Lemmas

```k
  rule [substr-substr]: substrBytes(substrBytes(B, I, _), I0, N0) => substrBytes(B, I +Int I0, I +Int N0) 
    requires I +Int N0 <=Int lengthBytes(B) [simplification, preserves-definedness]
  rule [substr-concat-1]: substrBytes(A +Bytes _, I, J) => substrBytes(A, I, J)
    requires J <Int lengthBytes(A)
    [simplification, preserves-definedness]
  rule [substr-concat-2]: substrBytes(A +Bytes B, I, J) => A +Bytes substrBytes(B, I -Int lengthBytes(A), J -Int lengthBytes(A))
    requires I <Int lengthBytes(A) andBool lengthBytes(A) <=Int J
    [simplification, preserves-definedness]
  rule [substr-concat-3]: substrBytes(A +Bytes B, I, J) => substrBytes(B, I -Int lengthBytes(A), J -Int lengthBytes(A))
    requires lengthBytes(A) <=Int I
    [simplification, preserves-definedness]
```

## Bytes2Int Lemmas

```k
  rule [bytes2int-substr-ff00]: Bytes2Int (substrBytes(B, S, _E), LE, Unsigned) &Int 65280 => B[S +Int 1] <<Int 8
    [simplification, preserves-definedness]
  rule [bytes2int-upperbound]: Bytes2Int(B, LE, Unsigned) <Int X => true
    requires 2 ^Int lengthBytes(B) <=Int X
    [simplification, preserves-definedness]
  rule [bytes2int-lowerbound]: 0 <=Int Bytes2Int(_, LE, Unsigned) => true [simplification, preserves-definedness]
```

```k
endmodule
```
