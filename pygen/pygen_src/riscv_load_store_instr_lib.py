
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

import sys
import copy
import random
import logging
import vsc
from enum import IntEnum, auto
from importlib import import_module
from pygen_src.riscv_instr_gen_config import cfg
from pygen_src.isa.riscv_instr import riscv_instr
from pygen_src.riscv_directed_instr_lib import riscv_mem_access_stream
from pygen_src.riscv_instr_pkg import riscv_reg_t, riscv_instr_name_t, riscv_instr_group_t
rcs = import_module("pygen_src.target." + cfg.argv.target + ".riscv_core_setting")


class locality_e(IntEnum):
    NARROW = 0
    HIGH = auto()
    MEDIUM = auto()
    SPARSE = auto()


CICC_SUBSET_OFFSET_RETRY_LIMIT = 1024


# Base class for all load/store instruction stream
@vsc.randobj
class riscv_load_store_base_instr_stream(riscv_mem_access_stream):
    def __init__(self):
        super().__init__()
        self.num_load_store = vsc.rand_uint32_t()
        self.num_mixed_instr = vsc.rand_uint32_t()
        self.base = vsc.rand_int32_t()
        self.offset = []
        self.addr = []
        self.load_store_instr = []
        self.data_page_id = vsc.rand_uint32_t()
        self.rs1_reg = vsc.rand_enum_t(riscv_reg_t)
        self.locality = vsc.rand_enum_t(locality_e)
        self.max_load_store_offset = vsc.rand_int32_t()
        self.use_sp_as_rs1 = vsc.rand_bit_t()

    @vsc.constraint
    def sp_rnd_order_c(self):
        vsc.solve_order(self.use_sp_as_rs1, self.rs1_reg)

    @vsc.constraint
    def sp_c(self):
        vsc.dist(self.use_sp_as_rs1, [vsc.weight(1, 1), vsc.weight(0, 2)])
        with vsc.if_then(self.use_sp_as_rs1 == 1):
            self.rs1_reg == riscv_reg_t.SP

    # TODO Getting pyvsc error -- > rs1 has not been build yet
    '''@vsc.constraint
    def rs1_c(self):
        self.rs1_reg.not_inside(vsc.rangelist(cfg.reserved_regs,
                                              self.reserved_rd, riscv_reg_t.ZERO))'''

    @vsc.constraint
    def addr_c(self):
        # TODO solve_order
        # vsc.solve_order(self.data_page_id, self.max_load_store_offset)
        # vsc.solve_order(self.max_load_store_offset, self.base)
        self.data_page_id < self.max_data_page_id
        with vsc.foreach(self.data_page, idx = True) as i:
            with vsc.if_then(i == self.data_page_id):
                self.max_load_store_offset == self.data_page[i].size_in_bytes
        self.base in vsc.rangelist(vsc.rng(0, self.max_load_store_offset - 1))

    def disable_sp_as_rs1(self):
        self.use_sp_as_rs1 = 0
        with vsc.raw_mode():
            self.use_sp_as_rs1.rand_mode = False
        self.sp_rnd_order_c.constraint_mode(False)

    def is_cicc_subset_load_store_mode(self):
        return self.is_cicc_subset_dmem_anchor_mode()

    def is_cicc_subset_generic_load_store_mode(self):
        return (self.is_cicc_subset_runtime() and
                not self.is_cicc_subset_load_store_mode() and
                not self.load_store_shared_memory and
                not self.kernel_mode)

    def get_cicc_subset_reserved_regs(self):
        reserved = {riscv_reg_t.ZERO, riscv_reg_t.SP,
                    self.get_cicc_subset_reg_enum(cfg.scratch_reg)}
        for reg in list(cfg.reserved_regs):
            reserved.add(self.get_cicc_subset_reg_enum(reg))
        for reg in list(self.reserved_rd):
            reserved.add(self.get_cicc_subset_reg_enum(reg))
        return reserved

    def get_cicc_subset_safe_rs1_regs(self):
        reserved = self.get_cicc_subset_reserved_regs()
        return [reg for reg in riscv_reg_t if reg not in reserved]

    def sanitize_cicc_subset_rs1_reg(self):
        safe_regs = self.get_cicc_subset_safe_rs1_regs()
        if len(safe_regs) == 0:
            logging.critical("No safe cicc subset load/store rs1 registers are available")
            sys.exit(1)
        current = self.get_cicc_subset_reg_enum(self.rs1_reg)
        if current not in safe_regs:
            self.rs1_reg = random.choice(safe_regs)

    def configure_cicc_subset_load_store_mode(self):
        base_regs = self.get_cicc_subset_base_regs()
        if len(base_regs) == 0:
            logging.critical("No approved cicc subset load/store base regs are available")
            sys.exit(1)
        for reg in base_regs:
            if reg not in cfg.reserved_regs:
                cfg.reserved_regs.append(reg)
        self.disable_sp_as_rs1()
        self.rs1_reg = random.choice(base_regs)
        self.base = 0

    def randomize_cicc_subset_offset(self):
        offset_choices = self.get_cicc_subset_offset_choices()
        if len(offset_choices) == 0:
            logging.critical("No approved cicc subset load/store offsets are available")
            sys.exit(1)
        anchor_addr = self.get_cicc_subset_anchor_addr(self.rs1_reg)
        self.offset = [0] * self.num_load_store
        self.addr = [0] * self.num_load_store
        for i in range(self.num_load_store):
            self.offset[i] = random.choice(offset_choices)
            self.addr[i] = anchor_addr + self.offset[i]

    def get_cicc_subset_final_ea(self, idx):
        idx = self.get_cicc_subset_int(idx)
        offset = self.get_cicc_subset_int(self.offset[idx])
        if self.is_cicc_subset_load_store_mode():
            return self.get_cicc_subset_anchor_addr(self.rs1_reg) + offset
        page_base = self.get_cicc_subset_user_data_page_abs_base(self.data_page_id)
        return page_base + self.get_cicc_subset_int(self.base) + offset

    def get_cicc_subset_allowed_instr(self, idx):
        final_ea = self.get_cicc_subset_final_ea(idx)
        if (final_ea % 4) != 0:
            logging.critical("Unexpected unaligned cicc subset load/store ea=%0d offset=%0d",
                             final_ea, self.offset[idx])
            sys.exit(1)
        return [riscv_instr_name_t.LW, riscv_instr_name_t.SW]

    def randomize_offset_addr_once(self):
        addr_ = vsc.rand_int32_t()
        offset_ = vsc.rand_int32_t()
        try:
            if self.locality == locality_e.NARROW:
                offset_ = random.randrange(-16, 16)
            elif self.locality == locality_e.HIGH:
                offset_ = random.randrange(-64, 64)
            elif self.locality == locality_e.MEDIUM:
                offset_ = random.randrange(-256, 256)
            elif self.locality == locality_e.SPARSE:
                offset_ = random.randrange(-2048, 2047)
            var1 = self.base + offset_ - 1
            var2 = self.base + offset_ + 1
            addr_ = random.randrange(var1, var2)
        except Exception:
            logging.critical("Cannot randomize load/store offset")
            sys.exit(1)
        return offset_, addr_

    def randomize_cicc_subset_generic_offset_once(self):
        page_base = self.get_cicc_subset_user_data_page_abs_base(self.data_page_id)
        for _ in range(CICC_SUBSET_OFFSET_RETRY_LIMIT):
            offset_, addr_ = self.randomize_offset_addr_once()
            final_ea = page_base + self.get_cicc_subset_int(self.base) + offset_
            if self.is_cicc_subset_user_data_ea_legal(final_ea) and ((final_ea % 4) == 0):
                return offset_, addr_
        logging.critical(
            "Cannot randomize legal cicc subset load/store offset page=%0d base=%0d after %0d attempts",
            self.get_cicc_subset_int(self.data_page_id),
            self.get_cicc_subset_int(self.base),
            CICC_SUBSET_OFFSET_RETRY_LIMIT)
        sys.exit(1)

    def randomize_offset(self):
        if self.is_cicc_subset_load_store_mode():
            self.randomize_cicc_subset_offset()
            return
        self.offset = [0] * self.num_load_store
        self.addr = [0] * self.num_load_store
        for i in range(self.num_load_store):
            if self.is_cicc_subset_generic_load_store_mode():
                offset_, addr_ = self.randomize_cicc_subset_generic_offset_once()
            else:
                offset_, addr_ = self.randomize_offset_addr_once()
            self.offset[i] = offset_
            self.addr[i] = addr_

    def pre_randomize(self):
        super().pre_randomize()
        if self.is_cicc_subset_runtime():
            self.disable_sp_as_rs1()
        elif (riscv_reg_t.SP in cfg.reserved_regs or
              riscv_reg_t.SP in self.reserved_rd):
            self.disable_sp_as_rs1()

    def post_randomize(self):
        if self.is_cicc_subset_load_store_mode():
            self.configure_cicc_subset_load_store_mode()
        elif self.is_cicc_subset_generic_load_store_mode():
            self.sanitize_cicc_subset_rs1_reg()
        self.randomize_offset()
        # rs1 cannot be modified by other instructions
        if not(self.rs1_reg in self.reserved_rd):
            self.reserved_rd.append(self.rs1_reg)
        self.gen_load_store_instr()
        self.add_mixed_instr(self.num_mixed_instr)
        if self.is_cicc_subset_load_store_mode():
            self.add_rs1_init_instr(self.rs1_reg, 0, 0)
        else:
            self.add_rs1_init_instr(self.rs1_reg, self.data_page_id, self.base)
        super().post_randomize()

    # Generate each load/store instruction
    def gen_load_store_instr(self):
        allowed_instr = []
        enable_compressed_load_store = 0
        self.randomize_avail_regs()
        if ((self.rs1_reg in [riscv_reg_t.S0, riscv_reg_t.S1, riscv_reg_t.A0, riscv_reg_t.A1,
                              riscv_reg_t.A2, riscv_reg_t.A3, riscv_reg_t.A4, riscv_reg_t.A5,
                              riscv_reg_t.SP]) and not(cfg.disable_compressed_instr)):
            enable_compressed_load_store = 1
        for i in range(len(self.addr)):
            if self.is_cicc_subset_runtime() and not self.load_store_shared_memory and \
                    not self.kernel_mode:
                instr = copy.deepcopy(riscv_instr.get_instr(random.choice(
                    self.get_cicc_subset_allowed_instr(i))))
                instr.has_rs1 = 0
                instr.has_imm = 0
                self.randomize_gpr(instr)
                instr.rs1 = self.rs1_reg
                instr.imm_str = str(instr.uintToInt(self.offset[i]))
                instr.process_load_store = 0
                self.instr_list.append(instr)
                self.load_store_instr.append(instr)
                continue
            # Assign the allowed load/store instructions based on address alignment
            # This is done separately rather than a constraint to improve the randomization
            # performance
            allowed_instr.extend(
                [riscv_instr_name_t.LB, riscv_instr_name_t.LBU, riscv_instr_name_t.SB])
            if not cfg.enable_unaligned_load_store:
                if (self.addr[i] & 1) == 0:
                    allowed_instr.extend(
                        [riscv_instr_name_t.LH, riscv_instr_name_t.LHU, riscv_instr_name_t.SH])
                if self.addr[i] % 4 == 0:
                    allowed_instr.extend([riscv_instr_name_t.LW, riscv_instr_name_t.SW])
                    if cfg.enable_floating_point:
                        allowed_instr.extend([riscv_instr_name_t.FLW,
                                              riscv_instr_name_t.FSW])
                    if ((self.offset[i] in range(128)) and (self.offset[i] % 4 == 0) and
                        (riscv_instr_group_t.RV32C in rcs.supported_isa) and
                            (enable_compressed_load_store)):
                        if self.rs1_reg == riscv_reg_t.SP:
                            logging.info("Add LWSP/SWSP to allowed instr")
                            allowed_instr.extend(
                                [riscv_instr_name_t.C_LWSP, riscv_instr_name_t.C_SWSP])
                        else:
                            allowed_instr.extend(
                                [riscv_instr_name_t.C_LW, riscv_instr_name_t.C_SW])
                            if (cfg.enable_floating_point and
                                    riscv_instr_group_t.RV32FC in rcs.supported_isa):
                                allowed_instr.extend(
                                    [riscv_instr_name_t.C_FLW, riscv_instr_name_t.C_FSW])
                if (rcs.XLEN >= 64) and (self.addr[i] % 8 == 0):
                    allowed_instr.extend([riscv_instr_name_t.LWU,
                                          riscv_instr_name_t.LD,
                                          riscv_instr_name_t.SD])
                    if (cfg.enable_floating_point and
                            (riscv_instr_group_t.RV32D in rcs.supported_isa)):
                        allowed_instr.extend([riscv_instr_name_t.FLD,
                                              riscv_instr_name_t.FSD])
                    if (self.offset[i] in range(256) and (self.offset[i] % 8 == 0) and
                        (riscv_instr_group_t.RV64C in rcs.supported_isa) and
                            enable_compressed_load_store):
                        if self.rs1_reg == riscv_reg_t.SP:
                            allowed_instr.extend(
                                [riscv_instr_name_t.C_LDSP, riscv_instr_name_t.C_SDSP])
                        else:
                            allowed_instr.extend(
                                [riscv_instr_name_t.C_LD, riscv_instr_name_t.C_SD])
                            if (cfg.enable_floating_point and
                                    (riscv_instr_group_t.RV32DC in rcs.supported_isa)):
                                allowed_instr.extend(
                                    [riscv_instr_name_t.C_FLD, riscv_instr_name_t.C_FSD])
                else:  # unalligned load/store
                    allowed_instr.extend([riscv_instr_name_t.LW, riscv_instr_name_t.SW,
                                          riscv_instr_name_t.LH, riscv_instr_name_t.LHU,
                                          riscv_instr_name_t.SH])
                    # Compressed load/store still needs to be alligned
                    if (self.offset[i] in range(128) and (self.offset[i] % 4 == 0) and
                        (riscv_instr_group_t.RV32C in rcs.supported_isa) and
                            enable_compressed_load_store):
                        if self.rs1_reg == riscv_reg_t.SP:
                            allowed_instr.extend(
                                [riscv_instr_name_t.C_LWSP, riscv_instr_name_t.C_SWSP])
                        else:
                            allowed_instr.extend(
                                [riscv_instr_name_t.C_LW, riscv_instr_name_t.C_SW])
                    if rcs.XLEN >= 64:
                        allowed_instr.extend(
                            [riscv_instr_name_t.LWU, riscv_instr_name_t.LD, riscv_instr_name_t.SD])
                        if (self.offset[i] in range(256) and (self.offset[i] % 8 == 0) and
                            (riscv_instr_group_t.RV64C in rcs.supported_isa) and
                                enable_compressed_load_store):
                            if self.rs1_reg == riscv_reg_t.SP:
                                allowed_instr.extend(
                                    [riscv_instr_name_t.C_LWSP, riscv_instr_name_t.C_SWSP])
                            else:
                                allowed_instr.extend(
                                    [riscv_instr_name_t.C_LD, riscv_instr_name_t.C_SD])
            instr = copy.deepcopy(riscv_instr.get_load_store_instr(allowed_instr))
            instr.has_rs1 = 0
            instr.has_imm = 0
            self.randomize_gpr(instr)
            instr.rs1 = self.rs1_reg
            instr.imm_str = str(instr.uintToInt(self.offset[i]))
            instr.process_load_store = 0
            self.instr_list.append(instr)
            self.load_store_instr.append(instr)


# A single load/store instruction
@vsc.randobj
class riscv_single_load_store_instr_stream(riscv_load_store_base_instr_stream):
    def __init__(self):
        super().__init__()

    @vsc.constraint
    def legal_c(self):
        self.num_load_store == 1
        self.num_mixed_instr < 5


# Back to back load/store instructions
@vsc.randobj
class riscv_load_store_stress_instr_stream(riscv_load_store_base_instr_stream):
    def __init__(self):
        super().__init__()
        self.max_instr_cnt = 30
        self.min_instr_cnt = 10

    @vsc.constraint
    def legal_c(self):
        self.num_load_store.inside(vsc.rangelist(vsc.rng(self.min_instr_cnt, self.max_instr_cnt)))
        self.num_mixed_instr == 0


# Back to back load/store instructions
@vsc.randobj
class riscv_load_store_shared_mem_stream(riscv_load_store_stress_instr_stream):
    def __init__(self):
        super().__init__()

    def pre_randomize(self):
        self.load_store_shared_memory = 1
        super().pre_randomize()


# Random load/store sequence
# A random mix of load/store instructions and other instructions
@vsc.randobj
class riscv_load_store_rand_instr_stream(riscv_load_store_base_instr_stream):
    def __init__(self):
        super().__init__()

    @vsc.constraint
    def legal_c(self):
        self.num_load_store.inside(vsc.rangelist(vsc.rng(10, 30)))
        self.num_mixed_instr.inside(vsc.rangelist(vsc.rng(10, 30)))


# Use a small set of GPR to create various WAW, RAW, WAR hazard scenario
@vsc.randobj
class riscv_load_store_hazard_instr_stream(riscv_load_store_base_instr_stream):
    def __init__(self):
        super().__init__()
        self.hazard_ratio = vsc.rand_int32_t()

    @vsc.constraint
    def hazard_ratio_c(self):
        self.hazard_ratio.inside(vsc.rangelist(vsc.rng(20, 100)))

    @vsc.constraint
    def legal_c(self):
        self.num_load_store.inside(vsc.rangelist(vsc.rng(10, 20)))
        self.num_mixed_instr.inside(vsc.rangelist(vsc.rng(1, 7)))

    def randomize_offset(self):
        if self.is_cicc_subset_load_store_mode():
            offset_choices = self.get_cicc_subset_offset_choices()
            if len(offset_choices) == 0:
                logging.critical("No approved cicc subset hazard load/store offsets are available")
                sys.exit(1)
            anchor_addr = self.get_cicc_subset_anchor_addr(self.rs1_reg)
            self.offset = [0] * self.num_load_store
            self.addr = [0] * self.num_load_store
            rand_num = random.randrange(0, 100)
            for i in range(self.num_load_store):
                if (i > 0) and (rand_num < self.hazard_ratio):
                    self.offset[i] = self.offset[i - 1]
                    self.addr[i] = self.addr[i - 1]
                else:
                    self.offset[i] = random.choice(offset_choices)
                    self.addr[i] = anchor_addr + self.offset[i]
            return
        self.offset = [0] * self.num_load_store
        self.addr = [0] * self.num_load_store
        rand_num = random.randrange(0, 100)
        for i in range(self.num_load_store):
            if (i > 0) and (rand_num < self.hazard_ratio):
                self.offset[i] = self.offset[i - 1]
                self.addr[i] = self.addr[i - 1]
            else:
                if self.is_cicc_subset_generic_load_store_mode():
                    offset_, addr_ = self.randomize_cicc_subset_generic_offset_once()
                else:
                    offset_, addr_ = self.randomize_offset_addr_once()
                self.offset[i] = offset_
                self.addr[i] = addr_
