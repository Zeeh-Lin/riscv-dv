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

import logging
import sys
import time
from importlib import import_module

sys.path.append("pygen/")

from pygen_src.test.riscv_instr_base_test import (  # noqa: E402
    riscv_instr_base_test,
)
from pygen_src.riscv_instr_gen_config import cfg  # noqa: E402
from pygen_src.riscv_utils import gen_config_table  # noqa: E402

rcs = import_module("pygen_src.target." + cfg.argv.target + ".riscv_core_setting")


class cicc_rand_instr_test(riscv_instr_base_test):
    def __init__(self):
        super().__init__()

    def randomize_cfg(self):
        cfg.randomize()
        cfg.stack_len = 16
        cfg.enable_misaligned_instr = 0
        for reg in getattr(rcs, "cicc_reserved_data_regs", []):
            if reg not in cfg.reserved_regs:
                cfg.reserved_regs.append(reg)
        for region in cfg.mem_region:
            region.size_in_bytes = 1024
        logging.info("riscv_instr_gen_config is randomized")
        gen_config_table()

    def apply_directed_instr(self):
        self.asm.add_directed_instr_stream("riscv_load_store_rand_instr_stream", 80)
        self.asm.add_directed_instr_stream("riscv_load_store_hazard_instr_stream", 80)


start_time = time.time()
cicc_rand_test_ins = cicc_rand_instr_test()
cicc_rand_test_ins.run()
end_time = time.time()
logging.info("Total execution time: {}s".format(round(end_time - start_time)))
