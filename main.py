from math import ceil

from config import Config
from layer_trace import generate_trace_noc
from chiplet_layer_range import get_static_chiplet_layer_range,get_static_chiplet_layers,get_dest_layers
from layer_mapping import get_layer_energy_latency
from Interconnect.noc_estimation import interconnect_estimation
from Interconnect.nop_estimation import nop_interconnect_estimation
from Interconnect.NoP_hardware import NoP_hardware_estimation
from Integration import *

def main(config):
    # load in model and hw config info from config file
    # hw_config_filename = 'hw_config.txt'
    # data_loader = GetData(model_filename)
    # NetStructure = data_loader.load_model()
    # hw_configs = data_loader.load_hardware_config()
    NetStructure = config.load_model()

    static_chiplet_size = config.static_chiplet_height * config.static_chiplet_width
    dynamic_chiplet_size = config.dynamic_chiplet_height * config.dynamic_chiplet_width
    
    # get static/dynamic layer dataflow
    # initialize PPA
    Total_DynamicPower = 0
    Total_LeakPower = 0
    Total_Latency = 0
    Total_Area = 0
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

    # get TOPS of this layer
    for row in NetStructure:
        tops_thisLayer = row[0]*row[1]*row[3] *2 *1e-12
        Total_tops += tops_thisLayer

    # breakdown value #####################
    Area_logic = 1.5e-4 
    Area_buffer = 3e-4

    Area_DynamicPE_sfu = 3e-7
    DynamicPower_sfu = 8e-3 /512 # for 512 input
    Latency_sfu = 7e-7 /512 # for 512 input

    buffer_bw = 9e9 # SRAM-2D:9Gb/s=1.125GB/s
    buffer_dynamicEnergy = 17.5e-15 * 40/65  # [depends on tech] unit:J/read or J/write, SRAM-2D-65nm:17.5fJ/bit=140fJ/byte

    DynamicPower_logic = 4.67e-3/7.6e7*Total_tops
    DynamicPower_buffer = 1.04e-3/7.6e7*Total_tops
    Latency_logic = 1.5e-2/7.6e7*Total_tops
    Latency_buffer = 2.88e-3/7.6e7*Total_tops
    
    ##########################################
    
    num_static_chiplet_eachLayer = []
    num_dynamic_chiplet_eachLayer = []
    # get num of used static subarray/PE or used dynamic subarray/PE of each model layer
    # get dynamic power and latency
    for layer_index, row in enumerate(NetStructure):
        # get this layer operation is static or dynamic
        if row[6]== 0: # is static layer
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer = get_layer_energy_latency(row,config,config.static_chiplet_technode,chiplet_type='static',memory_cell_type=config.static_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(num_used_chiplet_this_layer)
            num_dynamic_chiplet_eachLayer.append(0)

            Num_StaticPE_eachLayer.append(num_used_pe_this_layer)
            Num_DynamicPE_eachLayer.append(0)

            Num_StaticSubArray_eachLayer.append(num_used_subarray_this_layer)
            Num_DynamicSubArray_eachLayer.append(0)
        else: # is dynamic layer
            num_used_chiplet_this_layer,num_used_pe_this_layer, num_used_subarray_this_layer,performance_this_layer = get_layer_energy_latency(row,config,config.dynamic_chiplet_technode,chiplet_type='dynamic',memory_cell_type=config.dynamic_chiplet_memory_cell_type)

            num_static_chiplet_eachLayer.append(0)
            num_dynamic_chiplet_eachLayer.append(num_used_chiplet_this_layer)

            Num_StaticPE_eachLayer.append(0)
            Num_DynamicPE_eachLayer.append(num_used_pe_this_layer)

            Num_StaticSubArray_eachLayer.append(0)
            Num_DynamicSubArray_eachLayer.append(num_used_subarray_this_layer)
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
    
    num_used_chiplets = num_used_static_chiplet_all_layers + used_num_dynamic_chiplet

    # # NoC Estimation
    # noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
    
    # # NoP Estimation
    # nop_area, nop_latency, nop_energy = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size)
    
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
        Integration = Integration2D(config,maxnum_layer_in_bit,num_used_static_chiplet_all_layers, used_num_dynamic_chiplet)
        # get chip area
        chip_area = Integration.CalculateArea()
        # NoC Estimation
        noc_area, noc_latency, noc_energy = 0,0,0
        noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        # NoP
        nop_area, nop_latency, nop_energy = 0,0,0
        nop_driver_area, nop_driver_energy = 0,0
    elif config.Packaging_dimension == 2.5:
        Integration = Integration2_5D(config,maxnum_layer_in_bit,num_used_static_chiplet_all_layers, used_num_dynamic_chiplet)
        # get chip area
        chip_area = Integration.CalculateArea()
        # NoC Estimation
        noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        # NoP Estimation
        nop_area, nop_latency, nop_energy, num_bits_nop_eachLayer = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size)

        # NoP Hardware Cost (Nop_area:um2, NoP_energy:pJ)
        # TODO: change data for 2.5D and 3D NoP driver
        # NoP Parameters - Extracted from GRS Nvidia 
        ebit = 0.58e-12
        area_per_lane = 5304.5e-12 # 5304.5 um2
        clocking_area = 10609e-12 # 10609 um2
        n_lane = 32
        n_bits_all_chiplets = sum(num_bits_nop_eachLayer)
        nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_all_chiplets)

    else: # H3D
        Integration = Integration3D(config,maxnum_layer_in_bit)
        #get chip area
        chip_area = Integration.CalculateArea()
        noc_area, noc_latency, noc_energy = interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, Num_StaticPE_eachLayer, Num_In_eachLayer, static_chiplet_layers, dest_layers, layer_location_begin_chiplet, config.net_name, config.static_chiplet_size)
        # NoP Estimation
        nop_area, nop_latency, nop_energy,num_bits_nop_eachLayer = nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, used_num_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, Num_In_eachLayer, config.net_name, config.static_chiplet_size)

        # NoP Hardware Cost (Nop_area:um2, NoP_energy:pJ)
        # TODO: change data for 2.5D and 3D NoP driver
        # NoP Parameters - Extracted from GRS Nvidia 
        ebit = 0.58e-12
        area_per_lane = 5304.5e-12 # 5304.5 um2
        clocking_area = 10609e-12 # 10609 um2
        n_lane = 32
        n_bits_all_chiplets = sum(num_bits_nop_eachLayer)
        nop_driver_area, nop_driver_energy = NoP_hardware_estimation(ebit, area_per_lane, clocking_area, n_lane, num_used_chiplets, n_bits_all_chiplets)

    # utilization and PPA
    static_chiplet_utilization = [x / static_chiplet_size for x in static_chiplet_availability]
    dynamic_chiplet_utilization = [x / dynamic_chiplet_size * used_num_dynamic_chiplet for x in Num_DynamicPE_eachLayer]
    
    Total_Area = 0
    Total_Area += chip_area
    Total_Area += noc_area + nop_driver_area
    Total_Area_mm2 = Total_Area*1e6
    
    total_write_energy_input = sum(performance_each_layer[0])
    total_write_latency_weight = sum(performance_each_layer[1])
    total_write_energy_weight = sum(performance_each_layer[2])
    total_read_energy_output = sum(performance_each_layer[3])
    total_refresh_latency_weight = sum(performance_each_layer[4])
    total_refresh_energy_weight = sum(performance_each_layer[5])
    
    Total_Energy = 0
    Total_Energy += total_write_energy_input
    Total_Energy += noc_energy + nop_driver_energy

    Total_Latency = 0
    total_read_latency_output = sum(performance_each_layer[3])
    Total_Latency += total_read_latency_output + noc_latency + nop_latency

    Energy_Efficiency = Total_tops / Total_Energy
    Energy_Efficiency_Per_Area = Energy_Efficiency / Total_Area_mm2

    print("==========================================")
    print("Integration_dimension:",config.Packaging_dimension)
    print("===== Total =====")
    print("Total write input Energy (J):",total_write_energy_input)
    # print("Total Leak Power (W):",Total_LeakPower)
    # print("Total Latency (s):",Total_Latency)
    print("Total Area (mm2):",Total_Area_mm2)
    print("Total TOPS:",Total_tops)

    print("Energy Efficiency (TOPS/W):", Energy_Efficiency)
    print("Energy Efficiency Per Area (TOPS/W/mm2):", Energy_Efficiency_Per_Area)

    print("===== Breakdown =====")

    print("Num used Static Chiplets:", num_used_static_chiplet_all_layers)
    print("Num used Dynamic Chiplets:", used_num_dynamic_chiplet)
    
    print("static chiplet utilization:", static_chiplet_utilization) # for each static-chiplet, ?% pe used 
    print("dynamic chiplet utilization:", dynamic_chiplet_utilization) # for each dynamic-layer, ?% pe used  in all dynamic chiplets
    
    print(f"NOC Area: {noc_area}, NOC Latency: {noc_latency}, NOC Energy: {noc_energy}")
    print(f"NOP Area: {nop_area}, NOP Latency: {nop_latency}, NOP Energy: {nop_energy}")
    print(f"NOP driver Area: {nop_driver_area}, NOP driver Energy: {nop_driver_energy}")
    
    print("==========================================")

if __name__ == "__main__":
    config = Config()
    main(config)