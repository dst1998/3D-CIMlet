import csv

class Config:
    def __init__(self):
        self.model_filename = 'user_defined_example.csv' # 'user_defined_example_small.csv','user_defined_example.csv', 'hdvit_changed.csv'
        self.net_name = self.model_filename.rsplit('.csv', 1)[0]
        self.model_data = {}
        self.NetStructure = []
        self.clk_freq = 700e6 # 700MHz # TODO: depends on technode and memory device type (e.g. edram or rram)
        self.SRAM_tech = 65
        self.SRAM_height = 256
        self.SRAM_width = 256

        self.eDRAM_tech = 45
        self.eDRAM_cellSize_height = 0.84e-6 # 0.84um
        self.eDRAM_cellSize_width = 0.84e-6 # 0.84um
        self.eDRAM_SubArray_height = 128  # 128*0.84um=107.52e-6
        self.eDRAM_SubArray_width = 128   # 128*0.84um=107.52e-6
        self.eDRAM_SubArray_latency = 1
        self.eDRAM_SubArray_power = 1
        self.eDRAM_SubArray_area = 1
        self.eDRAM_PE_latency = 5e-9 # freq: 200Mhz
        self.eDRAM_PE_dynamicEnergy = 0.385e-9 # 5.88fj/bit * 256 * 256 = 0.385e-9J, refresh? retention?
        self.eDRAM_PE_leakPower = 0.188e-6 # cell: 2.87pW, PE: 2.87e-12 *256*256=0.188e-6

        self.RRAM_tech = 40
        self.RRAM_cellSize_height = 2* self.RRAM_tech * 1e-9 # 2F=2*40nm
        self.RRAM_cellSize_width = 2* self.RRAM_tech * 1e-9 # 2F=2*40nm
        self.RRAM_SubArray_height = 128  # 128*2F=128*2*40nm=10240e-9
        self.RRAM_SubArray_width = 128  # 128*2F=128*2*40nm=10240e-9
        self.RRAM_SubArray_latency = 1
        self.RRAM_SubArray_power = 1
        self.RRAM_SubArray_area = 1
        self.RRAM_PE_latency = 25e-9 #read/wrte: 10~30ns
        self.RRAM_PE_dynamicEnergy = 196.608e-9 # 3.0pJ/bit * 256 * 256 = 196.608e-9J
        self.RRAM_PE_leakPower = 0 # [195.41uW for 256*256]

        # -----subarray-----
        self.static_subarray_height = 256 # num of cell rows in a subarray
        self.static_subarray_width = 256 # num of cell cols in a subarray
        self.static_subarray_size = self.static_subarray_height * self.static_subarray_width
        self.dynamic_subarray_height = 128 # num of cell rows in a subarray
        self.dynamic_subarray_width = 128 # num of cell cols in a subarray
        self.dynamic_subarray_size = self.dynamic_subarray_height * self.dynamic_subarray_width

        self.subarray_readout_mux = 8

        # -----pe-----
        self.static_pe_height = 8 # num of subarray rows in a pe
        self.static_pe_width = 8 # num of subarray cols in a pe
        self.static_pe_size = self.static_pe_height * self.static_pe_width
        self.dynamic_pe_height = 4 # num of subarray rows in a pe
        self.dynamic_pe_width = 4 # num of subarray cols in a pe
        self.dynamic_pe_size = self.dynamic_pe_height * self.dynamic_pe_width

        # -----chiplet-----
        # -----static chiplet-----
        self.static_chiplet_technode = 45
        self.static_chiplet_memory_cell_type = 'RRAM'
        self.num_static_chiplet = 9
        self.static_chiplet_height = 8 # num of PE rows in a chiplet
        self.static_chiplet_width = 4 # num of PE cols in a chiplet
        self.static_chiplet_size = self.static_chiplet_height * self.static_chiplet_width
        
        # -----dynamic chiplet-----
        self.dynamic_chiplet_technode = 45
        self.dynamic_chiplet_memory_cell_type = 'eDRAM'
        self.num_dynamic_chiplet = 9
        self.dynamic_chiplet_height = 2 # num of PE rows in a chiplet
        self.dynamic_chiplet_width = 4 # num of PE cols in a chiplet
        self.dynamic_chiplet_size = self.dynamic_chiplet_height * self.dynamic_chiplet_width
        
        # -----logic chiplet-----
        self.logic_chiplet_technode = 45
        self.global_buffer_core_height = 128 # global buffer only in logic chiplet
        self.global_buffer_core_width = 128 # global buffer only in logic chiplet



        self.MacType_InMemoryCompute = 1
        self.MacType_DigitalPE = 0
        self.Mac_tech = 40
        self.Packaging_dimension = 3 # 2, 2.5, 3
        self.BitWidth_in = 8
        self.BitWidth_weight = 8
        self.Static_MemoryCellType = 'RRAM'
        self.Dynamic_MemoryCellType = 'eDRAM'

        

        self.pe_bus_width_2D = 32 # SIAM: 32
        self.chiplet_bus_width_2D = 32 # SIAM: 8,16,32
        self.scale_noc = 100 # SIAM: 100
        self.scale_nop = 10 # SIAM: 10
        self.type = 'Homogeneous_Design'
        
        self.eDRAM_refresh_retention_time = 1e-6
        self.RRAM_refresh_retention_time = 1e6

        self.Packaging_dimension = 3

    def load_model(self):
        try:
            with open(self.model_filename, mode='r', newline='') as file:
                csv_reader = csv.reader(file)
                first_row = next(csv_reader)  # Read the first line to determine the model type
                if first_row[1] == "Transformer":
                    for row in csv_reader:
                        if len(row) == 2:  # check if there's a key-value pair in each row
                            key, value = row[0], int(row[1])
                            self.model_data[key] = value
                        else:
                            print(f"Ignoring invalid row: {row}")
                    return self.model_data
                elif first_row[1] == "Transformer_NetStructure":
                    for row in csv_reader:
                        converted_row = [int(item) for item in row]
                        self.NetStructure.append(converted_row)  # Add each row to the NetStructure list
                    return self.NetStructure
        
        except FileNotFoundError:
            print(f"File '{self.model_filename}' not found.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
