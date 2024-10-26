from config import Config
from peripheral import *
import math

class Subarray:
    def __init__(self,config,technode,chiplet_type,memory_cell_type):
        self.chiplet_type = chiplet_type # chiplet_type = dynamic, static_0, static_2, acc_and_buffer
        self.technode = technode
        # self.buffer = Buffer(config,technode)
        self.subarray_height = None
        self.subarray_width = None
        self.cell_size = 0
        self.read_energy_per_bit = 0
        self.write_energy_per_bit = 0 # now, only used in refresh energy, how about write energy? write energy only include buffer_write energy
        if chiplet_type == 'static_0':
            self.subarray_height = config.static_subarray_height # num of cell rows in a subarray
            self.subarray_width = config.static_subarray_width # num of cell cols in a subarray
        elif chiplet_type == 'static_2':
            self.subarray_height = config.dynamic_subarray_height # num of cell rows in a subarray
            self.subarray_width = config.dynamic_subarray_width # num of cell cols in a subarray
        elif chiplet_type == 'dynamic':
            self.subarray_height = config.dynamic_subarray_height # num of cell rows in a subarray
            self.subarray_width = config.dynamic_subarray_width # num of cell cols in a subarray
        self.memory_cell_type = memory_cell_type # 'eDRAM', RRAM, none (acc_and_buffer)
        if memory_cell_type == 'eDRAM':
            if self.technode == 28:
                self.cell_size = config.eDRAM_cell_size_28nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_28nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_28nm
            elif self.technode == 40:
                self.cell_size = config.eDRAM_cell_size_40nm
                self.read_energy_per_bit =  config.eDRAM_read_energy_per_bit_40nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_40nm
            elif self.technode == 65:
                self.cell_size = config.eDRAM_cell_size_65nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_65nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_65nm
            elif self.technode == 130:
                self.cell_size = config.eDRAM_cell_size_130nm
                self.read_energy_per_bit = config.eDRAM_read_energy_per_bit_130nm
                self.write_energy_per_bit = config.eDRAM_write_energy_per_bit_130nm
        if memory_cell_type == 'RRAM':
            self.cell_size = config.RRAM_cell_size_40nm
            self.read_energy_per_bit =  config.RRAM_read_energy_per_bit_40nm
            self.write_energy_per_bit = config.RRAM_write_energy_per_bit_40nm
            
        self.shiftadd = ShiftAdd(config,technode,self.memory_cell_type,self.subarray_width)
        
    
    def get_area(self):
        # cells_area = self.cellSize_height * self.cellSize_width * self.subarray_height * self.subarray_width
        # used_area = 81453 * 1e-12 * (self.technode/40)**2 # Neurosim: when featuresize=40, empty_area=234096 um2, for 256*256 subarray.
        # empty_area = 234096 * 1e-12 * (self.technode/40)**2 # Neurosim: when featuresize=40, empty_area=234096 um2, for all subarray height=width.
        # # area = cells_area + (used_area-cells_area)*(self.subarray_height/256) + empty_area #Neurosim
        # area = cells_area *4

        area = self.cell_size * self.subarray_height * self.subarray_width
        return area
    def get_size_height(self):
        return math.sqrt(self.get_area())
    def get_size_width(self):
        return math.sqrt(self.get_area())