from config import Config
from wire import Wire
# class acc,buffer,noc

class Accumulator:
    def __init__(self,config,technode):
        self.clk_freq = config.clk_freq
        self.power = 1
        self.latency = 1
        self.area = 0
        self.latency_per_bit = 0 #not use
        self.energy_per_bit = 0 # depends on clk_freq
    def get_area(self):
        return 1

class SoftmaxUnit:
    def __init__(self,config,technode):
        self.clk_freq = config.clk_freq
        self.latency_per_byte = 7e-7 /512 # input values: 512
        self.power = 8e-3 # input values: 512
        self.energy_per_byte = self.latency_per_byte * self.power # depends on clk_freq
        self.area = 3.00E-07 # input values: 512
    def get_area(self):
        return self.area

class Buffer:
    def __init__(self,config,technode,mem_width=128,mem_height=128):
        self.clk_freq = config.clk_freq
        self.power = 1
        self.latency = 1
        self.area = 0
        self.bandwidth = 3.18e12 # unit: scale from original constant:(ddr_bandwidth=370 GBps) * 1024 * 1024 * 1024 * 8bit
        self.energy_per_bit = 0 # depends on clk_freq
        self.mem_width = mem_width
        self.mem_height = mem_height
    def get_area(self):
        return 1

class Noc:
    def __init__(self,config,technode,chiplet_type):
        self.clk_freq = config.clk_freq
        self.power = 1
        self.latency = 1
        self.area = 0
    def get_area(self):
        return 1

class Htree:
    def __init__(self,config,technode,num_unit_height,num_unit_width,subarray_size_height,subarray_size_width):
        self.clk_freq = config.clk_freq
        self.power = 1
        self.latency = 1
        self.area = 0
        self.technode = technode
        self.wire = Wire(technode)
        self.num_unit_height = num_unit_height
        self.num_unit_width = num_unit_width
        self.subarray_size_height = subarray_size_height
        self.subarray_size_width = subarray_size_width
    def get_area(self):
        # self.Area_StaticPE_Wire = StaticWire_unitLengthArea * (Static_PESize_height * staticChip_PErowNum + Static_PESize_width * staticChip_PEcolNum)

        # StaticWire_unitLengthArea = self.wire.get_wire_unitLengthArea()
        # Static_PESize_height = self.subarray_size_height
        # staticChip_PErowNum = self.num_unit_height
        # Static_PESize_width = self.subarray_size_width
        # staticChip_PEcolNum = self.num_unit_width
        # self.area = 

        # nearly 2e-08: from Neurosim 
        # [Desired Conventional Mapped Tile Storage Size: 1024x1024
        # Desired Conventional PE Storage Size: 512x512
        # User-defined SubArray Size: 128x128]
        return 2e-08 
    def get_latency(self):
        # nearly 2e-05 each Transformer layer: from Neurosim 
        # [Desired Conventional Mapped Tile Storage Size: 1024x1024
        # Desired Conventional PE Storage Size: 512x512
        # User-defined SubArray Size: 128x128]
        return 2e-05 
    def get_energy(self):
        # nearly 3.5e-07 each Transformer layer: from Neurosim 
        # [Desired Conventional Mapped Tile Storage Size: 1024x1024
        # Desired Conventional PE Storage Size: 512x512
        # User-defined SubArray Size: 128x128]
        return 3.5e-07

# TODO: factor in, e.g. latency and energy/power is xxx% of total chip.    
class ClkTree:
    def __init__(self,config,technode):
        self.clk_freq = config.clk_freq
        self.power = 0
        self.latency = 0
        self.area = 0
    def get_area(self):
        return self.area

# TODO: factor in, e.g. latency and energy/power is xxx% of total chip.
class Controller:
    def __init__(self,config,technode):
        self.clk_freq = config.clk_freq
        self.power = 0
        self.latency = 0
        self.area = 0
    def get_area(self):
        return self.area
