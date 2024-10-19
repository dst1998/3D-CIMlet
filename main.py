import math

from config import Config
from layer_trace import generate_trace_noc
from chiplet_layer_range import get_static_chiplet_layer_range,get_static_chiplet_layers,get_dest_layers
from layer_mapping import get_layer_energy_latency
from peripheral import *
from Interconnect.noc_estimation import interconnect_estimation
from Interconnect.nop_estimation import *
from Interconnect.NoP_hardware import NoP_hardware_estimation
from Integration import *

def main(config):
    # load in model and hw config info from config file
    # hw_config_filename = 'hw_config.txt'
    # data_loader = GetData(model_filename)
    # NetStructure = data_loader.load_model()
    # hw_configs = data_loader.load_hardware_config()
    NetStructure = config.load_model()
    NetStructure_layer_def  = config.load_model_layer_def()
    print("layerdef:",NetStructure_layer_def)
    static_chiplet_size = config.static_chiplet_height * config.static_chiplet_width
    dynamic_chiplet_size = config.dynamic_chiplet_height * config.dynamic_chiplet_width
    
    # get static/dynamic layer dataflow
    # initialize PPA
    Total_DynamicPower = 0
    Total_LeakPower = 0
    Total_Latency = 0
    Total_Area = 0
    Total_top_num = 0

    Num_StaticSubArray = 0
    Num_DynamicSubArray = 0
    Num_StaticSubArray_eachLayer = []
    Num_DynamicSubArray_eachLayer = []
    Num_StaticPE = 0
    Num_DynamicPE = 0
    Num_StaticPE_eachLayer = []
    Num_DynamicPE_eachLayer = []
    performance_each_layer = []

    # get TOPS of this layer
    for row in NetStructure:
        tops_thisLayer = row[0]*row[1]*row[3] *2 *1e-12
        Total_top_num += tops_thisLayer

    # breakdown value #####################
    Area_logic = 1.5e-4 
    Area_buffer = 3e-4

    Area_DynamicPE_sfu = 3e-7
    DynamicPower_sfu = 8e-3 /512 # for 512 input
    Latency_sfu = 7e-7 /512 # for 512 input

    buffer_bw = 9e9 # SRAM-2D:9Gb/s=1.125GB/s
    buffer_dynamicEnergy = 17.5e-15 * 40/65  # [depends on tech] unit:J/read or J/write, SRAM-2D-65nm:17.5fJ/bit=140fJ/byte

    DynamicPower_logic = 4.67e-3/7.6e7*Total_top_num
    DynamicPower_buffer = 1.04e-3/7.6e7*Total_top_num
    Latency_logic = 1.5e-2/7.6e7*Total_top_num
    Latency_buffer = 2.88e-3/7.6e7*Total_top_num
    
    ##########################################
    
    num_static_chiplet_eachLayer = []
    num_dynamic_chiplet_eachLayer = []
    # get num of used static subarray/PE or used dynamic subarray/PE of each model layer
    # get dynamic power and latency
    for layer_index, row in enumerate(NetStructure):
        # get this layer operation is static or dynamic
        if row[6]== 0: # is static layer
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer, static_chip_write_energy_per_bit = get_layer_energy_latency(row,config,config.static_chiplet_technode,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(num_used_chiplet_this_layer)
            num_dynamic_chiplet_eachLayer.append(0)

            Num_StaticPE_eachLayer.append(num_used_pe_this_layer)
            Num_DynamicPE_eachLayer.append(0)

            Num_StaticSubArray_eachLayer.append(num_used_subarray_this_layer)
            Num_DynamicSubArray_eachLayer.append(0)
        elif row[6]== 1: # is dynamic layer
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer, dynamic_chip_write_energy_per_bit= get_layer_energy_latency(row,config,config.dynamic_chiplet_technode,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(0)
            num_dynamic_chiplet_eachLayer.append(num_used_chiplet_this_layer)

            Num_StaticPE_eachLayer.append(0)
            Num_DynamicPE_eachLayer.append(num_used_pe_this_layer)

            Num_StaticSubArray_eachLayer.append(0)
            Num_DynamicSubArray_eachLayer.append(num_used_subarray_this_layer)
        elif row[6]== 2: # is semi-static layer. (In this layer, weight need to stay  static for some time but not forever)
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer, semi_static_chip_write_energy_per_bit = get_layer_energy_latency(row,config,config.dynamic_chiplet_technode,chiplet_type='static',memory_cell_type=config.dynamic_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(num_used_chiplet_this_layer)
            num_dynamic_chiplet_eachLayer.append(0)

            Num_StaticPE_eachLayer.append(num_used_pe_this_layer)
            Num_DynamicPE_eachLayer.append(0)

            Num_StaticSubArray_eachLayer.append(num_used_subarray_this_layer)
            Num_DynamicSubArray_eachLayer.append(0)
        Num_StaticPE = sum(Num_StaticPE_eachLayer)
        Num_DynamicPE = sum(Num_DynamicPE_eachLayer)
        num_used_dynamic_chiplet = max(num_dynamic_chiplet_eachLayer)
        num_chiplet_eachLayer = [a + b for a, b in zip(num_static_chiplet_eachLayer, num_dynamic_chiplet_eachLayer)]

        # TODO: add [weight] [write latency and energy], global buffer to each chiplet (chiplet-to-chiplet).
        # TODO: for first layer, add the [input] [write latency and energy] , global buffer to first chiplet (chiplet-to-chiplet).
        # TODO: for last layer, add the [output] [write latency and energy] , last chiplet to global buffer(chiplet-to-chiplet).
        # TODO: add [weight] in static chip [refresh latency and energy] based on below (all-layer latency) and noc,nop latency:
        performance_each_layer.append(performance_this_layer)



    # get location in chiplet for each model static layer (layer?: pe?~pe? in chiplet?)
    # static_chiplet_layer_range, static_chiplet_availability, num_used_static_chiplet_all_layers,layer_location_begin_chiplet = get_static_chiplet_layer_range(config,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer)
    
    dest_layers, to_bp_dest_layers, num_to_bp_transfer_byte_to_layer = get_dest_layers(config,NetStructure,NetStructure_layer_def)
    
    static_chiplet_layers, static_chiplet_availability, num_used_static_chiplet_all_layers,chiplet_static_type,layer_location_begin_chiplet = get_static_chiplet_layers(config,NetStructure,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer)

    # get Num of input Activation each Layer
    Num_In_eachLayer = []
    Num_Weight_eachLayer = []
    Num_Output_eachLayer = []
    for row in NetStructure:
        Num_In_eachLayer.append(row[0]*row[1])
        Num_Weight_eachLayer.append(row[2]*row[3])
        Num_Output_eachLayer.append(row[4]*row[5])
    
    # get global buffer size
    maxnum_layer_in_bit = max(Num_In_eachLayer) * config.BitWidth_in
    
    num_used_chiplets = num_used_static_chiplet_all_layers + num_used_dynamic_chiplet

    # # NoC Estimation
    # noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
    
    # # NoP Estimation
    # nop_area, nop_latency, nop_energy = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size)
    
    # # NoP Hardware Cost (Nop_area:um2, NoP_energy:pJ)
    # # TODO: change data for 2.5D and 3D NoP driver
    # # NoP Parameters - Extracted from GRS Nvidia 
    # ebit = 43.2 # pJ 
    # # (0.58pJ/b in GRS Nvidia 28nm [CICC'18: Ground-Referenced Signaling for Intra-Chip and Short-Reach Chip-to-Chip Interconnects])
    # # (1.2pJ/b in ISSCC'17: A 14nm 1GHz FPGA with 2.5 D Transceiver Integration)
    # area_per_lane = 5304.5 #um2
    # clocking_area = 10609 #um2
    # n_lane = 32
    # n_bits_per_chiplet = 4.19E+06 #Automate this in next version
    # nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_per_chiplet)



    # get Num of input Activation each Layer
    Latency_eachLayer = []
    DynamicEnergy_eachLayer = []
    LeakEnergy_eachLayer = []
    AvgPower_eachLayer = []

    if config.Packaging_dimension == 2:
        Integration = Integration2D(config,maxnum_layer_in_bit,num_used_static_chiplet_all_layers, num_used_dynamic_chiplet)
        # get chip area
        chip_area = Integration.CalculateArea()
        # NoC Estimation
        noc_area, noc_latency, noc_energy = 0,0,0
        noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        
        noc_area_train, noc_latency_train, noc_energy_train = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, num_to_bp_transfer_byte_to_layer, static_chiplet_layers, to_bp_dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        # NoP
        nop_area, nop_latency, nop_energy = 0,0,0
        nop_driver_area, nop_driver_energy = 0,0
    elif config.Packaging_dimension == 2.5:
        Integration = Integration2_5D(config,maxnum_layer_in_bit,num_used_static_chiplet_all_layers, num_used_dynamic_chiplet)
        # get chip area
        chip_area = Integration.CalculateArea()
        # NoC Estimation
        noc_area, noc_latency, noc_energy = 0,0,0
        noc_area_train, noc_latency_train, noc_energy_train = 0,0,0
        
        # noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        
        # noc_area_train, noc_latency_train, noc_energy_train = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, num_to_bp_transfer_byte_to_layer, static_chiplet_layers, to_bp_dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        
        # NoP Estimation
        nop_area, nop_latency, nop_energy, num_bits_nop_eachLayer = 0,0,0,0
        nop_area, nop_latency, nop_energy, num_bits_nop_eachLayer = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size)
        
        nop_area_train, nop_latency_train, nop_energy_train, num_bits_nop_eachLayer_train = 0,0,0,0
        # nop_area_train, nop_latency_train, nop_energy_train, num_bits_nop_eachLayer_train = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, to_bp_dest_layers, layer_location_begin_chiplet, num_to_bp_transfer_byte_to_layer, config.net_name, config.static_chiplet_size)

        nop_driver_area, nop_driver_energy = 0,0
        
        # NoP Hardware Cost (Nop_area:um2, NoP_energy:pJ)
        # TODO: change data for 2.5D and 3D NoP driver
        # NoP Parameters - Extracted from GRS Nvidia 
        
        # # SIAM
        # ebit = 0.58e-12
        # area_per_lane = 5304.5e-12 # 5304.5 um2
        # clocking_area = 10609e-12 # 10609 um2
        # n_lane = 32
        # n_bits_all_chiplets = sum(num_bits_nop_eachLayer)
        # n_bits_all_chiplets += sum(num_bits_nop_eachLayer_train)
        # nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_all_chiplets)
        
        # # # CoWoS
        # ebit = 0.56e-12
        # area_per_lane = config.chiplet_bus_width_2D * (45e-6*45e-6)
        # clocking_area = 0
        # n_lane = 1
        # n_bits_all_chiplets = sum(num_bits_nop_eachLayer)
        # n_bits_all_chiplets += sum(num_bits_nop_eachLayer_train)
        # nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_all_chiplets)

    else: # H3D
        Integration = Integration3D(config,maxnum_layer_in_bit)
        #get chip area
        chip_area = Integration.CalculateArea()
        # NoC Estimation
        noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        
        noc_area_train, noc_latency_train, noc_energy_train = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, num_to_bp_transfer_byte_to_layer, static_chiplet_layers, to_bp_dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        # NoP Estimation
        nop_area, nop_latency, nop_energy,num_bits_nop_eachLayer = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, dest_layers,layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size)
        
        nop_area_train, nop_latency_train, nop_energy_train, num_bits_nop_eachLayer_train = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, to_bp_dest_layers, layer_location_begin_chiplet, num_to_bp_transfer_byte_to_layer, config.net_name, config.static_chiplet_size)

        # NoP Hardware Cost (Nop_area:um2, NoP_energy:pJ)
        # TODO: change data for 2.5D and 3D NoP driver
        # now, 3D use 2.5D same data
        ebit = 0.58e-12
        area_per_lane = 5304.5e-12 # 5304.5 um2
        clocking_area = 10609e-12 # 10609 um2
        n_lane = 32
        n_bits_all_chiplets = sum(num_bits_nop_eachLayer)
        n_bits_all_chiplets += sum(num_bits_nop_eachLayer_train)
        nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_all_chiplets)

    # utilization and PPA
    static_chiplet_utilization = [(1- x/static_chiplet_size) for x in static_chiplet_availability]
    dynamic_chiplet_utilization = [x / (dynamic_chiplet_size * num_used_dynamic_chiplet) for x in Num_DynamicPE_eachLayer]
    
    Total_Area = 0
    Total_Area += chip_area
    Total_Area += noc_area + nop_driver_area
    Total_Area_mm2 = Total_Area*1e6

    write_latency_input_eachLayer = [layer[0] for layer in performance_each_layer]
    write_energy_input_eachLayer = [layer[1] for layer in performance_each_layer]
    write_latency_weight_eachLayer = [layer[2] for layer in performance_each_layer]
    write_energy_weight_eachLayer = [layer[3] for layer in performance_each_layer]
    read_latency_output_eachLayer = [layer[4] for layer in performance_each_layer]
    read_energy_output_eachLayer = [layer[5] for layer in performance_each_layer]
    refresh_latency_weight_eachLayer = [layer[6] for layer in performance_each_layer]
    refresh_energy_weight_eachLayer = [layer[7] for layer in performance_each_layer]
    
    # get total_latency of eachLayer
    # consider if rram weight write-in is included in for each layer
    total_latency_eachLayer = [0] * len(NetStructure)
    for layer_idx, layer in enumerate(NetStructure):
        total_latency_eachLayer[layer_idx] = write_latency_input_eachLayer[layer_idx] + read_latency_output_eachLayer[layer_idx] + refresh_latency_weight_eachLayer[layer_idx]
        if layer[6] == 1: # dynamic layer, need weight write-in
            total_latency_eachLayer[layer_idx] += write_latency_weight_eachLayer[layer_idx]
    # consider if semi-static layers' edram weight write-in is included in for each layer (by comparing to the latency from src_layer to dest_layer)
    layers_process_latency_eachDestLayer = [0] * len(NetStructure)
    for layer in range(len(NetStructure)):
        for dest_layer_idx in (to_bp_dest_layers[layer]):
            for layer_idx in range(layer,dest_layer_idx):
                layers_process_latency_eachDestLayer[dest_layer_idx] += total_latency_eachLayer[layer_idx]
            if (NetStructure[dest_layer_idx][6] == 2) and (write_latency_weight_eachLayer[dest_layer_idx] > layers_process_latency_eachDestLayer[dest_layer_idx]): # semi_static layer, and need count in weight write-in latency
                total_latency_eachLayer[dest_layer_idx] += write_latency_weight_eachLayer[dest_layer_idx]
    
    # get total_energy of eachLayer
    # consider if rram weight write-in is included in for each layer
    total_energy_eachLayer = [0] * len(NetStructure)
    for layer_idx, layer in enumerate(NetStructure):
        total_energy_eachLayer[layer_idx] = write_energy_input_eachLayer[layer_idx] + read_energy_output_eachLayer[layer_idx] + refresh_energy_weight_eachLayer[layer_idx]
        if (layer[6] == 1) or (layer[6] == 2): # dynamic layer or semi-static layer, need weight write-in
            total_energy_eachLayer[layer_idx] += write_energy_weight_eachLayer[layer_idx]
    
    # get refresh weight energy of each static layer (useful if in edram). and for each semi-static layer, weight refresh energy (stored in edram CIM) or weight leakage energy (stored in edram chip buffer) 
    refresh_retention_time = getattr(config, 'eDRAM' + '_refresh_retention_time')
    static_refresh_energy_weight_eachLayer = [0] * len(NetStructure)
    semi_static_refresh_energy_weight_eachLayer = [0] * len(NetStructure)
    buffer_leak_energy_weight_eachLayer = [0] * len(NetStructure)
    for layer_idx, layer in enumerate(NetStructure):
        if (layer[6] == 0) and (config.static_chiplet_memory_cell_type == 'eDRAM'): # static layer
            num_refresh_times = math.ceil(sum(total_latency_eachLayer) / refresh_retention_time)
            static_refresh_energy_weight_eachLayer[layer_idx] = (layer[2]*layer[3]*config.BitWidth_weight * num_refresh_times) * static_chip_write_energy_per_bit
        elif layer[6] == 2: # semi-static layer
            # option 1: for each semi-static layer, weight refresh energy (stored in edram CIM)
            num_refresh_times = math.ceil(layers_process_latency_eachDestLayer[layer_idx] / refresh_retention_time)
            semi_static_refresh_energy_weight_eachLayer[layer_idx] = (layer[2]*layer[3]*config.BitWidth_weight * num_refresh_times) * semi_static_chip_write_energy_per_bit
            # option 2: for each semi-static layer, weight leakage energy (stored in edram chip buffer)
            buffer = Buffer(config,config.dynamic_chiplet_technode,mem_width=math.ceil(math.log2(layer[2]*config.BitWidth_weight)),mem_height=math.ceil(math.log2(layer[3])))
            buffer_leak_energy_weight_eachLayer[layer_idx] = layers_process_latency_eachDestLayer[layer_idx] * buffer.get_leak_power()
    
    total_write_latency_input = sum(write_latency_input_eachLayer)
    total_write_energy_input = sum(write_energy_input_eachLayer)
    total_write_latency_weight = sum(write_latency_weight_eachLayer)
    total_write_energy_weight = sum(write_energy_weight_eachLayer)
    total_read_latency_output = sum(read_latency_output_eachLayer)
    total_read_energy_output = sum(read_energy_output_eachLayer)
    total_refresh_latency_weight = sum(refresh_latency_weight_eachLayer)
    total_refresh_energy_weight = sum(refresh_energy_weight_eachLayer)

    total_latency = sum(total_latency_eachLayer)
    total_energy = sum(total_energy_eachLayer)
    total_static_refresh_energy_weight = sum(static_refresh_energy_weight_eachLayer)
    total_semi_static_refresh_energy_weight = sum(semi_static_refresh_energy_weight_eachLayer)
    total_buffer_leak_energy_weight = sum(buffer_leak_energy_weight_eachLayer)
    
    Total_Energy = 0
    Total_Energy += total_energy + total_static_refresh_energy_weight
    Total_Energy += noc_energy + noc_energy_train
    Total_Energy += nop_driver_energy
    Total_Energy_opt_1 = Total_Energy + total_semi_static_refresh_energy_weight
    Total_Energy_opt_2 = Total_Energy + total_buffer_leak_energy_weight

    Total_Latency = 0
    Total_Latency += total_latency
    Total_Latency += noc_latency + noc_latency_train
    Total_Latency += nop_latency + nop_latency_train
    
    Total_tops = Total_top_num / Total_Latency

    Energy_Efficiency_opt_1 = Total_top_num / Total_Energy_opt_1
    Energy_Efficiency_Per_Area_opt_1 = Energy_Efficiency_opt_1 / Total_Area_mm2

    Energy_Efficiency_opt_2 = Total_top_num / Total_Energy_opt_2
    Energy_Efficiency_Per_Area_opt_2 = Energy_Efficiency_opt_2 / Total_Area_mm2

    print("==========================================")
    print("Integration_dimension:",config.Packaging_dimension)
    print("===== Total =====")
    print("Total TOP num:",Total_top_num)
    print("Total Area (mm2):",Total_Area_mm2)
    print("Total Latency (s) -- w/o NoC,NoP:",total_latency)
    print("Total Latency (s) -- w/ NoC,NoP:",Total_Latency)
    print("Performance (TOPS):",Total_tops)
    print("total_static_refresh_energy_weight (static weight store in eDRAN CIM):",total_static_refresh_energy_weight)
    print("===== option1: refresh eDRAM =====")
    print("Total Energy (J) -- option1: refresh eDRAM:",Total_Energy_opt_1)
    print("Total refresh bp weight Energy (J) -- refresh_energy store bp changing weight:",total_semi_static_refresh_energy_weight)
    print("Energy Efficiency (TOPS/W) -- option1: refresh eDRAM:", Energy_Efficiency_opt_1)
    print("Energy Efficiency Per Area (TOPS/W/mm2) -- option1: refresh eDRAM:", Energy_Efficiency_Per_Area_opt_1)

    print("===== option2: SRAM leak =====")
    print("Total Energy (J) -- option2: SRAM leak :",Total_Energy_opt_2)
    print("Total Leak Energy (J) -- buffer_leak_energy store bp changing weight:",total_buffer_leak_energy_weight)
    print("Energy Efficiency (TOPS/W) -- option2: refresh eDRAM:", Energy_Efficiency_opt_2)
    print("Energy Efficiency Per Area (TOPS/W/mm2) -- option2: refresh eDRAM:", Energy_Efficiency_Per_Area_opt_2)

    print("===== Breakdown =====")
    print("Num used Static Chiplets (static and semi-static):", num_used_static_chiplet_all_layers)
    print("Num used Dynamic Chiplets:", num_used_dynamic_chiplet)
    
    print("static chiplet utilization:", static_chiplet_utilization) # for each static-chiplet, ?% pe used 
    print("dynamic chiplet utilization:", dynamic_chiplet_utilization) # for each dynamic-layer, ?% pe used  in all dynamic chiplets
    
    print("total_write_latency_input:",total_write_latency_input)
    print("total_write_latency_weight:",total_write_latency_weight)
    print("total_read_latency_output:",total_read_latency_output)
    print("total_refresh_latency_weight:",total_refresh_latency_weight)
    
    print("total_write_energy_input:",total_write_energy_input)
    print("total_write_energy_weight:",total_write_energy_weight)
    print("total_read_energy_output:",total_read_energy_output)
    print("total_refresh_energy_weight:",total_refresh_energy_weight)
    
    
    print(f"NOC Area: {noc_area}, NOC Latency: {noc_latency}, NOC Energy: {noc_energy}")
    print(f"NOC Area (for train): {noc_area_train}, NOC Latency (for train): {noc_latency_train}, NOC Energy (for train): {noc_energy_train}")
    print(f"NOP Area: {nop_area}, NOP Latency: {nop_latency}, NOP Energy: {nop_energy}")
    print(f"NOP Area (for train): {nop_area_train}, NOP Latency (for train): {nop_latency_train}, NOP Energy (for train): {nop_energy_train}")
    print(f"NOP driver Area: {nop_driver_area}, NOP driver Energy: {nop_driver_energy}")
    
    print("==========================================")

if __name__ == "__main__":
    config = Config()
    main(config)