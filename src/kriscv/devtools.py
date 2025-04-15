import sys


def kriscv_asm() -> None:
    """
    Convert a RISC-V assembly instruction to a binary string.

    Usage:
        kriscv-asm <instruction>
    """
    from riscv_assembler.convert import AssemblyConverter  # type: ignore

    instr = sys.argv[1]  # e.g., lw x3, 0(x3)
    converter = AssemblyConverter()
    binary_str = converter.convert(instr)[0]
    binary_int = int(binary_str, 2)
    little_endian_bytes = binary_int.to_bytes(4, byteorder='little')
    print(''.join(f'\\x{b:02x}' for b in little_endian_bytes))
