import math
from config import Config
from pe import Pe
from peripheral import *

class Chiplet:
    def __init__(self,config,chiplet_type,memory_cell_type,maxnum_layer_in_bit):
        self.chiplet_type = chiplet_type # chiplet_type = dynamic, static_0, static_2, logic:acc_and_buffer
        self.technode = None
        self.accumulator = None
        self.buffer = None
        self.memory_cell_type = None
        self.chiplet_height = None
        self.chiplet_width = None
        self.pe = None
        self.noc = None
        self.maxnum_layer_in_bit = maxnum_layer_in_bit
        self.buffer_mem_height = None
        self.buffer_mem_width = None
        if chiplet_type == 'static_0':
            self.technode = config.static_chiplet_technode
            self.chiplet_height = config. static_chiplet_height # num of PE rows in a chiplet
            self.chiplet_width = config.static_chiplet_width # num of PE cols in a chiplet
            self.memory_cell_type = memory_cell_type # 'eDRAM','RRAM', none (acc_and_buffer)
            self.noc = Noc(config,self.technode,chiplet_type)
            self.buffer_mem_height = config.chip_buffer_core_height
            self.buffer_mem_width = config.chip_buffer_core_width * math.ceil(maxnum_layer_in_bit / self.buffer_mem_height / config.chip_buffer_core_width)
            self.buffer = Buffer(config,self.technode,self.buffer_mem_width,self.buffer_mem_height)
            self.pe = Pe(config,self.technode,chiplet_type,memory_cell_type,self.buffer_mem_height,self.buffer_mem_width)
            self.accumulator = Accumulator(config,self.technode,memory_cell_type,self.chiplet_width * self.pe.pe_width * self.pe.subarray.subarray_width)
        elif chiplet_type == 'static_2':
            self.technode = config.dynamic_chiplet_technode
            self.chiplet_height = config. dynamic_chiplet_height # num of PE rows in a chiplet
            self.chiplet_width = config.dynamic_chiplet_width # num of PE cols in a chiplet
            self.memory_cell_type = memory_cell_type # 'eDRAM','RRAM', none (acc_and_buffer)
            self.noc = Noc(config,self.technode,chiplet_type)
            self.buffer_mem_height = config.chip_buffer_core_height
            self.buffer_mem_width = config.chip_buffer_core_width * math.ceil(maxnum_layer_in_bit / self.buffer_mem_height / config.chip_buffer_core_width)
            self.buffer = Buffer(config,self.technode,self.buffer_mem_width,self.buffer_mem_height)
            self.pe = Pe(config,self.technode,chiplet_type,memory_cell_type,self.buffer_mem_height,self.buffer_mem_width)
            self.accumulator = Accumulator(config,self.technode,memory_cell_type,self.chiplet_width * self.pe.pe_width * self.pe.subarray.subarray_width)
        elif chiplet_type == 'dynamic':
            self.technode = config.dynamic_chiplet_technode
            self.chiplet_height = config.dynamic_chiplet_height # num of PE rows in a chiplet
            self.chiplet_width = config.dynamic_chiplet_width # num of PE cols in a chiplet
            self.memory_cell_type = memory_cell_type # 'eDRAM','RRAM', none (acc_and_buffer)
            self.noc = Noc(config,self.technode,chiplet_type)
            self.buffer_mem_height = config.chip_buffer_core_height
            self.buffer_mem_width = config.chip_buffer_core_width * math.ceil(maxnum_layer_in_bit / self.buffer_mem_height / config.chip_buffer_core_width)
            self.buffer = Buffer(config,self.technode,self.buffer_mem_width,self.buffer_mem_height)
            self.pe = Pe(config,self.technode,chiplet_type,memory_cell_type,self.buffer_mem_height,self.buffer_mem_width)
            self.accumulator = Accumulator(config,self.technode,memory_cell_type,self.chiplet_width * self.pe.pe_width * self.pe.subarray.subarray_width)
        elif chiplet_type == 'logic':
            self.technode = config.logic_chiplet_technode
            self.accumulator = Accumulator(config,self.technode)
            self.buffer_mem_height = config.global_buffer_core_height
            self.buffer_mem_width = config.global_buffer_core_width * math.ceil(maxnum_layer_in_bit / self.buffer_mem_height / config.global_buffer_core_width)
            self.buffer = Buffer(config,self.technode,self.buffer_mem_width,self.buffer_mem_height)
    
    def get_area(self):
        area = 0
        area = self.buffer.get_area() + self.accumulator.get_area()
        if self.chiplet_type in ('static_0', 'static_2','dynamic'):
            PEs_area = self.pe.get_area() * self.chiplet_height * self.chiplet_width
            # print("chip.PEs_area: ",PEs_area)
            area += PEs_area
            area += self.noc.get_area()
        
        # print("chip.buffer.get_area(): ",self.buffer.get_area())
        # print("chip.accumulator.get_area(): ",self.accumulator.get_area())
        # print("chip_area: ",area)

        return area