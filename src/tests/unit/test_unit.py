from __future__ import annotations

from typing import TYPE_CHECKING

# isort: off
from kriscv.build import semantics

# isort: on
import pytest
from pyk.kast.inner import KToken, KVariable
from pyk.kllvm.convert import llvm_to_pattern, pattern_to_llvm
from pyk.kore.match import kore_int
from pyk.prelude.kint import INT, intToken

from kriscv import build, term_builder
from kriscv.term_builder import register
from kriscv.term_manip import kore_sparse_bytes, normalize_memory

if TYPE_CHECKING:
    from typing import Final

    from pyk.kast.inner import KInner, KSort
    from pyk.kore.syntax import Pattern

    from kriscv.tools import Tools


def _eval_call(tools: Tools, call: KInner, sort: KSort) -> KInner:
    return tools.krun.kore_to_kast(_eval_call_to_kore(tools, call, sort))


def _eval_call_to_kore(tools: Tools, call: KInner, sort: KSort) -> Pattern:
    llvm_input = pattern_to_llvm(tools.krun.kast_to_kore(call, sort))
    llvm_res = build.runtime.evaluate(llvm_input)
    return llvm_to_pattern(llvm_res)


# test id, instruction binary as a string of 0s/1s, disassembled instruction
DISASS_TEST_DATA: Final[tuple[tuple[str, str, KInner], ...]] = (
    (
        'addi x1, x2, 3',
        '00000000010100010000000010010011',
        term_builder.addi_instr(register(1), register(2), intToken(5)),
    ),
    (
        'slti x2, x3, 2047',
        '01111111111100011010000100010011',
        term_builder.slti_instr(register(2), register(3), intToken(2047)),
    ),
    (
        'sltiu x3, x4, -2048',
        '10000000000000100011000110010011',
        term_builder.sltiu_instr(register(3), register(4), intToken(-2048)),
    ),
    (
        'andi x4, x5, -1',
        '11111111111100101111001000010011',
        term_builder.andi_instr(register(4), register(5), intToken(-1)),
    ),
    (
        'ori x5, x6, -2',
        '11111111111000110110001010010011',
        term_builder.ori_instr(register(5), register(6), intToken(-2)),
    ),
    (
        'xori x6, x7, 3',
        '00000000001100111100001100010011',
        term_builder.xori_instr(register(6), register(7), intToken(3)),
    ),
    (
        'slli x7, x8, 31',
        '00000001111101000001001110010011',
        term_builder.slli_instr(register(7), register(8), intToken(31)),
    ),
    (
        'srli x8, x9, 1',
        '00000000000101001101010000010011',
        term_builder.srli_instr(register(8), register(9), intToken(1)),
    ),
    (
        'srai x9, x10, 2',
        '01000000001001010101010010010011',
        term_builder.srai_instr(register(9), register(10), intToken(2)),
    ),
    (
        'beq x10, x11, 4094',
        '01111110101101010000111111100011',
        term_builder.beq_instr(register(10), register(11), intToken(4094)),
    ),
    (
        'bne x11, x12, -4096',
        '10000000110001011001000001100011',
        term_builder.bne_instr(register(11), register(12), intToken(-4096)),
    ),
    (
        'blt x12, x13, 0',
        '00000000110101100100000001100011',
        term_builder.blt_instr(register(12), register(13), intToken(0)),
    ),
    (
        'bltu x13, x14, -100',
        '11111000111001101110111011100011',
        term_builder.bltu_instr(register(13), register(14), intToken(-100)),
    ),
    (
        'bge x14, x15, 2048',
        '00000000111101110101000011100011',
        term_builder.bge_instr(register(14), register(15), intToken(2048)),
    ),
    (
        'bgeu x15, x15, -2050',
        '11111110111101111111111101100011',
        term_builder.bgeu_instr(register(15), register(15), intToken(-2050)),
    ),
    (
        'lui x1, 0xFFFFF',
        '11111111111111111111000010110111',
        term_builder.lui_instr(register(1), intToken(int('FFFFF', 16))),
    ),
    (
        'auipc x2, 0xA1',
        '00000000000010100001000100010111',
        term_builder.auipc_instr(register(2), intToken(int('A1', 16))),
    ),
    ('jal x0, -1048576', '10000000000000000000000001101111', term_builder.jal_instr(register(0), intToken(-1048576))),
    (
        'add x0, x1, x2',
        '00000000001000001000000000110011',
        term_builder.add_instr(register(0), register(1), register(2)),
    ),
    (
        'sub x3, x4, x5',
        '01000000010100100000000110110011',
        term_builder.sub_instr(register(3), register(4), register(5)),
    ),
    (
        'slt x6, x7, x8',
        '00000000100000111010001100110011',
        term_builder.slt_instr(register(6), register(7), register(8)),
    ),
    (
        'sltu x9, x10, x11',
        '00000000101101010011010010110011',
        term_builder.sltu_instr(register(9), register(10), register(11)),
    ),
    (
        'and x12, x13, x14',
        '00000000111001101111011000110011',
        term_builder.and_instr(register(12), register(13), register(14)),
    ),
    (
        'or x15, x0, x1',
        '00000000000100000110011110110011',
        term_builder.or_instr(register(15), register(0), register(1)),
    ),
    (
        'xor x2, x3, x4',
        '00000000010000011100000100110011',
        term_builder.xor_instr(register(2), register(3), register(4)),
    ),
    (
        'sll x5, x6, x7',
        '00000000011100110001001010110011',
        term_builder.sll_instr(register(5), register(6), register(7)),
    ),
    (
        'srl x8, x9, x10',
        '00000000101001001101010000110011',
        term_builder.srl_instr(register(8), register(9), register(10)),
    ),
    (
        'sra x11, x12, x13',
        '01000000110101100101010110110011',
        term_builder.sra_instr(register(11), register(12), register(13)),
    ),
    (
        'jalr x0, -2048(x1)',
        '10000000000000001000000001100111',
        term_builder.jalr_instr(register(0), intToken(-2048), register(1)),
    ),
    (
        'lw x2, 2047(x3)',
        '01111111111100011010000100000011',
        term_builder.lw_instr(register(2), intToken(2047), register(3)),
    ),
    (
        'lh x4, 0(x5)',
        '00000000000000101001001000000011',
        term_builder.lh_instr(register(4), intToken(0), register(5)),
    ),
    (
        'lhu x6, 7(x7)',
        '00000000011100111101001100000011',
        term_builder.lhu_instr(register(6), intToken(7), register(7)),
    ),
    (
        'lb x8, -10(x9)',
        '11111111011001001000010000000011',
        term_builder.lb_instr(register(8), intToken(-10), register(9)),
    ),
    (
        'lbu x10, 2047(x11)',
        '01111111111101011100010100000011',
        term_builder.lbu_instr(register(10), intToken(2047), register(11)),
    ),
    (
        'sw x2, 2047(x3)',
        '01111110001000011010111110100011',
        term_builder.sw_instr(register(2), intToken(2047), register(3)),
    ),
    (
        'sh x4, 0(x5)',
        '00000000010000101001000000100011',
        term_builder.sh_instr(register(4), intToken(0), register(5)),
    ),
    (
        'sb x8, -10(x9)',
        '11111110100001001000101100100011',
        term_builder.sb_instr(register(8), intToken(-10), register(9)),
    ),
    (
        'fence ow, ir',
        '00000101101000000000000000001111',
        term_builder.fence_instr(term_builder.fence_bits('ow'), term_builder.fence_bits('ir')),
    ),
    (
        'fence.tso',
        '10000011001100000000000000001111',
        term_builder.fence_tso_instr(),
    ),
    (
        'ecall',
        '00000000000000000000000001110011',
        term_builder.ecall_instr(),
    ),
    (
        'ebreak',
        '00000000000100000000000001110011',
        term_builder.ebreak_instr(),
    ),
    (
        'invalid instruction',
        '00000000000000000000000000000000',
        term_builder.invalid_instr(),
    ),
)


@pytest.mark.parametrize(
    'instr_bits,expected',
    [(instr_bits, expected) for (_, instr_bits, expected) in DISASS_TEST_DATA],
    ids=[test_id for test_id, *_ in DISASS_TEST_DATA],
)
def test_disassemble(instr_bits: str, expected: KInner) -> None:
    assert len(instr_bits) == 32
    tools = semantics()
    disass_call = term_builder.disassemble(intToken(int(instr_bits, 2)))
    actual = _eval_call(tools, disass_call, term_builder.sort_instruction())
    assert actual == expected


# test id, initial memory, addr to write, byte to write
MEMORY_TEST_DATA: Final[tuple[tuple[str, dict[int, bytes], int, int], ...]] = (
    ('empty_start', {}, 0, 0x1A),
    ('empty_later', {}, 10, 0x1A),
    ('mid_bytes', {1: b'\x7f\x7f'}, 2, 0x1A),
    ('start_pre_bytes', {1: b'\x7f\x7f'}, 0, 0x1A),
    ('empty_pre_bytes', {2: b'\x7f\x7f'}, 1, 0x1A),
    ('end_post_bytes', {2: b'\x7f\x7f'}, 4, 0x1A),
    ('empty_post_bytes', {2: b'\x7f\x7f', 6: b'\x7f'}, 4, 0x1A),
    ('end', {2: b'\x7f\x7f'}, 5, 0x1A),
    ('merge_bytes', {1: b'\x7f\x7f', 4: b'\x7f'}, 3, 0x1A),
)


@pytest.mark.parametrize(
    'memory,addr,byte',
    [(memory, addr, byte) for (_, memory, addr, byte) in MEMORY_TEST_DATA],
    ids=[test_id for test_id, *_ in MEMORY_TEST_DATA],
)
def test_memory(memory: dict[int, bytes], addr: int, byte: int) -> None:
    assert 0 <= byte <= 0xFF
    for val in memory.values():
        for byte in val:
            assert 0 <= byte <= 0xFF

    byte_val = byte.to_bytes(1, 'big')

    # Manually compute the expected final memory state
    memory_expect: dict[int, bytes] = {}
    stored = False
    for start, val in memory.items():
        if start <= addr and addr < start + len(val):
            val_idx = addr - start
            memory_expect[start] = val[:val_idx] + byte_val + val[val_idx + 1 :]
            stored = True
        else:
            memory_expect[start] = val
    if not stored:
        memory_expect[addr] = byte_val
    memory_expect = normalize_memory(memory_expect)

    # Execute storeByte to get the actual final memory state
    tools = semantics()
    memory_sb = term_builder.sparse_bytes(memory)
    addr_word = term_builder.word(addr)

    store_call = term_builder.store_byte(memory_sb, addr_word, intToken(byte))
    memory_actual_sb_kore = _eval_call_to_kore(tools, store_call, term_builder.sort_memory())
    memory_actual = kore_sparse_bytes(memory_actual_sb_kore)

    assert memory_actual == memory_expect

    # Also execute loadByte and check that we correctly read back the written value
    memory_actual_sb = tools.krun.kore_to_kast(memory_actual_sb_kore)
    load_call = term_builder.load_byte(memory_actual_sb, addr_word)
    load_actual = kore_int(_eval_call_to_kore(tools, load_call, INT))

    assert load_actual == byte


SYMBOLIC_MEMORY_TEST_DATA: Final = (
    (
        'empty-bytes-2-3',
        {2: b'\x7f\x7f\x7f\x7f\x7f'},
        {3: (1, 'W0'), 2: (1, 'W1')},
        # #empty(2) #bytes(W1 +Bytes +W0 +Bytes b'\x7f\x7f\x7f')
        term_builder.sb_empty_cons(
            term_builder.sb_empty(intToken(2)),
            term_builder.sb_bytes_cons(
                term_builder.sb_bytes(
                    term_builder.add_bytes(
                        term_builder.add_bytes(KVariable('W1', 'Bytes'), KVariable('W0', 'Bytes')),
                        KToken('b"\\x7f\\x7f\\x7f"', 'Bytes'),
                    )
                ),
                term_builder.dot_sb(),
            ),
        ),
    ),
    (
        'empty-bytes-6',
        {2: b'\x7f\x7f', 12: b'\x7f\x7f\x7f'},
        {14: (1, 'W0')},
        # #empty(2) #bytes(b'\x7f\x7f') #empty(8) #bytes(b'\x7f\x7f' +Bytes +W0)
        term_builder.sb_empty_cons(
            term_builder.sb_empty(intToken(2)),
            term_builder.sb_bytes_cons(
                term_builder.sb_bytes(KToken('b"\\x7f\\x7f"', 'Bytes')),
                term_builder.sb_empty_cons(
                    term_builder.sb_empty(intToken(8)),
                    term_builder.sb_bytes_cons(
                        term_builder.sb_bytes(
                            term_builder.add_bytes(KToken('b"\\x7f\\x7f"', 'Bytes'), KVariable('W0', 'Bytes'))
                        ),
                        term_builder.dot_sb(),
                    ),
                ),
            ),
        ),
    ),
)


@pytest.mark.parametrize(
    'memory,symdata,expected',
    [(memory, symdata, expected) for (_, memory, symdata, expected) in SYMBOLIC_MEMORY_TEST_DATA],
    ids=[test_id for test_id, *_ in SYMBOLIC_MEMORY_TEST_DATA],
)
def test_symbolic_memory(memory: dict[int, bytes], symdata: dict[int, tuple[int, str]], expected: int) -> None:
    result = term_builder.sparse_bytes(memory, symdata)
    assert result == expected
