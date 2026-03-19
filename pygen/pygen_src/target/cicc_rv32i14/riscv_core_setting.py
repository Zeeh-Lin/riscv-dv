"""
Copyright 2020 Google LLC
Copyright 2020 PerfectVIPs Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

import math
from pygen_src.riscv_instr_pkg import (
    mtvec_mode_t,
    privileged_mode_t,
    riscv_instr_group_t,
    riscv_instr_name_t,
    satp_mode_t,
)


XLEN = 32
SATP_MODE = satp_mode_t.BARE

supported_privileged_mode = [privileged_mode_t.MACHINE_MODE]

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
    riscv_instr_name_t.XOR,
    riscv_instr_name_t.SRA,
    riscv_instr_name_t.NOP,
    riscv_instr_name_t.FENCE,
    riscv_instr_name_t.FENCE_I,
    riscv_instr_name_t.ECALL,
    riscv_instr_name_t.EBREAK,
    riscv_instr_name_t.CSRRW,
    riscv_instr_name_t.CSRRS,
    riscv_instr_name_t.CSRRC,
    riscv_instr_name_t.CSRRWI,
    riscv_instr_name_t.CSRRSI,
    riscv_instr_name_t.CSRRCI,
]

supported_isa = [riscv_instr_group_t.RV32I]
supported_interrupt_mode = [mtvec_mode_t.DIRECT]
max_interrupt_vector_num = 0

support_pmp = 0
support_debug_mode = 0
support_umode_trap = 0
support_sfence = 0
support_unaligned_load_store = 0

NUM_FLOAT_GPR = 32
NUM_GPR = 32
NUM_VEC_GPR = 32

VECTOR_EXTENSION_ENABLE = 0
VLEN = 512
ELEN = 32
SELEN = 8
VELEN = int(math.log(ELEN) // math.log(2)) - 3
MAX_LMUL = 8

NUM_HARTS = 1

implemented_csr = []
custom_csr = []

# Used by the local wrapper in riscv_asm_program_gen.py to emit a CSR-free
# single-hart runtime scaffold.
cicc_simplified_runtime = 1
cicc_allow_random_load_store = 1
