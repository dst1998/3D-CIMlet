from math import ceil,sqrt
from abc import ABC, abstractmethod
from tsv_path import TSVPath

from config import Config
from chiplet import Chiplet

class Integration(ABC):
    # Area
    @abstractmethod    
    def CalculateArea(self):
        pass

class Integration2D(Integration):
    def __init__(self,config,maxnum_layer_in_bit,num_used_static_chiplet_all_layers, used_num_dynamic_chiplet):

        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_static_chiplet = num_used_static_chiplet_all_layers
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_dynamic_chiplet = used_num_dynamic_chiplet
        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit=maxnum_layer_in_bit)

    def CalculateArea(self):

        area = self.static_chiplet.get_area() * self.num_static_chiplet + self.dynamic_chiplet.get_area() * self.num_dynamic_chiplet + self.logic_chiplet.get_area()
        return area

class Integration2_5D(Integration):
    
    def __init__(self,config,maxnum_layer_in_bit,num_used_static_chiplet_all_layers, used_num_dynamic_chiplet):

        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_static_chiplet = num_used_static_chiplet_all_layers
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_dynamic_chiplet = used_num_dynamic_chiplet
        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit=maxnum_layer_in_bit)

    def CalculateArea(self):

        area = self.static_chiplet.get_area() * self.num_static_chiplet + self.dynamic_chiplet.get_area() * self.num_dynamic_chiplet + self.logic_chiplet.get_area()
        # area *= (1+0.3) # only for 2.5D, need change to addition of NoP area
        return area

class Integration3D(Integration):

    def __init__(self,config,maxnum_layer_in_bit):

        self.tsv = TSVPath()
        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit = maxnum_layer_in_bit)
        self.num_static_chiplet = config.num_static_chiplet
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit = maxnum_layer_in_bit)
        self.num_dynamic_chiplet = config.num_dynamic_chiplet
        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit = maxnum_layer_in_bit)
    
    def CalculateArea(self):

        # new: need add tsv,nop area, factor in stack layers
        self.area = max(self.static_chiplet.get_area(), self.dynamic_chiplet.get_area(), self.logic_chiplet.get_area())
        self.total_tsv_area = self.tsv.CalculateArea() * (self.logic_chiplet.buffer.mem_width + self.logic_chiplet.buffer.mem_height)
        self.area += self.total_tsv_area
        return self.area
