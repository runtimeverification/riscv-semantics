# Int Simplifications

```k
module INT-SIMPLIFICATIONS [symbolic]
  imports INT
  imports BYTES
  imports K-EQUAL
  imports BOOL
```

## Shift Lemmas

```k
  rule [int-lsh-lsh]: (W0 <<Int N0) <<Int N1 => W0 <<Int (N0 +Int N1)
    requires 0 <=Int N0 andBool 0 <=Int N1
    [simplification, preserves-definedness]
  rule [int-lsh-less-than-32bits]: (X <<Int Y) <Int 4294967296 => true
    requires 0 <=Int X andBool 0 <=Int Y andBool Y <Int 32 andBool X <Int 2 ^Int (32 -Int Y)
    [simplification, preserves-definedness]
  rule [int-lsh-non-negative]: 0 <=Int (X <<Int Y) => true
    requires 0 <=Int X andBool 0 <=Int Y [simplification]
  rule [rsh-0]: X >>Int 0 => X [simplification, preserves-definedness]
```

## &Int Lemmas

```k
  rule [chop-32bits]: X &Int 4294967295 => X requires 0 <=Int X andBool X <Int 4294967296 [simplification]
  rule [chop-16bits]: X &Int 65535 => X requires 0 <=Int X andBool X <Int 65536 [simplification]
  rule [int-and-assoc]: (X &Int Y) &Int Z => X &Int (Y &Int Z) [simplification, symbolic(X), concrete(Y,Z)]
  rule [int-and-add-assoc-8]: ((X &Int 255) +Int Y) &Int 255 => (X +Int Y) &Int 255
    [simplification]
  rule [int-and-add-assoc-16]: ((X &Int 65535) +Int Y) &Int 65535 => (X +Int Y) &Int 65535
    [simplification]
  rule [int-and-add-assoc-32]: ((X &Int 4294967295) +Int Y) &Int 4294967295 => (X +Int Y) &Int 4294967295
    [simplification]
  rule [bytes2int-and-255-noop]: Bytes2Int(X, LE, Unsigned) &Int 255 => Bytes2Int(X, LE, Unsigned)
    requires lengthBytes(X) <=Int 1 [simplification]
  rule [bytes2int-zero-prefix-or-to-concat]: Bytes2Int(b"\x00" +Bytes X, LE, Unsigned) |Int Y => Bytes2Int(Int2Bytes(Y, LE, Unsigned) +Bytes X, LE, Unsigned)
    requires 0 <=Int Y andBool Y <Int 256 [simplification, concrete(Y)]
```

## Equality Lemmas

```k
  rule [int-eq-bytes-concat-split]: X ==Int Bytes2Int(B0 +Bytes B1, LE, Unsigned) => 
    (X &Int ((1 <<Int (lengthBytes(B0) *Int 8)) -Int 1)) ==Int Bytes2Int(B0, LE, Unsigned)
    andBool
    (X >>Int (lengthBytes(B0) *Int 8)) ==Int Bytes2Int(B1, LE, Unsigned)
    [simplification, concrete(B0), preserves-definedness]
    // without preserves-definedness, the rule is not applicable to B1 == substrBytes(B2, I, J)
```

## Inequality Lemmas

```k
  rule [int-and-ineq]: 0 <=Int A &Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]
  rule [int-and-ineq-4294967295]: 0 <=Int _ &Int 4294967295 => true [simplification(45)]
  rule [int-and-ineq-65535]: 0 <=Int _ &Int 65535 => true [simplification(45)]
  rule [int-and-ineq-255]: 0 <=Int _ &Int 255 => true [simplification(45)]
  rule [int-or-gt]: 0 <Int A |Int B => true requires 0 <Int A orBool 0 <Int B [simplification]
  rule [int-rhs-ineq]: 0 <=Int A >>Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]
  rule [int-add-ineq]: A <=Int A +Int B => true requires 0 <=Int B [simplification]
  rule [int-add-ineq-0]: 0 <=Int A +Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]
  rule [int-add-ineq-4294967295]: X &Int 4294967295 <Int A => 4294967295 <Int X
    requires 0 <=Int A andBool A <=Int X [simplification]
```

## Additional Int Simplifications

```k
  rule [int-add-ineq-pos-1]: 0 <Int A +Int B => true 
    requires 0 <=Int A andBool 0 <Int B [simplification(45)]
  rule [int-add-ineq-pos-2]: 0 <Int A +Int B => true 
    requires 0 <Int A andBool 0 <=Int B [simplification]
```

## Int Expression Simplifications for Bytes

### Shift Left for Bytes

```k
  rule [int-lsh-bytes-lookup]: B:Bytes[I:Int] <<Int Y => Bytes2Int(padLeftBytes(substrBytes(B, I, I +Int 1), Y /Int 8, 0), LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0
    [simplification, preserves-definedness]
  rule [int-lsh-bytes2int]: Bytes2Int(B, LE, Unsigned) <<Int Y => Bytes2Int(padLeftBytes(B, Y /Int 8, 0), LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0
    [simplification, preserves-definedness]
```

### Shift Right for Bytes

```k
  rule [int-rsh-substrbytes]: Bytes2Int(substrBytes(B, I, J), LE, Unsigned) >>Int Y => Bytes2Int(substrBytes(B, I +Int Y /Int 8, J), LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0 andBool I +Int Y /Int 8 <=Int J
    [simplification, preserves-definedness]
```

### |Int for Bytes

```k
  rule [int-or-bytes-1]: Bytes2Int(b"\x00" +Bytes X, LE, Unsigned) |Int Bytes2Int(Y, _, Unsigned) => Bytes2Int(Y +Bytes X, LE, Unsigned)
    requires lengthBytes(Y) ==Int 1
    [simplification]
  rule [int-or-bytes-2]: Bytes2Int(b"\x00\x00" +Bytes X, LE, Unsigned) |Int Bytes2Int(Y, LE, Unsigned) => Bytes2Int(Y +Bytes X, LE, Unsigned)
    requires lengthBytes(Y) ==Int 2
    [simplification]
  rule [int-or-bytes-2s]: Bytes2Int(b"\x00\x00" +Bytes X, LE, Unsigned) |Int Bytes2Int(Y +Bytes b"\x00\x00", LE, Unsigned) => Bytes2Int(Y +Bytes X, LE, Unsigned)
    requires lengthBytes(Y) ==Int 2 andBool lengthBytes(X) ==Int 2
    [simplification]
  rule [int-or-bytes-3]: Bytes2Int(b"\x00\x00\x00" +Bytes X, LE, Unsigned) |Int Bytes2Int(Y, LE, Unsigned) => Bytes2Int(Y +Bytes X, LE, Unsigned)
    requires lengthBytes(Y) ==Int 3
    [simplification]
```

```k
endmodule
```