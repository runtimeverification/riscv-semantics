# Int Simplifications

```k
module INT-SIMPLIFICATIONS
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
    requires 0 <=Int X andBool 0 <=Int Y [simplification, preserves-definedness]
  rule [int-lsh-less-than-32bits-bytes-update]: (B[I] <<Int Y) <Int 4294967296 => true
    requires 0 <=Int I andBool I <Int lengthBytes(B) andBool 0 <=Int Y andBool 256 <Int 2 ^Int (32 -Int Y)
    [simplification, preserves-definedness]
```

## Chop Lemmas

```k
  rule [chop-32bits]: X &Int 4294967295 => X requires 0 <=Int X andBool X <Int 4294967296 [simplification]
```

```k
endmodule
```
