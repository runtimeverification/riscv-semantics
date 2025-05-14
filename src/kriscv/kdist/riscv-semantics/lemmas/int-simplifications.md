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
    [simplification, preserves-definedness]
  rule [int-lsh-less-than-32bits]: (X <<Int Y) <Int 4294967296 => true
    requires 0 <=Int X andBool 0 <=Int Y andBool Y <Int 32 andBool X <Int 2 ^Int (32 -Int Y)
    [simplification, preserves-definedness]
  rule [int-lsh-non-negative]: 0 <=Int (X <<Int Y) => true
    requires 0 <=Int X andBool 0 <=Int Y [simplification]
```

## Chop Lemmas

```k
  rule [chop-32bits]: X &Int 4294967295 => X requires 0 <=Int X andBool X <Int 4294967296 [simplification]
```

## Int Expression Simplifications for Bytes

### Shift Left for Bytes

```k
  rule [int-lsh-bytes-lookup]: B:Bytes[I:Int] <<Int Y => Bytes2Int(padRightBytes(.Bytes, Y /Int 8, 0) +Bytes substrBytes(B, I, I +Int 1), LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0
    [simplification, preserves-definedness]
  rule [int-lsh-bytes2int]: Bytes2Int(B, LE, Unsigned) <<Int Y => Bytes2Int(padRightBytes(.Bytes, Y /Int 8, 0) +Bytes B, LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0
    [simplification, preserves-definedness]
```

### Shift Right for Bytes

```k
  rule [int-rsh-substrbytes]: Bytes2Int(substrBytes(B, I, J), LE, Unsigned) >>Int Y => Bytes2Int(substrBytes(B, I +Int Y /Int 8, J), LE, Unsigned)
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0 andBool I +Int Y /Int 8 <Int J
    [simplification, preserves-definedness]
  rule [int-rsh-substrbytes-0]: Bytes2Int(substrBytes(_, I, J), LE, Unsigned) >>Int Y => 0
    requires 0 <=Int Y andBool Y modInt 8 ==Int 0 andBool I +Int Y /Int 8 ==Int J
    [simplification, preserves-definedness]
```

```k
endmodule
```
