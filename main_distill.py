import numpy as np

# model_data = GetData(model_file, config_file).load_model()

# model_type,Transformer
vocabulary_size = 30522
encoder_layer = 1
decoder_layer = 0
head = 12
token_length = 512
hidden_size = 768
# memory_augmentation_flag = 1
# memory_token_length = 32

# hw_configs = GetData(model_file, config_file).load_hardware_config()
MemoryCellType_SRAM = 1
SRAM_tech = 65
SRAM_height = 256
SRAM_width = 256
cell_byte = 1

MemoryCellType_eDRAM = 1
eDRAM_tech = 65
eDRAM_height = 256
eDRAM_width = 256
cell_byte = 1

MacType_CIM = 1
CIM_mem_type_RRAM = 1
MacType_DigitalPE = 0
Mac_tech = 40
Packaging_dimension = 2 # 2, 2.5, 3
BitWidth_if = 8
Bitwidth_weight = 8

# fixed hw_config and data_flow

# memory
# mem_instance_list = [eDRAM, SRAM]

# eDRAM_instance_1
eDRAM = {
    "tech": 65,
    "height": 256,
    "width": 256,
    "cell_byte": 1,
    "cell_area": 1e-6,
    "cell_read_energy": 10e-3,
    "cell_write_energy": 10e-3,
    "cell_refresh_energy": 10e-3,
    "cell_read_latency": 10e-3,
    "cell_write_latency": 10e-3,
    "cell_refresh_latency": 10e-3,
    "read_count": 1234,
    "write_count": 1234,
    "cycle_retention_time": 1e-6,  #1e-3
    "total_retention_time": 10e-3,
    "cell_refresh_energy": 10-3
    "n_bit_driver_energy": 10e-3 #LUT
    "n_bit_driver_latency": 10e-3 #LUT
    "n_bit_driver_area": 10e-3 #LUT
}
# mem_instance_list[i].energy = memorySubClass(mem_instance_list[i]).getEnergy
# mem_instance_list[i].latency = memorySubClass(mem_instance_list[i]).getLatency
# mem_instance_list[i].area = memorySubClass(mem_instance_list[i]).getArea

# energy = read + write + referesh + driver
eDRAM_instance_1_energy = eDRAM["read_count"]* eDRAM["cell_read_energy"] + eDRAM["write_count"]* eDRAM["cell_write_energy"]
eDRAM_instance_1_refresh_energy = np.ceil(eDRAM["total_retention_time"]/eDRAM["cycle_retention_time"]) * eDRAM["height"] * eDRAM["width"] * eDRAM["cell_refresh_energy"]
eDRAM_instance_1_energy += eDRAM_instance_1_refresh_energy + eDRAM["n_bit_driver_energy"]
# latency = read + write + referesh(row by row) + driver
eDRAM_instance_1_latency = eDRAM["read_count"]* eDRAM["cell_read_latency"] + eDRAM["write_count"]* eDRAM["cell_write_latency"]
eDRAM_instance_1_refresh_latency = np.ceil(eDRAM["total_retention_time"]/eDRAM["cycle_retention_time"]) * eDRAM["height"] * eDRAM["cell_refresh_latency"] #refresh row by row
eDRAM_instance_1_latency += eDRAM_instance_1_refresh_energy + eDRAM["n_bit_driver_latency"]
# area = cell array + driver
eDRAM_instance_1_area = eDRAM["cell_area"] * eDRAM["height"] * eDRAM["width"] + eDRAM["n_bit_driver_area"]


# SRAM_instance_1
SRAM = {
    "tech": 65,
    "height": 256,
    "width": 256,
    "cell_byte": 1,
    "cell_area": 1e-6,
    "cell_read_energy": 10e-3,
    "cell_write_energy": 10e-3,
    "cell_leak_energy": 10e-3,
    "cell_read_latency": 10e-3,
    "cell_write_latency": 10e-3,
    "read_count": 1234,
    "write_count": 1234,
    "n_bit_driver_energy": 10e-3 #LUT
    "n_bit_driver_latency": 10e-3 #LUT
    "n_bit_driver_area": 10e-3 #LUT
}
# mem_instance_list[i].energy = memorySubClass(mem_instance_list[i]).getEnergy
# mem_instance_list[i].latency = memorySubClass(mem_instance_list[i]).getLatency
# mem_instance_list[i].area = memorySubClass(mem_instance_list[i]).getArea

# energy = read + write + leak + driver
SRAM_instance_1_energy = SRAM["read_count"]* SRAM["cell_read_energy"] + SRAM["write_count"]* SRAM["cell_write_energy"]
SRAM_instance_1_leak_energy = SRAM["height"] * SRAM["width"] * SRAM["cell_leak_energy"]
SRAM_instance_1_energy += SRAM_instance_1_leak_energy + SRAM["n_bit_driver_energy"]
# latency = read + write + driver
SRAM_instance_1_latency = SRAM["read_count"]* SRAM["cell_read_latency"] + SRAM["write_count"]* SRAM["cell_write_latency"]
SRAM_instance_1_latency += eDRAM_instance_1_refresh_energy + SRAM["n_bit_driver_latency"]
# area = cell array + driver
SRAM_instance_1_area = SRAM["cell_area"] * SRAM["height"] * SRAM["width"] + SRAM["n_bit_driver_area"]


# PE
# PE_instance = CIM_RRAM
# Intra-Memory interconnect: tile -> (processingUnit + hTree + shiftAdd) -> SubArray
CIM_RRAM = {
    "tech": 65,
    "tile_num": 8
    "PE_num_per_tile":6
    "subarray_height":64
    "subarray_width":64
    
    "cell_byte": 1,
    "cell_area": 1e-6,
    "cell_read_energy": 10e-3,
    "cell_write_energy": 10e-3,

    "cell_read_latency": 10e-3,
    "cell_write_latency": 10e-3,
    "read_count": 1234,
    "write_count": 1234,
    "n_bit_driver_energy": 10e-3 #LUT
    "n_bit_driver_latency": 10e-3 #LUT
    "n_bit_driver_area": 10e-3 #LUT
    "ADC_energy":10e-3 #LUT
    "ADC_latency": 10e-3 #LUT
    "ADC_area": 10e-3 #LUT
    "HTree_energy":10e-3 #LUT
    "HTree_latency": 10e-3 #LUT
    "HTree_area": 10e-3 #LUT
}

# code needed here: reference to 3Dneurosim            
CIM_RRAM_energy += (hTree.energy + ADC.energy)
CIM_RRAM_latency += (hTree.latency + ADC.latency)
CIM_RRAM_area += (hTree.area + ADC.area)

# Now get all attributes of mem and PE instances.
# go through packaing cases loop

if Packaging_dimension == 2:
    # area
    chip_area = eDRAM_instance_1_area + SRAM_instance_1_area + CIM_RRAM_area
    # energy, latency
    chip_energy = eDRAM_instance_1_energy + SRAM_instance_1_energy + CIM_RRAM_energy
    chip_latency = eDRAM_instance_1_latency + SRAM_instance_1_latency + CIM_RRAM_latency

    #no factor in data transferring 
    


if Packaging_dimension == 2.5:
# chiplet1: eDRAM, chiplet2: SRAM + CIM_RRAM
    # area
    chip_area = eDRAM_instance_1_area + SRAM_instance_1_area + CIM_RRAM_area
    # energy, latency
    chip_energy = eDRAM_instance_1_energy + SRAM_instance_1_energy + CIM_RRAM_energy
    chip_latency = eDRAM_instance_1_latency + SRAM_instance_1_latency + CIM_RRAM_latency
    # in interposer, data transferring betwwen m-m or m-c; TSV of potential interconnection
    chip_energy +=  data_transfer_eDRAM_SRAM_energy + TSV_energy
    chip_latency += data_transfer_eDRAM_SRAM_latency + TSV_latency # ?


else if Packaging_dimension == 3:
    if M3D == 1:
        # top_tier = CIM_RRAM
        # bottom_tier = eDRAM + SRAM
        # area
        top_area = CIM_RRAM_area
        bottom_area = eDRAM_instance_1_area + SRAM_instance_1_area
        chip_area = max(top_area,bottom_area)
        # energy, latency
        chip_energy = eDRAM_instance_1_energy + SRAM_instance_1_energy + CIM_RRAM_energy
        chip_latency = eDRAM_instance_1_latency + SRAM_instance_1_latency + CIM_RRAM_latency
        # interco of tiers...
        

    if H3D == 1:
        # area
        top_area = CIM_RRAM_area
        bottom_area = eDRAM_instance_1_area + SRAM_instance_1_area
        chip_area = max(top_area,bottom_area)
        # energy, latency
        chip_energy = eDRAM_instance_1_energy + SRAM_instance_1_energy + CIM_RRAM_energy
        chip_latency = eDRAM_instance_1_latency + SRAM_instance_1_latency + CIM_RRAM_latency
        # data transferring betwwen m-m or m-c; TSV between tiers
        chip_energy += TSV_energy
        chip_latency += TSV_latency # ?









#     mems = [] #list of used memory instances
# for i in input.len:
#     if(key==MemoryCellType_SRAM){
#         num = value[1]
#         w = value[2]
#         h = value[3]
#         new sRAM =(value1,value2,value3)
#         mems.push(sRAM)
#     }elif(key==...){
#         same
#         mems.push(bRAM)
#     }...

# Pack2D(mems)