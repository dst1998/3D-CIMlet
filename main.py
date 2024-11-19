import math

from config import Config
from chiplet_layer_range import *
from layer_mapping import get_layer_energy_latency
from peripheral import *
from Interconnect.noc_estimation import interconnect_estimation
from Interconnect.nop_estimation import *
from Interconnect.NoP_hardware import NoP_hardware_estimation
from integration import *

def main(config):
    
    NetStructure = config.load_model()
    NetStructure_layer_def  = config.load_model_layer_def()
    # print("layerdef:",NetStructure_layer_def)
    static_chiplet_size = config.static_chiplet_size
    dynamic_chiplet_size = config.dynamic_chiplet_size
    
    # get static/dynamic layer dataflow
    # initialize PPA
    Total_Latency = 0
    Total_Area = 0
    Total_top_num = 0

    Num_StaticSubArray_eachLayer = []
    Num_DynamicSubArray_eachLayer = []
    Num_StaticPE_eachLayer = []
    Num_DynamicPE_eachLayer = []
    performance_each_layer = []
    tops_eachLayer = [0] * len(NetStructure)

    # get TOPS of this layer
    for layer_idx, layer in enumerate(NetStructure):
        tops_eachLayer[layer_idx] = layer[0]*layer[1]*layer[3] *2 *1e-12
        Total_top_num += tops_eachLayer[layer_idx]

    # breakdown value #####################

    buffer_bw = 9e9 # SRAM-2D:9Gb/s=1.125GB/s
    buffer_dynamicEnergy = 17.5e-15 * 40/65  # [depends on tech] unit:J/read or J/write, SRAM-2D-65nm:17.5fJ/bit=140fJ/byte
    
    ##########################################
    
    num_static_chiplet_eachLayer = []
    num_dynamic_chiplet_eachLayer = []
    # get num of used static subarray/PE or used dynamic subarray/PE of each model layer
    # get dynamic power and latency
    for layer_index, row in enumerate(NetStructure):
        # get this layer operation is static or dynamic
        if row[6]== 0: # is static layer
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer, static_chip_write_energy_per_bit = get_layer_energy_latency(row,config,config.static_chiplet_technode,chiplet_type='static_0',memory_cell_type=config.static_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(num_used_chiplet_this_layer)
            num_dynamic_chiplet_eachLayer.append(0)

            Num_StaticPE_eachLayer.append(num_used_pe_this_layer)
            Num_DynamicPE_eachLayer.append(0)

            Num_StaticSubArray_eachLayer.append(num_used_subarray_this_layer)
            Num_DynamicSubArray_eachLayer.append(0)
        elif row[6]== 1: # is dynamic layer
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer, dynamic_chip_write_energy_per_bit= get_layer_energy_latency(row,config,config.static_chiplet_technode,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(0)
            num_dynamic_chiplet_eachLayer.append(num_used_chiplet_this_layer)
            # print("layer :",layer_index)
            # print("num_used_dynamic_chiplet_this_layer",num_used_chiplet_this_layer)

            Num_StaticPE_eachLayer.append(0)
            Num_DynamicPE_eachLayer.append(num_used_pe_this_layer)

            Num_StaticSubArray_eachLayer.append(0)
            Num_DynamicSubArray_eachLayer.append(num_used_subarray_this_layer)
        elif row[6]== 2: # is semi-static layer. (In this layer, weight need to stay static for some time but not forever)
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer, semi_static_chip_write_energy_per_bit = get_layer_energy_latency(row,config,config.dynamic_chiplet_technode,chiplet_type='static_2',memory_cell_type=config.dynamic_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(num_used_chiplet_this_layer)
            num_dynamic_chiplet_eachLayer.append(0)

            Num_StaticPE_eachLayer.append(num_used_pe_this_layer)
            Num_DynamicPE_eachLayer.append(0)

            Num_StaticSubArray_eachLayer.append(num_used_subarray_this_layer)
            Num_DynamicSubArray_eachLayer.append(0)

        # print("num_dynamic_chiplet_eachLayer:",num_dynamic_chiplet_eachLayer)
        num_used_dynamic_chiplet = max(num_dynamic_chiplet_eachLayer)
        num_chiplet_eachLayer = [a + b for a, b in zip(num_static_chiplet_eachLayer, num_dynamic_chiplet_eachLayer)]

        # TODO: add [weight] [write latency and energy], global buffer to each chiplet (chiplet-to-chiplet).
        # TODO: for first layer, add the [input] [write latency and energy] , global buffer to first chiplet (chiplet-to-chiplet).
        # TODO: for last layer, add the [output] [write latency and energy] , last chiplet to global buffer(chiplet-to-chiplet).
        # TODO: add [weight] in static chip [refresh latency and energy] based on below (all-layer latency) and noc,nop latency:
        performance_each_layer.append(performance_this_layer)



    # get location in chiplet for each model static layer (layer?: pe?~pe? in chiplet?)
    dest_layers, to_bp_dest_layers, num_to_bp_transfer_byte_to_layer = get_dest_layers(config,NetStructure,NetStructure_layer_def)
    
    # print("dest_layers:",dest_layers)
    # print("to_bp_dest_layers:",to_bp_dest_layers)
    
    static_chiplet_layers, static_chiplet_availability, num_used_static_chiplet_all_layers,num_used_static_chiplet,num_used_semi_static_chiplet,chiplet_static_type,layer_location_begin_chiplet = get_static_chiplet_layers(config,NetStructure,NetStructure_layer_def,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer)

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



    # Integrate in 2D/2.5D/3D
    if config.Packaging_dimension == 2:
        Integration = Integration2D(config,maxnum_layer_in_bit,num_used_static_chiplet,num_used_semi_static_chiplet,num_used_dynamic_chiplet)
        # get chip area
        chip_area = Integration.CalculateArea()
        # NoC Estimation
        noc_area, noc_latency, noc_energy = 0,0,0
        noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        
        noc_train_area, noc_train_latency, noc_train_energy = 0,0,0
        if "inf" not in config.net_name:
            noc_train_area, noc_train_latency, noc_train_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, num_to_bp_transfer_byte_to_layer, static_chiplet_layers, to_bp_dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        
        # NoP Estimation
        nop_area, nop_latency, nop_energy = 0,0,0
        nop_num_bits_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        nop_latencyCycle_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        nop_area, nop_latency, nop_energy, nop_num_bits_eachLayer,nop_latencyCycle_eachLayer = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size, config.nop_clk_freq_2d)
        
        # get static_dynamic_chip-to-chip_nop_cycles and latency when rram+edram on same chip 
        total_exclude_static_dynamic_nop_cycles = 0
        for src_layer in range(len(nop_latencyCycle_eachLayer)):
            for dest_layer in range(len(nop_latencyCycle_eachLayer)):
                if (NetStructure[src_layer][6] == 1 and NetStructure[dest_layer][6] != 1) or (NetStructure[src_layer][6] != 1 and NetStructure[dest_layer][6] == 1):
                    total_exclude_static_dynamic_nop_cycles += nop_latencyCycle_eachLayer[src_layer][dest_layer]
        total_exclude_static_dynamic_nop_latency = total_exclude_static_dynamic_nop_cycles / config.nop_clk_freq_2d
        total_exclude_static_dynamic_nop_energy = total_exclude_static_dynamic_nop_latency / nop_latency * nop_energy
        print("# nop_latency:",nop_latency)
        print("# nop_energy:",nop_energy)
        print("# total_exclude_static_dynamic_nop_latency:",total_exclude_static_dynamic_nop_latency, "s")
        print("# total_exclude_static_dynamic_nop_energy:",total_exclude_static_dynamic_nop_energy, "J")
        
        nop_train_area, nop_train_latency, nop_train_energy= 0,0,0
        nop_num_bits_train_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        nop_latencyCycle_train_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        if "inf" not in config.net_name:
            nop_train_area, nop_train_latency, nop_train_energy, nop_num_bits_train_eachLayer, nop_latencyCycle_train_eachLayer = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, to_bp_dest_layers, layer_location_begin_chiplet, num_to_bp_transfer_byte_to_layer, config.net_name, config.static_chiplet_size,config.nop_clk_freq_2d)
            # print("# nop_train_latency:",nop_train_latency)
            # print("# nop_latencyCycle_train_eachLayer sum:",sum(sum(row) for row in nop_latencyCycle_train_eachLayer), "cycles","cycles")
        
            # get static_dynamic_chip-to-chip_nop_cycles and latency when rram+edram on same chip 
            total_exclude_static_dynamic_nop_train_cycles = 0
            for src_layer in range(len(nop_latencyCycle_train_eachLayer)):
                for dest_layer in range(len(nop_latencyCycle_train_eachLayer)):
                    if (NetStructure[src_layer][6] == 1 and NetStructure[dest_layer][6] != 1) or (NetStructure[src_layer][6] != 1 and NetStructure[dest_layer][6] == 1):
                        total_exclude_static_dynamic_nop_train_cycles += nop_latencyCycle_train_eachLayer[src_layer][dest_layer]
            total_exclude_static_dynamic_nop_train_latency = total_exclude_static_dynamic_nop_train_cycles / config.nop_clk_freq_2d
            total_exclude_static_dynamic_nop_train_energy = total_exclude_static_dynamic_nop_train_latency / nop_train_latency * nop_train_energy
            print("# nop_train_latency:",nop_train_latency)
            print("# nop_train_energy:",nop_train_energy)
            print("# total_exclude_static_dynamic_nop_train_latency:",total_exclude_static_dynamic_nop_train_latency, "s")
            print("# total_exclude_static_dynamic_nop_train_energy:",total_exclude_static_dynamic_nop_train_energy, "J")

        nop_driver_area, nop_driver_energy = 0,0
        
        # NoP Hardware Cost (Nop_area:m2, NoP_energy:J)
        # 2D NoP Driver
        ebit = 6.6e-12
        area_per_lane = 0.33E-6
        clocking_area = 0
        n_lane = 1
        n_bits_all_chiplets = sum(sum(row) for row in nop_num_bits_eachLayer)
        n_bits_all_chiplets += sum(sum(row) for row in nop_num_bits_train_eachLayer)
        nop_driver_area, nop_driver_energy = NoP_hardware_estimation(config, ebit, area_per_lane, clocking_area, n_lane, num_used_static_chiplet,num_used_semi_static_chiplet, num_used_dynamic_chiplet, n_bits_all_chiplets)

    elif config.Packaging_dimension == 2.5:
        Integration = Integration2_5D(config,maxnum_layer_in_bit,num_used_static_chiplet,num_used_semi_static_chiplet,num_used_dynamic_chiplet)
        
        # get chip area and get nop freq
        chip_area = Integration.CalculateArea()
        # min_memory_chip_area_mm2 = Integration.min_memory_chip_area * 1e6
        # print("min_memory_chip_area_mm2: ", min_memory_chip_area_mm2)
        # num_pin = Integration.min_memory_chip_area / math.pow(config.pitch_size_2_5d, 2)
        # print("num_pin: ", num_pin)
        # nop_clk_freq = num_pin * config.nop_clk_freq_2_5d_3d
        
        nop_clk_freq = config.nop_clk_freq_2_5d
        
        
        # NoC Estimation
        noc_area, noc_latency, noc_energy = 0,0,0
        noc_train_area, noc_train_latency, noc_train_energy = 0,0,0
        
        # noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        
        # if "inf" not in config.net_name:
        #     noc_train_area, noc_train_latency, noc_train_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, num_to_bp_transfer_byte_to_layer, static_chiplet_layers, to_bp_dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        
        # NoP Estimation
        nop_area, nop_latency, nop_energy= 0,0,0
        nop_num_bits_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        nop_latencyCycle_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        nop_area, nop_latency, nop_energy, nop_num_bits_eachLayer,nop_latencyCycle_eachLayer = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size, nop_clk_freq)
        
        print("# nop_latencyCycle_eachLayer sum:",sum(sum(row) for row in nop_latencyCycle_eachLayer), "cycles")
        
        # get static_dynamic_chip-to-chip_nop_cycles and latency when rram+edram on same chip 
        total_exclude_static_dynamic_nop_cycles = 0
        for src_layer in range(len(nop_latencyCycle_eachLayer)):
            for dest_layer in range(len(nop_latencyCycle_eachLayer)):
                if (NetStructure[src_layer][6] == 1 and NetStructure[dest_layer][6] != 1) or (NetStructure[src_layer][6] != 1 and NetStructure[dest_layer][6] == 1):
                    # print("")
                    # print("exclude_src_layer :",src_layer)
                    # print("exclude_dest_layer :",dest_layer)
                    # print("nop_latencyCycle :",nop_latencyCycle_eachLayer[src_layer][dest_layer])
                    total_exclude_static_dynamic_nop_cycles += nop_latencyCycle_eachLayer[src_layer][dest_layer]
        total_exclude_static_dynamic_nop_latency = total_exclude_static_dynamic_nop_cycles / nop_clk_freq
        total_exclude_static_dynamic_nop_energy = total_exclude_static_dynamic_nop_latency / nop_latency * nop_energy
        print("# nop_latency:",nop_latency)
        print("# nop_energy:",nop_energy)
        print("# total_exclude_static_dynamic_nop_latency:",total_exclude_static_dynamic_nop_latency, "s")
        print("# total_exclude_static_dynamic_nop_energy:",total_exclude_static_dynamic_nop_energy, "J")
        
        nop_train_area, nop_train_latency, nop_train_energy= 0,0,0
        nop_num_bits_train_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        nop_latencyCycle_train_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        # if "inf" not in config.net_name:
        #     nop_train_area, nop_train_latency, nop_train_energy, nop_num_bits_train_eachLayer,nop_latencyCycle_train_eachLayer = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, to_bp_dest_layers, layer_location_begin_chiplet, num_to_bp_transfer_byte_to_layer, config.net_name, config.static_chiplet_size,nop_clk_freq)
            
        #     # print("# nop_train_latency:",nop_train_latency)
        #     # print("# nop_latencyCycle_train_eachLayer sum:",sum(sum(row) for row in nop_latencyCycle_train_eachLayer), "cycles","cycles")
        
        #     # get static_dynamic_chip-to-chip_nop_cycles and latency when rram+edram on same chip 
        #     total_exclude_static_dynamic_nop_train_cycles = 0
        #     for src_layer in range(len(nop_latencyCycle_train_eachLayer)):
        #         for dest_layer in range(len(nop_latencyCycle_train_eachLayer)):
        #             if (NetStructure[src_layer][6] == 1 and NetStructure[dest_layer][6] != 1) or (NetStructure[src_layer][6] != 1 and NetStructure[dest_layer][6] == 1):
        #                 total_exclude_static_dynamic_nop_train_cycles += nop_latencyCycle_train_eachLayer[src_layer][dest_layer]
        #     total_exclude_static_dynamic_nop_train_latency = total_exclude_static_dynamic_nop_train_cycles / nop_clk_freq
        #     total_exclude_static_dynamic_nop_train_energy = total_exclude_static_dynamic_nop_train_latency / nop_train_latency * nop_train_energy
        #     print("# nop_train_latency:",nop_train_latency)
        #     print("# nop_train_energy:",nop_train_energy)
        #     print("# total_exclude_static_dynamic_nop_train_latency:",total_exclude_static_dynamic_nop_train_latency, "s")
        #     print("# total_exclude_static_dynamic_nop_train_energy:",total_exclude_static_dynamic_nop_train_energy, "J")

        nop_driver_area, nop_driver_energy = 0,0
        # NoP Hardware Cost (Nop_area:m2, NoP_energy:J)
        
        ebit = 0.26e-12
        area_per_lane_28nm = 463.5 * 206 * 1E-12 / 16
        clocking_area = 0
        n_lane = 4
        n_bits_all_chiplets = sum(sum(row) for row in nop_num_bits_eachLayer)
        n_bits_all_chiplets += sum(sum(row) for row in nop_num_bits_train_eachLayer)
        nop_driver_area, nop_driver_energy = NoP_hardware_estimation(config,ebit, area_per_lane_28nm, clocking_area, n_lane, num_used_static_chiplet,num_used_semi_static_chiplet,num_used_dynamic_chiplet, n_bits_all_chiplets)

        print("nop_driver_energy",nop_driver_energy)
        
        # # SIAM: - Extracted from GRS Nvidia
        # ebit = 0.58e-12
        # area_per_lane = 5304.5e-12 # 5304.5 um2
        # clocking_area = 10609e-12 # 10609 um2
        # n_lane = 32
        # n_bits_all_chiplets = sum(sum(row) for row in nop_num_bits_eachLayer)
        # n_bits_all_chiplets += sum(sum(row) for row in nop_num_bits_train_eachLayer)
        # nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_all_chiplets)
        
        # # # CoWoS
        # ebit = 0.56e-12
        # area_per_lane = 0 # config.chiplet_bus_width_2D * (45e-6*45e-6)
        # clocking_area = 0
        # n_lane = 1
        # n_bits_all_chiplets = sum(sum(row) for row in nop_num_bits_eachLayer)
        # n_bits_all_chiplets += sum(sum(row) for row in nop_num_bits_train_eachLayer)
        # nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_all_chiplets)

    else: # H3D
        Integration = Integration3D(config,maxnum_layer_in_bit)
        #get chip area
        chip_area = Integration.CalculateArea()
        total_tsv_area_mm2 =  Integration.total_tsv_area * 1e06
        print("total_tsv_area_mm2: ", total_tsv_area_mm2)
        num_pin = Integration.num_tsv
        print("num_pin: ", num_pin)
        nop_clk_freq = config.nop_clk_freq_3d
        
        # NoC Estimation
        noc_area, noc_latency, noc_energy = 0,0,0
        noc_train_area, noc_train_latency, noc_train_energy = 0,0,0

        # noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        noc_area /= num_used_chiplets
        
        # if "inf" not in config.net_name:
        #     noc_train_area, noc_train_latency, noc_train_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, chiplet_static_type, Num_StaticPE_eachLayer, num_to_bp_transfer_byte_to_layer, static_chiplet_layers, to_bp_dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        #     noc_train_area /= num_used_chiplets
        
        # NoP Estimation
        nop_area, nop_latency, nop_energy = 0,0,0
        nop_num_bits_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        num_bits_src_chip_to_dest_chip = [[0] * num_used_chiplets for _ in range(num_used_chiplets)]
        num_bits_src_chip_to_dest_chip_for_energy = [[0] * num_used_chiplets for _ in range(num_used_chiplets)]
        num_cycle_src_chip_to_dest_chip_for_latency = [[0] * num_used_chiplets for _ in range(num_used_chiplets)]
        ebit = config.ebit_3d # 0.015e-12
        
        nop_num_bits_eachLayer, num_bits_src_chip_to_dest_chip = generate_chip2chip_num_bit(config, num_used_chiplets, num_used_static_chiplet_all_layers, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer)
        
        #=============================================
        chip_list = list(range(num_used_chiplets))
        # Separate the last n items
        last_n_items = chip_list[-num_used_dynamic_chiplet:]
        # The remaining part of the list after removing the last n items
        remaining_chip_list = chip_list[:-num_used_dynamic_chiplet]
        # Calculate the middle index of the remaining list
        middle_index = len(remaining_chip_list) // 2
        
        # Insert the last n items into the middle
        new_chip_list = remaining_chip_list[:middle_index] + last_n_items + remaining_chip_list[middle_index:]
        print("new_chip_list:",new_chip_list)
        # print("new_chip_list.index(18):",new_chip_list.index(18))
        # print("new_chip_list.index(9):",new_chip_list.index(9))

        for i in range(len(num_bits_src_chip_to_dest_chip)):
            for j in range(len(num_bits_src_chip_to_dest_chip[i])):
                # num_bits_src_chip_to_dest_chip_ordered[i][j] = num_bits_src_chip_to_dest_chip[i][j] * abs(i - j) # need change, if change chip-chip distance
                
                # if num_bits_src_chip_to_dest_chip[i][j] !=0:
                    # print("")
                    # print("exclude_src_chip_idx :",i)
                    # print("exclude_dest_chip_idx :",j)
                    # print("nop_bits :",num_bits_src_chip_to_dest_chip[i][j])
                    
                pos_i = new_chip_list.index(i)
                pos_j = new_chip_list.index(j)
                num_bits_src_chip_to_dest_chip_for_energy[i][j] = num_bits_src_chip_to_dest_chip[i][j] * abs(pos_j - pos_i) - 1
                
                num_batch = math.ceil(num_bits_src_chip_to_dest_chip[i][j] / num_pin)
                if num_batch != 0:
                    num_cycle_src_chip_to_dest_chip_for_latency[i][j] = (num_batch + (abs(pos_j - pos_i) - 1))/num_batch
        weighted_num_bits_src_chip_to_dest_chip = sum(sum(row) for row in num_bits_src_chip_to_dest_chip_for_energy)
        weighted_num_cycles_src_chip_to_dest_chip = sum(sum(row) for row in num_cycle_src_chip_to_dest_chip_for_latency)
        
        nop_energy = weighted_num_bits_src_chip_to_dest_chip * ebit
        nop_latency = weighted_num_cycles_src_chip_to_dest_chip * (1 / nop_clk_freq)
        #=============================================
        #=============================================
        total_exclude_static_dynamic_nop_bits = 0
        total_exclude_static_dynamic_nop_cycles = 0
        for src_chip_idx in range(len(num_bits_src_chip_to_dest_chip)):
            for dest_chip_idx in range(len(num_bits_src_chip_to_dest_chip[src_chip_idx])):
                if (src_chip_idx < num_used_static_chiplet_all_layers and dest_chip_idx >= num_used_static_chiplet_all_layers) or (src_chip_idx >= num_used_static_chiplet_all_layers and dest_chip_idx < num_used_static_chiplet_all_layers):
                    # print("")
                    # print("exclude_src_chip_idx :",src_chip_idx)
                    # print("exclude_dest_chip_idx :",dest_chip_idx)
                    # print("nop_bits :",num_bits_src_chip_to_dest_chip[src_chip_idx][dest_chip_idx])
                    total_exclude_static_dynamic_nop_bits += num_bits_src_chip_to_dest_chip[src_chip_idx][dest_chip_idx]
                    total_exclude_static_dynamic_nop_cycles += num_cycle_src_chip_to_dest_chip_for_latency[src_chip_idx][dest_chip_idx]
        total_exclude_static_dynamic_nop_latency = total_exclude_static_dynamic_nop_cycles / nop_clk_freq
        total_exclude_static_dynamic_nop_energy = total_exclude_static_dynamic_nop_bits * ebit
        print("# nop_latency:",nop_latency)
        print("# nop_energy:",nop_energy)
        print("# total_exclude_static_dynamic_nop_latency:",total_exclude_static_dynamic_nop_latency, "s")
        print("# total_exclude_static_dynamic_nop_energy:",total_exclude_static_dynamic_nop_energy, "J")
        #=============================================
        
        nop_train_area, nop_train_latency, nop_train_energy= 0,0,0
        nop_num_bits_train_eachLayer = [[0] * len(NetStructure) for _ in range(len(NetStructure))]
        num_train_bits_src_chip_to_dest_chip = [[0] * num_used_chiplets for _ in range(num_used_chiplets)]
        num_train_bits_src_chip_to_dest_chip_for_energy = [[0] * num_used_chiplets for _ in range(num_used_chiplets)]
        num_train_cycle_src_chip_to_dest_chip_for_latency = [[0] * num_used_chiplets for _ in range(num_used_chiplets)]
        if "inf" not in config.net_name:
            nop_num_train_bits_eachLayer, num_train_bits_src_chip_to_dest_chip = generate_chip2chip_num_bit(config, num_used_chiplets, num_used_static_chiplet_all_layers, num_chiplet_eachLayer, to_bp_dest_layers, layer_location_begin_chiplet, num_to_bp_transfer_byte_to_layer)
            
            #=============================================
            for i in range(len(num_train_bits_src_chip_to_dest_chip)):
                for j in range(len(num_train_bits_src_chip_to_dest_chip[i])):
                    # num_train_bits_src_chip_to_dest_chip_ordered[i][j] = num_train_bits_src_chip_to_dest_chip[i][j] * abs(i - j) # need change, if change chip-chip distance # need change, add chip-chip distance

                    pos_i = new_chip_list.index(i)
                    pos_j = new_chip_list.index(j)
                    num_train_bits_src_chip_to_dest_chip_for_energy[i][j] = num_train_bits_src_chip_to_dest_chip[i][j] * abs(pos_j - pos_i) - 1
                    
                    num_batch = math.ceil(num_train_bits_src_chip_to_dest_chip[i][j] / num_pin)
                    if num_batch != 0:
                        num_train_cycle_src_chip_to_dest_chip_for_latency[i][j] = (num_batch + (abs(pos_j - pos_i) - 1))/num_batch

            weighted_num_train_bits_src_chip_to_dest_chip = sum(sum(row) for row in num_train_bits_src_chip_to_dest_chip_for_energy)
            weighted_num_train_cycles_src_chip_to_dest_chip = sum(sum(row) for row in num_train_cycle_src_chip_to_dest_chip_for_latency)
            
            nop_train_energy = weighted_num_train_bits_src_chip_to_dest_chip * ebit
            nop_train_latency = weighted_num_train_cycles_src_chip_to_dest_chip * (1 / nop_clk_freq)
            #=============================================
            #=============================================
            total_exclude_static_dynamic_nop_train_bits = 0
            total_exclude_static_dynamic_nop_train_cycles = 0
            for src_chip_idx in range(len(num_train_bits_src_chip_to_dest_chip)):
                for dest_chip_idx in range(len(num_train_bits_src_chip_to_dest_chip[src_chip_idx])):
                    if (src_chip_idx < num_used_static_chiplet_all_layers and dest_chip_idx >= num_used_static_chiplet_all_layers) or (src_chip_idx >= num_used_static_chiplet_all_layers and dest_chip_idx < num_used_static_chiplet_all_layers):
                        total_exclude_static_dynamic_nop_train_bits += num_train_bits_src_chip_to_dest_chip[src_chip_idx][dest_chip_idx]
                        total_exclude_static_dynamic_nop_train_cycles += num_train_cycle_src_chip_to_dest_chip_for_latency[src_chip_idx][dest_chip_idx]
            total_exclude_static_dynamic_nop_train_latency = total_exclude_static_dynamic_nop_train_cycles / nop_clk_freq
            total_exclude_static_dynamic_nop_train_energy = total_exclude_static_dynamic_nop_train_bits * ebit
            print("# nop_train_latency:",nop_train_latency)
            print("# nop_train_energy:",nop_train_energy)
            print("# total_exclude_static_dynamic_nop_train_latency:",total_exclude_static_dynamic_nop_train_latency, "s")
            print("# total_exclude_static_dynamic_nop_train_energy:",total_exclude_static_dynamic_nop_train_energy, "J")
            #=============================================
        
        n_bits_all_chiplets = sum(sum(row) for row in nop_num_bits_eachLayer)
        n_bits_all_chiplets += sum(sum(row) for row in nop_num_bits_train_eachLayer)
        print("n_bits_all_chiplets :",n_bits_all_chiplets)
        
        nop_driver_area, nop_driver_energy = 0,0
        # NoP Hardware Cost (Nop_area:m2, NoP_energy:J)

        # # 3D SoIC F2B (SoIC bond & TSV)
        # ebit = 0.015e-12
        # area_per_lane = 0
        # clocking_area = 0
        # n_lane = 1
        # n_bits_all_chiplets = sum(sum(row) for row in nop_num_bits_eachLayer)
        # n_bits_all_chiplets += sum(sum(row) for row in nop_num_bits_train_eachLayer)
        # nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_all_chiplets)

    # utilization and PPA
    static_chiplet_utilization = [(1- x/static_chiplet_size) for x in static_chiplet_availability]
    dynamic_chiplet_utilization = [x / (dynamic_chiplet_size * num_used_dynamic_chiplet) for x in Num_DynamicPE_eachLayer]
    
    Total_Area = 0
    Total_Area += chip_area
    Total_Area += noc_area + nop_area
    Total_Area_mm2 = Total_Area*1e6

    chip_area_mm2 = chip_area*1e6

    write_latency_input_eachLayer = [layer[0] for layer in performance_each_layer]
    write_energy_input_eachLayer = [layer[1] for layer in performance_each_layer]
    write_latency_weight_eachLayer = [layer[2] for layer in performance_each_layer]
    write_energy_weight_eachLayer = [layer[3] for layer in performance_each_layer]
    read_latency_output_eachLayer = [layer[4] for layer in performance_each_layer]
    read_energy_output_eachLayer = [layer[5] for layer in performance_each_layer]
    refresh_latency_weight_eachLayer = [layer[6] for layer in performance_each_layer]
    refresh_energy_weight_eachLayer = [layer[7] for layer in performance_each_layer]
    # -----htree breakdown
    write_latency_input_peHtree_eachLayer = [layer[8] for layer in performance_each_layer]
    write_energy_input_peHtree_eachLayer = [layer[9] for layer in performance_each_layer]
    write_latency_weight_peHtree_eachLayer = [layer[10] for layer in performance_each_layer]
    write_energy_weight_peHtree_eachLayer = [layer[11] for layer in performance_each_layer]
    read_latency_output_peHtree_eachLayer = [layer[12] for layer in performance_each_layer]
    read_energy_output_peHtree_eachLayer = [layer[13] for layer in performance_each_layer]
    
    # get total_latency of eachLayer
    # consider if rram weight write-in is included in for each layer
    total_latency_eachLayer = [0] * len(NetStructure)
    for layer_idx, layer in enumerate(NetStructure):
        total_latency_eachLayer[layer_idx] = write_latency_input_eachLayer[layer_idx] + read_latency_output_eachLayer[layer_idx] + refresh_latency_weight_eachLayer[layer_idx]
        # add htree latency
        total_latency_eachLayer[layer_idx] += write_latency_input_peHtree_eachLayer[layer_idx] + read_latency_output_peHtree_eachLayer[layer_idx]
        if layer_idx == 329 or layer_idx == 360:
            print("layer:",layer_idx)
            print("write_latency_input:",write_latency_input_eachLayer[layer_idx])
            print("read_latency_output:",read_latency_output_eachLayer[layer_idx])
            print("refresh_latency_weight:",refresh_latency_weight_eachLayer[layer_idx])
            print("write_latency_input_peHtree:",write_latency_input_peHtree_eachLayer[layer_idx])
            print("read_latency_output_peHtree:",read_latency_output_peHtree_eachLayer[layer_idx])



        if layer[6] == 1: # dynamic layer, need weight write-in (no matter edram or rram for dynamic or semi-static op)
            total_latency_eachLayer[layer_idx] += write_latency_weight_eachLayer[layer_idx]
        # if (layer[6] == 0) and (config.static_chiplet_memory_cell_type == 'eDRAM'): # static layer, need weight write-in (only when eDRAM for static layer)
        #     total_latency_eachLayer[layer_idx] += write_latency_weight_eachLayer[layer_idx]
    
    # consider if semi-static layers' edram weight write-in is included in for each layer (by comparing to the latency from src_layer to dest_layer)
    layers_process_latency_eachDestLayer = [0] * len(NetStructure)
    for layer in range(len(NetStructure)):
        for dest_layer_idx in (to_bp_dest_layers[layer]):
            for layer_idx in range(layer,dest_layer_idx):
                layers_process_latency_eachDestLayer[dest_layer_idx] += total_latency_eachLayer[layer_idx]

            # count in waiting latency in a iteration of multi-batch. weight update once per iteration.
            layers_process_latency_eachDestLayer[dest_layer_idx] += (config.train_batch_size - 1) * total_latency_eachLayer[0]

            # semi_static layer, and need count in weight write-in latency
            if (NetStructure[dest_layer_idx][6] == 2) and (write_latency_weight_eachLayer[dest_layer_idx] > layers_process_latency_eachDestLayer[dest_layer_idx]): 
                total_latency_eachLayer[dest_layer_idx] += write_latency_weight_eachLayer[dest_layer_idx]
    # print("layers_process_latency_eachDestLayer :",layers_process_latency_eachDestLayer)
    
    # get total_energy of eachLayer
    # consider if rram weight write-in is included in for each layer
    total_energy_eachLayer = [0] * len(NetStructure)
    for layer_idx, layer in enumerate(NetStructure):
        total_energy_eachLayer[layer_idx] = write_energy_input_eachLayer[layer_idx] + read_energy_output_eachLayer[layer_idx] + refresh_energy_weight_eachLayer[layer_idx]
        if layer_idx == 329 or layer_idx == 360:
            print("layer:",layer_idx)
            print("write_energy_input:",write_energy_input_eachLayer[layer_idx])
            print("read_energy_output:",read_energy_output_eachLayer[layer_idx])
            print("refresh_energy_weight:",refresh_energy_weight_eachLayer[layer_idx])
            print("read_energy_output_peHtree:",read_energy_output_peHtree_eachLayer[layer_idx])
            # print("refresh_energy_weight:",refresh_energy_weight_eachLayer[layer_idx])
        
        if (layer[6] == 1) or (layer[6] == 2): # dynamic layer or semi-static layer, need weight write-in (no matter edram or rram for dynamic or semi-static op)
            total_energy_eachLayer[layer_idx] += write_energy_weight_eachLayer[layer_idx]
        # if (layer[6] == 0) and (config.static_chiplet_memory_cell_type == 'eDRAM'): # static layer, need weight write-in (only when eDRAM for static layer)
        #     total_energy_eachLayer[layer_idx] += write_energy_weight_eachLayer[layer_idx]
        
    
    # total_latency = sum(total_latency_eachLayer)
    
    # get refresh weight energy of each static layer (useful if in edram). and for each semi-static layer, weight refresh energy (stored in edram CIM) or weight leakage energy (stored in edram chip buffer) 
    refresh_retention_time = getattr(config, f'eDRAM_refresh_retention_time_{config.dynamic_chiplet_technode}nm')
    refresh_power_per_bit = getattr(config, f'eDRAM_refresh_power_per_bit_{config.dynamic_chiplet_technode}nm')
    static_refresh_energy_weight_eachLayer = [0] * len(NetStructure)
    semi_static_refresh_energy_weight_eachLayer = [0] * len(NetStructure)
    buffer_leak_energy_weight_eachLayer = [0] * len(NetStructure)
    for layer_idx, layer in enumerate(NetStructure):
        if (layer[6] == 0) and (config.static_chiplet_memory_cell_type == 'eDRAM'): # static layer
            num_refresh_times = math.ceil(sum(total_latency_eachLayer) / refresh_retention_time)
            static_refresh_energy_weight_eachLayer[layer_idx] = (layer[2]*layer[3]*config.BitWidth_weight * num_refresh_times) * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)
        elif layer[6] == 2: # semi-static layer
            # option 1: for each semi-static layer, weight refresh energy (stored in edram CIM)
            num_refresh_times = math.ceil(layers_process_latency_eachDestLayer[layer_idx] / refresh_retention_time)
            semi_static_refresh_energy_weight_eachLayer[layer_idx] = (layer[2]*layer[3]*config.BitWidth_weight * num_refresh_times) * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)
            # option 2: for each semi-static layer, weight leakage energy (stored in edram chip buffer)
            buffer = Buffer(config,config.dynamic_chiplet_technode,'SRAM',mem_width=config.chip_buffer_core_width * math.ceil(layer[2]*layer[3]*config.BitWidth_weight / config.chip_buffer_core_height / config.chip_buffer_core_width) ,mem_height=config.chip_buffer_core_height)
            buffer_leak_energy_weight_eachLayer[layer_idx] = layers_process_latency_eachDestLayer[layer_idx] * buffer.get_leak_power()
            # buffer_leak_energy_weight_eachLayer[layer_idx] = total_latency * buffer.get_leak_power()
    
    # =============== analysis: hybrid storage - first consider store in sram buffer (cost: sram leakage); if sram full, store in eDRAM (cost: edram refresh) =============== #
    bp_weight_storage_energy_eachLayer = [0] * len((NetStructure)) # show sram+edram breakdown
    bp_weight_storage_edram_energy_eachLayer = [0] * len((NetStructure)) # show edram breakdown
    extra_bp_weight_storage_energy_eachLayer = [0] * len((NetStructure)) # add to total energy
    # option 3: hybrid edram-sram buffer
    if any(keyword in config.model_filename for keyword in ("cl", "ft")):
        available_sram_buffer_size_each_static2_chip = [Integration.static2_chiplet.buffer_size] * num_used_semi_static_chiplet
        buffer = Integration.static2_chiplet.buffer
        print("Integration.static2_chiplet.buffer_size=",Integration.static2_chiplet.buffer_size)
        print("buffer_height=",buffer.mem_height)
        print("buffer_width=",buffer.mem_width)
        
        for layer_idx, layer in enumerate(NetStructure):
            if layer[6] == 2:
                for chip_idx, chip_layers_group in enumerate(static_chiplet_layers):
                    if layer_idx in chip_layers_group:
                        num_this_layer_input_bit = Num_In_eachLayer[layer_idx] * config.BitWidth_in
                        # if sram buffer is available for all input bits of this layer, store all in sram buffer
                        chip_idx -= num_used_static_chiplet
                        if available_sram_buffer_size_each_static2_chip[chip_idx] >= num_this_layer_input_bit :
                            extra_bp_weight_storage_energy_eachLayer[layer_idx] += layers_process_latency_eachDestLayer[layer_idx] * buffer.get_leak_power() / (buffer.mem_width * buffer.mem_height) * num_this_layer_input_bit

                            bp_weight_storage_energy_eachLayer[layer_idx] += layers_process_latency_eachDestLayer[layer_idx] * buffer.get_leak_power() / (buffer.mem_width * buffer.mem_height) * num_this_layer_input_bit + (buffer.get_energy_per_bit(config)[0] + buffer.get_energy_per_bit(config)[1]) * num_this_layer_input_bit

                            available_sram_buffer_size_each_static2_chip[chip_idx] -= num_this_layer_input_bit # update buffer availability
                        # else: sram buffer has no enough availablability for this layer
                        else:
                            # sram has 0 availablity, store and refresh all in eDRAM CIM
                            if available_sram_buffer_size_each_static2_chip[chip_idx] == 0:
                                num_refresh_times = math.ceil(layers_process_latency_eachDestLayer[layer_idx] / refresh_retention_time)
                                extra_bp_weight_storage_energy_eachLayer[layer_idx] += num_this_layer_input_bit * num_refresh_times * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)
                                extra_bp_weight_storage_energy_eachLayer[layer_idx] -= (buffer.get_energy_per_bit(config)[0] + buffer.get_energy_per_bit(config)[1])* num_this_layer_input_bit

                                bp_weight_storage_energy_eachLayer[layer_idx] += num_this_layer_input_bit * num_refresh_times * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)

                                bp_weight_storage_edram_energy_eachLayer[layer_idx] += num_this_layer_input_bit * num_refresh_times * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)

                            # sram has some availablity, store and refresh a part of this layer in eDRAM CIM, store others in eDRAM CIM 
                            elif available_sram_buffer_size_each_static2_chip[chip_idx] < num_this_layer_input_bit :
                                # store a part in SRAM
                                extra_bp_weight_storage_energy_eachLayer[layer_idx] += layers_process_latency_eachDestLayer[layer_idx] * buffer.get_leak_power() / (buffer.mem_width * buffer.mem_height) * available_sram_buffer_size_each_static2_chip[chip_idx]

                                bp_weight_storage_energy_eachLayer[layer_idx] += layers_process_latency_eachDestLayer[layer_idx] * buffer.get_leak_power() / (buffer.mem_width * buffer.mem_height) * available_sram_buffer_size_each_static2_chip[chip_idx] + (buffer.get_energy_per_bit(config)[0] + buffer.get_energy_per_bit(config)[1]) * num_this_layer_input_bit

                                # store a part in eDRAM CIM
                                num_refresh_times = math.ceil(layers_process_latency_eachDestLayer[layer_idx] / refresh_retention_time)
                                extra_bp_weight_storage_energy_eachLayer[layer_idx] += (num_this_layer_input_bit - available_sram_buffer_size_each_static2_chip[chip_idx]) * num_refresh_times * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)
                                extra_bp_weight_storage_energy_eachLayer[layer_idx] -= (buffer.get_energy_per_bit(config)[0] + buffer.get_energy_per_bit(config)[1])* (num_this_layer_input_bit - available_sram_buffer_size_each_static2_chip[chip_idx])

                                bp_weight_storage_energy_eachLayer[layer_idx] += (num_this_layer_input_bit - available_sram_buffer_size_each_static2_chip[chip_idx]) * num_refresh_times * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)

                                bp_weight_storage_edram_energy_eachLayer[layer_idx] += (num_this_layer_input_bit - available_sram_buffer_size_each_static2_chip[chip_idx]) * num_refresh_times * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)

                                # update sram buffer availability
                                available_sram_buffer_size_each_static2_chip[chip_idx] = 0 
        # print("extra_bp_weight_storage_energy_eachLayer:",extra_bp_weight_storage_energy_eachLayer)
    # ===============            analysis done: hybrid storage             =============== #
    
    # # =============== analysis: adapter-layer weight gradient storage location - store back to learned-weight-rram or refresh in advnced technode edram. depends on 1. learning batch size, 2. 2D/2.5D/3D link energy/bit, 3. adapter-layer location in whole learning model =============== #
    # adapter_weight_gradient_storage_latency_eachLayer = [0] * len((NetStructure))
    # adapter_weight_gradient_edram_storage_energy_eachLayer = [0] * len((NetStructure))
    # adapter_weight_gradient_rram_storage_energy_eachLayer = [0] * len((NetStructure))
    # adapter_weight_gradient_rram_edram_storage_energy_ratio_eachLayer = [0] * len((NetStructure))
    
    # if any(keyword in config.model_filename for keyword in ("cl")):
    #     for layer_idx, layer in enumerate(NetStructure):
    #         for dest_layer_idx in (to_bp_dest_layers[layer_idx]):
    #             if NetStructure_layer_def[dest_layer_idx] in ('W Gradient:weight_adapter1-1,','W Gradient:weight_adapter1-2,','W Gradient:weight_adapter2-1,','W Gradient:weight_adapter2-2,'):
    #                 if config.train_pipeline_parallel == 1:
    #                     adapter_weight_gradient_storage_latency_eachLayer[dest_layer_idx] = sum(total_latency_eachLayer) - layers_process_latency_eachDestLayer[dest_layer_idx] + 2 * (config.train_batch_size - 1) * total_latency_eachLayer[0]
    #                 else:
    #                     adapter_weight_gradient_storage_latency_eachLayer[dest_layer_idx] = sum(total_latency_eachLayer) - layers_process_latency_eachDestLayer[dest_layer_idx] + 2 * (config.train_batch_size - 1) * sum(total_latency_eachLayer)
                    
    #                 print("adapter_weight_gradient_storage_latency_eachLayer",dest_layer_idx,":",adapter_weight_gradient_storage_latency_eachLayer[dest_layer_idx])
                    
    #                 refresh_retention_time = getattr(config, f'eDRAM_refresh_retention_time_{config.dynamic_chiplet_technode}nm') # should be advanced technode
    #                 num_refresh_times = math.ceil(adapter_weight_gradient_storage_latency_eachLayer[dest_layer_idx] / refresh_retention_time)
    #                 refresh_power_per_bit = getattr(config, f'eDRAM_refresh_power_per_bit_{config.dynamic_chiplet_technode}nm') # should be advanced technode
    #                 adapter_weight_gradient_edram_storage_energy_eachLayer[dest_layer_idx] =  (num_refresh_times) * refresh_power_per_bit * (100* 1/config.eDRAM_clk_freq)
                    
    #                 adapter_weight_gradient_rram_storage_energy_eachLayer[dest_layer_idx] = getattr(config, f'RRAM_write_energy_per_bit_{config.static_chiplet_technode}nm') + config.ebit_2d # can change to 2/2.5/3d
    #                 adapter_weight_gradient_rram_edram_storage_energy_ratio_eachLayer[dest_layer_idx] = adapter_weight_gradient_rram_storage_energy_eachLayer[dest_layer_idx] / adapter_weight_gradient_edram_storage_energy_eachLayer[dest_layer_idx]
    #                 print("adapter_weight_gradient_rram_edram_storage_energy_ratio_eachLayer",dest_layer_idx,":",adapter_weight_gradient_rram_edram_storage_energy_ratio_eachLayer[dest_layer_idx])
    #                 print("refresh_retention_time :",refresh_retention_time)
    #                 print("num_refresh_times :",num_refresh_times)
    #                 print("refresh_power_per_bit :",refresh_power_per_bit)
    # # =============== analysis done: adapter-layer weight gradient storage location =============== #
    
    # get total power each layer and total power each layer per PE
    total_power_eachLayer = [0] * len(NetStructure)
    total_power_per_PE_eachLayer = [0] * len(NetStructure)
    total_power_mW_eachLayer = [0] * len(NetStructure)
    total_power_per_PE_mW_eachLayer = [0] * len(NetStructure)
    for layer_idx, layer in enumerate(NetStructure):
        total_power_eachLayer[layer_idx] = total_energy_eachLayer[layer_idx] / total_latency_eachLayer[layer_idx] 
        total_power_mW_eachLayer[layer_idx] = total_power_eachLayer[layer_idx] * 1e3
        
        total_power_per_PE_eachLayer[layer_idx] = total_power_eachLayer[layer_idx] / (Num_StaticPE_eachLayer[layer_idx] + Num_DynamicPE_eachLayer[layer_idx])
        total_power_per_PE_mW_eachLayer[layer_idx] = total_power_per_PE_eachLayer[layer_idx] * 1e3
    # print("total_power_per_PE_eachLayer (mW) : ", total_power_per_PE_mW_eachLayer)
    
    # get avarage power of each chip (mW per chip and mW/mm2 per chip)
    chip_power_mW_eachChip = [0] * num_used_chiplets
    max_chip_power_mW_eachChip = [0] * num_used_chiplets # useful only for dynamic chips
    # for static and semi-static chip, each chip power = sum (all pe power in one chip), assuming all pes are working all the time when batch size >1
    # for dynamic chip, each chip power = max of all dynamic layers of [all pe power in one chip], assuming all pes are working all the time when batch size >1
    for layer_idx, layer in enumerate(NetStructure):
            if layer[6] == 0 or layer[6] == 2: # static or semi-static
                for chip_idx, chip_layers_group in enumerate(static_chiplet_layers):
                    if layer_idx in chip_layers_group:
                        chip_power_mW_eachChip[chip_idx] += total_power_mW_eachLayer[layer_idx]/ num_static_chiplet_eachLayer[layer_idx]
                        
            else: # dynamic
                for chip_idx in range(num_dynamic_chiplet_eachLayer[layer_idx]):
                    chip_idx += num_used_static_chiplet_all_layers
                    chip_power_mW_eachChip[chip_idx] = total_power_mW_eachLayer[layer_idx] / num_dynamic_chiplet_eachLayer[layer_idx]
                    if chip_power_mW_eachChip[chip_idx] > max_chip_power_mW_eachChip[chip_idx]:
                        max_chip_power_mW_eachChip[chip_idx] = chip_power_mW_eachChip[chip_idx]
    # if layer_idx == 348:
    #     print("")
    #     print("layer 348 power :")
    #     print("total_power_mW_eachLayer[layer_348]",total_power_mW_eachLayer[layer_idx])
    #     print("num_static_chiplet_eachLayer[layer_348]",num_static_chiplet_eachLayer[layer_idx])
    #     print("chip_power_mW_eachChip[chip 16]",chip_power_mW_eachChip[16])
    #     print("")
    #     print("total_energy_eachLayer[layer_348]",total_energy_eachLayer[layer_idx])
    #     print("write_energy_input_eachLayer[layer_348]",write_energy_input_eachLayer[layer_idx])
    #     print("read_energy_output_eachLayer[layer_348]",read_energy_output_eachLayer[layer_idx])
    #     print("refresh_energy_weight_eachLayer[layer_348]",refresh_energy_weight_eachLayer[layer_idx])
    #     print("")
    #     print("total_latency_eachLayer[layer_348]",total_latency_eachLayer[layer_idx])
    #     # total_latency_eachLayer[layer_idx] = write_latency_input_eachLayer[layer_idx] + read_latency_output_eachLayer[layer_idx] + 
    #     print("read_latency_output_eachLayer[layer_348]",read_latency_output_eachLayer[layer_idx])
    #     print("")
    #     print("write_latency_input_peHtree_eachLayer[layer_348]",write_latency_input_peHtree_eachLayer[layer_idx])
    #     print("write_latency_weight_peHtree_eachLayer[layer_348]",write_latency_weight_peHtree_eachLayer[layer_idx])
    #     print("read_latency_output_peHtree_eachLayer[layer_348]",read_latency_output_peHtree_eachLayer[layer_idx])
    #     # write_latency_input_peHtree_eachLayer[layer_idx] + write_latency_weight_peHtree_eachLayer[layer_idx] + read_latency_output_peHtree_eachLayer[layer_idx]
    #     print("")
    
    # update max dynamic chip power to dynamic chip power (consider as worst case)
    for chip_idx in range(num_used_static_chiplet_all_layers,num_used_chiplets):
        chip_power_mW_eachChip[chip_idx] = max_chip_power_mW_eachChip[chip_idx]
    print("chip_power_mW_eachChip (mW) : ", chip_power_mW_eachChip)
    
    chip_power_mW_per_area_mm2_eachChip = [0] * num_used_chiplets
    area_eachChip = [0] * num_used_chiplets
    for chip_idx in range(num_used_chiplets):
        if chip_idx < num_used_static_chiplet:
            area_eachChip[chip_idx] = Integration.static0_chiplet.get_area() * 1E6
        elif chip_idx < num_used_static_chiplet_all_layers:
            area_eachChip[chip_idx] = Integration.static2_chiplet.get_area() * 1E6
        else:
            area_eachChip[chip_idx] = Integration.dynamic_chiplet.get_area() * 1E6
        chip_power_mW_per_area_mm2_eachChip[chip_idx] = chip_power_mW_eachChip[chip_idx] / area_eachChip[chip_idx]

    print("chip_power_mW_per_area_mm2_eachChip (mW/mm2) : ")
    print("static 0 chip : ")
    print(chip_power_mW_per_area_mm2_eachChip[0:num_used_static_chiplet])
    print("static 2 chip : ")
    print(chip_power_mW_per_area_mm2_eachChip[num_used_static_chiplet:num_used_static_chiplet_all_layers])
    print("dynamic chip : ")
    print(chip_power_mW_per_area_mm2_eachChip[num_used_static_chiplet_all_layers:num_used_chiplets])
    print("")

    # ===== get TOPS/W/mm2 mW per chip and TOPS/mm2 per chip =====
    tops_per_w_per_mm2_eachChip = [0] * num_used_chiplets
    tops_per_mm2_eachChip = [0] * num_used_chiplets
    tops_eachChip = [0] * num_used_chiplets
    energy_eachChip = [0] * num_used_chiplets
    max_tops_per_w_per_mm2_eachChip = [0] * num_used_chiplets
    # for static and semi-static chip, each chip TOPS/W = sum (tops all layers in one chip) / sum (energy all layers in one chip), assuming all pes are working all the time when batch size >1
    # for dynamic chip, each chip TOPS/W = max of all dynamic layers of [all pe power in one chip], assuming all pes are working all the time when batch size >1

    for layer_idx, layer in enumerate(NetStructure):
        if layer[6] == 0 or layer[6] == 2:  # static or semi-static
            for chip_idx, chip_layers_group in enumerate(static_chiplet_layers):
                # print(f"chip_idx: {chip_idx}, chip_layers_group: {chip_layers_group}, layer_idx: {layer_idx}")
                if layer_idx in chip_layers_group:
                    tops_eachChip[chip_idx] += tops_eachLayer[layer_idx]
                    energy_eachChip[chip_idx] += total_energy_eachLayer[layer_idx]
        
        else: # dynamic
            for chip_idx in range(num_dynamic_chiplet_eachLayer[layer_idx]):
                chip_idx += num_used_static_chiplet_all_layers
                tops_per_w_per_mm2_eachChip[chip_idx] = (tops_eachChip[chip_idx] / (total_energy_eachLayer[layer_idx]+noc_energy/num_used_chiplets) / area_eachChip[chip_idx]) / num_dynamic_chiplet_eachLayer[layer_idx]
                if tops_per_w_per_mm2_eachChip[chip_idx] > max_tops_per_w_per_mm2_eachChip[chip_idx]:
                    max_tops_per_w_per_mm2_eachChip[chip_idx] = tops_per_w_per_mm2_eachChip[chip_idx]


    # update max dynamic chip TOPS/W/mm2 to dynamic TOPS/W/mm2 (consider as worst case)
    for chip_idx in range(num_used_static_chiplet_all_layers,num_used_chiplets):
        tops_per_w_per_mm2_eachChip[chip_idx] = max_tops_per_w_per_mm2_eachChip[chip_idx]
    # print("tops_per_w_per_mm2_eachChip (TOPS/W/mm2) : ", tops_per_w_per_mm2_eachChip)
    # print("len(static_chiplet_layers):",len(static_chiplet_layers))

    # get static chip TOPS/W/mm2
    
    for chip_idx, chip_layers_group in enumerate(static_chiplet_layers):
        tops_per_w_per_mm2_eachChip[chip_idx] = (tops_eachChip[chip_idx]/ (energy_eachChip[chip_idx]+noc_energy/num_used_chiplets) / area_eachChip[chip_idx]) / num_static_chiplet_eachLayer[layer_idx]
        # print("tops_eachChip", chip_idx, tops_eachChip[chip_idx])
        # print("energy_eachChip", chip_idx, energy_eachChip[chip_idx])
        # print("area_eachChip", chip_idx, area_eachChip[chip_idx])
        # print("num_static_chiplet_eachLayer", chip_idx, num_static_chiplet_eachLayer[chip_idx])
    
    # get all chip TOPS/mm2
    tops_per_mm2_eachChip = [0] * num_used_chiplets
    for chip_idx in range(num_used_chiplets):
            tops_per_mm2_eachChip[chip_idx] = tops_per_w_per_mm2_eachChip[chip_idx] * (chip_power_mW_eachChip[chip_idx] * 1e-03)
    
    # merge (static0,dynamic,static2) to (static0+dynamic,static2) for TOPS/W/mm2 and TOPS/mm2
    # for chip_idx in range(num_used_static_chiplet_all_layers,num_used_chiplets):
    #     tops_per_w_per_mm2_eachChip[chip_idx] = max_tops_per_w_per_mm2_eachChip[chip_idx]
    for chip_idx in range(0,num_used_static_chiplet):
        tops_per_w_per_mm2_eachChip[chip_idx] = (tops_per_w_per_mm2_eachChip[chip_idx]*area_eachChip[chip_idx] + tops_per_w_per_mm2_eachChip[num_used_static_chiplet_all_layers]*area_eachChip[num_used_static_chiplet_all_layers]) / (area_eachChip[chip_idx] + area_eachChip[num_used_static_chiplet_all_layers])

        tops_per_mm2_eachChip[chip_idx] = (tops_per_mm2_eachChip[chip_idx]*area_eachChip[chip_idx] + tops_per_mm2_eachChip[num_used_static_chiplet_all_layers]*area_eachChip[num_used_static_chiplet_all_layers]) / (area_eachChip[chip_idx] + area_eachChip[num_used_static_chiplet_all_layers])

    print("tops_per_mm2_eachChip (TOPS/mm2) : ")
    print("static 0 chip : ")
    print(tops_per_mm2_eachChip[0:num_used_static_chiplet])
    print("static 2 chip : ")
    print(tops_per_mm2_eachChip[num_used_static_chiplet:num_used_static_chiplet_all_layers])
    print("")
    print("tops_per_w_per_mm2_eachChip (TOPS/W/mm2) : ")
    print("static 0 chip : ")
    print(tops_per_w_per_mm2_eachChip[0:num_used_static_chiplet])
    print("static 2 chip : ")
    print(tops_per_w_per_mm2_eachChip[num_used_static_chiplet:num_used_static_chiplet_all_layers])
    print("")

    # print("dynamic chip : ")
    # print(tops_per_mm2_eachChip[num_used_static_chiplet_all_layers:num_used_chiplets])
    # ===== done: TOPS/W/mm2 mW per chip and TOPS/mm2 per chip =====
                            
    total_write_latency_input = sum(write_latency_input_eachLayer)
    total_write_energy_input = sum(write_energy_input_eachLayer)
    total_write_latency_weight = sum(write_latency_weight_eachLayer)
    total_write_energy_weight = sum(write_energy_weight_eachLayer)
    total_read_latency_output = sum(read_latency_output_eachLayer)
    total_read_energy_output = sum(read_energy_output_eachLayer)
    total_refresh_latency_weight = sum(refresh_latency_weight_eachLayer)
    total_refresh_energy_weight = sum(refresh_energy_weight_eachLayer)
    # -----htree breakdown
    total_write_latency_input_peHtree = sum(write_latency_input_peHtree_eachLayer)
    total_write_energy_input_peHtree = sum(write_energy_input_peHtree_eachLayer)
    total_write_latency_weight_peHtree = sum(write_latency_weight_peHtree_eachLayer)
    total_write_energy_weight_peHtree = sum(write_energy_weight_peHtree_eachLayer)
    total_read_latency_output_peHtree = sum(read_latency_output_peHtree_eachLayer)
    total_read_energy_output_peHtree = sum(read_energy_output_peHtree_eachLayer)

    total_latency = sum(total_latency_eachLayer)
    
    # get total latency when all attn head operations happen simultaneously in large edram capacity (in hybrid RRAM-eDRAM chip)
    total_latency_w_parallel_dynamic_op = 0
    sum_parallel_latency = 0
    sum_compressed_parallel_latency = 0
    for layer_idx in range(len(NetStructure_layer_def)):
        if NetStructure_layer_def[layer_idx] in ('K.Q,','KQT softmax * V,','FP:K.Q,','FP:KQT softmax * V,','BP:V,','BP:Q,'):
            sum_parallel_latency += total_latency_eachLayer[layer_idx]
    sum_compressed_parallel_latency = sum_parallel_latency / config.num_T_head
    total_latency_w_parallel_dynamic_op = total_latency - sum_parallel_latency + sum_compressed_parallel_latency
    
    total_energy = sum(total_energy_eachLayer)

    total_static_refresh_energy_weight = sum(static_refresh_energy_weight_eachLayer)
    # option 1:
    total_semi_static_refresh_energy_weight = sum(semi_static_refresh_energy_weight_eachLayer) 
    # option 2:
    total_buffer_leak_energy_weight = sum(buffer_leak_energy_weight_eachLayer)
    # option 3:
    total_extra_bp_weight_storage_energy = sum(extra_bp_weight_storage_energy_eachLayer)
    total_bp_weight_storage_energy = sum(bp_weight_storage_energy_eachLayer) # sram+edram
    total_bp_weight_storage_edram_energy = sum(bp_weight_storage_edram_energy_eachLayer) # edram breakdown
    
    Total_Energy = 0
    Total_Energy += total_energy + total_static_refresh_energy_weight
    Total_Energy_opt_1 = Total_Energy + total_semi_static_refresh_energy_weight
    Total_Energy_opt_2 = Total_Energy + total_buffer_leak_energy_weight
    Total_Energy_opt_3 = Total_Energy + total_extra_bp_weight_storage_energy

    # w/ NoC,NoP
    Total_Energy += noc_energy + noc_train_energy + nop_energy + nop_train_energy
    Total_Energy += nop_driver_energy
    Total_Energy_opt_1_ = Total_Energy + total_semi_static_refresh_energy_weight
    Total_Energy_opt_2_ = Total_Energy + total_buffer_leak_energy_weight
    Total_Energy_opt_3_ = Total_Energy + total_extra_bp_weight_storage_energy

    Total_Latency = 0
    Total_Latency += total_latency
    Total_Latency_w_NoC = Total_Latency + noc_latency + noc_train_latency
    Total_Latency_w_NoCNoP = Total_Latency_w_NoC + nop_latency + nop_train_latency
    
    Total_tops = Total_top_num / Total_Latency

    Energy_Efficiency_opt_1 = Total_top_num / Total_Energy_opt_1
    Energy_Efficiency_Per_Area_opt_1 = Energy_Efficiency_opt_1 / Total_Area_mm2

    Energy_Efficiency_opt_2 = Total_top_num / Total_Energy_opt_2
    Energy_Efficiency_Per_Area_opt_2 = Energy_Efficiency_opt_2 / Total_Area_mm2
    
    Energy_Efficiency_opt_3 = Total_top_num / Total_Energy_opt_3
    Energy_Efficiency_Per_Area_opt_3 = Energy_Efficiency_opt_3 / Total_Area_mm2

    # w/ NoC,NoP
    Energy_Efficiency_opt_1_ = Total_top_num / Total_Energy_opt_1_
    Energy_Efficiency_Per_Area_opt_1_ = Energy_Efficiency_opt_1_ / Total_Area_mm2

    Energy_Efficiency_opt_2_ = Total_top_num / Total_Energy_opt_2_
    Energy_Efficiency_Per_Area_opt_2_ = Energy_Efficiency_opt_2_ / Total_Area_mm2
    
    Energy_Efficiency_opt_3_ = Total_top_num / Total_Energy_opt_3_
    Energy_Efficiency_Per_Area_opt_3_ = Energy_Efficiency_opt_3_ / Total_Area_mm2

    print("==========================================")
    print("Integration_dimension:",config.Packaging_dimension)
    print("===== Total =====")
    print("Total TOP num:",Total_top_num)
    print("")
    print("Total Area (mm2) -- w/o NoC,NoP:",chip_area_mm2)
    print("Total Area (mm2) -- w/ NoC,NoP:",Total_Area_mm2)
    if config.Packaging_dimension == 3:
        print("TSV Area (mm2) : ", Integration.total_tsv_area * 1E6)
        print("num tsv:",Integration.num_tsv)
        print("TSV power density (mW/mm2) : ", config.ebit_3d *Integration.num_tsv / config.nop_clk_freq_3d * 1E03 / (Integration.total_tsv_area * 1E6))
        
    print("")
    print("Total Latency (s) -- w/o NoC,NoP:",total_latency)
    print("Total Latency (s) -- w/o NoC,NoP (parallel head attn operations):",total_latency_w_parallel_dynamic_op)
    print("Total Latency (s) -- w/ NoC:",Total_Latency_w_NoC)
    print("Total Latency (s) -- w/ NoC,NoP:",Total_Latency_w_NoCNoP)
    print("")
    print("Performance (TOPS):",Total_tops)
    print("total_static_refresh_energy_weight (static weight store in eDRAN CIM):",total_static_refresh_energy_weight)
    print("")

    print("===== option1: refresh eDRAM =====")
    print("")
    print("-- w/o NoC,NoP:")
    print("Total Energy (J) :",Total_Energy_opt_1)
    print("Total refresh bp weight Energy (J) -- refresh_energy (store bp changing weight) :",total_semi_static_refresh_energy_weight)
    print("Energy Efficiency (TOPS/W) :", Energy_Efficiency_opt_1)
    print("Energy Efficiency Per Area (TOPS/W/mm2) :", Energy_Efficiency_Per_Area_opt_1)
    print("")
    print("-- w/ NoC,NoP:")
    print("Total Energy (J) :",Total_Energy_opt_1_)
    print("Total refresh bp weight Energy (J) -- refresh_energy (store bp changing weight) :",total_semi_static_refresh_energy_weight)
    print("Energy Efficiency (TOPS/W) :", Energy_Efficiency_opt_1_)
    print("Energy Efficiency Per Area (TOPS/W/mm2) :", Energy_Efficiency_Per_Area_opt_1_)
    print("")

    print("===== option2: SRAM leak =====")
    print("")
    print("-- w/o NoC,NoP:")
    print("Total Energy (J) :",Total_Energy_opt_2)
    print("Total Leak Energy (J) -- buffer_leak_energy (store bp changing weight in SRAM) :",total_buffer_leak_energy_weight)
    print("Energy Efficiency (TOPS/W) :", Energy_Efficiency_opt_2)
    print("Energy Efficiency Per Area (TOPS/W/mm2) :", Energy_Efficiency_Per_Area_opt_2)
    print("")
    print("-- w/ NoC,NoP:")
    print("Total Energy (J) :",Total_Energy_opt_2_)
    print("Total Leak Energy (J) -- buffer_leak_energy (store bp changing weight in SRAM) :",total_buffer_leak_energy_weight)
    print("Energy Efficiency (TOPS/W) :", Energy_Efficiency_opt_2_)
    print("Energy Efficiency Per Area (TOPS/W/mm2) :", Energy_Efficiency_Per_Area_opt_2_)
    print("")
    
    print("===== option3: SRAM leak + eDRAM CIM refresh =====")
    print("")
    print("-- w/o NoC,NoP:")
    print("Total Energy (J) :",Total_Energy_opt_3)
    print(" -- bp_weight_store_energy (store bp changing weight in SRAM buffer and eDRAM CIM) :",total_bp_weight_storage_energy)
    print("-- bp_weight_store_energy (ony edram part) :", "{:.5e}".format(total_bp_weight_storage_edram_energy))
    print("Energy Efficiency (TOPS/W) :", Energy_Efficiency_opt_3)
    print("Energy Efficiency Per Area (TOPS/W/mm2) :", Energy_Efficiency_Per_Area_opt_3)
    print("")
    print("-- w/ NoC,NoP:")
    print("Total Energy (J) :",Total_Energy_opt_3_)
    print(" -- bp_weight_store_energy (store bp changing weight in SRAM buffer and eDRAM CIM) :",total_bp_weight_storage_energy)
    print("-- bp_weight_store_energy (ony edram part) :",total_bp_weight_storage_edram_energy)
    print("Energy Efficiency (TOPS/W) :", Energy_Efficiency_opt_3_)
    print("Energy Efficiency Per Area (TOPS/W/mm2) :", Energy_Efficiency_Per_Area_opt_3_)
    print("")

    print("===== Breakdown =====")
    print("Num used Static Chiplets (static and semi-static):", num_used_static_chiplet_all_layers)
    print("Num used Static Chiplets (static):", num_used_static_chiplet)
    print("Num used Static Chiplets (semi-static):", num_used_semi_static_chiplet)
    print("Num used Dynamic Chiplets:", num_used_dynamic_chiplet)
    
    print("static chiplet utilization:", static_chiplet_utilization) # for each static-chiplet, ?% pe used 
    formatted_dynamic_utilization = [f"{util:.4f}" for util in dynamic_chiplet_utilization]
    # print("dynamic chiplet utilization each layer:", formatted_dynamic_utilization)
    print("")

    # print("total_write_latency_input:",total_write_latency_input)
    # print("total_write_latency_weight:",total_write_latency_weight)
    # print("total_read_latency_output:",total_read_latency_output)
    # print("total_refresh_latency_weight:",total_refresh_latency_weight)
    # print("")
    
    # print("total_write_energy_input:",total_write_energy_input)
    # print("total_write_energy_weight:",total_write_energy_weight)
    # print("total_read_energy_output:",total_read_energy_output)
    # print("total_refresh_energy_weight:",total_refresh_energy_weight)
    # print("")
    # # -----htree breakdown
    print("total_write_latency_input_peHtree:",total_write_latency_input_peHtree)
    print("total_write_latency_weight_peHtree:",total_write_latency_weight_peHtree)
    print("total_read_latency_output_peHtree:",total_read_latency_output_peHtree)

    # print("total_write_energy_input_peHtree:",total_write_energy_input_peHtree)
    # print("total_write_energy_weight_peHtree:",total_write_energy_weight_peHtree)
    # print("total_read_energy_output_peHtree:",total_read_energy_output_peHtree)
    # print("")

    print(f"NOC Area: {noc_area}, NOC Latency: {noc_latency}, NOC Energy: {noc_energy}")
    print(f"NOC Area (for train): {noc_train_area}, NOC Latency (for train): {noc_train_latency}, NOC Energy (for train): {noc_train_energy}")
    print(f"NOP Area: {nop_area}, NOP Latency: {nop_latency}, NOP Energy: {nop_energy}")
    print(f"NOP Area (for train): {nop_train_area}, NOP Latency (for train): {nop_train_latency}, NOP Energy (for train): {nop_train_energy}")
    print(f"NOP driver Area: {nop_driver_area}, NOP driver Energy: {nop_driver_energy}")
    
    print("==========================================")

if __name__ == "__main__":
    config = Config()
    main(config)