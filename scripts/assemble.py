#! /usr/bin/env python3
from riscv_assembler.convert import AssemblyConverter
import sys

# arg: lw x3, 0(x3)
arg = sys.argv[1]

# Convert assembly to binary
converter = AssemblyConverter()
binary_str = converter.convert(arg)[0]

# Convert binary string to integer
binary_int = int(binary_str, 2)

# Convert to little-endian bytes
little_endian_bytes = binary_int.to_bytes(4, byteorder='little')

# Print each byte in hex format
print(''.join(f'\\x{b:02x}' for b in little_endian_bytes))