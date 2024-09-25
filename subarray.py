from config import Config
from peripheral import Accumulator,Buffer
import math

class Subarray:
    def __init__(self,config,technode,chiplet_type,memory_cell_type):
        self.chiplet_type = chiplet_type # chiplet_type = 'dynamic', static, acc_and_buffer
        self.technode = technode
        self.accumulator = Accumulator(config,technode)
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
        if memory_cell_type == 'RRAM':
            self.cellSize_height = config.RRAM_cellSize_height
            self.cellSize_width = config.RRAM_cellSize_width
        
    
    def get_area(self):
        cells_area = self.cellSize_height * self.cellSize_width * self.subarray_height * self.subarray_width
        used_area = 81453 * 1e-12 * (self.technode/40)**2 # Neurosim: when featuresize=40, empty_area=234096 um2, for 256*256 subarray.
        empty_area = 234096 * 1e-12 * (self.technode/40)**2 # Neurosim: when featuresize=40, empty_area=234096 um2, for all subarray height=width.
        # area = cells_area + (used_area-cells_area)*(self.subarray_height/256) + empty_area #Neurosim
        area = cells_area *4
        print("cells_area: ",cells_area)
        print("used_area: ",used_area)
        print("empty_area: ",empty_area)
        print("subarray area: ",area)
        return area
    def get_size_height(self):
        return math.sqrt(self.get_area())
    def get_size_width(self):
        return math.sqrt(self.get_area())