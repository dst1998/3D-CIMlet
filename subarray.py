from config import Config
from peripheral import *
import math

class Subarray:
    def __init__(self,config,technode,chiplet_type,memory_cell_type):
        self.chiplet_type = chiplet_type # chiplet_type = 'dynamic', static, acc_and_buffer
        self.technode = technode
        # self.buffer = Buffer(config,technode)
        self.subarray_height = None
        self.subarray_width = None
        self.read_energy_per_bit = 0
        self.write_energy_per_bit = 0 # now, only used in refresh energy, how about write energy? write energy only include buffer_write energy
        if chiplet_type == 'static':
            self.subarray_height = config.static_subarray_height # num of cell rows in a subarray
            self.subarray_width = config.static_subarray_width # num of cell cols in a subarray
        if chiplet_type == 'dynamic':
            self.subarray_height = config.dynamic_subarray_height # num of cell rows in a subarray
            self.subarray_width = config.dynamic_subarray_width # num of cell cols in a subarray
        self.memory_cell_type = memory_cell_type # 'eDRAM', RRAM, none (acc_and_buffer)
        if memory_cell_type == 'eDRAM':
            self.cellSize_height = config.eDRAM_cellSize_height
            self.cellSize_width = config.eDRAM_cellSize_width
            self.read_energy_per_bit = 0.04e-12 # 40nm
            self.write_energy_per_bit = 0.1e-12 # 40nm
        if memory_cell_type == 'RRAM':
            self.cellSize_height = config.RRAM_cellSize_height
            self.cellSize_width = config.RRAM_cellSize_width
            self.read_energy_per_bit = 0.014e-12 # 40nm
            self.write_energy_per_bit = 2.3e-12 # 40nm
        self.shiftadd = ShiftAdd(config,technode,self.memory_cell_type,self.subarray_width)
        
    
    def get_area(self):
        # cells_area = self.cellSize_height * self.cellSize_width * self.subarray_height * self.subarray_width
        # used_area = 81453 * 1e-12 * (self.technode/40)**2 # Neurosim: when featuresize=40, empty_area=234096 um2, for 256*256 subarray.
        # empty_area = 234096 * 1e-12 * (self.technode/40)**2 # Neurosim: when featuresize=40, empty_area=234096 um2, for all subarray height=width.
        # # area = cells_area + (used_area-cells_area)*(self.subarray_height/256) + empty_area #Neurosim
        # area = cells_area *4

        # 40 nm
        if self.memory_cell_type == 'eDRAM':
            area = 1.35e05 * 1e-12 / (256*128) * self.subarray_height * self.subarray_width
        if self.memory_cell_type == 'RRAM':
            area = 6.34e04 * 1e-12 / (256*256) * self.subarray_height * self.subarray_width
        return area
    def get_size_height(self):
        return math.sqrt(self.get_area())
    def get_size_width(self):
        return math.sqrt(self.get_area())