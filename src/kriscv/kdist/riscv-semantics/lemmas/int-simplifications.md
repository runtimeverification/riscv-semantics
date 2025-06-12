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
```

## &Int Lemmas

```k
  rule [chop-32bits]: X &Int 4294967295 => X requires 0 <=Int X andBool X <Int 4294967296 [simplification]
  rule [int-and-assoc]: (X &Int Y) &Int Z => X &Int (Y &Int Z) [simplification, symbolic(X), concrete(Y,Z)]
  rule [int-and-add-assoc-8]: ((X &Int 255) +Int Y) &Int 255 => (X +Int Y) &Int 255
    requires 0 <=Int X andBool 0 <=Int Y
    [simplification]
  rule [int-and-add-assoc-16]: ((X &Int 65535) +Int Y) &Int 65535 => (X +Int Y) &Int 65535
    requires 0 <=Int X andBool 0 <=Int Y
    [simplification]
  rule [int-and-add-assoc-32]: ((X &Int 4294967295) +Int Y) &Int 4294967295 => (X +Int Y) &Int 4294967295
    requires 0 <=Int X andBool 0 <=Int Y
    [simplification]
```

## Inequality Lemmas

```k
  rule [int-and-ineq]: 0 <=Int A &Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]
  rule [int-rhs-ineq]: 0 <=Int A >>Int B => true requires 0 <=Int A andBool 0 <=Int B [simplification]
  rule [int-add-ineq]: A <=Int A +Int B => true requires 0 <=Int B [simplification]
  rule [int-add-ineq-4294967295]: X &Int 4294967295 <Int A => 4294967295 <Int X
    requires 0 <=Int A andBool A <=Int X [simplification]
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
  rule [int-or-bytes-3]: Bytes2Int(b"\x00\x00\x00" +Bytes X, LE, Unsigned) |Int Bytes2Int(Y, LE, Unsigned) => Bytes2Int(Y +Bytes X, LE, Unsigned)
    requires lengthBytes(Y) ==Int 3
    [simplification]
```

```k
endmodule
```