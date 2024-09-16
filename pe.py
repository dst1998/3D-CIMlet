from config import Config
from subarray import Subarray
from peripheral import Accumulator,Buffer,Htree,SoftmaxUnit

class Pe:
    def __init__(self,config,technode,chiplet_type,memory_cell_type):
        self.chiplet_type = chiplet_type # chiplet_type = 'dynamic', static, acc_and_buffer
        self.technode = technode
        self.pe_height = None
        self.pe_width = None
        self.subarray = Subarray(config,technode,chiplet_type,memory_cell_type)
        self.subarray_size_height = self.subarray.get_size_height() # how long (m)
        self.subarray_size_width = self.subarray.get_size_width() # how long (m)
        self.accumulator = Accumulator(config,technode)
        self.buffer = Buffer(config,technode)
        self.sfu = None
        self.htree = Htree(config,technode,self.pe_height,self.pe_width,self.subarray_size_height,self.subarray_size_width)
        self.memory_cell_type = memory_cell_type # 'eDRAM', 'RRAM', none (acc_and_buffer)
        self.used_pe_height = None
        self.used_pe_width = None
        
        if chiplet_type == 'static':
            self.pe_height = config.static_pe_height # num of subarray rows in a pe
            self.pe_width = config.static_pe_width # num of subarray cols in a pe
        if chiplet_type == 'dynamic':
            self.pe_height = config.dynamic_pe_height # num of subarray rows in a pe
            self.pe_width = config.dynamic_pe_width # num of subarray cols in a pe
            self.sfu = SoftmaxUnit(config,technode)
        

    def get_area(self):
        subarrays_area = self.subarray.get_area() * self.pe_height * self.pe_width
        area = subarrays_area + self.buffer.get_area() + self.accumulator.get_area() + self.htree.get_area()
        return area