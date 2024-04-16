from model import GetData
from Package import Pack2D, Pack2_5D, Pack3D
from tsv_path import TSVPath
from math import ceil
from layer_trace import generate_trace_noc
from wire import Wire

def main(Packaging_dimension):
    # load in model and hw confic info
    model_filename = 'user_defined_example.csv'  # 'user_defined_example.csv', 'hdvit_changed.csv'
    hw_config_filename = 'hw_config.txt'
    data_loader = GetData(model_filename, hw_config_filename)
    NetStructure = data_loader.load_model()
    hw_configs = data_loader.load_hardware_config()

    BitWidth_in = int(hw_configs.get('BitWidth_in', 'Key not found'))
    BitWidth_weight = int(hw_configs.get('BitWidth_weight', 'Key not found'))
    # Packaging_dimension = float(hw_configs.get('Packaging_dimension', 'Key not found'))

    eDRAM_cellSize_height = float(hw_configs.get('eDRAM_cellSize_height', 'Key not found'))
    eDRAM_cellSize_width = float(hw_configs.get('eDRAM_cellSize_width', 'Key not found'))
    eDRAM_SubArray_height = int(hw_configs.get('eDRAM_SubArray_height', 'Key not found'))
    eDRAM_SubArray_width = int(hw_configs.get('eDRAM_SubArray_width', 'Key not found'))
    eDRAM_SubArray_latency = float(hw_configs.get('eDRAM_SubArray_latency', 'Key not found'))
    eDRAM_SubArray_power = float(hw_configs.get('eDRAM_SubArray_power', 'Key not found'))
    eDRAM_SubArray_area = float(hw_configs.get('eDRAM_SubArray_area', 'Key not found'))
    eDRAM_PE_latency = float(hw_configs.get('eDRAM_PE_latency', 'Key not found'))
    eDRAM_PE_dynamicEnergy = float(hw_configs.get('eDRAM_PE_dynamicEnergy', 'Key not found'))
    eDRAM_PE_leakPower = float(hw_configs.get('eDRAM_PE_leakPower', 'Key not found'))
    eDRAM_cell_area = eDRAM_cellSize_height * eDRAM_cellSize_width
    eDRAM_SubArraySize_height = eDRAM_cellSize_height * eDRAM_SubArray_height
    eDRAM_SubArraySize_width = eDRAM_cellSize_width * eDRAM_SubArray_width

    RRAM_cellSize_height = float(hw_configs.get('RRAM_cellSize_height', 'Key not found'))
    RRAM_cellSize_width = float(hw_configs.get('RRAM_cellSize_width', 'Key not found'))
    RRAM_SubArray_height = int(hw_configs.get('RRAM_SubArray_height', 'Key not found'))
    RRAM_SubArray_width = int(hw_configs.get('RRAM_SubArray_width', 'Key not found'))
    RRAM_SubArray_latency = float(hw_configs.get('RRAM_SubArray_latency', 'Key not found'))
    RRAM_SubArray_power = float(hw_configs.get('RRAM_SubArray_power', 'Key not found'))
    RRAM_SubArray_area = float(hw_configs.get('RRAM_SubArray_area', 'Key not found'))
    RRAM_PE_latency = float(hw_configs.get('RRAM_PE_latency', 'Key not found'))
    RRAM_PE_dynamicEnergy = float(hw_configs.get('RRAM_PE_dynamicEnergy', 'Key not found'))
    RRAM_PE_leakPower = float(hw_configs.get('RRAM_PE_leakPower', 'Key not found'))
    RRAM_cell_area = RRAM_cellSize_height * RRAM_cellSize_width
    RRAM_SubArraySize_height = RRAM_cellSize_height * RRAM_SubArray_height
    RRAM_SubArraySize_width = RRAM_cellSize_width * RRAM_SubArray_width

    
    
    # define memorycell type of static layer and dynamic layer
    Static_MemoryCellType = hw_configs.get('Static_MemoryCellType', 'Key not found')
    if Static_MemoryCellType == 'RRAM':
        Static_SubArray_height = RRAM_SubArray_height
        Static_SubArray_width = RRAM_SubArray_width
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
        Static_SubArray_height = eDRAM_SubArray_height
        Static_SubArray_width = eDRAM_SubArray_width
        Static_SubArraySize_height = eDRAM_SubArraySize_height
        Static_SubArraySize_width = eDRAM_SubArraySize_width
        # Static_SubArray_latency = eDRAM_SubArray_latency
        # Static_SubArray_power = eDRAM_SubArray_power
        # Static_SubArray_area = eDRAM_SubArray_area
        Latency_StaticPE = eDRAM_PE_latency
        DynamicEnergy_StaticPE = eDRAM_PE_dynamicEnergy
        LeakPower_StaticPE = eDRAM_PE_leakPower
        Area_StaticCell = eDRAM_cell_area
    Num_StaticSubArrayPerPERow = 2 # can change
    Num_StaticSubArrayPerPECol = 2 # can change
    Static_PE_height = Static_SubArray_height * Num_StaticSubArrayPerPERow 
    Static_PE_width = Static_SubArray_width * Num_StaticSubArrayPerPECol
    Num_StaticSubArrayPerPE = Num_StaticSubArrayPerPERow * Num_StaticSubArrayPerPECol
    Static_PESize_height = Static_SubArraySize_height * Num_StaticSubArrayPerPERow
    Static_PESize_width = Static_SubArraySize_width * Num_StaticSubArrayPerPECol
    Area_StaticPE = Area_StaticCell * Static_PE_height * Static_PE_width
    

    
    Dynamic_MemoryCellType = hw_configs.get('Dynamic_MemoryCellType', 'Key not found')
    if Dynamic_MemoryCellType == 'RRAM':
        Dynamic_SubArray_height = RRAM_SubArray_height
        Dynamic_SubArray_width = RRAM_SubArray_width
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
        Dynamic_SubArray_height = eDRAM_SubArray_height
        Dynamic_SubArray_width = eDRAM_SubArray_width
        Dynamic_SubArraySize_height = eDRAM_SubArraySize_height
        Dynamic_SubArraySize_width = eDRAM_SubArraySize_width
        # Dynamic_SubArray_latency = eDRAM_SubArray_latency
        # Dynamic_SubArray_power = eDRAM_SubArray_power
        # Dynamic_SubArray_area = eDRAM_SubArray_area
        Latency_DynamicPE = eDRAM_PE_latency
        DynamicEnergy_DynamicPE = eDRAM_PE_dynamicEnergy
        LeakPower_DynamicPE = eDRAM_PE_leakPower
        Area_DynamicCell = eDRAM_cell_area
    Num_DynamicSubArrayPerPERow = 2 # can change
    Num_DynamicSubArrayPerPECol = 2 # can change
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

    # breakdown value #####################
    Area_logic = 1.5e-4 
    Area_buffer = 3e-4
    DynamicPower_logic = 4.67e-3/7.6e7*Total_tops
    DynamicPower_buffer = 1.04e-3/7.6e7*Total_tops
    Latency_logic = 1.5e-2/7.6e7*Total_tops
    Latency_buffer = 2.88e-3/7.6e7*Total_tops

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

    Num_StaticTier = 4 # change from user
    Num_DynamicTier = 4 # change from user
    ##########################################
    
    # get total num of static subarray/PE and dynamic subarray/PE
    for row in NetStructure:

        if row[6]==0: # static layer
            Num_StaticSubArray_thisLayer = ceil(row[2]/Static_SubArray_height) * ceil(row[3]*BitWidth_weight/Static_SubArray_width) # weightRowNum * weightColNum
            Num_StaticSubArray_eachLayer.append(Num_StaticSubArray_thisLayer)
            Num_DynamicSubArray_eachLayer.append(0)
            Num_StaticSubArray += Num_StaticSubArray_thisLayer

            Num_StaticPE_thisLayer = ceil(Num_StaticSubArray_thisLayer / Num_StaticSubArrayPerPE)
            Num_StaticPE_eachLayer.append(Num_StaticPE_thisLayer)
            Num_DynamicPE_eachLayer.append(0)
            
        else: # dynamic layer
            Num_DynamicSubArray_thisLayer = ceil(row[2]/Dynamic_SubArray_height) * ceil(row[3]*BitWidth_weight/Dynamic_SubArray_width) * row[8] # weightRowNum * weightColNum
            Num_DynamicSubArray_eachLayer.append(Num_DynamicSubArray_thisLayer)
            Num_StaticSubArray_eachLayer.append(0)
            Num_DynamicSubArray += Num_DynamicSubArray_thisLayer

            Num_DynamicPE_thisLayer = ceil(Num_DynamicSubArray_thisLayer / Num_DynamicSubArrayPerPE)
            Num_DynamicPE_eachLayer.append(Num_DynamicPE_thisLayer)
            Num_StaticPE_eachLayer.append(0)
        
        Num_StaticPE = sum(Num_StaticPE_eachLayer)
        Num_DynamicPE = sum(Num_DynamicPE_eachLayer)
        
        # LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + LeakPower_StaticPE_Wire + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        # LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + LeakPower_DynamicPE_Wire + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_buffer

    # print("Num StaticPE EachLayer:",Num_StaticPE_eachLayer)
    # print("Num DynamicPE EachLayer:",Num_DynamicPE_eachLayer)
    # print("Num_StaticPE:", Num_StaticPE)
    # print("Num_DynamicPE:", Num_DynamicPE)

    # get Num of input Activation each Layer
    Num_Output_eachLayer = []
    Num_Weight_eachLayer = []
    for row in NetStructure:
        Num_Output_eachLayer.append(row[4]*row[5] *row[8]) #row[8] is num_head
        Num_Weight_eachLayer.append(row[2]*row[3] *row[8])
    
    # print("Num_Activation_eachLayer:",Num_Output_eachLayer)
    # print("Num_Weight_eachLayer:",Num_Weight_eachLayer)
    
    # # get trace inside/inter layers
    Bus_width = 32
    layer_trace = generate_trace_noc(Num_StaticPE_eachLayer, Num_DynamicPE_eachLayer, Num_Output_eachLayer, Num_Weight_eachLayer,
                        BitWidth_in, BitWidth_weight, Bus_width)
    
    # get Num of input Activation each Layer
    Latency_eachLayer = []
    DynamicEnergy_eachLayer = []
    LeakEnergy_eachLayer = []
    AvgPower_eachLayer = []

    
    if Packaging_dimension == 2:
        Pack = Pack2D()
        # get chip area
        Total_Area = Pack.CalculateArea(
            Num_StaticPE, Area_StaticPE, StaticWire_unitLengthArea, Static_PESize_height, Static_PESize_width, Area_logic,Area_buffer,
            Num_DynamicPE, Area_DynamicPE, DynamicWire_unitLengthArea, Dynamic_PESize_height, Dynamic_PESize_width, Area_DynamicPE_sfu)
        
        # get leak power (need change!)
        LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + Pack.CalculateLeakPower_StaticPE_Wire() + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + Pack.CalculateLeakPower_DynamicPE_Wire() + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_sfu + LeakPower_DynamicPE_buffer
        Total_LeakPower = LeakPower_staticLayers + LeakPower_dynamicLayers


        # get dynamic power and latency
        for row in NetStructure:
            # get TOPS of this layer
            tops_thisLayer = (row[0]*row[1]*row[3] + (row[0]-1)*row[1]*row[3]) *1e-12
            Total_tops += tops_thisLayer

            # get this layer operation is static or dynamic
            if row[6]: # is static layer
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
                
        Wire_DynamicPower = Pack.CalculateDynamicPower_StaticPE_Wire(layer_trace, Num_StaticPE, Num_DynamicPE,StaticWire_unitLengthDynPower)
        Wire_Latency = Pack.CalculateLatency_StaticPE_Wire(layer_trace, Num_StaticPE, Num_DynamicPE, StaticWire_unitLengthLatency)
        Wire_DynamicEnergy = Wire_DynamicPower*Wire_Latency

        Total_DynamicEnergy = sum(Latency_eachLayer) 
        # Total_DynamicEnergy += Wire_DynamicEnergy
        Total_Latency = sum(Latency_eachLayer) 
        # Total_Latency += Wire_Latency
        ##

        
    
    elif Packaging_dimension == 2.5:

        Pack = Pack2_5D()

        # get chip area
        Total_Area = Pack.CalculateArea(
            Num_StaticPE, Area_StaticPE, Area_logic,Area_buffer,
            Num_DynamicPE, Area_DynamicPE, Area_DynamicPE_sfu)
        
        # get leak power
        LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + Pack.CalculateLeakPower_StaticPE_Wire() + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + Pack.CalculateLeakPower_DynamicPE_Wire() + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_sfu + LeakPower_DynamicPE_buffer
        Total_LeakPower = LeakPower_staticLayers + LeakPower_dynamicLayers
        
        # get dynamic power and latency
        for row in NetStructure:
            # get TOPS of this layer
            tops_thisLayer = (row[0]*row[1]*row[3] + (row[0]-1)*row[1]*row[3]) *1e-12
            Total_tops += tops_thisLayer

            # get this layer operation is static or dynamic
            if row[6]: # is static layer
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
        Pack = Pack3D(Num_StaticPE,Num_DynamicPE,Num_StaticTier,Num_DynamicTier,
                    StaticWire_unitLengthArea, Static_PE_height, Static_PE_width,
                    DynamicWire_unitLengthArea, Dynamic_PE_height, Dynamic_PE_width)
        #get chip area
        Total_Area = Pack.CalculateArea(
            Area_StaticPE, Area_logic,Area_buffer,
            Area_DynamicPE, Area_DynamicPE_sfu
            )

        # get leak power
        LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + Pack.CalculateLeakPower_StaticPE_Wire() + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + Pack.CalculateLeakPower_DynamicPE_Wire() + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_sfu + LeakPower_DynamicPE_buffer
        Total_LeakPower = LeakPower_staticLayers + LeakPower_dynamicLayers
        
        # get dynamic power and latency
        for row in NetStructure:
            # get TOPS of this layer
            tops_thisLayer = (row[0]*row[1]*row[3] + (row[0]-1)*row[1]*row[3]) *1e-12
            Total_tops += tops_thisLayer

            # get this layer operation is static or dynamic
            if row[6]: # is static layer
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
        Wire_DynamicPower = Pack.CalculateDynamicPower_StaticPE_Wire(layer_trace, StaticWire_unitLengthDynPower)
        Wire_Latency = Pack.CalculateLatency_StaticPE_Wire(layer_trace, StaticWire_unitLengthLatency)
        Wire_DynamicEnergy = Wire_DynamicPower*Wire_Latency

        Total_DynamicEnergy = sum(Latency_eachLayer) + Wire_DynamicEnergy
        Total_Latency = sum(Latency_eachLayer) + Wire_Latency
        ##
    
    DynamicEnergy_logic = DynamicPower_logic * Latency_logic
    DynamicEnergy_buffer = DynamicPower_buffer * Latency_buffer
    
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
    print("Packaging_dimension:",Packaging_dimension)
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

    print("Area_Total_Wire:",Pack.Area_Total_Wire)
    print("DynamicPower_Total_Wire:",Wire_DynamicPower)
    print("Latency_Total_Wire:",Wire_Latency)
    print("DynamicEnergy_Wire:",Wire_DynamicEnergy)

    if (Packaging_dimension) == 3:
        print("Area Total_tsv",Pack.Area_Total_tsv)
        print("Latency_Total_tsv:",Pack.latency_z)
    
    print("==========================================")

    # print("Num_StaticPE EachLayer",Num_StaticPE_eachLayer)
    # print("Num_DynamicPE EachLayer",Num_DynamicPE_eachLayer)
    # print(NetStructure)


main(2)
main(2.5)
main(3)