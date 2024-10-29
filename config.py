import csv
import sys

class Config:
	def __init__(self):
		self.model_filename = 'Transformer_adapter_cl_3layer_12head_16token.csv'
		self.net_name = self.model_filename.rsplit('.csv', 1)[0]
		self.NetStructure = []
		self.NetStructure_layer_def = []
		self.num_T_head = 12
		self.clk_freq = 800e6 # TODO: depends on technode and memory device type (e.g. edram or rram)
		self.eDRAM_clk_freq = 200e6
		self.RRAM_clk_freq = 800e6
		self.nop_clk_freq_2d = 0.2E09 # 5.3e9 (MCM:pin speed)
		self.nop_clk_freq_2_5d_3d = 0.2E09 # 0.2GHz
		# self.nop_bw_density_2_5d = 1.6E12 # CoWoS: 1.6 Tb/s/mm2
		# self.nop_bw_density_3d = 9456E12 # 3D SoIC F2B (SoIC bond & TSV) 9456 Tb/s/mm2
		self.Packaging_dimension = 2.5 # 2, 2.5, 3
		self.pitch_size_2_5d = 40E-06 # CoWoS
		self.pitch_size_3d = 9E-06 # 3D SoIC F2B (SoIC bond & TSV)

		# eDRAM calibrated data, cell size include peripheral
		# self.eDRAM_cell_size_40nm = 1.35e05 * 1e-12 / (256*128)
		self.eDRAM_cell_size_40nm = 57564 * 1E-12 / (256*128)
		self.eDRAM_read_energy_per_bit_40nm = 0.04e-12
		self.eDRAM_write_energy_per_bit_40nm = 0.1e-12

		self.eDRAM_cell_size_28nm = 0.002769 * 1e-6 / (0.008e06)
		self.eDRAM_read_energy_per_bit_28nm = 7.2e-12 * (1/3) * 0.155e-03 * (200/66) # refresh: 7.2e-12W/b, 66MHz (scale to 200MHz),retention time=0.155ms
		self.eDRAM_write_energy_per_bit_28nm = 7.2e-12 * (2/3)* 0.155e-03 * (200/66) # refresh: 7.2e-12W/b, 66MHz (scale to 200MHz),retention time=0.155ms

		self.eDRAM_cell_size_65nm = 0.047096688 * 1e-6 / (0.024e06)
		self.eDRAM_read_energy_per_bit_65nm = 3.54e-03/(0.024*1024*1024) * (1/3) * 0.04e-03 # refresh: 3.54mW/0.024Mb, 200MHz,retention time=0.04ms
		self.eDRAM_write_energy_per_bit_65nm = 3.54e-03/(0.024*1024*1024) * (2/3) * 0.04e-03 # refresh: 3.54mW/0.024Mb, 200MHz,retention time=0.04ms

		self.eDRAM_cell_size_130nm = 0.268 * 1e-6 / (0.064e06)
		self.eDRAM_read_energy_per_bit_130nm = 4.9e-03/(0.064*1024*1024) * (1/3) * 0.95e-03 # refresh: 4.9mW/0.064Mb, 200MHz,retention time=0.95ms
		self.eDRAM_write_energy_per_bit_130nm = 4.9e-03/(0.064*1024*1024) * (2/3) * 0.95e-03 # refresh: 4.9mW/0.064Mb, 200MHz,retention time=0.95ms

		# RRAM calibrated data, cell size include peripheral
		self.RRAM_cell_size_40nm = 6.34e04 * 1e-12 / (256*256) # Luqi
		self.RRAM_read_energy_per_bit_40nm = 0.14e-12 # Luqi
		self.RRAM_write_energy_per_bit_40nm = 2.3e-12 # Luqi
		# self.RRAM_read_energy_per_bit_40nm = 1e-12 # Luke
		# self.RRAM_write_energy_per_bit_40nm = 400e-12 # Luke

		self.RRAM_cell_size_130nm = 3.03 * 1e-6 / (0.0625*1e6)
		self.RRAM_read_energy_per_bit_130nm = 1.36e-12
		self.RRAM_write_energy_per_bit_130nm = 10e-12
		

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
		self.dynamic_pe_height = 8 # num of subarray rows in a pe
		self.dynamic_pe_width = 8 # num of subarray cols in a pe
		self.dynamic_pe_size = self.dynamic_pe_height * self.dynamic_pe_width

		# -----chiplet-----
		# -----static chiplet-----
		self.static_chiplet_technode = 40 # 40, 130
		self.static_chiplet_memory_cell_type = 'RRAM'
		self.num_static_chiplet = 20
		self.static_chiplet_height = 8 # num of PE rows in a chiplet
		self.static_chiplet_width = 4 # num of PE cols in a chiplet
		self.static_chiplet_size = self.static_chiplet_height * self.static_chiplet_width
		
		# -----dynamic chiplet-----
		self.dynamic_chiplet_technode = 28 # 28,40,65,130
		self.dynamic_chiplet_memory_cell_type = 'eDRAM'
		self.num_dynamic_chiplet = 9
		self.dynamic_chiplet_height = 8 # num of PE rows in a chiplet
		self.dynamic_chiplet_width = 4 # num of PE cols in a chiplet
		self.dynamic_chiplet_size = self.dynamic_chiplet_height * self.dynamic_chiplet_width
		
		# -----logic chiplet-----
		self.logic_chiplet_technode = 40
		self.global_buffer_core_height = 128 # global buffer only in logic chiplet
		self.global_buffer_core_width = 128 # global buffer only in logic chiplet
		self.chip_buffer_core_height = 128
		self.chip_buffer_core_width = 128
		self.pe_buffer_core_height = 32 
		self.pe_buffer_core_width = 32

		self.BitWidth_in = 8
		self.BitWidth_weight = 8

		self.pe_bus_width_2D = 32 # SIAM: 32
		self.chiplet_bus_width_2D = 32 # SIAM: 8,16,32
		self.scale_noc = 100 # SIAM: 100
		self.scale_nop = 10 # SIAM: 10
		self.type = 'Homogeneous_Design'
		
		self.eDRAM_refresh_retention_time_28nm = 0.155e-03
		self.eDRAM_refresh_retention_time_40nm = 20e-6
		self.eDRAM_refresh_retention_time_65nm = 0.04e-03
		self.eDRAM_refresh_retention_time_130nm = 0.95e-03
		self.RRAM_refresh_retention_time_28nm = 1e6
		self.RRAM_refresh_retention_time_40nm = 1e6
		self.RRAM_refresh_retention_time_65nm = 1e6
		self.RRAM_refresh_retention_time_130nm = 1e6
  
		self.RRAM_refresh_retention_time = 1e6
		
		# from Neurosim:
		AR = 0
		Rho = 0
		self.wireWidth = 0 
		memcelltype = 'RRAM' 
		accesstype = 1  
		self.temp = 300       # Temperature (K)
		self.technode = 22 
		self.featureSize = 40e-9    # Wire width for subArray simulation

		heightInFeatureSizeSRAM = 10  
		widthInFeatureSizeSRAM = 10   
		heightInFeatureSize1T1R = 10  
		widthInFeatureSize1T1R = 10   
		heightInFeatureSizeCrossbar = 10  
		widthInFeatureSizeCrossbar = 10   

		# Initialize interconnect wires
		# def update_params(self, technode):
		if self.technode == 130:
			self.wireWidth = 175
			self.featureSize = 175e-9
			self.vdd = 1.3
			AR = 1.60
			Rho = 2.20e-8
		elif self.technode == 90:
			self.wireWidth = 110
			self.featureSize = 110e-9 
			self.vdd = 1.2
			AR = 1.60
			Rho = 2.52e-8
		elif self.technode == 65:
			self.wireWidth = 105
			self.featureSize = 105e-9
			self.vdd = 1.1
			AR = 1.70
			Rho = 2.68e-8
		elif self.technode == 45:
			self.wireWidth = 80
			self.featureSize = 80e-9 
			self.vdd = 1.0
			AR = 1.70
			Rho = 3.31e-8
		elif self.technode == 40: # need second-order calibration
			self.wireWidth = 70 
			self.featureSize = 70e-9 
			self.vdd = 0.9
			AR = 1.75 
			Rho = 3.50e-8
		elif self.technode == 32:
			self.wireWidth = 56
			self.featureSize = 56e-9 
			self.vdd = 0.9
			AR = 1.80
			Rho = 3.70e-8
		elif self.technode == 28: # need second-order calibration
			self.wireWidth = 50 
			self.featureSize = 50e-9 
			self.vdd = 0.9
			AR = 1.80 
			Rho = 3.80e-8 
		elif self.technode == 22:
			self.wireWidth = 40
			self.featureSize = 40e-9 
			self.vdd = 0.85
			AR = 1.90
			Rho = 4.03e-8
		elif self.technode == 14:
			self.wireWidth = 25
			self.featureSize = 25e-9 
			self.vdd = 0.8
			AR = 2.00
			Rho = 5.08e-8
		elif self.technode == 10:
			self.vdd = 0.75
			self.wireWidth = 18
			self.featureSize = 18e-9 
			AR = 2.00
			Rho = 6.35e-8
		elif self.technode == 7:
			self.vdd = 0.7
			self.wireWidth = 18
			self.featureSize = 18e-9 
			AR = 2.00
			Rho = 6.35e-8
		else:
			self.wireWidth = -1 # Ignore wire resistance or user define
			print("tachnode:",self.technode)
			sys.exit("Wire width out of range")

		# get wireLengthRow, wireLengthCol
		heightInFeatureSizeSRAM = 10        # SRAM Cell height in feature size  
		widthInFeatureSizeSRAM = 28        # SRAM Cell width in feature size 
		heightInFeatureSize1T1R = 4        # 1T1R Cell height in feature size
		widthInFeatureSize1T1R = 12         # 1T1R Cell width in feature size
		heightInFeatureSizeCrossbar = 2    # Crossbar Cell height in feature size
		widthInFeatureSizeCrossbar = 2     # Crossbar Cell width in feature size
		
		if memcelltype == 'SRAM':
			wireLengthRow = self.wireWidth * 1e-9 * heightInFeatureSizeSRAM
			wireLengthCol = self.wireWidth * 1e-9 * widthInFeatureSizeSRAM
		elif memcelltype == 'RRAM':
			if accesstype == 1:
				wireLengthRow = self.wireWidth * 1e-9 * heightInFeatureSize1T1R
				wireLengthCol = self.wireWidth * 1e-9 * widthInFeatureSize1T1R
			else:
				wireLengthRow = self.wireWidth * 1e-9 * heightInFeatureSizeCrossbar
				wireLengthCol = self.wireWidth * 1e-9 * widthInFeatureSizeCrossbar
		else: #'eDRAM'
			pass
			

		# get resistance
		Rho *= (1 + 0.00451 * abs(self.temp - 300))
		if self.wireWidth == -1:
			self.unitLengthWireResistance = 1.0  # Use a small number to prevent numerical error for NeuroSim
			wireResistanceRow = 0
			wireResistanceCol = 0
		else:
			self.unitLengthWireResistance = Rho / (self.wireWidth * 1e-9 * self.wireWidth * 1e-9 * AR)
			wireResistanceRow = self.unitLengthWireResistance * wireLengthRow
			wireResistanceCol = self.unitLengthWireResistance * wireLengthCol

	def update_params(self, technode):
		if technode == 130:
			self.wireWidth = 175
			self.featureSize = 175e-9
			self.vdd = 1.3
			AR = 1.60
			Rho = 2.20e-8
		elif technode == 90:
			self.wireWidth = 110
			self.featureSize = 110e-9 
			self.vdd = 1.2
			AR = 1.60
			Rho = 2.52e-8
		elif technode == 65:
			self.wireWidth = 105
			self.featureSize = 105e-9
			self.vdd = 1.1
			AR = 1.70
			Rho = 2.68e-8
		elif technode == 45:
			self.wireWidth = 80
			self.featureSize = 80e-9 
			self.vdd = 1.0
			AR = 1.70
			Rho = 3.31e-8
		elif technode == 40: # need second-order calibration
			self.wireWidth = 70 
			self.featureSize = 70e-9 
			self.vdd = 0.9
			AR = 1.75 
			Rho = 3.50e-8
		elif technode == 32:
			self.wireWidth = 56
			self.featureSize = 56e-9 
			self.vdd = 0.9
			AR = 1.80
			Rho = 3.70e-8
		elif technode == 28: # need second-order calibration
			self.wireWidth = 50 
			self.featureSize = 50e-9 
			self.vdd = 0.9
			AR = 1.80 
			Rho = 3.80e-8 
		elif technode == 22:
			self.wireWidth = 40
			self.featureSize = 40e-9 
			self.vdd = 0.85
			AR = 1.90
			Rho = 4.03e-8
		elif technode == 14:
			self.wireWidth = 25
			self.featureSize = 25e-9 
			self.vdd = 0.8
			AR = 2.00
			Rho = 5.08e-8
		elif technode == 10:
			self.vdd = 0.75
			self.wireWidth = 18
			self.featureSize = 18e-9 
			AR = 2.00
			Rho = 6.35e-8
		elif technode == 7:
			self.vdd = 0.7
			self.wireWidth = 18
			self.featureSize = 18e-9 
			AR = 2.00
			Rho = 6.35e-8
		else:
			self.wireWidth = -1 # Ignore wire resistance or user define
			print("tachnode:",technode)
			sys.exit("Wire width out of range")	
	
	def load_model(self):
		try:
			with open(self.model_filename, mode='r', newline='') as file:
				csv_reader = csv.reader(file)
				first_row = next(csv_reader)  # Read the first line to determine the model type
				if (first_row[1] in ["Transformer_inf","Transformer_adapter_inf","Transformer_adapter_cl","Transformer_ft"]):
					for row in csv_reader:
						row = row[:-1]
						converted_row = [int(item) for item in row]
						self.NetStructure.append(converted_row)  # Add each row to the NetStructure list
					return self.NetStructure
		
		except FileNotFoundError:
			print(f"File '{self.model_filename}' not found.")
		except Exception as e:
			print(f"An error occurred: {str(e)}")
	
	def load_model_layer_def(self):
		try:
			with open(self.model_filename, mode='r', newline='') as file:
				csv_reader = csv.reader(file)
				first_row = next(csv_reader)  # Read the first line to determine the model type
				if first_row[1] in ["Transformer_inf", "Transformer_adapter_inf", "Transformer_adapter_cl","Transformer_ft"]:
					for row in csv_reader:
						row_def = row[-1]
						self.NetStructure_layer_def.append(row_def)  # Add each row to the NetStructure list1
					return self.NetStructure_layer_def
		
		except FileNotFoundError:
			print(f"File '{self.model_filename}' not found.")
		except Exception as e:
			print(f"An error occurred: {str(e)}")
