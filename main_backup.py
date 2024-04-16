from model import GetData
from Package import Pack2D, Pack2_5D, Pack3D
from tsv_path import TSVPath
from math import ceil
from layer_trace import generate_trace_noc
from wire import Wire

def main():
    # load in model and hw confic info
    model_filename = 'user_defined_example.csv'
    hw_config_filename = 'hw_config.txt'
    data_loader = GetData(model_filename, hw_config_filename)
    NetStructure = data_loader.load_model()
    hw_configs = data_loader.load_hardware_config()

    BitWidth_in = int(hw_configs.get('BitWidth_in', 'Key not found'))
    BitWidth_weight = int(hw_configs.get('BitWidth_weight', 'Key not found'))
    Packaging_dimension = float(hw_configs.get('Packaging_dimension', 'Key not found'))

    eDRAM_SubArray_height = int(hw_configs.get('eDRAM_SubArray_height', 'Key not found'))
    eDRAM_SubArray_width = int(hw_configs.get('eDRAM_SubArray_width', 'Key not found'))
    eDRAM_SubArray_latency = float(hw_configs.get('eDRAM_SubArray_latency', 'Key not found'))
    eDRAM_SubArray_power = float(hw_configs.get('eDRAM_SubArray_power', 'Key not found'))
    eDRAM_SubArray_area = float(hw_configs.get('eDRAM_SubArray_area', 'Key not found'))
    eDRAM_PE_latency = float(hw_configs.get('eDRAM_PE_latency', 'Key not found'))
    eDRAM_PE_dynamicPower = float(hw_configs.get('eDRAM_PE_dynamicPower', 'Key not found'))
    eDRAM_PE_leakPower = float(hw_configs.get('eDRAM_PE_leakPower', 'Key not found'))
    eDRAM_PE_area = float(hw_configs.get('eDRAM_PE_area', 'Key not found'))

    RRAM_SubArray_height = int(hw_configs.get('RRAM_SubArray_height', 'Key not found'))
    RRAM_SubArray_width = int(hw_configs.get('RRAM_SubArray_width', 'Key not found'))
    RRAM_SubArray_latency = float(hw_configs.get('RRAM_SubArray_latency', 'Key not found'))
    RRAM_SubArray_power = float(hw_configs.get('RRAM_SubArray_power', 'Key not found'))
    RRAM_SubArray_area = float(hw_configs.get('RRAM_SubArray_area', 'Key not found'))
    RRAM_PE_latency = float(hw_configs.get('RRAM_PE_latency', 'Key not found'))
    RRAM_PE_dynamicPower = float(hw_configs.get('RRAM_PE_dynamicPower', 'Key not found'))
    RRAM_PE_leakPower = float(hw_configs.get('RRAM_PE_leakPower', 'Key not found'))
    RRAM_PE_area = float(hw_configs.get('RRAM_PE_area', 'Key not found'))

    # # get PPA difference of 2D/2.5D/3D###############################
    # if Packaging_dimension == 2:
    #     Latency_StaticPE_Wire = Pack2D().CalculateLatency
    #     DynamicPower_StaticPE_Wire = Pack2D().CalculateDynamicPower
    #     LeakPower_StaticPE_Wire = Pack2D().CalculateLeakPower_s
    #     LeakPower_DynamicPE_Wire = Pack2D().CalculateLeakPower_d
    #     Area_StaticPE_Wire = Pack2D().CalculateArea
    # elif Packaging_dimension == 2.5:
    #     Latency_StaticPE_Wire = Pack2_5D().CalculateLatency
    #     DynamicPower_StaticPE_Wire = Pack2_5D().CalculateDynamicPower
    #     LeakPower_StaticPE_Wire = Pack2_5D().CalculateLeakPower
    #     Area_StaticPE_Wire = Pack2_5D().CalculateArea
    # else: # 3D
    #     Latency_StaticPE_Wire = Pack3D().CalculateLatency
    #     DynamicPower_StaticPE_Wire = Pack3D().CalculateDynamicPower
    #     LeakPower_StaticPE_Wire = Pack3D().CalculateLeakPower
    #     Area_StaticPE_Wire = Pack3D().CalculateArea
    # ###############################
    
    Num_StaticSubArrayPerPE = 4 # can be changed
    Num_DynamicSubArrayPerPE = 4 # can be changed
    
    # define memorycell type of static layer and dynamic layer
    Static_MemoryCellType = hw_configs.get('Static_MemoryCellType', 'Key not found')
    if Static_MemoryCellType == 'RRAM':
        Static_SubArray_height = RRAM_SubArray_height
        Static_SubArray_width = RRAM_SubArray_width
        # Static_SubArray_latency = RRAM_SubArray_latency
        # Static_SubArray_power = RRAM_SubArray_power
        # Static_SubArray_area = RRAM_SubArray_area
        Latency_StaticPE = RRAM_PE_latency
        DynamicPower_StaticPE = RRAM_PE_dynamicPower
        LeakPower_StaticPE = RRAM_PE_leakPower
        Area_StaticPE = RRAM_PE_area
    if Static_MemoryCellType == 'eDRAM':
        Static_SubArray_height = eDRAM_SubArray_height
        Static_SubArray_width = eDRAM_SubArray_width
        # Static_SubArray_latency = eDRAM_SubArray_latency
        # Static_SubArray_power = eDRAM_SubArray_power
        # Static_SubArray_area = eDRAM_SubArray_area
        Latency_StaticPE = eDRAM_PE_latency
        DynamicPower_StaticPE = eDRAM_PE_dynamicPower
        LeakPower_StaticPE = eDRAM_PE_leakPower
        Area_StaticPE = eDRAM_PE_area

    
    Dynamic_MemoryCellType = hw_configs.get('Dynamic_MemoryCellType', 'Key not found')
    if Dynamic_MemoryCellType == 'RRAM':
        Dynamic_SubArray_height = RRAM_SubArray_height
        Dynamic_SubArray_width = RRAM_SubArray_width
        # Dynamic_SubArray_latency = RRAM_SubArray_latency
        # Dynamic_SubArray_power = RRAM_SubArray_power
        # Dynamic_SubArray_area = RRAM_SubArray_area
        Latency_DynamicPE = RRAM_PE_latency
        DynamicPower_DynamicPE = RRAM_PE_dynamicPower
        LeakPower_DynamicPE = RRAM_PE_leakPower
        Area_DynamicPE = RRAM_PE_area
    if Dynamic_MemoryCellType == 'eDRAM':
        Dynamic_SubArray_height = eDRAM_SubArray_height
        Dynamic_SubArray_width = eDRAM_SubArray_width
        # Dynamic_SubArray_latency = eDRAM_SubArray_latency
        # Dynamic_SubArray_power = eDRAM_SubArray_power
        # Dynamic_SubArray_area = eDRAM_SubArray_area
        Latency_DynamicPE = eDRAM_PE_latency
        DynamicPower_DynamicPE = eDRAM_PE_dynamicPower
        LeakPower_DynamicPE = eDRAM_PE_leakPower
        Area_DynamicPE = eDRAM_PE_area
    
    # get static/dynamic layer dataflow
    # initialize PPA
    Total_DynamicPower = 0
    Total_LeakPower = 0
    Total_Latency = 0
    Total_Area = 0

    DynamicPower_staticLayers = 0
    DynamicPower_dynamicLayers = 0
    LeakPower_staticLayers = 0
    LeakPower_dynamicLayers = 0
    Latency_staticLayers = 0
    Latency_dynamicLayers = 0
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


    Area_StaticPE_Wire =  StaticWire_unitLengthArea # calculate

    Area_DynamicPE_Wire = DynamicWire_unitLengthArea # calculate

    Area_DynamicPE_sfu = 3e-7

    LeakPower_StaticPE_logic = 0
    LeakPower_StaticPE_buffer = 0
    LeakPower_DynamicPE_logic = 0
    LeakPower_DynamicPE_sfu = 0 
    LeakPower_DynamicPE_buffer = 0

    DynamicPower_weightLoadin = 0 # calculate
    Latency_weightLoadin = 0 # calculate

    DynamicPower_buffer2sfu = 0 # calculate
    Latency_buffer2sfu = 0 # calculate

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
        
        Num_StaticPE = ceil(Num_StaticSubArray / Num_StaticSubArrayPerPE)
        Num_DynamicPE = ceil(Num_DynamicSubArray / Num_DynamicSubArrayPerPE)
        
        
    print("Num StaticPE EachLayer:",Num_StaticPE_eachLayer)
    print("Num DynamicPE EachLayer:",Num_DynamicPE_eachLayer)

    # get Num of input Activation each Layer
    Num_Output_eachLayer = []
    Num_Weight_eachLayer = []
    for row in NetStructure:
        Num_Output_eachLayer.append(row[4]*row[5] *row[8]) #row[8] is num_head
        Num_Weight_eachLayer.append(row[2]*row[3] *row[8])
    
    print("Num_Activation_eachLayer:",Num_Output_eachLayer)
    print("Num_Weight_eachLayer:",Num_Weight_eachLayer)
    
    # # get trace inside/inter layers
    Bus_width = 32
    layer_trace = generate_trace_noc(Num_StaticPE_eachLayer, Num_DynamicPE_eachLayer, Num_Output_eachLayer, Num_Weight_eachLayer,
                        BitWidth_in, BitWidth_weight, Bus_width)
    

    
    if Packaging_dimension == 2:

        # get chip area
        Total_Area = Pack2D().CalculateArea(
            Num_StaticPE, Area_StaticPE, Area_StaticPE_Wire, Area_logic,Area_buffer,
            Num_DynamicPE, Area_DynamicPE, Area_DynamicPE_Wire, Area_DynamicPE_sfu)
        
        # get leak power
        LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + Pack2D().CalculateLeakPower_StaticPE_Wire() + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + Pack2D().CalculateLeakPower_DynamicPE_Wire() + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_sfu + LeakPower_DynamicPE_buffer
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

                DynamicPower_thisLayer = Num_StaticPE_thisLayer * DynamicPower_StaticPE + Pack2D().CalculateDynamicPower_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE,StaticWire_unitLengthDynPower)
                Latency_thisLayer = Latency_StaticPE + Pack2D().CalculateLatency_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE, StaticWire_unitLengthLatency)
            
                DynamicPower_staticLayers += DynamicPower_thisLayer
                Latency_staticLayers += Latency_thisLayer

            else: # is dynamic layer
                # get num of PE used of dynamic layer
                Num_DynamicSubArray_thisLayer = ceil(row[2]/Dynamic_SubArray_height) * ceil(row[3]*BitWidth_weight/Dynamic_SubArray_width) # weightRowNum * weightColNum
                Num_DynamicPE_thisLayer = ceil(Num_DynamicSubArray_thisLayer / Num_DynamicSubArrayPerPE)

                DynamicPower_thisLayer = (DynamicPower_weightLoadin)+ Num_DynamicPE_thisLayer * DynamicPower_DynamicPE + Pack2D().CalculateDynamicPower_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE,DynamicWire_unitLengthDynPower)
                Latency_thisLayer = (Latency_weightLoadin) + Latency_DynamicPE + Pack2D().CalculateLatency_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE, DynamicWire_unitLengthLatency)
            
            
                if row[7]: # have softmax operation, need sfu
                    DynamicPower_thisLayer += 2* DynamicPower_buffer2sfu
                    Latency_thisLayer += 2* Latency_buffer2sfu

                DynamicPower_dynamicLayers += DynamicPower_thisLayer
                Latency_dynamicLayers += Latency_thisLayer
        ##
        Total_DynamicPower = DynamicPower_staticLayers + DynamicPower_dynamicLayers
        Total_Latency = Latency_staticLayers + Latency_dynamicLayers
        ##
    
    elif Packaging_dimension == 2.5:

        # get chip area
        Total_Area = Pack2_5D().CalculateArea(
            Num_StaticPE, Area_StaticPE, Area_logic,Area_buffer,
            Num_DynamicPE, Area_DynamicPE, Area_DynamicPE_sfu)
        
        # get leak power
        LeakPower_staticLayers = Num_StaticPE * LeakPower_StaticPE + Pack2_5D().CalculateLeakPower_StaticPE_Wire() + LeakPower_StaticPE_logic + LeakPower_StaticPE_buffer
        LeakPower_dynamicLayers = Num_DynamicPE * LeakPower_DynamicPE + Pack2_5D().CalculateLeakPower_DynamicPE_Wire() + LeakPower_DynamicPE_logic + LeakPower_DynamicPE_sfu + LeakPower_DynamicPE_buffer
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

                
                DynamicPower_thisLayer = Num_StaticPE_thisLayer * DynamicPower_StaticPE + Pack2_5D().CalculateDynamicPower_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE,StaticWire_unitLengthDynPower)
                Latency_thisLayer = Latency_StaticPE + Pack2_5D().CalculateLatency_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE, StaticWire_unitLengthLatency)
               
                
                DynamicPower_staticLayers += DynamicPower_thisLayer
                Latency_staticLayers += Latency_thisLayer

            else: # is dynamic layer
                # get num of PE used of dynamic layer
                Num_DynamicSubArray_thisLayer = ceil(row[2]/Dynamic_SubArray_height) * ceil(row[3]*BitWidth_weight/Dynamic_SubArray_width) # weightRowNum * weightColNum
                Num_DynamicPE_thisLayer = ceil(Num_DynamicSubArray_thisLayer / Num_DynamicSubArrayPerPE)

                DynamicPower_thisLayer = (DynamicPower_weightLoadin)+ Num_DynamicPE_thisLayer * DynamicPower_DynamicPE + Pack2_5D().CalculateDynamicPower_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE,DynamicWire_unitLengthDynPower)
                Latency_thisLayer = (Latency_weightLoadin) + Latency_DynamicPE + Pack2_5D().CalculateLatency_StaticPE_Wire(row, layer_trace, Num_StaticPE, Num_DynamicPE, DynamicWire_unitLengthLatency)
                
                if row[7]: # have softmax operation, need sfu
                    DynamicPower_thisLayer += 2* DynamicPower_buffer2sfu
                    Latency_thisLayer += 2* Latency_buffer2sfu

                DynamicPower_dynamicLayers += DynamicPower_thisLayer
                Latency_dynamicLayers += Latency_thisLayer
        ##
        Total_DynamicPower = DynamicPower_staticLayers + DynamicPower_dynamicLayers
        Total_Latency = Latency_staticLayers + Latency_dynamicLayers
        ##

    else: # H3D
        Pack = Pack3D(Num_StaticPE,Num_DynamicPE,Num_StaticTier,Num_DynamicTier)
        #get chip area
        Total_Area = Pack.CalculateArea(
            Num_StaticPE, Area_StaticPE, Area_logic,Area_buffer,
            Num_DynamicPE, Area_DynamicPE, Area_DynamicPE_sfu,
            Num_StaticTier, Num_DynamicTier
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

                
                DynamicPower_thisLayer = Num_StaticPE_thisLayer * DynamicPower_StaticPE + Pack.CalculateDynamicPower_StaticPE_Wire(layer_trace, StaticWire_unitLengthDynPower)
                Latency_thisLayer = Latency_StaticPE + Pack.CalculateLatency_StaticPE_Wire(layer_trace, StaticWire_unitLengthLatency)
            
                
                DynamicPower_staticLayers += DynamicPower_thisLayer
                Latency_staticLayers += Latency_thisLayer

            else: # is dynamic layer
                # get num of PE used of dynamic layer
                Num_DynamicSubArray_thisLayer = ceil(row[2]/Dynamic_SubArray_height) * ceil(row[3]*BitWidth_weight/Dynamic_SubArray_width) # weightRowNum * weightColNum
                Num_DynamicPE_thisLayer = ceil(Num_DynamicSubArray_thisLayer / Num_DynamicSubArrayPerPE)

            
                DynamicPower_thisLayer = (DynamicPower_weightLoadin)+ Num_DynamicPE_thisLayer * DynamicPower_DynamicPE + Pack.CalculateDynamicPower_StaticPE_Wire(layer_trace, StaticWire_unitLengthDynPower)
                Latency_thisLayer = (Latency_weightLoadin) + Latency_DynamicPE + Pack.CalculateLatency_StaticPE_Wire(layer_trace, StaticWire_unitLengthLatency)
            
                
                if row[7]: # have softmax operation, need sfu
                    DynamicPower_thisLayer += 2* DynamicPower_buffer2sfu
                    Latency_thisLayer += 2* Latency_buffer2sfu

                DynamicPower_dynamicLayers += DynamicPower_thisLayer
                Latency_dynamicLayers += Latency_thisLayer

        ##
        Total_DynamicPower = DynamicPower_staticLayers + DynamicPower_dynamicLayers
        Total_Latency = Latency_staticLayers + Latency_dynamicLayers
        ##
    
    Total_DynamicPower += DynamicPower_logic
    Total_DynamicPower += DynamicPower_buffer
    Total_Latency += Latency_logic
    Total_Latency += Latency_buffer
    
    # get metrics
    Total_Area *= 1e6 # unit:mm2
    Total_Power = Total_DynamicPower + Total_LeakPower
    Total_Energy = Total_Power * Total_Latency
    Energy_Efficiency = Total_tops / Total_Energy
    Energy_Efficiency_Per_Area = Energy_Efficiency / Total_Area

    # print PPA
    print("Total Dynamic Power:",Total_DynamicPower)
    print("Total Leak Power:",Total_LeakPower)
    print("Total Latency:",Total_Latency)
    print("Total Area (mm2):",Total_Area)
    print("Total TOPS:",Total_tops)

    print("Energy Efficiency (TOPS/W):", Energy_Efficiency)
    print("Energy Efficiency Per Area (TOPS/W/mm2):", Energy_Efficiency_Per_Area)

    print("Num_StaticPE:", Num_StaticPE)
    print("Num_DynamicPE:", Num_DynamicPE)

    # print("Num_StaticPE EachLayer",Num_StaticPE_eachLayer)
    # print("Num_DynamicPE EachLayer",Num_DynamicPE_eachLayer)
    # print(NetStructure)


main()