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
    [simplification, preserves-definedness]
  
  rule [multiple-bytes-update-symbolic-value]:
    replaceAtBytes(B, I, V) => substrBytes(B, 0, I) +Bytes V +Bytes substrBytes(B, I +Int lengthBytes(V), lengthBytes(B))
    requires I +Int lengthBytes(V) <=Int lengthBytes(B)
    [simplification, preserves-definedness]
```


## Bytes Length Lemmas

```k
  rule [bytes-length-int2bytes]: lengthBytes(Int2Bytes(N, _:Int, _:Endianness)) => N 
    [simplification]   
  rule [bytes-length-substr]: lengthBytes(substrBytes(B, I, J)) => J -Int I
    requires 0 <=Int I andBool I <=Int J andBool J <=Int lengthBytes(B)
    [simplification, preserves-definedness]
  rule [bytes-length-concat]: lengthBytes(A +Bytes B) => lengthBytes(A) +Int lengthBytes(B) 
    [simplification]
  rule [bytes-length-reverse]: lengthBytes(reverseBytes(B)) => lengthBytes(B)
    [simplification]
```

## Bytes Substr Lemmas

```k
  rule [substr-substr]: substrBytes(substrBytes(B, I, J), I0, J0) => substrBytes(B, I +Int I0, I +Int J0) 
    requires 0 <=Int I  andBool I  <=Int J  andBool J  <=Int lengthBytes(B)
     andBool 0 <=Int I0 andBool I0 <=Int J0 andBool J0 <=Int J -Int I
  [simplification, preserves-definedness]
  rule [substr-bytes-eq-ij]: substrBytes(B, I, I) => b""
    requires 0 <=Int I andBool I <=Int lengthBytes(B)
  [simplification, preserves-definedness]
  rule [substr-bytes-self]: substrBytes(B, 0, J) => B
    requires J ==Int lengthBytes(B)
    [simplification, preserves-definedness]
  rule [substr-concat-0]: substrBytes(A +Bytes _, I, J) => substrBytes(A, I, J)
    requires J <=Int lengthBytes(A)
    [simplification, preserves-definedness]
  rule [substr-concat-1]: substrBytes(A +Bytes B, I, J) => substrBytes(A, I, lengthBytes(A)) +Bytes substrBytes(B, 0, J -Int lengthBytes(A))
    requires I <Int lengthBytes(A) andBool lengthBytes(A) <Int J
    [simplification, preserves-definedness]
  rule [substr-concat-2]: substrBytes(A +Bytes B, I, J) => substrBytes(B, I -Int lengthBytes(A), J -Int lengthBytes(A))
    requires lengthBytes(A) <=Int I
    [simplification, preserves-definedness]
  rule [substr-int2bytes]: substrBytes(Int2Bytes(Num, V, LE), SI, EI) => Int2Bytes(EI -Int SI, V >>Int (SI *Int 8), LE)
    requires 0 <=Int SI andBool SI <=Int EI andBool EI <=Int Num
    [simplification, preserves-definedness]
  
  rule [substr-reverse-concat-0]: substrBytes(B, I1, I2) +Bytes substrBytes(B, I0, I1) => reverseBytes(substrBytes(B, I0, I2))
    requires 0 <=Int I0 andBool I2 <=Int lengthBytes(B)
     andBool I0 +Int 1 ==Int I1 andBool I1 +Int 1 ==Int I2
    [simplification, preserves-definedness]
  rule [substr-reverse-concat-1]: substrBytes(B, I1, I2) +Bytes reverseBytes(substrBytes(B, I0, I1)) => reverseBytes(substrBytes(B, I0, I2))
    requires 0 <=Int I0  andBool I2 <=Int lengthBytes(B)
     andBool I0 <=Int I1 andBool I1 +Int 1 ==Int I2
    [simplification, preserves-definedness]
  rule [substr-reverse-concat-1-cxt]: substrBytes(B, I1, I2) +Bytes reverseBytes(substrBytes(B, I0, I1)) +Bytes C => reverseBytes(substrBytes(B, I0, I2)) +Bytes C
    requires 0 <=Int I0  andBool I2 <=Int lengthBytes(B)
     andBool I0 <=Int I1 andBool I1 +Int 1 ==Int I2
    [simplification, preserves-definedness]
  rule [substr-reverse-concat-2]: reverseBytes(substrBytes(B, I1, I2)) +Bytes substrBytes(B, I0, I1) => reverseBytes(substrBytes(B, I0, I2))
    requires 0 <=Int I0  andBool I2 <=Int lengthBytes(B)
     andBool I1 <=Int I2 andBool I0 +Int 1 ==Int I1
    [simplification, preserves-definedness]
  rule [substr-reverse-concat-2-cxt]: reverseBytes(substrBytes(B, I1, I2)) +Bytes substrBytes(B, I0, I1) +Bytes C => reverseBytes(substrBytes(B, I0, I2)) +Bytes C
    requires 0 <=Int I0  andBool I2 <=Int lengthBytes(B)
     andBool I1 <=Int I2 andBool I0 +Int 1 ==Int I1
    [simplification, preserves-definedness]
  rule [substr-reverse-concat-3]: reverseBytes(substrBytes(B, I1, I2)) +Bytes reverseBytes(substrBytes(B, I0, I1)) => reverseBytes(substrBytes(B, I0, I2))
    requires 0 <=Int I0 andBool I0 <=Int I1 andBool I1 <=Int I2 andBool I2 <=Int lengthBytes(B)
    [simplification, preserves-definedness]
  rule [substr-reverse-concat-3-cxt]: reverseBytes(substrBytes(B, I1, I2)) +Bytes reverseBytes(substrBytes(B, I0, I1)) +Bytes C => reverseBytes(substrBytes(B, I0, I2)) +Bytes C
    requires 0 <=Int I0 andBool I0 <=Int I1 andBool I1 <=Int I2 andBool I2 <=Int lengthBytes(B)
    [simplification, preserves-definedness]
```

## Bytes2Int Lemmas

```k
  rule [bytes2int-substr-ff00-0]: Bytes2Int (substrBytes(B, I, J), LE, Unsigned) &Int 65280 => 0
    requires 0 <=Int I andBool I <=Int J andBool J <=Int I +Int 1 andBool J <=Int lengthBytes(B)
    [simplification, preserves-definedness]
  rule [bytes2int-substr-ff00-1]: Bytes2Int (substrBytes(B, I, J), LE, Unsigned) &Int 65280 => B[I +Int 1] <<Int 8
    requires 0 <=Int I andBool I +Int 1 <Int J andBool J <=Int lengthBytes(B)
    [simplification, preserves-definedness]
  rule [bytes2int-ffffffff]: Bytes2Int(B, LE, Unsigned) &Int 4294967295 => Bytes2Int(substrBytes(B, 0, 4), LE, Unsigned)
    requires 4 <=Int lengthBytes(B)
    [simplification, preserves-definedness]
  rule [bytes2int-upperbound]: Bytes2Int(B, _, Unsigned) <Int X => true
    requires 2 ^Int (lengthBytes(B) *Int 8) <=Int X
    [simplification]
  rule [bytes2int-lowerbound]: 0 <=Int Bytes2Int(_, _, Unsigned) => true [simplification]
```

## PadBytes

```k
  rule [simp-padleftbytes]: padLeftBytes(B, L, V) => padLeftBytes(.Bytes, L, V) +Bytes B
    [simplification, preserves-definedness, concrete(L,V), symbolic(B)]
```

## Bytes2Int Lemmas

```k
  rule [int2bytes-bytes2int]: Int2Bytes(LEN:Int, Bytes2Int(B:Bytes, LE, Unsigned), LE) => substrBytes(B, 0, LEN)
    requires 0 <=Int LEN
     andBool LEN <=Int lengthBytes(B)
    [simplification, preserves-definedness]
  rule [bytes2int-int2bytes]: Bytes2Int(Int2Bytes(LEN, V, LE), LE, Unsigned) => V &Int (2 ^Int (LEN *Int 8) -Int 1)
    requires 0 <=Int LEN [simplification, preserves-definedness]
  
  rule [substr-reverse-bytes]:
    substrBytes(reverseBytes(B), START, END)
    => substrBytes(B, lengthBytes(B) -Int END, lengthBytes(B) -Int START)
    requires 0 <=Int START andBool START +Int 1 ==Int END andBool END <=Int lengthBytes(B)
    [simplification, preserves-definedness]
  
  rule [int2bytes-bytes2int-pad-zeros]:
    Int2Bytes(LEN, Bytes2Int(B, LE, Unsigned), LE)
    => B +Bytes Int2Bytes(LEN -Int lengthBytes(B), 0, LE)
    requires lengthBytes(B) <=Int LEN
    [simplification]
```

```k
endmodule
```
