import math
from abc import ABC, abstractmethod
from tsv_path import TSVPath
from chiplet import Chiplet
import sys

class Integration(ABC):
    # Area
    @abstractmethod    
    def CalculateArea(self):
        pass

class Integration2D(Integration):
    def __init__(self,config,maxnum_layer_in_bit,num_used_static_chiplet,num_used_semi_static_chiplet,num_used_dynamic_chiplet):
        
        self.total_IO_cell_area_40nm = 62.65 * 1E-12 * 8
        self.static_chiplet_technode = config.static_chiplet_technode
        self.dynamic_chiplet_technode = config.dynamic_chiplet_technode

        self.static0_chiplet = Chiplet(config,chiplet_type='static_0',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        self.num_static_chiplet = num_used_static_chiplet

        self.static2_chiplet = Chiplet(config,chiplet_type='static_2',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)

        self.num_semi_static_chiplet = num_used_semi_static_chiplet

        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_dynamic_chiplet = num_used_dynamic_chiplet

        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit=maxnum_layer_in_bit)

    def CalculateArea(self):

        print("static0_chiplet area", self.static0_chiplet.get_area() * 1E6, "mm2")
        print("static2_chiplet area", self.static2_chiplet.get_area() * 1E6, "mm2")
        print("dynamic_chiplet area", self.dynamic_chiplet.get_area() * 1E6, "mm2")
        print("logic_chiplet area", self.logic_chiplet.get_area() * 1E6, "mm2")

        # reticle limit
        if self.static0_chiplet.get_area() > 858E-06 or self.static2_chiplet.get_area() > 858E-06 or self.dynamic_chiplet.get_area() > 858E-06:
            print("Exit from Integration function: There exist a chip larger than reticle limit")
            # sys.exit()

        area = (self.static0_chiplet.get_area() + self.total_IO_cell_area_40nm * (math.pow(self.static_chiplet_technode, 2)/math.pow(40,2))) * self.num_static_chiplet + (self.static2_chiplet.get_area() + self.total_IO_cell_area_40nm * (math.pow(self.static_chiplet_technode, 2)/math.pow(40,2))) * self.num_semi_static_chiplet + (self.dynamic_chiplet.get_area() + self.total_IO_cell_area_40nm * (math.pow(self.dynamic_chiplet_technode, 2)/math.pow(40,2))) * self.num_dynamic_chiplet 
        
        # area +=  self.logic_chiplet.get_area()
        # area *= 1.1
        
        # add die-to-die spacing (assume trace len.: 300~500um)
        spacing_len = 300e-6
        num_die = self.num_static_chiplet + self.num_dynamic_chiplet
        num_die_spacing = math.ceil(math.sqrt(num_die)) - 1
        area += (num_die_spacing * spacing_len) * math.sqrt(area) * 2
        
        return area

class Integration2_5D(Integration):
    
    def __init__(self,config,maxnum_layer_in_bit,num_used_static_chiplet,num_used_semi_static_chiplet, num_used_dynamic_chiplet):

        self.static0_chiplet = Chiplet(config,chiplet_type='static_0',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        self.num_static_chiplet = num_used_static_chiplet

        self.static2_chiplet = Chiplet(config,chiplet_type='static_2',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        self.num_semi_static_chiplet = num_used_semi_static_chiplet
        
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_dynamic_chiplet = num_used_dynamic_chiplet
        
        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        self.min_memory_chip_area = min(self.static0_chiplet.get_area(),self.static2_chiplet.get_area(),self.dynamic_chiplet.get_area())
        self.total_tsv_area = self.logic_chiplet.buffer.get_area()

    def CalculateArea(self):

        print("static0_chiplet area", self.static0_chiplet.get_area() * 1E6, "mm2")
        print("static0_chiplet buffer size", self.static0_chiplet.buffer_size)
        print("static0_chiplet buffer area", self.static0_chiplet.buffer.get_area() * 1E6, "mm2")
        print("static2_chiplet area", self.static2_chiplet.get_area() * 1E6, "mm2")
        print("static2_chiplet buffer area", self.static2_chiplet.buffer.get_area() * 1E6, "mm2")
        print("dynamic_chiplet area", self.dynamic_chiplet.get_area() * 1E6, "mm2")
        print("logic_chiplet area", self.logic_chiplet.get_area() * 1E6, "mm2")

        # reticle limit
        if self.static0_chiplet.get_area() > 858E-06 or self.static2_chiplet.get_area() > 858E-06 or self.dynamic_chiplet.get_area() > 858E-06:
            print("Exit from Integration function: There exist a chip larger than reticle limit")
            # sys.exit()

        area = self.static0_chiplet.get_area() * self.num_static_chiplet + self.static2_chiplet.get_area() * self.num_semi_static_chiplet + self.dynamic_chiplet.get_area() * self.num_dynamic_chiplet 
        # area += self.logic_chiplet.get_area()
        
        # add die-to-die spacing (assume trace len.: 300~500um)
        spacing_len = 300e-6
        num_die = self.num_static_chiplet + self.num_dynamic_chiplet
        num_die_spacing = math.ceil(math.sqrt(num_die)) - 1
        area += (num_die_spacing * spacing_len) * math.sqrt(area) * 2
        
        return area

class Integration3D(Integration):

    def __init__(self,config,maxnum_layer_in_bit):

        self.tsv = TSVPath()
        self.static0_chiplet = Chiplet(config,chiplet_type='static_0',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)

        self.static2_chiplet = Chiplet(config,chiplet_type='static_2',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        
        
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit = maxnum_layer_in_bit)

        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit = maxnum_layer_in_bit)
        
        self.pitch_size_3d = config.pitch_size_3d # not used
        self.num_tsv = self.logic_chiplet.buffer_mem_width
    
    def CalculateArea(self):
        print("static0_chiplet area", self.static0_chiplet.get_area() * 1E6, "mm2")
        
        print("static2_chiplet area", self.static2_chiplet.get_area() * 1E6, "mm2")
        print("static2_chiplet buffer area", self.static2_chiplet.buffer.get_area() * 1E6, "mm2")
        print("dynamic_chiplet area", self.dynamic_chiplet.get_area() * 1E6, "mm2")
        print("logic_chiplet area", self.logic_chiplet.get_area() * 1E6, "mm2")

        # reticle limit
        if self.static0_chiplet.get_area() > 858E-06 or self.static2_chiplet.get_area() > 858E-06 or self.dynamic_chiplet.get_area() > 858E-06:
            print("Exit from Integration function: There exist a chip larger than reticle limit")
            # sys.exit()

        # self.area = max(self.static0_chiplet.get_area(), self.static2_chiplet.get_area(), self.dynamic_chiplet.get_area(), self.logic_chiplet.get_area())
        
        self.area = max(self.static0_chiplet.get_area(), self.static2_chiplet.get_area(), self.dynamic_chiplet.get_area())
        
        self.total_tsv_area = self.tsv.CalculateArea() * self.num_tsv
        self.area += self.total_tsv_area
        return self.area
