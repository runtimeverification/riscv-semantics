from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, cast

from pyk.kast.inner import KApply, KInner, KSort
from pyk.prelude.bytes import bytesToken
from pyk.prelude.collections import map_of
from pyk.prelude.kint import intToken

from kriscv.term_manip import normalize_memory

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import TypeVar

    T = TypeVar('T')


def halt_never() -> KInner:
    return KApply('HaltNever')


def halt_at_address(address: KInner) -> KInner:
    return KApply('HaltAtAddress', address)


def disassemble(instr: KInner) -> KInner:
    return KApply('disassemble', instr)


def sort_instruction() -> KSort:
    return KSort('Instruction')


def _reg_reg_imm_instr(reg_reg_imm_instr_name: KInner, reg1: KInner, reg2: KInner, imm: KInner) -> KInner:
    return KApply('RegRegImmInstr', reg_reg_imm_instr_name, reg1, reg2, imm)


def _reg_imm_instr(reg_imm_instr_name: KInner, reg: KInner, imm: KInner) -> KInner:
    return KApply('RegImmInstr', reg_imm_instr_name, reg, imm)


def _reg_reg_reg_instr(reg_reg_reg_instr_name: KInner, reg1: KInner, reg2: KInner, reg3: KInner) -> KInner:
    return KApply('RegRegRegInstr', reg_reg_reg_instr_name, reg1, reg2, reg3)


def _reg_imm_reg_instr(reg_imm_reg_instr_name: KInner, reg1: KInner, imm: KInner, reg2: KInner) -> KInner:
    return KApply('RegImmRegInstr', reg_imm_reg_instr_name, reg1, imm, reg2)


def register(num: int) -> KInner:
    return intToken(num)


def addi_instr(rd: KInner, rs1: KInner, imm: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('ADDI'), rd, rs1, imm)


def slti_instr(rd: KInner, rs1: KInner, imm: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('SLTI'), rd, rs1, imm)


def sltiu_instr(rd: KInner, rs1: KInner, imm: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('SLTIU'), rd, rs1, imm)


def andi_instr(rd: KInner, rs1: KInner, imm: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('ANDI'), rd, rs1, imm)


def ori_instr(rd: KInner, rs1: KInner, imm: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('ORI'), rd, rs1, imm)


def xori_instr(rd: KInner, rs1: KInner, imm: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('XORI'), rd, rs1, imm)


def slli_instr(rd: KInner, rs1: KInner, shamt: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('SLLI'), rd, rs1, shamt)


def srli_instr(rd: KInner, rs1: KInner, shamt: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('SRLI'), rd, rs1, shamt)


def srai_instr(rd: KInner, rs1: KInner, shamt: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('SRAI'), rd, rs1, shamt)


def beq_instr(rs1: KInner, rs2: KInner, offset: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('BEQ'), rs1, rs2, offset)


def bne_instr(rs1: KInner, rs2: KInner, offset: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('BNE'), rs1, rs2, offset)


def blt_instr(rs1: KInner, rs2: KInner, offset: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('BLT'), rs1, rs2, offset)


def bltu_instr(rs1: KInner, rs2: KInner, offset: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('BLTU'), rs1, rs2, offset)


def bge_instr(rs1: KInner, rs2: KInner, offset: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('BGE'), rs1, rs2, offset)


def bgeu_instr(rs1: KInner, rs2: KInner, offset: KInner) -> KInner:
    return _reg_reg_imm_instr(KApply('BGEU'), rs1, rs2, offset)


def lui_instr(rd: KInner, imm: KInner) -> KInner:
    return _reg_imm_instr(KApply('LUI'), rd, imm)


def auipc_instr(rd: KInner, imm: KInner) -> KInner:
    return _reg_imm_instr(KApply('AUIPC'), rd, imm)


def jal_instr(rd: KInner, offset: KInner) -> KInner:
    return _reg_imm_instr(KApply('JAL'), rd, offset)


def add_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('ADD'), rd, rs1, rs2)


def sub_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('SUB'), rd, rs1, rs2)


def slt_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('SLT'), rd, rs1, rs2)


def sltu_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('SLTU'), rd, rs1, rs2)


def and_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('AND'), rd, rs1, rs2)


def or_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('OR'), rd, rs1, rs2)


def xor_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('XOR'), rd, rs1, rs2)


def sll_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('SLL'), rd, rs1, rs2)


def srl_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('SRL'), rd, rs1, rs2)


def sra_instr(rd: KInner, rs1: KInner, rs2: KInner) -> KInner:
    return _reg_reg_reg_instr(KApply('SRA'), rd, rs1, rs2)


def jalr_instr(rd: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('JALR'), rd, offset, rs1)


def lw_instr(rd: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('LW'), rd, offset, rs1)


def lh_instr(rd: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('LH'), rd, offset, rs1)


def lhu_instr(rd: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('LHU'), rd, offset, rs1)


def lb_instr(rd: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('LB'), rd, offset, rs1)


def lbu_instr(rd: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('LBU'), rd, offset, rs1)


def sw_instr(rs2: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('SW'), rs2, offset, rs1)


def sh_instr(rs2: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('SH'), rs2, offset, rs1)


def sb_instr(rs2: KInner, offset: KInner, rs1: KInner) -> KInner:
    return _reg_imm_reg_instr(KApply('SB'), rs2, offset, rs1)


def _is_subseq(sub: Iterable[T], sup: Iterable[T]) -> bool:
    it = iter(sup)
    return all(x in it for x in sub)


def fence_bits(iorw_str: str) -> KInner:
    if not _is_subseq(iorw_str, 'iorw'):
        raise AssertionError(f"Expected a subsequence of 'iorw', but got {iorw_str!r}")
    bits = ''.join('1' if c in iorw_str else '0' for c in 'iorw')
    return intToken(int(bits, 2))


def fence_instr(pred: KInner, succ: KInner) -> KInner:
    return KApply('FENCE', pred, succ)


def fence_tso_instr() -> KInner:
    return KApply('FENCETSO')


def ecall_instr() -> KInner:
    return KApply('ECALL')


def ebreak_instr() -> KInner:
    return KApply('EBREAK')


def invalid_instr() -> KInner:
    return KApply('INVALID_INSTR')


def word(bits: KInner | int | str | bytes) -> KInner:
    match bits:
        case KInner():
            val = bits
        case int():
            assert bits >= 0
            val = intToken(bits)
        case str():
            val = intToken(int(bits, 2))
        case bytes():
            val = intToken(int.from_bytes(bits, 'big', signed=False))
    return KApply('W', val)


def dot_sb() -> KInner:
    return KApply('.SparseBytes')


def sb_empty(count: KInner) -> KInner:
    return KApply('SparseBytes:#empty', count)


def sb_bytes(bs: KInner) -> KInner:
    return KApply('SparseBytes:#bytes', bs)


def sb_empty_cons(empty: KInner, rest_bf: KInner) -> KInner:
    return KApply('SparseBytes:EmptyCons', empty, rest_bf)


def sb_bytes_cons(bs: KInner, rest_ef: KInner) -> KInner:
    return KApply('SparseBytes:BytesCons', bs, rest_ef)


def sparse_bytes(data: dict[int, bytes]) -> KInner:
    clean_data: list[tuple[int, bytes]] = sorted(normalize_memory(data).items())

    if len(clean_data) == 0:
        return dot_sb()

    # Collect all empty gaps between segements
    gaps = []
    start = clean_data[0][0]
    if start != 0:
        gaps.append((0, start))
    for (start1, val1), (start2, _) in itertools.pairwise(clean_data):
        end1 = start1 + len(val1)
        # normalize_memory should already have merged consecutive segments
        assert end1 < start2
        gaps.append((end1, start2 - end1))

    # Merge segments and gaps into a list of sparse bytes items
    sparse_data: list[tuple[int, int | bytes]] = sorted(
        cast('list[tuple[int, int | bytes]]', clean_data) + cast('list[tuple[int, int | bytes]]', gaps), reverse=True
    )

    sparse_k = dot_sb()
    for _, gap_or_val in sparse_data:
        if isinstance(gap_or_val, int):
            sparse_k = sb_empty_cons(sb_empty(intToken(gap_or_val)), sparse_k)
        elif isinstance(gap_or_val, bytes):
            sparse_k = sb_bytes_cons(sb_bytes(bytesToken(gap_or_val)), sparse_k)
        else:
            raise AssertionError()
    return sparse_k


def sort_memory() -> KSort:
    return KSort('SparseBytes')


def load_byte(mem: KInner, addr: KInner) -> KInner:
    return KApply('Memory:loadByte', mem, addr)


def store_byte(mem: KInner, addr: KInner, value: KInner) -> KInner:
    return KApply('Memory:storeByte', mem, addr, value)


def regs(dct: dict[int, int]) -> KInner:
    regs: dict[KInner, KInner] = {intToken(k): word(v) for k, v in dct.items()}
    return map_of(regs)
