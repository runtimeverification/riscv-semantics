from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.proof import ProofStatus

from kriscv.elf_parser import ELF, Symbol

from .utils import TEST_DATA_DIR

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

    from pyk.kast import KInner
    from pyk.kast.outer import KClaim

    from kriscv.symtools import SymTools
    from kriscv.tools import Tools


_ELF: Final = ELF(
    entry_point=8,
    memory={
        0: (
            b'\x01\x00\x00\x00'  # OP1 data
            b'\x02\x00\x00\x00'  # OP2 data
            b'\x83\x20\x00\x00'  # lw  x1, 0(x0)
            b'\x03\x21\x40\x00'  # lw  x2, 4(x0)
            b'\xb3\x81\x20\x00'  # add x3, x1, x2
        )
    },
    symbols={
        'OP1': [Symbol(0, 4)],
        'OP2': [Symbol(4, 4)],
        'END': [Symbol(20, 0)],
    },
)


def test_concrete_config_from_elf(tools: Tools) -> None:
    # Given
    config = tools.config_from_elf(_ELF, end_symbol='END')

    # When
    config = tools.run_config(config)

    # Then
    assert tools.get_registers(config) == {0: 0, 1: 1, 2: 2, 3: 3}


def test_symbolic_config_from_elf(tools: Tools, symtools: SymTools, tmp_path: Path) -> None:
    from pyk.kast.inner import KApply, KLabel, KSequence, KSort, KVariable, Subst
    from pyk.kast.outer import KFlatModule, KImport
    from pyk.kast.prelude.collections import map_of
    from pyk.kast.prelude.kint import addInt, andInt
    from pyk.kast.prelude.utils import token

    OP1 = KVariable('OP1', 'Bytes')  # noqa: N806
    OP2 = KVariable('OP2', 'Bytes')  # noqa: N806
    LE = KApply('littleEndianBytes')  # noqa: N806
    Unsigned = KApply('unsignedBytes')  # noqa: N806
    Bytes2Int = KLabel('Bytes2Int(_,_,_)_BYTES-HOOKED_Int_Bytes_Endianness_Signedness')  # noqa: N806

    # Given
    spec_file = tmp_path / 'test-spec.k'

    init_config = tools.config_from_elf(_ELF, end_symbol='END', symbolic_names=['OP1', 'OP2'])
    empty_config = tools.krun.definition.empty_config(KSort('GeneratedTopCell'))
    regs: dict[KInner, KInner] = {
        token(1): Bytes2Int(OP1, LE, Unsigned),
        token(2): Bytes2Int(OP2, LE, Unsigned),
        token(3): andInt(addInt(Bytes2Int(OP1, LE, Unsigned), Bytes2Int(OP2, LE, Unsigned)), token(4294967295)),
    }
    final_config = Subst(
        {
            'INSTRS_CELL': KSequence(KApply('#HALT'), KApply('#EXECUTE')),
            'REGS_CELL': map_of(regs),
        },
    )(empty_config)

    claim = _claim_from_configs(init_config, final_config)
    module = KFlatModule('TEST-SPEC', sentences=(claim,), imports=(KImport('RISCV'),))
    spec_file.write_text(tools.kprint.pretty_print(module))

    # When
    proof = symtools.prove(spec_file=spec_file, spec_module='TEST-SPEC', claim_id='test')

    # Then
    assert proof.status == ProofStatus.PASSED

    # And given
    show_expected = (TEST_DATA_DIR / 'symbolic-config-from-elf.golden').read_text()

    # When
    show_actual = '\n'.join(symtools.proof_show.show(proof, nodes=[node.id for node in proof.kcfg.nodes]))

    # Then
    assert show_actual == show_expected


def _claim_from_configs(init_config: KInner, final_config: KInner) -> KClaim:
    from pyk.cterm import CTerm, cterm_build_rule
    from pyk.kast.manip import remove_generated_cells
    from pyk.kast.outer import KClaim

    init_cterm = CTerm.from_kast(remove_generated_cells(init_config))
    final_cterm = CTerm.from_kast(remove_generated_cells(final_config))

    rule, _ = cterm_build_rule('test', init_cterm, final_cterm)
    claim = KClaim(body=rule.body, requires=rule.requires, att=rule.att)

    return claim
