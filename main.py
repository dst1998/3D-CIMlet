from math import ceil
import numpy as np
import re

from config import Config
from model import GetData
from Package import Pack2D, Pack2_5D, Pack3D
from tsv_path import TSVPath
from layer_trace import generate_trace_noc
from wire import Wire
from chiplet_layer_range import get_static_chiplet_layer_range,get_static_chiplet_layers,get_dest_layers
from layer_mapping import get_layer_energy_latency
from Interconnect.noc_estimation import interconnect_estimation
from Interconnect.nop_estimation import nop_interconnect_estimation
from Interconnect.NoP_hardware import NoP_hardware_estimation
# from NoP_hardware import *

def main(config):
    # load in model and hw confic info
    model_filename = config.model_filename
    # hw_config_filename = 'hw_config.txt'
    # data_loader = GetData(model_filename)
    # NetStructure = data_loader.load_model()
    # hw_configs = data_loader.load_hardware_config()
    NetStructure = config.load_model()

    BitWidth_in = config.BitWidth_in
    BitWidth_weight = config.BitWidth_weight

    eDRAM_tech = config.eDRAM_tech
    eDRAM_cellSize_height = config.eDRAM_cellSize_height
    eDRAM_cellSize_width = config.eDRAM_cellSize_width
    eDRAM_SubArray_height = config.eDRAM_SubArray_height
    eDRAM_SubArray_width = config.eDRAM_SubArray_width
    eDRAM_SubArray_latency = config.eDRAM_SubArray_latency
    eDRAM_SubArray_power = config.eDRAM_SubArray_power
    eDRAM_SubArray_area = config.eDRAM_SubArray_area
    eDRAM_PE_latency = config.eDRAM_PE_latency
    eDRAM_PE_dynamicEnergy = config.eDRAM_PE_dynamicEnergy
    eDRAM_PE_leakPower = config.eDRAM_PE_leakPower
    eDRAM_cell_area = eDRAM_cellSize_height * eDRAM_cellSize_width
    eDRAM_SubArraySize_height = eDRAM_cellSize_height * eDRAM_SubArray_height
    eDRAM_SubArraySize_width = eDRAM_cellSize_width * eDRAM_SubArray_width

    RRAM_tech = config.RRAM_tech
    RRAM_cellSize_height = config.RRAM_cellSize_height
    RRAM_cellSize_width = config.RRAM_cellSize_width
    RRAM_SubArray_height = config.RRAM_SubArray_height
    RRAM_SubArray_width = config.RRAM_SubArray_width
    RRAM_SubArray_latency = config.RRAM_SubArray_latency
    RRAM_SubArray_power = config.RRAM_SubArray_power
    RRAM_SubArray_area = config.RRAM_SubArray_area
    RRAM_PE_latency = config.RRAM_PE_latency
    RRAM_PE_dynamicEnergy = config.RRAM_PE_dynamicEnergy
    RRAM_PE_leakPower = config.RRAM_PE_leakPower
    RRAM_cell_area = RRAM_cellSize_height * RRAM_cellSize_width
    RRAM_SubArraySize_height = RRAM_cellSize_height * RRAM_SubArray_height
    RRAM_SubArraySize_width = RRAM_cellSize_width * RRAM_SubArray_width

    Static_SubArray_height = config.static_subarray_height
    Static_SubArray_width = config.static_subarray_width
    Dynamic_SubArray_height = config.dynamic_subarray_height
    Dynamic_SubArray_width = config.dynamic_subarray_width


    static_chiplet_size = config.static_chiplet_height * config.static_chiplet_width
    dynamic_chiplet_size = config.dynamic_chiplet_height * config.dynamic_chiplet_width
    
    
    # define memorycell type of static layer and dynamic layer
    Static_MemoryCellType = config.Static_MemoryCellType
    if Static_MemoryCellType == 'RRAM':
        Static_SubArraySize_height = RRAM_SubArraySize_height
        Static_SubArraySize_width = RRAM_SubArraySize_width
        # Static_SubArray_latency = RRAM_SubArray_latency
        # Static_SubArray_power = RRAM_SubArray_power
        # Static_SubArray_area = RRAM_SubArray_area
        Latency_StaticPE = RRAM_PE_latency
        DynamicEnergy_StaticPE = RRAM_PE_dynamicEnergy
        LeakPower_StaticPE = RRAM_PE_leakPower
        Area_StaticCell = RRAM_cell_area
    if Static_MemoryCellType == 'eDRAM':
        Static_SubArraySize_height = eDRAM_SubArraySize_height
        Static_SubArraySize_width = eDRAM_SubArraySize_width
        # Static_SubArray_latency = eDRAM_SubArray_latency
        # Static_SubArray_power = eDRAM_SubArray_power
        # Static_SubArray_area = eDRAM_SubArray_area
        Latency_StaticPE = eDRAM_PE_latency
        DynamicEnergy_StaticPE = eDRAM_PE_dynamicEnergy
        LeakPower_StaticPE = eDRAM_PE_leakPower
        Area_StaticCell = eDRAM_cell_area
    Num_StaticSubArrayPerPERow = config.static_pe_width # num of subarray cols in a pe
    Num_StaticSubArrayPerPECol = config.static_pe_height # num of subarray rows in a pe
    Static_PE_height = Static_SubArray_height * Num_StaticSubArrayPerPECol
    Static_PE_width = Static_SubArray_width * Num_StaticSubArrayPerPERow
    Num_StaticSubArrayPerPE = Num_StaticSubArrayPerPERow * Num_StaticSubArrayPerPECol
    Static_PESize_height = Static_SubArraySize_height * Num_StaticSubArrayPerPERow
    Static_PESize_width = Static_SubArraySize_width * Num_StaticSubArrayPerPECol
    Area_StaticPE = Area_StaticCell * Static_PE_height * Static_PE_width
    

    
    Dynamic_MemoryCellType = config.Dynamic_MemoryCellType
    if Dynamic_MemoryCellType == 'RRAM':
        Dynamic_SubArraySize_height = RRAM_SubArraySize_height
        Dynamic_SubArraySize_width = RRAM_SubArraySize_width
        # Dynamic_SubArray_latency = RRAM_SubArray_latency
        # Dynamic_SubArray_power = RRAM_SubArray_power
        # Dynamic_SubArray_area = RRAM_SubArray_area
        Latency_DynamicPE = RRAM_PE_latency
        DynamicEnergy_DynamicPE = RRAM_PE_dynamicEnergy
        LeakPower_DynamicPE = RRAM_PE_leakPower
        Area_DynamicCell = RRAM_cell_area
    if Dynamic_MemoryCellType == 'eDRAM':
        Dynamic_SubArraySize_height = eDRAM_SubArraySize_height
        Dynamic_SubArraySize_width = eDRAM_SubArraySize_width
        # Dynamic_SubArray_latency = eDRAM_SubArray_latency
        # Dynamic_SubArray_power = eDRAM_SubArray_power
        # Dynamic_SubArray_area = eDRAM_SubArray_area
        Latency_DynamicPE = eDRAM_PE_latency
        DynamicEnergy_DynamicPE = eDRAM_PE_dynamicEnergy
        LeakPower_DynamicPE = eDRAM_PE_leakPower
        Area_DynamicCell = eDRAM_cell_area
    Num_DynamicSubArrayPerPERow = config.dynamic_pe_width # num of subarray cols in a pe
    Num_DynamicSubArrayPerPECol = config.dynamic_pe_height # num of subarray rows in a pe
    Dynamic_PE_height = Dynamic_SubArray_height * Num_DynamicSubArrayPerPERow 
    Dynamic_PE_width = Dynamic_SubArray_width * Num_DynamicSubArrayPerPECol
    Num_DynamicSubArrayPerPE = Num_DynamicSubArrayPerPERow * Num_DynamicSubArrayPerPECol
    Dynamic_PESize_height = Dynamic_SubArraySize_height * Num_DynamicSubArrayPerPERow
    Dynamic_PESize_width = Dynamic_SubArraySize_width * Num_DynamicSubArrayPerPECol
    Area_DynamicPE = Area_DynamicCell * Dynamic_PE_height * Dynamic_PE_width
    
    # get static/dynamic layer dataflow
    # initialize PPA
    Total_DynamicPower = 0
    Total_LeakPower = 0
    Total_Latency = 0
    Total_Area = 0

    LeakPower_staticLayers = 0
    LeakPower_dynamicLayers = 0
    # Latency_staticLayers = 0
    # Latency_dynamicLayers = 0
    Total_tops = 0

    Num_StaticSubArray = 0
    Num_DynamicSubArray = 0
    Num_StaticSubArray_eachLayer = []
    Num_DynamicSubArray_eachLayer = []
    Num_StaticPE = 0
    Num_DynamicPE = 0
    Num_StaticPE_eachLayer = []
    Num_DynamicPE_eachLayer = []
    performance_each_layer = []

    for row in NetStructure:
        # get TOPS of this layer
        tops_thisLayer = row[0]*row[1]*row[3] *2 *1e-12
        Total_tops += tops_thisLayer

    # breakdown value #####################
    Area_logic = 1.5e-4 
    Area_buffer = 3e-4

    technode_static = 45
    technode_dynamic = 45
    StaticWire = Wire(technode_static)
    StaticWire.get_wire_properties()
    StaticWire_unitLengthLatency = StaticWire.get_wire_unitLengthLatency()
    StaticWire_unitLengthArea = StaticWire.get_wire_unitLengthArea()
    StaticWire_unitLengthDynPower = StaticWire.get_wire_unitLengthDynPower()

    DynamicWire = Wire(technode_dynamic)
    DynamicWire.get_wire_properties()
    DynamicWire_unitLengthLatency = DynamicWire.get_wire_unitLengthLatency()
    DynamicWire_unitLengthArea = DynamicWire.get_wire_unitLengthArea()
    DynamicWire_unitLengthDynPower = DynamicWire.get_wire_unitLengthDynPower()
    # print(W.get_wire_unitLengthLatency())
    # print(W.get_wire_unitLengthArea())


    # Area_StaticPE_Wire =  StaticWire_unitLengthArea  * wireLength # calculate in Pack2D class
    # Area_DynamicPE_Wire = DynamicWire_unitLengthArea * wireLength # calculate in Pack2D class

    Area_DynamicPE_sfu = 3e-7
    DynamicPower_sfu = 8e-3 /512 # for 512 input
    Latency_sfu = 7e-7 /512 # for 512 input

    LeakPower_StaticPE_logic = 0
    LeakPower_StaticPE_buffer = 0
    LeakPower_DynamicPE_logic = 0
    LeakPower_DynamicPE_sfu = 0 
    LeakPower_DynamicPE_buffer = 0

    buffer_bw = 9e9 # SRAM-2D:9Gb/s=1.125GB/s
    buffer_dynamicEnergy = 17.5e-15 * 40/65  # [depends on tech] unit:J/read or J/write, SRAM-2D-65nm:17.5fJ/bit=140fJ/byte
    # DynamicPower_weightLoadin = 0 # calculate later
    # Latency_weightLoadin = 0 # calculate later

    # DynamicPower_buffer2sfu = 0 # calculate later
    # Latency_buffer2sfu = 0 # calculate later

    DynamicPower_logic = 4.67e-3/7.6e7*Total_tops
    DynamicPower_buffer = 1.04e-3/7.6e7*Total_tops
    Latency_logic = 1.5e-2/7.6e7*Total_tops
    Latency_buffer = 2.88e-3/7.6e7*Total_tops
    

    Num_StaticTier = 4 # change from user
    Num_DynamicTier = 4 # change from user
    ##########################################
    
    num_static_chiplet_eachLayer = []
    num_dynamic_chiplet_eachLayer = []
    # get num of used static subarray/PE or used dynamic subarray/PE of each model layer
    # get dynamic power and latency
    for layer_index, row in enumerate(NetStructure):
        # get this layer operation is static or dynamic
        if row[6]==0: # is static layer
            # test
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer = get_layer_energy_latency(row,config,config.static_chiplet_technode,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(num_used_chiplet_this_layer)
            num_dynamic_chiplet_eachLayer.append(0)

            Num_StaticPE_eachLayer.append(num_used_pe_this_layer)
            Num_DynamicPE_eachLayer.append(0)

            Num_StaticSubArray_eachLayer.append(num_used_subarray_this_layer)
            Num_DynamicSubArray_eachLayer.append(0)
            # test end
        
        else: # dynamic layer
            # test
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer = get_layer_energy_latency(row,config,config.dynamic_chiplet_technode,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(0)
            num_dynamic_chiplet_eachLayer.append(num_used_chiplet_this_layer)

            Num_StaticPE_eachLayer.append(0)
            Num_DynamicPE_eachLayer.append(num_used_pe_this_layer)

            Num_StaticSubArray_eachLayer.append(0)
            Num_DynamicSubArray_eachLayer.append(num_used_subarray_this_layer)
            # test end
        Num_StaticPE = sum(Num_StaticPE_eachLayer)
        Num_DynamicPE = sum(Num_DynamicPE_eachLayer)
        used_num_dynamic_chiplet = max(num_dynamic_chiplet_eachLayer)
        num_chiplet_eachLayer = [a + b for a, b in zip(num_static_chiplet_eachLayer, num_dynamic_chiplet_eachLayer)]

        # TODO: add [weight] [write latency and energy], global buffer to each chiplet (chiplet-to-chiplet).
        # TODO: for first layer, add the [input] [write latency and energy] , global buffer to first chiplet (chiplet-to-chiplet).
        # TODO: for last layer, add the [output] [write latency and energy] , last chiplet to global buffer(chiplet-to-chiplet).
        # TODO: add [weight] in static chip [refresh latency and energy] based on below (all-layer latency) and noc,nop latency:
        performance_each_layer.append(performance_this_layer)






    # get location in chiplet for each model static layer (layer?: pe?~pe? in chiplet?)
    # static_chiplet_layer_range, static_chiplet_availability, num_used_static_chiplet_all_layers,layer_location_begin_chiplet = get_static_chiplet_layer_range(config,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer)
    
    dest_layers = get_dest_layers(config,NetStructure)
    
    static_chiplet_layers, static_chiplet_availability, num_used_static_chiplet_all_layers,layer_location_begin_chiplet = get_static_chiplet_layers(config,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer)

    


    # print("Num StaticPE EachLayer:",Num_StaticPE_eachLayer)
    # print("Num DynamicPE EachLayer:",Num_DynamicPE_eachLayer)
    # print("Num_StaticPE:", Num_StaticPE)
    # print("Num_DynamicPE:", Num_DynamicPE)

    # get Num of input Activation each Layer
    Num_In_eachLayer = []
    Num_Weight_eachLayer = []
    Num_Output_eachLayer = []
    for row in NetStructure:
        Num_In_eachLayer.append(row[0]*row[1] *row[8])
        Num_Weight_eachLayer.append(row[2]*row[3] *row[8])
        Num_Output_eachLayer.append(row[4]*row[5] *row[8]) #row[8] is num_head
    
    # get global buffer size
    maxnum_layer_in_bit = max(Num_In_eachLayer) * config.BitWidth_in
    
    # # get trace inside/inter layers
    # Bus_width = 32
    # layer_trace = generate_trace_noc(config, Num_StaticPE_eachLayer, Num_DynamicPE_eachLayer, Num_Output_eachLayer, Num_Weight_eachLayer,
    #                     BitWidth_in, BitWidth_weight, config.pe_bus_width_2D)
    
    num_used_chiplets = num_used_static_chiplet_all_layers + used_num_dynamic_chiplet

    # NoC Estimation
    noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
    
    # NoP Estimation
    nop_area, nop_latency, nop_energy = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size)
    
    # NoP Hardware Cost (Nop_area:um2, NoP_energy:pJ)
    # NoP Parameters - Extracted from GRS Nvidia 
    ebit = 43.2 # pJ 
    # (0.58pJ/b in GRS Nvidia 28nm [CICC'18: Ground-Referenced Signaling for Intra-Chip and Short-Reach Chip-to-Chip Interconnects])
    # (1.2pJ/b in ISSCC'17: A 14nm 1GHz FPGA with 2.5 D Transceiver Integration)
    area_per_lane = 5304.5 #um2
    clocking_area = 10609 #um2
    n_lane = 32
    n_bits_per_chiplet = 4.19E+06 #Automate this in next version
    Nop_area, NoP_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_per_chiplet)

    # get Num of input Activation each Layer
    Latency_eachLayer = []
    DynamicEnergy_eachLayer = []
    LeakEnergy_eachLayer = []
    AvgPower_eachLayer = []

    
    if config.Packaging_dimension == 2:
        # Pack = Pack2D()
        Pack = Pack2D(config,maxnum_layer_in_bit)

        # get chip area
        Total_Area = Pack.CalculateArea()
        
        # get leak power (need change!)
        LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + Pack.CalculateLeakPower_StaticPE_Wire() + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + Pack.CalculateLeakPower_DynamicPE_Wire() + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_sfu + LeakPower_DynamicPE_buffer
        Total_LeakPower = LeakPower_staticLayers + LeakPower_dynamicLayers


        # get dynamic power and latency
        for row in NetStructure:

            # get this layer operation is static or dynamic
            if row[6]==0: # is static layer
                # get num of PE used of static layer
                Num_StaticSubArray_thisLayer = ceil(row[2]/Static_SubArray_height) * ceil(row[3]*BitWidth_weight/Static_SubArray_width) # weightRowNum * weightColNum
                Num_StaticPE_thisLayer = ceil(Num_StaticSubArray_thisLayer / Num_StaticSubArrayPerPE)

                DynamicEnergy_thisLayer = Num_StaticPE_thisLayer * DynamicEnergy_StaticPE *row[0] * row[1]
                Latency_compute = Latency_StaticPE * ceil(row[1]/Static_PE_height) * ceil(row[0]/Static_PE_height)
                Latency_thisLayer = Latency_compute

            else: # is dynamic layer
                # get num of PE used of dynamic layer
                Num_DynamicSubArray_thisLayer = ceil(row[2]/Dynamic_SubArray_height) * ceil(row[3]*BitWidth_weight/Dynamic_SubArray_width) # weightRowNum * weightColNum
                Num_DynamicPE_thisLayer = ceil(Num_DynamicSubArray_thisLayer / Num_DynamicSubArrayPerPE)

                DynamicEnergy_weightLoadin = buffer_dynamicEnergy * row[2]*row[3]*BitWidth_weight
                DynamicEnergy_thisLayer = (DynamicEnergy_weightLoadin)+ Num_DynamicPE_thisLayer * DynamicEnergy_DynamicPE

                Latency_weightLoadin = row[2]*row[3]*BitWidth_weight / buffer_bw
                Latency_compute = Latency_DynamicPE * ceil(row[1]/Dynamic_PE_height) * ceil(row[0]/Dynamic_PE_height)
                Latency_thisLayer = (Latency_weightLoadin) + Latency_compute

                if row[7]: # have softmax operation, need sfu
                    DynamicPower_buffer2sfu = DynamicPower_buffer *(row[4]*row[5]*BitWidth_in) 
                    DynamicPower_buffer2sfu_thisLayer = 2* DynamicPower_buffer2sfu
                    DynamicPower_sfu_thisLayer = DynamicPower_sfu *(row[4]*row[5])

                    Latency_buffer2sfu = Latency_buffer *(row[4]*row[5]*BitWidth_in)
                    Latency_sfu_thisLayer = Latency_sfu *(row[4]*row[5])
                    Latency_buffer2sfu_thisLayer = 2* Latency_buffer2sfu
                    Latency_thisLayer += Latency_buffer2sfu_thisLayer
                    Latency_thisLayer += Latency_sfu_thisLayer

                    DynamicEnergy_thisLayer += DynamicPower_buffer2sfu_thisLayer * Latency_buffer2sfu_thisLayer + DynamicPower_sfu_thisLayer * Latency_sfu_thisLayer

            DynamicEnergy_eachLayer.append(DynamicEnergy_thisLayer)
            Latency_eachLayer.append(Latency_thisLayer)
                
        ##
                
        # Wire_DynamicPower = Pack.CalculateDynamicPower_StaticPE_Wire(layer_trace, Num_StaticPE, Num_DynamicPE,StaticWire_unitLengthDynPower)
        # Wire_Latency = Pack.CalculateLatency_StaticPE_Wire(layer_trace, Num_StaticPE, Num_DynamicPE, StaticWire_unitLengthLatency)
        # Wire_DynamicEnergy = Wire_DynamicPower*Wire_Latency

        # Total_DynamicEnergy = sum(Latency_eachLayer) 
        # # Total_DynamicEnergy += Wire_DynamicEnergy
        # Total_Latency = sum(Latency_eachLayer) 
        # # Total_Latency += Wire_Latency
        ##

        
    
    elif config.Packaging_dimension == 2.5:

        # Pack = Pack2_5D()
        Pack = Pack2_5D(config,maxnum_layer_in_bit)

        # get chip area
        Total_Area = Pack.CalculateArea()
        
        # get leak power
        LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + Pack.CalculateLeakPower_StaticPE_Wire() + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + Pack.CalculateLeakPower_DynamicPE_Wire() + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_sfu + LeakPower_DynamicPE_buffer
        Total_LeakPower = LeakPower_staticLayers + LeakPower_dynamicLayers
        
        # get dynamic power and latency
        for row in NetStructure:

            # get this layer operation is static or dynamic
            if row[6]==0: # is static layer
                # get num of PE used of static layer
                Num_StaticSubArray_thisLayer = ceil(row[2]/Static_SubArray_height) * ceil(row[3]*BitWidth_weight/Static_SubArray_width) # weightRowNum * weightColNum
                Num_StaticPE_thisLayer = ceil(Num_StaticSubArray_thisLayer / Num_StaticSubArrayPerPE)

                
                DynamicEnergy_thisLayer = Num_StaticPE_thisLayer * DynamicEnergy_StaticPE *row[0] * row[1]
                Latency_compute = Latency_StaticPE * ceil(row[1]/Static_PE_height) * ceil(row[0]/Static_PE_height)
                Latency_thisLayer = Latency_compute

            else: # is dynamic layer
                # get num of PE used of dynamic layer
                Num_DynamicSubArray_thisLayer = ceil(row[2]/Dynamic_SubArray_height) * ceil(row[3]*BitWidth_weight/Dynamic_SubArray_width) # weightRowNum * weightColNum
                Num_DynamicPE_thisLayer = ceil(Num_DynamicSubArray_thisLayer / Num_DynamicSubArrayPerPE)

                DynamicEnergy_weightLoadin = buffer_dynamicEnergy * row[2]*row[3]*BitWidth_weight
                DynamicEnergy_thisLayer = (DynamicEnergy_weightLoadin)+ Num_DynamicPE_thisLayer * DynamicEnergy_DynamicPE

                Latency_weightLoadin = row[2]*row[3]*BitWidth_weight / buffer_bw
                Latency_compute = Latency_DynamicPE * ceil(row[1]/Dynamic_PE_height) * ceil(row[0]/Dynamic_PE_height)
                Latency_thisLayer = (Latency_weightLoadin) + Latency_compute

                if row[7]: # have softmax operation, need sfu
                    DynamicPower_buffer2sfu = DynamicPower_buffer *(row[4]*row[5]*BitWidth_in) 
                    DynamicPower_buffer2sfu_thisLayer = 2* DynamicPower_buffer2sfu
                    DynamicPower_sfu_thisLayer = DynamicPower_sfu *(row[4]*row[5])

                    Latency_buffer2sfu = Latency_buffer *(row[4]*row[5]*BitWidth_in)
                    Latency_sfu_thisLayer = Latency_sfu *(row[4]*row[5])
                    Latency_buffer2sfu_thisLayer = 2* Latency_buffer2sfu
                    Latency_thisLayer += Latency_buffer2sfu_thisLayer
                    Latency_thisLayer += Latency_sfu_thisLayer

                    DynamicEnergy_thisLayer += DynamicPower_buffer2sfu_thisLayer * Latency_buffer2sfu_thisLayer + DynamicPower_sfu_thisLayer * Latency_sfu_thisLayer

            DynamicEnergy_eachLayer.append(DynamicEnergy_thisLayer)
            Latency_eachLayer.append(Latency_thisLayer)
        ##
        # way 1:
        # Wire_DynamicPower = Pack.CalculateDynamicPower_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE,StaticWire_unitLengthDynPower)
        # Wire_Latency = Pack.CalculateLatency_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE, StaticWire_unitLengthLatency)

        # way 2:
        # interposer I/O energy: 7.5 pJ/bit
        # interposer I/O bandwidth: 8Gbps (A pair of 8 Gbps 2.5D silicon interposer I/O is designed for each of 12 inter-die communication channels)
        Wire_DynamicEnergy = sum(Num_Output_eachLayer) * BitWidth_in * 7.5e-12
        Wire_Latency = sum(Num_Output_eachLayer) * BitWidth_in / 8e9
        Wire_DynamicPower = Wire_DynamicEnergy/Wire_Latency #avg power

        Total_DynamicEnergy = sum(Latency_eachLayer) + Wire_DynamicEnergy
        Total_Latency = sum(Latency_eachLayer) + Wire_Latency
        ##

    else: # H3D
        Pack = Pack3D(config,Num_StaticPE,Num_DynamicPE,Num_StaticTier,Num_DynamicTier,
                    StaticWire_unitLengthArea, Static_PE_height, Static_PE_width,
                    DynamicWire_unitLengthArea, Dynamic_PE_height, Dynamic_PE_width,
                    maxnum_layer_in_bit)
        #get chip area
        Total_Area = Pack.CalculateArea()

        # get leak power
        LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + Pack.CalculateLeakPower_StaticPE_Wire() + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + Pack.CalculateLeakPower_DynamicPE_Wire() + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_sfu + LeakPower_DynamicPE_buffer
        Total_LeakPower = LeakPower_staticLayers + LeakPower_dynamicLayers
        
        # get dynamic power and latency
        for row in NetStructure:

            # get this layer operation is static or dynamic
            if row[6]==0: # is static layer
                # get num of PE used of static layer
                Num_StaticSubArray_thisLayer = ceil(row[2]/Static_SubArray_height) * ceil(row[3]*BitWidth_weight/Static_SubArray_width) # weightRowNum * weightColNum
                Num_StaticPE_thisLayer = ceil(Num_StaticSubArray_thisLayer / Num_StaticSubArrayPerPE)

                
                DynamicEnergy_thisLayer = Num_StaticPE_thisLayer * DynamicEnergy_StaticPE *row[0] * row[1]
                Latency_compute = Latency_StaticPE * ceil(row[1]/Static_PE_height) * ceil(row[0]/Static_PE_height)
                Latency_thisLayer = Latency_compute

            else: # is dynamic layer
                # get num of PE used of dynamic layer
                Num_DynamicSubArray_thisLayer = ceil(row[2]/Dynamic_SubArray_height) * ceil(row[3]*BitWidth_weight/Dynamic_SubArray_width) # weightRowNum * weightColNum
                Num_DynamicPE_thisLayer = ceil(Num_DynamicSubArray_thisLayer / Num_DynamicSubArrayPerPE)

                DynamicEnergy_weightLoadin = buffer_dynamicEnergy * row[2]*row[3]*BitWidth_weight
                DynamicEnergy_thisLayer = (DynamicEnergy_weightLoadin)+ Num_DynamicPE_thisLayer * DynamicEnergy_DynamicPE

                Latency_weightLoadin = row[2]*row[3]*BitWidth_weight / buffer_bw
                Latency_compute = Latency_DynamicPE * ceil(row[1]/Dynamic_PE_height) * ceil(row[0]/Dynamic_PE_height)
                Latency_thisLayer = (Latency_weightLoadin) + Latency_compute

                if row[7]: # have softmax operation, need sfu
                    DynamicPower_buffer2sfu = DynamicPower_buffer *(row[4]*row[5]*BitWidth_in) 
                    DynamicPower_buffer2sfu_thisLayer = 2* DynamicPower_buffer2sfu
                    DynamicPower_sfu_thisLayer = DynamicPower_sfu *(row[4]*row[5])

                    Latency_buffer2sfu = Latency_buffer *(row[4]*row[5]*BitWidth_in)
                    Latency_sfu_thisLayer = Latency_sfu *(row[4]*row[5])
                    Latency_buffer2sfu_thisLayer = 2* Latency_buffer2sfu
                    Latency_thisLayer += Latency_buffer2sfu_thisLayer
                    Latency_thisLayer += Latency_sfu_thisLayer

                    DynamicEnergy_thisLayer += DynamicPower_buffer2sfu_thisLayer * Latency_buffer2sfu_thisLayer + DynamicPower_sfu_thisLayer * Latency_sfu_thisLayer

                DynamicEnergy_eachLayer.append(DynamicEnergy_thisLayer)
                Latency_eachLayer.append(Latency_thisLayer)

        ##
        # Wire_DynamicPower = Pack.CalculateDynamicPower_StaticPE_Wire(layer_trace, StaticWire_unitLengthDynPower)
        # Wire_Latency = Pack.CalculateLatency_StaticPE_Wire(layer_trace, StaticWire_unitLengthLatency)
        # Wire_DynamicEnergy = Wire_DynamicPower*Wire_Latency

        # Total_DynamicEnergy = sum(Latency_eachLayer) + Wire_DynamicEnergy
        # Total_Latency = sum(Latency_eachLayer) + Wire_Latency
        ##
    
    
    DynamicEnergy_logic = DynamicPower_logic * Latency_logic
    DynamicEnergy_buffer = DynamicPower_buffer * Latency_buffer
    
    Total_DynamicEnergy = 0
    Total_DynamicEnergy += DynamicEnergy_logic
    Total_DynamicEnergy += DynamicEnergy_buffer

    # get metrics
    Total_Area *= 1e6 # unit:mm2
    Total_Power = Total_DynamicPower + Total_LeakPower
    Total_Energy = Total_DynamicEnergy # + Total_LeakEnergy
    Energy_Efficiency = Total_tops / Total_Energy
    Energy_Efficiency_Per_Area = Energy_Efficiency / Total_Area

    # print PPA
    print("==========================================")
    print("Packaging_dimension:",config.Packaging_dimension)
    print("===== Total =====")
    print("Total Dynamic Energy (J):",Total_DynamicEnergy)
    print("Total Leak Power (W):",Total_LeakPower)
    print("Total Latency (s):",Total_Latency)
    print("Total Area (mm2):",Total_Area)
    print("Total TOPS:",Total_tops)

    print("Energy Efficiency (TOPS/W):", Energy_Efficiency)
    print("Energy Efficiency Per Area (TOPS/W/mm2):", Energy_Efficiency_Per_Area)

    print("===== Breakdown =====")
    print("Num_StaticPE:", Num_StaticPE)
    print("Num_DynamicPE:", Num_DynamicPE)

    # print("Area_Total_Wire:",Pack.Area_Total_Wire)
    # print("DynamicPower_Total_Wire:",Wire_DynamicPower)
    # print("Latency_Total_Wire:",Wire_Latency)
    # print("DynamicEnergy_Wire:",Wire_DynamicEnergy)

    if (config.Packaging_dimension) == 3:
        print("Area Total_tsv",Pack.total_tsv_area)
        # print("Latency_Total_tsv:",Pack.latency_z)
    
    print("==========================================")

    # print("Num_StaticPE EachLayer",Num_StaticPE_eachLayer)
    # print("Num_DynamicPE EachLayer",Num_DynamicPE_eachLayer)
    # print(NetStructure)


# main(2)
# main(2.5)
# main(3)

if __name__ == "__main__":
    config = Config()
    main(config)