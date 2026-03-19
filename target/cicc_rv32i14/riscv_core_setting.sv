/*
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

//-----------------------------------------------------------------------------
// Processor feature configuration
//-----------------------------------------------------------------------------
parameter int XLEN = 32;

parameter satp_mode_t SATP_MODE = BARE;

privileged_mode_t supported_privileged_mode[] = {MACHINE_MODE};

riscv_instr_name_t unsupported_instr[] = {
    LUI, AUIPC,
    BLT, BGE, BLTU, BGEU,
    LB, LH, LBU, LHU,
    SB, SH,
    SLTI, SLTIU, XORI, ANDI, SLLI, SRLI, SRAI,
    SLT, SLTU, XOR, SRA,
    NOP, FENCE, FENCE_I,
    ECALL, EBREAK,
    CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI
};

riscv_instr_group_t supported_isa[$] = {RV32I};

mtvec_mode_t supported_interrupt_mode[$] = {DIRECT};

int max_interrupt_vector_num = 0;

bit support_pmp = 0;
bit support_epmp = 0;
bit support_debug_mode = 0;
bit support_umode_trap = 0;
bit support_sfence = 0;
bit support_unaligned_load_store = 1'b0;

parameter int NUM_FLOAT_GPR = 32;
parameter int NUM_GPR = 32;
parameter int NUM_VEC_GPR = 32;

parameter int VECTOR_EXTENSION_ENABLE = 0;
parameter int VLEN = 512;
parameter int ELEN = 32;
parameter int SELEN = 8;
parameter int VELEN = int'($ln(ELEN)/$ln(2)) - 3;
parameter int MAX_LMUL = 8;

parameter int NUM_HARTS = 1;

`ifdef DSIM
privileged_reg_t implemented_csr[] = {
`else
const privileged_reg_t implemented_csr[] = {
`endif
};

bit [11:0] custom_csr[] = {
};

`ifdef DSIM
interrupt_cause_t implemented_interrupt[] = {
`else
const interrupt_cause_t implemented_interrupt[] = {
`endif
};

`ifdef DSIM
exception_cause_t implemented_exception[] = {
`else
const exception_cause_t implemented_exception[] = {
`endif
};
