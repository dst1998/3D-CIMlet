import math
from config import Config
from subarray import Subarray
from peripheral import *

class Pe:
    def __init__(self,config,technode,chiplet_type,memory_cell_type,chip_buffer_mem_height,chip_buffer_mem_width):
        self.chiplet_type = chiplet_type # chiplet_type = 'dynamic', static, acc_and_buffer
        self.technode = technode
        self.pe_height = None
        self.pe_width = None
        self.subarray = Subarray(config,technode,chiplet_type,memory_cell_type)
        self.subarray_size_height = self.subarray.get_size_height() # how long (m)
        self.subarray_size_width = self.subarray.get_size_width() # how long (m)
        self.sfu = None
        self.memory_cell_type = memory_cell_type # 'eDRAM', 'RRAM', none (acc_and_buffer)
        self.used_pe_height = None
        self.used_pe_width = None
        
        if chiplet_type == 'static':
            self.pe_height = config.static_pe_height # num of subarray rows in a pe
            self.pe_width = config.static_pe_width # num of subarray cols in a pe
            self.sfu = SoftmaxUnit(config,technode,memory_cell_type)
        if chiplet_type == 'dynamic':
            self.pe_height = config.dynamic_pe_height # num of subarray rows in a pe
            self.pe_width = config.dynamic_pe_width # num of subarray cols in a pe
            self.sfu = SoftmaxUnit(config,technode,memory_cell_type)
        self.buffer = Buffer(config,technode,math.ceil(chip_buffer_mem_height/self.pe_height),math.ceil(chip_buffer_mem_width/self.pe_width))
        self.accumulator = Accumulator(config,technode,memory_cell_type,self.pe_width * self.subarray.subarray_width)
        self.htree = Htree(config,technode,self.pe_height,self.pe_width,self.subarray.subarray_height,self.subarray_size_height,self.subarray_size_width,foldedratio=16)
        

    def get_area(self):
        subarrays_area = self.subarray.get_area() * self.pe_height * self.pe_width
        area = subarrays_area + self.buffer.get_area() + self.accumulator.get_area() + self.htree.get_area() + self.sfu.get_area()
        # print("pe area: ",area)
        return area