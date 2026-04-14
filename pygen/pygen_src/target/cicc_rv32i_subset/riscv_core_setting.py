import math
from pygen_src.riscv_instr_pkg import (privileged_reg_t, riscv_instr_group_t,
                                       riscv_instr_name_t, mtvec_mode_t,
                                       privileged_mode_t, satp_mode_t)


# -----------------------------------------------------------------------------
# Processor feature configuration
# -----------------------------------------------------------------------------

# XLEN
XLEN = 32

# set to BARE if address translation is not supported
SATP_MODE = satp_mode_t.BARE

# Supported Privileged mode
supported_privileged_mode = [privileged_mode_t.MACHINE_MODE]

# Unsupported instructions
unsupported_instr = [
    riscv_instr_name_t.LUI,
    riscv_instr_name_t.AUIPC,
    riscv_instr_name_t.BLT,
    riscv_instr_name_t.BGE,
    riscv_instr_name_t.BLTU,
    riscv_instr_name_t.BGEU,
    riscv_instr_name_t.LB,
    riscv_instr_name_t.LH,
    riscv_instr_name_t.LBU,
    riscv_instr_name_t.LHU,
    riscv_instr_name_t.SB,
    riscv_instr_name_t.SH,
    riscv_instr_name_t.SLTI,
    riscv_instr_name_t.SLTIU,
    riscv_instr_name_t.XORI,
    riscv_instr_name_t.ANDI,
    riscv_instr_name_t.SLLI,
    riscv_instr_name_t.SRLI,
    riscv_instr_name_t.SRAI,
    riscv_instr_name_t.SLT,
    riscv_instr_name_t.SLTU,
    riscv_instr_name_t.NOP,
    riscv_instr_name_t.FENCE,
    riscv_instr_name_t.FENCE_I,
    riscv_instr_name_t.SFENCE_VMA,
    riscv_instr_name_t.ECALL,
    riscv_instr_name_t.EBREAK,
    riscv_instr_name_t.URET,
    riscv_instr_name_t.SRET,
    riscv_instr_name_t.MRET,
    riscv_instr_name_t.DRET,
    riscv_instr_name_t.WFI,
    riscv_instr_name_t.CSRRW,
    riscv_instr_name_t.CSRRS,
    riscv_instr_name_t.CSRRC,
    riscv_instr_name_t.CSRRWI,
    riscv_instr_name_t.CSRRSI,
    riscv_instr_name_t.CSRRCI
]

# ISA supported by the processor
supported_isa = [riscv_instr_group_t.RV32I]

# MARK: Target-local bring-up flag for subset-safe shared runtime scaffold
cicc_subset_runtime_enable = 1

# MARK: CICC runtime data memory base aligned with soc_8000 linker/platform layout
cicc_subset_dmem_base = 0x80001000

# MARK: Target-local flag for first-stage controlled DMem base/offset bring-up
# Keep the anchor path available as a fallback, but generic load/store is now the default path.
cicc_dmem_anchor_mode_enable = 0

# MARK: Subset-safe scaffold anchors used by phase-1 load/store bring-up
cicc_subset_imem_anchor_pc = 0x80000004
cicc_dmem_anchor_addrs = [
    0x800010C8,
    0x800011C8,
    0x800014C8,
    0x800015C8
]
cicc_dmem_anchor_offsets = [-16, -12, -8, -4, 0, 4, 8, 12, 16]

# Interrupt mode support
supported_interrupt_mode = [mtvec_mode_t.DIRECT, mtvec_mode_t.VECTORED]

# The number of interrupt vectors to be generated, only used if VECTORED
# interrupt mode is supported
max_interrupt_vector_num = 16

# Physical memory protection support
support_pmp = 0

# Debug mode support
support_debug_mode = 0

# Support delegate trap to user mode
support_umode_trap = 0

# Support sfence.vma instruction
support_sfence = 0

# Support unaligned load/store
support_unaligned_load_store = 1

# GPR Setting
NUM_FLOAT_GPR = 32
NUM_GPR = 32
NUM_VEC_GPR = 32

# -----------------------------------------------------------------------------
# Vector extension configuration
# -----------------------------------------------------------------------------

# Parameter for vector extension
VECTOR_EXTENSION_ENABLE = 0

VLEN = 512

# Maximum size of a single vector element
ELEN = 32

# Minimum size of a sub-element, which must be at most 8-bits.
SELEN = 8

# Maximum size of a single vector element (encoded in vsew format)
VELEN = int(math.log(ELEN) // math.log(2)) - 3

# Maxium LMUL supported by the core
MAX_LMUL = 8


# -----------------------------------------------------------------------------
# Multi-harts configuration
# -----------------------------------------------------------------------------

# Number of harts
NUM_HARTS = 1

# -----------------------------------------------------------------------------
# Previleged CSR implementation
# -----------------------------------------------------------------------------

# Implemented previlieged CSR list
implemented_csr = [privileged_reg_t.MVENDORID,  # Vendor ID
                   privileged_reg_t.MARCHID,  # Architecture ID
                   privileged_reg_t.MIMPID,  # Implementation ID
                   privileged_reg_t.MHARTID,  # Hardware thread ID
                   privileged_reg_t.MSTATUS,  # Machine status
                   privileged_reg_t.MISA,  # ISA and extensions
                   privileged_reg_t.MIE,  # Machine interrupt-enable register
                   privileged_reg_t.MTVEC,  # Machine trap-handler base address
                   privileged_reg_t.MCOUNTEREN,  # Machine counter enable
                   privileged_reg_t.MSCRATCH,  # Scratch register for machine trap handlers
                   privileged_reg_t.MEPC,  # Machine exception program counter
                   privileged_reg_t.MCAUSE,  # Machine trap cause
                   privileged_reg_t.MTVAL,  # Machine bad address or instruction
                   privileged_reg_t.MIP  # Machine interrupt pending
                   ]

# Implementation-specific custom CSRs
custom_csr = []
