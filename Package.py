from math import ceil,sqrt
from abc import ABC, abstractmethod
from tsv_path import TSVPath

from config import Config
from chiplet import Chiplet

def get_PE_relative_dist_xy(PE_Loc,PE_idx1,PE_idx2):
    dist = abs(PE_Loc[0][PE_idx1] - PE_Loc[0][PE_idx2]) + abs(PE_Loc[1][PE_idx1] - PE_Loc[1][PE_idx2])
    return dist

def get_PE_relative_dist_z(PE_Loc,PE_idx1,PE_idx2):
    dist = abs(PE_Loc[2][PE_idx1] - PE_Loc[2][PE_idx2])
    return dist


class Pack(ABC):
    # Area
    @abstractmethod    
    def CalculateArea(self):
        pass

    # Latency
    @abstractmethod
    def CalculateLatency_StaticPE_Wire(self):
        pass

    @abstractmethod
    def CalculateLatency_DynamicPE_Wire(self):
        pass
    
    # DynamicPower
    @abstractmethod
    def CalculateDynamicPower_StaticPE_Wire(self):
        pass

    @abstractmethod
    def CalculateDynamicPower_DynamicPE_Wire(self):
        pass

    # LeakPower
    @abstractmethod
    def CalculateLeakPower_StaticPE_Wire(self):
        pass

    @abstractmethod
    def CalculateLeakPower_DynamicPE_Wire(self):
        pass


class Pack2D(Pack):
    def __init__(self,config,maxnum_layer_in_bit):
        # self.Area_StaticPE_Wire = 0
        # self.Area_DynamicPE_Wire = 0
        # self.Area_Total_Wire = 0

        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_static_chiplet = config.num_static_chiplet
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_dynamic_chiplet = config.num_dynamic_chiplet
        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit=maxnum_layer_in_bit)

    def CalculateArea(self):
        
        # staticChip_PErowNum = ceil(sqrt(Num_StaticPE))
        # staticChip_PEcolNum = ceil(Num_StaticPE / staticChip_PErowNum)
        # self.Area_StaticPE_Wire = StaticWire_unitLengthArea * (Static_PESize_height * staticChip_PErowNum + Static_PESize_width * staticChip_PEcolNum)
        # self.static_area = Num_StaticPE * Area_StaticPE + self.Area_StaticPE_Wire

        # dynamicChip_PErowNum = ceil(sqrt(Num_DynamicPE))
        # dynamicChip_PEcolNum = ceil(Num_DynamicPE / dynamicChip_PErowNum)
        # self.Area_DynamicPE_Wire = DynamicWire_unitLengthArea * (Dynamic_PESize_height * dynamicChip_PErowNum + Dynamic_PESize_width * dynamicChip_PEcolNum)
        # self.dynamic_area = Num_DynamicPE * Area_DynamicPE + self.Area_DynamicPE_Wire + Area_DynamicPE_sfu
        # self.area = self.static_area + self.dynamic_area + Area_logic + Area_buffer

        # self.Area_Total_Wire = self.Area_StaticPE_Wire + self.Area_DynamicPE_Wire
        # return self.area

        area = self.static_chiplet.get_area() * self.num_static_chiplet + self.dynamic_chiplet.get_area() * self.num_dynamic_chiplet + self.logic_chiplet.get_area()
        return area
    
    def getWireLength(self, layer_trace, Num_StaticPE, Num_DynamicPE):
        PE_Loc = [] 
        PE_rowLoc = []        
        PE_colLoc = []

        staticChip_PErowNum = ceil(sqrt(Num_StaticPE))
        staticChip_PEcolNum = ceil(Num_StaticPE / staticChip_PErowNum)
        for thisStaticPE in range(Num_StaticPE):
            thisStaticPE_rowLoc = int(thisStaticPE / staticChip_PEcolNum)
            thisStaticPE_colLoc = int(thisStaticPE % staticChip_PEcolNum)

            PE_rowLoc.append(thisStaticPE_rowLoc)
            PE_colLoc.append(thisStaticPE_colLoc)


        dynamicChip_PErowNum = ceil(sqrt(Num_DynamicPE))
        dynamicChip_PEcolNum = ceil(Num_DynamicPE / dynamicChip_PErowNum)
        for thisDynamicPE in range(Num_DynamicPE):
            thisDynamicPE_rowLoc = int(thisDynamicPE / dynamicChip_PEcolNum)
            thisDynamicPE_colLoc = int(thisDynamicPE % dynamicChip_PEcolNum) + staticChip_PEcolNum

            PE_rowLoc.append(thisDynamicPE_rowLoc)
            PE_colLoc.append(thisDynamicPE_colLoc)
        

        PE_Loc.append(PE_rowLoc)
        PE_Loc.append(PE_colLoc)


        # num_rows = len(PE_Loc)
        # num_columns = len(PE_Loc[0]) if PE_Loc else 0
        # print("Number of rows:", num_rows)
        # print("Number of columns:", num_columns)

        dist = 0
        for layer in enumerate(layer_trace):
            for row in layer[1]:
                # print("row value:", row, "type:", type(row))
                dist += get_PE_relative_dist_xy(PE_Loc,row[0],row[1])
        
        return dist

    # Latency
    def CalculateLatency_StaticPE_Wire(self, layer_trace, Num_StaticPE, Num_DynamicPE, StaticWire_unitLengthLatency):
        latency = StaticWire_unitLengthLatency  * self.getWireLength(layer_trace, Num_StaticPE, Num_DynamicPE)
        return latency

    def CalculateLatency_DynamicPE_Wire(self):
        return 0
    
    # DynamicPower
    def CalculateDynamicPower_StaticPE_Wire(self, layer_trace, Num_StaticPE, Num_DynamicPE,StaticWire_unitLengthDynPower):
        self.freq = 1e9
        self.vdd = 1
        self.delta = 0.15 # switching activity of adder, delta = 0.15 by default
        self.StaticWire_unitLengthDynPower = StaticWire_unitLengthDynPower
        self.dynamicPower = self.StaticWire_unitLengthDynPower * self.getWireLength(layer_trace, Num_StaticPE, Num_DynamicPE)
        return self.dynamicPower

    def CalculateDynamicPower_DynamicPE_Wire(self):
        return 0

    # LeakPower
    def CalculateLeakPower_StaticPE_Wire(self):
        return 0

    def CalculateLeakPower_DynamicPE_Wire(self):
        return 0

class Pack2_5D(Pack):
    
    def __init__(self,config,maxnum_layer_in_bit):
        # self.Area_Total_Wire = 0

        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_static_chiplet = config.num_static_chiplet
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit=maxnum_layer_in_bit)
        self.num_dynamic_chiplet = config.num_dynamic_chiplet
        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit=maxnum_layer_in_bit)

    def CalculateArea(self):
        # self.static_area = Num_StaticPE * Area_StaticPE
        # self.dynamic_area = Num_DynamicPE * Area_DynamicPE + Area_DynamicPE_sfu
        # self.area = self.static_area + self.dynamic_area + Area_logic + Area_buffer
        # return self.area

        area = self.static_chiplet.get_area() * self.num_static_chiplet + self.dynamic_chiplet.get_area() * self.num_dynamic_chiplet + self.logic_chiplet.get_area()
        area *= (1+0.3) # only for 2.5D, need change to addition of NoP area
        return area
    
    def getWireLength(self, layer_trace, Num_StaticPE, Num_DynamicPE):

        PE_Loc = [] 
        PE_rowLoc = []        
        PE_colLoc = []

        staticChip_PErowNum = ceil(sqrt(Num_StaticPE))
        staticChip_PEcolNum = ceil(Num_StaticPE / staticChip_PErowNum)
        for thisStaticPE in range(Num_StaticPE):
            thisStaticPE_rowLoc = int(thisStaticPE / staticChip_PEcolNum)
            thisStaticPE_colLoc = int(thisStaticPE % staticChip_PEcolNum)

            PE_rowLoc.append(thisStaticPE_rowLoc)
            PE_colLoc.append(thisStaticPE_colLoc)


        dynamicChip_PErowNum = ceil(sqrt(Num_DynamicPE))
        dynamicChip_PEcolNum = ceil(Num_DynamicPE / dynamicChip_PErowNum)
        for thisDynamicPE in range(Num_DynamicPE):
            thisDynamicPE_rowLoc = int(thisDynamicPE / dynamicChip_PEcolNum)
            thisDynamicPE_colLoc = int(thisDynamicPE % dynamicChip_PEcolNum) + staticChip_PEcolNum

            PE_rowLoc.append(thisDynamicPE_rowLoc)
            PE_colLoc.append(thisDynamicPE_colLoc)
        

        PE_Loc.append(PE_rowLoc)
        PE_Loc.append(PE_colLoc)

        dist = 0
        for layer in enumerate(layer_trace):
            for row in layer[1]:
                # print("row value:", row, "type:", type(row))
                dist += get_PE_relative_dist_xy(PE_Loc,row[0],row[1])
        
        return dist
    
    # Latency
    def CalculateLatency_StaticPE_Wire(self, layer_trace, Num_StaticPE, Num_DynamicPE, StaticWire_unitLengthLatency):
        latency = StaticWire_unitLengthLatency  * self.getWireLength(layer_trace, Num_StaticPE, Num_DynamicPE)
        return latency

    def CalculateLatency_DynamicPE_Wire(self):
        return 0
    
    # DynamicPower
    def CalculateDynamicPower_StaticPE_Wire(self, layer_trace, Num_StaticPE, Num_DynamicPE,StaticWire_unitLengthDynPower):
        self.freq = 1e9
        self.vdd = 1
        self.delta = 0.15 # switching activity of adder, delta = 0.15 by default
        self.StaticWire_unitLengthDynPower = StaticWire_unitLengthDynPower
        self.dynamicPower = self.StaticWire_unitLengthDynPower * self.getWireLength(layer_trace, Num_StaticPE, Num_DynamicPE)
        return self.dynamicPower

    def CalculateDynamicPower_DynamicPE_Wire(self):
        return 0

    # LeakPower
    def CalculateLeakPower_StaticPE_Wire(self):
        return 0

    def CalculateLeakPower_DynamicPE_Wire(self):
        return 0

class Pack3D(Pack):

    def __init__(self,config,Num_StaticPE,Num_DynamicPE,Num_StaticTier,Num_DynamicTier,
                 StaticWire_unitLengthArea, Static_PE_height, Static_PE_width,
                 DynamicWire_unitLengthArea, Dynamic_PE_height, Dynamic_PE_width,
                 maxnum_layer_in_bit
                 ):
        self.tsv = TSVPath()
        self.PE_Loc = []
        self.Num_StaticPE = Num_StaticPE
        self.Num_DynamicPE = Num_DynamicPE
        self.Num_StaticTier = Num_StaticTier
        self.Num_DynamicTier = Num_DynamicTier
        self.Area_Total_Wire = 0
        self.Area_StaticPE_Wire = 0
        self.Area_DynamicPE_Wire = 0
        self.StaticWire_unitLengthArea = StaticWire_unitLengthArea
        self.Static_PE_height = Static_PE_height
        self.Static_PE_width = Static_PE_width
        self.DynamicWire_unitLengthArea = DynamicWire_unitLengthArea
        self.Dynamic_PE_height = Dynamic_PE_height
        self.Dynamic_PE_width = Dynamic_PE_width

        self.staticChip_PErowNum = ceil(sqrt(ceil(self.Num_StaticPE / self.Num_StaticTier)))
        self.staticChip_PEcolNum = ceil(ceil(self.Num_StaticPE / self.Num_StaticTier) / self.staticChip_PErowNum)
        self.dynamicChip_PErowNum = ceil(sqrt(ceil(self.Num_DynamicPE / self.Num_DynamicTier)))
        
        print("self.Num_DynamicPE",self.Num_DynamicPE)
        print("self.dynamicChip_PErowNum:",self.dynamicChip_PErowNum)
        self.dynamicChip_PEcolNum = ceil(ceil(self.Num_DynamicPE / self.Num_DynamicTier) / self.dynamicChip_PErowNum)
        

        #new
        self.static_chiplet = Chiplet(config,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type,maxnum_layer_in_bit = maxnum_layer_in_bit)
        self.num_static_chiplet = config.num_static_chiplet
        self.dynamic_chiplet = Chiplet(config,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type,maxnum_layer_in_bit = maxnum_layer_in_bit)
        self.num_dynamic_chiplet = config.num_dynamic_chiplet
        self.logic_chiplet = Chiplet(config,chiplet_type='logic',memory_cell_type=None,maxnum_layer_in_bit = maxnum_layer_in_bit)
    
    def CalculateArea(self):

        # self.static_area = self.Num_StaticPE * Area_StaticPE + (Area_logic + Area_buffer)/2
        # self.dynamic_area = self.Num_DynamicPE * Area_DynamicPE + Area_DynamicPE_sfu + (Area_logic + Area_buffer)/2
        # Num_StaticTier_tsv = ceil(self.Num_StaticPE / self.Num_StaticTier)
        # Num_DynamicTier_tsv = ceil(self.Num_DynamicPE / self.Num_DynamicTier)
        # Area_tsv = self.tsv.CalculateArea()

        # self.Area_StaticPE_Wire = self.StaticWire_unitLengthArea * (self.Static_PE_height * self.staticChip_PErowNum + self.Static_PE_width * self.staticChip_PEcolNum)
        # self.Area_DynamicPE_Wire = self.DynamicWire_unitLengthArea * (self.Dynamic_PE_height * self.dynamicChip_PErowNum + self.Dynamic_PE_width * self.dynamicChip_PEcolNum)
        # # then...

        # self.static_tier_area = (self.static_area + Num_StaticTier_tsv * Area_tsv + self.Area_StaticPE_Wire ) / self.Num_StaticTier
        # self.dynamic_tier_area = (self.dynamic_area + Num_DynamicTier_tsv * Area_tsv + self.Area_DynamicPE_Wire) / self.Num_DynamicTier
        # self.area = max(self.static_tier_area, self.dynamic_tier_area) # H3D

        # self.Area_Total_tsv = max(Num_StaticTier_tsv * Area_tsv, Num_DynamicTier_tsv * Area_tsv)
        # self.Area_Total_Wire = max(self.Area_StaticPE_Wire,self.Area_DynamicPE_Wire)

        # return self.area

        # new: need add tsv,nop area, factor in stack layers
        self.area = max(self.static_chiplet.get_area(), self.dynamic_chiplet.get_area(), self.logic_chiplet.get_area())
        self.total_tsv_area = self.tsv.CalculateArea() * (self.logic_chiplet.buffer.mem_width + self.logic_chiplet.buffer.mem_height)
        self.area += self.total_tsv_area
        return self.area
    
    def getPELocation(self):
        
        PE_tierLoc = []
        PE_rowLoc = []        
        PE_colLoc = []
    
        
        staticChip_PENumPerTier = self.staticChip_PErowNum * self.staticChip_PEcolNum
        for thisStaticPE in range(self.Num_StaticPE):
            # on which tier
            # if (thisStaticPE % staticChip_PENumPerTier) == 0:
            #     thisStaticPE_tierLoc = int(thisStaticPE / staticChip_PENumPerTier) - 1
            #     thisStaticPE_idxInTier = staticChip_PENumPerTier
            # else:
            #     thisStaticPE_tierLoc = int(thisStaticPE / staticChip_PENumPerTier)
            #     thisStaticPE_idxInTier = int(thisStaticPE % staticChip_PENumPerTier)
            thisStaticPE_tierLoc = int(thisStaticPE / staticChip_PENumPerTier)
            thisStaticPE_idxInTier = int(thisStaticPE % staticChip_PENumPerTier)
            PE_tierLoc.append(thisStaticPE_tierLoc)

            # location inside tier
            thisStaticPE_rowLoc = int(thisStaticPE_idxInTier / self.staticChip_PEcolNum)
            thisStaticPE_colLoc = int(thisStaticPE % self.staticChip_PEcolNum)

            PE_rowLoc.append(thisStaticPE_rowLoc)
            PE_colLoc.append(thisStaticPE_colLoc)

        
        dynamicChip_PENumPerTier = self.dynamicChip_PErowNum * self.dynamicChip_PEcolNum
        for thisDynamicPE in range(self.Num_DynamicPE):
            # if (thisDynamicPE % dynamicChip_PENumPerTier) == 0:
            #     thisDynamicPE_tierLoc = int(thisDynamicPE / dynamicChip_PENumPerTier) - 1
            #     thisDynamicPE_idxInTier = dynamicChip_PENumPerTier
            # else:
            #     thisDynamicPE_tierLoc = int(thisDynamicPE / dynamicChip_PENumPerTier)
            #     thisDynamicPE_idxInTier = int(thisDynamicPE % dynamicChip_PENumPerTier)

            # on which tier
            thisDynamicPE_tierLoc = int(thisDynamicPE / dynamicChip_PENumPerTier)
            thisDynamicPE_idxInTier = int(thisDynamicPE % dynamicChip_PENumPerTier)

            PE_tierLoc.append(thisDynamicPE_tierLoc)

            # location inside tier
            thisDynamicPE_rowLoc = int(thisDynamicPE_idxInTier / self.dynamicChip_PEcolNum)
            thisDynamicPE_colLoc = int(thisDynamicPE % self.dynamicChip_PEcolNum)
            
            PE_rowLoc.append(thisDynamicPE_rowLoc)
            PE_colLoc.append(thisDynamicPE_colLoc)
        
        self.PE_Loc.append(PE_rowLoc)
        self.PE_Loc.append(PE_colLoc)
        self.PE_Loc.append(PE_tierLoc)

        return self.PE_Loc

    def getWireLength_xy(self,layer_trace):
        self.getPELocation()
        self.dist_xy = 0
        for layer in enumerate(layer_trace):
            for row in layer[1]:
                # print("row value:", row, "type:", type(row))
                self.dist_xy += get_PE_relative_dist_xy(self.PE_Loc,row[0],row[1])
        
        return self.dist_xy
    
    def getWireLength_z(self,layer_trace):
        self.getPELocation()
        self.dist_z = 0
        for layer in enumerate(layer_trace):
            for row in layer[1]:
                # print("row value:", row, "type:", type(row))
                self.dist_z += get_PE_relative_dist_z(self.PE_Loc,row[0],row[1])

        return self.dist_z

    # Latency
    def CalculateLatency_StaticPE_Wire(self,layer_trace, StaticWire_unitLengthLatency):
        self.latency_xy = StaticWire_unitLengthLatency  * self.getWireLength_xy(layer_trace)
        self.latency_z = self.tsv.CalculateLatency() * self.getWireLength_z(layer_trace)
        self.latency = self.latency_xy + self.latency_z
        return self.latency

    def CalculateLatency_DynamicPE_Wire(self):
        return 0
    
    # DynamicPower
    def CalculateDynamicPower_StaticPE_Wire(self,layer_trace,StaticWire_unitLengthDynPower):
        self.freq = 1e9
        self.vdd = 1
        self.delta = 0.15 # switching activity of adder, delta = 0.15 by default
        self.StaticWire_unitLengthDynPower = StaticWire_unitLengthDynPower
        self.dynamicPower_xy = self.StaticWire_unitLengthDynPower * self.getWireLength_xy(layer_trace)
        self.dynamicPower_z = self.tsv.CalculatePower() * self.getWireLength_z(layer_trace)
        self.dynamicPower = self.dynamicPower_xy + self.dynamicPower_z
        return self.dynamicPower

    def CalculateDynamicPower_DynamicPE_Wire(self):
        return 0

    # LeakPower
    def CalculateLeakPower_StaticPE_Wire(self):
        return 0

    def CalculateLeakPower_DynamicPE_Wire(self):
        return 0
