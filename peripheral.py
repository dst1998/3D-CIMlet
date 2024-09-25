from config import Config
from wire import Wire
import math
# class acc,buffer,noc

class Accumulator:
	def __init__(self,config,technode):
		self.clk_freq = config.clk_freq
		self.power = 0
		self.latency = 0
		self.area = 0
		self.latency_per_bit = 0 #not use
		self.energy_per_bit = 0 # depends on clk_freq
	def get_area(self):
		return 1e-12 # need change

class SoftmaxUnit:
	def __init__(self,config,technode):
		self.clk_freq = config.clk_freq
		self.latency_per_byte = 7e-7 /512 # input values: 512
		self.power = 8e-3 # input values: 512
		self.energy_per_byte = self.latency_per_byte * self.power # depends on clk_freq
		self.area = 3.00E-07 # input values: 512
	def get_area(self):
		return self.area

class Buffer:
	def __init__(self,config,technode,mem_width=128,mem_height=128):
		self.clk_freq = config.clk_freq
		self.power = 1
		self.latency = 1
		self.area = 0
		self.bandwidth = 3.18e12 # unit: scale from original constant:(ddr_bandwidth=370 GBps) * 1024 * 1024 * 1024 * 8bit
		self.energy_per_bit = 0 # depends on clk_freq
		self.mem_width = mem_width
		self.mem_height = mem_height
	def get_area(self):
		return 1e-12 # need change

class Noc:
	def __init__(self,config,technode,chiplet_type):
		self.clk_freq = config.clk_freq
		self.power = 0
		self.latency = 0
		self.area = 0
	def get_area(self):
		return 0 # not used

class Htree:
	def __init__(self,config,technode, numRow, numCol, busWidth, unitHeight, unitWidth, foldedratio=16):
		self.clk_freq = config.clk_freq
		self.energy = 0
		self.latency = 0
		self.area = 0
		self.technode = technode
		config.technode = self.technode
		self.vdd = config.vdd
		self.featureSize = config.featureSize
		self.wireWidth = config.wireWidth
		self.temp = config.temp
		self.numRow = numRow # = pe hight
		self.numCol = numCol # = pe width

		self.busWidth = busWidth # =subarray_height 
  		# numPECM*param->numRowSubArray
		# numPECM = ceil((double)(desiredTileSizeCM)/(double)(desiredPESizeCM))
		self.unitHeight = unitHeight 
		self.unitWidth = unitWidth 
		self.foldedratio = foldedratio

		self.numStage = 2*math.ceil(math.log2(max(self.numRow, self.numCol)))+1   # vertical has N stage, horizontal has N+1 stage
		unitLengthWireResistance = config.unitLengthWireResistance
		self.unitLengthWireCap = 0.2e-15/1e-6   # 0.2 fF/mm

	
		# define min INV resistance and capacitance to calculate repeater size
		# widthMinInvN = MIN_NMOS_SIZE * tech.featureSize;
		# widthMinInvP = tech.pnSizeRatio * MIN_NMOS_SIZE * tech.featureSize;
		# CalculateGateArea(INV, 1, widthMinInvN, widthMinInvP, tech.featureSize * MAX_TRANSISTOR_HEIGHT, tech, &hMinInv, &wMinInv);
		# CalculateGateCapacitance(INV, 1, widthMinInvN, widthMinInvP, hMinInv, tech, &capMinInvInput, &capMinInvOutput);
		# double resOnRep = CalculateOnResistance(widthMinInvN, NMOS, 300, tech, 0) + CalculateOnResistance(widthMinInvP, PMOS, 300, tech, 0);
		# // optimal repeater design to achieve highest speed
		# repeaterSize = floor((double)sqrt( (double) resOnRep*unitLengthWireCap/capMinInvInput/unitLengthWireResistance));
		# minDist = sqrt(2*resOnRep*(capMinInvOutput+capMinInvInput)/(unitLengthWireResistance*unitLengthWireCap));
		# CalculateGateArea(INV, 1, MIN_NMOS_SIZE * tech.featureSize * repeaterSize, tech.pnSizeRatio * MIN_NMOS_SIZE * tech.featureSize * repeaterSize, tech.featureSize * MAX_TRANSISTOR_HEIGHT, tech, &hRep, &wRep);
		# CalculateGateCapacitance(INV, 1, MIN_NMOS_SIZE * tech.featureSize * repeaterSize, tech.pnSizeRatio * MIN_NMOS_SIZE * tech.featureSize * repeaterSize, hRep, tech, &capRepInput, &capRepOutput);
		# resOnRep = CalculateOnResistance(MIN_NMOS_SIZE * tech.featureSize * repeaterSize, NMOS, 300, tech, 0) + CalculateOnResistance(tech.pnSizeRatio * MIN_NMOS_SIZE * tech.featureSize * repeaterSize, PMOS, 300, tech, 0);
		# double minUnitLengthDelay = 0.7*(resOnRep*(capRepInput+capRepOutput+unitLengthWireCap*minDist)+0.5*unitLengthWireResistance*minDist*unitLengthWireCap*minDist+unitLengthWireResistance*minDist*capRepInput)/minDist;
		# double maxUnitLengthEnergy = (capRepInput+capRepOutput+unitLengthWireCap*minDist)*tech.vdd*tech.vdd/minDist;
		
		# if (delaytolerance) {   // tradeoff: increase delay to decrease energy
		#     double delay = 0;
		#     double energy = 100;
		#     while(delay<minUnitLengthDelay*(1+delaytolerance)) {
		#         repeaterSize /=2;
		#         minDist *= 0.9;
		#         CalculateGateArea(INV, 1, MIN_NMOS_SIZE * tech.featureSize * repeaterSize, tech.pnSizeRatio * MIN_NMOS_SIZE * tech.featureSize * repeaterSize, tech.featureSize * MAX_TRANSISTOR_HEIGHT, tech, &hRep, &wRep);
		#         CalculateGateCapacitance(INV, 1, MIN_NMOS_SIZE * tech.featureSize * repeaterSize, tech.pnSizeRatio * MIN_NMOS_SIZE * tech.featureSize * repeaterSize, hRep, tech, &capRepInput, &capRepOutput);
		#         resOnRep = CalculateOnResistance(MIN_NMOS_SIZE * tech.featureSize * repeaterSize, NMOS, 300, tech, 0) + CalculateOnResistance(tech.pnSizeRatio * MIN_NMOS_SIZE * tech.featureSize * repeaterSize, PMOS, 300, tech, 0);
		#         delay = 0.7*(resOnRep*(capRepInput+capRepOutput+unitLengthWireCap*minDist)+0.5*unitLengthWireResistance*minDist*unitLengthWireCap*minDist+unitLengthWireResistance*minDist*capRepInput)/minDist;
		#         energy = (capRepInput+capRepOutput+unitLengthWireCap*minDist)*tech.vdd*tech.vdd/minDist;
		#     }
		# }
		
		# widthInvN = MAX(1,repeaterSize) * MIN_NMOS_SIZE * tech.featureSize;
		# widthInvP = MAX(1,repeaterSize) * tech.pnSizeRatio * MIN_NMOS_SIZE * tech.featureSize;
	
		#*** define center point ***#
		self.x_center = math.floor(math.log2(min(self.numRow, self.numCol)))
		self.y_center = math.floor(math.log2(min(self.numRow, self.numCol)))
		orc = 1    # over-routing constraint: (important for unbalanced tree) avoid routing outside chip boundray
		
		if (self.numCol-self.x_center < orc): 
			self.x_center -= orc

		if (self.numRow-self.y_center < orc):
			self.y_center -= orc  # redefine center point: try to slightly move to the actual chip center
		
		self.find_stage = 0   # assume the top stage as find_stage = 0
		self.hit = 0
		self.skipVer = 0
		self.totalWireLength = 0
  
  		# from Neurosim simulation when technode=22,featuresize=40e-9,wirewidth=40
		self.minDist = 0.000108832
		self.resOnRep = 86357.3
		self.capInvInput = 6.85804e-15
		self.capInvOutput = 7.14011e-16

	
	def get_area(self):
		# unitHeight = sqrt(subarray.get_area)
		# unitWidth = sqrt(subarray.get_area)

		# CalculateGateArea(INV, 1, widthInvN, widthInvP, tech.featureSize * MAX_TRANSISTOR_HEIGHT, tech, &hInv, &wInv);
		wInv=1.368e-06
  
		MAX_TRANSISTOR_HEIGHT = 28
		MAX_TRANSISTOR_HEIGHT_FINFET = 34
		hInv=1.26e-06
		if (self.featureSize <= 14 * 1e-9):  # finfet
			hInv *= (MAX_TRANSISTOR_HEIGHT_FINFET/MAX_TRANSISTOR_HEIGHT)

		
		area = 0
		self.totalWireLength = 0
		wireLengthV = self.unitHeight*pow(2, (self.numStage-1)/2)/2   # first vertical stage
		wireLengthH = self.unitWidth*pow(2, (self.numStage-1)/2)/2    # first horizontal stage (despite of main bus)
		wireWidV = 0
		wireWidH = 0
		numRepeater = 0
		
		for i in range(1, (self.numStage - 1) // 2):   # start from center point, consider both vertical and horizontal stage at each time, ignore last stage, assume it overlap with unit's layout
			wireWidth, unitLengthWireResistance = 0.0,0.0

			#*** vertical stage ***#
			wireLengthV /= 2   # wire length /2 
			wireWidth, unitLengthWireResistance = self.GetUnitLengthRes(wireLengthV)
			numRepeater = math.ceil(wireLengthV/self.minDist)
			if (numRepeater > 0):
				wireWidV += self.busWidth*wInv/self.foldedratio   # which ever stage, the sum of wireWidth should always equal to busWidth (main bus width)
			else:
				wireWidV += self.busWidth*wireWidth/self.foldedratio
			
			area += wireWidV*wireLengthV/2
			
			#*** horizontal stage ***#
			wireLengthH /= 2   # wire length /2 
			wireWidth, unitLengthWireResistance = self.GetUnitLengthRes(wireLengthH)
			numRepeater = math.ceil(wireLengthH/self.minDist)
			if (numRepeater > 0):
				wireWidH += self.busWidth*hInv/self.foldedratio   # which ever stage, the sum of wireWidth should always equal to busWidth (main bus width)
			else:
				wireWidH += self.busWidth*wireWidth/self.foldedratio
			area += wireWidH*wireLengthH/2
			
			#*** count totalWireLength ***#
			self.totalWireLength += wireLengthV + wireLengthH
		
		self.totalWireLength += min(self.numCol-self.x_center, self.x_center)*self.unitWidth
		area += (self.busWidth*hInv/self.foldedratio)*min(self.numCol-self.x_center, self.x_center)*self.unitWidth   # main bus: find the way nearest to the boundray as source
		self.area = area
		######
		# nearly 2e-08: from Neurosim 
		# [Desired Conventional Mapped Tile Storage Size: 1024x1024
		# Desired Conventional PE Storage Size: 512x512
		# User-defined SubArray Size: 128x128]
		######
		return self.area

	def GetUnitLengthRes(self,wireLength):
		AR = 0
		Rho = 0
		unitLengthWireResistance = 0

		if wireLength / self.featureSize >= 100000:
			wireWidth = 4 * self.wireWidth
		elif 10000 <= wireLength / self.featureSize <= 100000:
			wireWidth = 2 * self.wireWidth
		else:
			wireWidth = 1 * self.wireWidth

		if wireWidth >= 175:
			AR = 1.6
			Rho = 2.20e-8
		elif 110 <= wireWidth < 175:
			AR = 1.6
			Rho = 2.52e-8
		elif 105 <= wireWidth < 110:
			AR = 1.7
			Rho = 2.68e-8
		elif 80 <= wireWidth < 105:
			AR = 1.7
			Rho = 3.31e-8
		elif 56 <= wireWidth < 80:
			AR = 1.8
			Rho = 3.70e-8
		elif 40 <= wireWidth < 56:
			AR = 1.9
			Rho = 4.03e-8
		elif 25 <= wireWidth < 40:
			AR = 2.0
			Rho = 5.08e-8
		else:
			AR = 2.0
			Rho = 6.35e-8

		Rho *= (1 + 0.00451 * (self.temp - 300))

		# get unitLengthWireResistance
		if wireWidth == -1:
			unitLengthWireResistance = 1.0  # Use a small number to prevent numerical error for NeuroSim
		else:
			unitLengthWireResistance = Rho / (wireWidth * 1e-9 * wireWidth * 1e-9 * AR)
		return wireWidth, unitLengthWireResistance



	def get_latency(self, x_init, y_init, x_end, y_end, numBitToLoadOut, numBitToLoadIn):
		# x_init=0, y_init=0, x_end=0, y_end=0,unitHeight = sqrt(subarray.get_area)
		# unitWidth = sqrt(subarray.get_area)
		# numRead = ceil((numBitToLoadOut+numBitToLoadIn)/GhTree->busWidth)
		numRead = (numBitToLoadOut+numBitToLoadIn)/self.busWidth

		readLatency = 0
		
		wireLengthV = self.unitHeight*pow(2, (self.numStage-1)/2)   # first vertical stage
		wireLengthH = self.unitWidth*pow(2, (self.numStage-1)/2)    # first horizontal stage (despite of main bus)
		numRepeater = 0
		# resOnRep = CalculateOnResistance(widthInvN, NMOS, inputParameter.temperature, tech, M3D) + CalculateOnResistance(widthInvP, PMOS, inputParameter.temperature, tech, M3D);
		
		if (((not x_init) & (not y_init)) | ((not x_end) & (not y_end))): # root-leaf communicate (fixed addr)
			for i in range(1, (self.numStage - 1) // 2): # ignore main bus here, but need to count until last stage (diff from area calculation)
				wireWidth, unitLengthWireResistance = 0.0,0.0
			
				#*** vertical stage ***#
				wireLengthV /= 2   # wire length /2 
				wireWidth, unitLengthWireResistance = self.GetUnitLengthRes(wireLengthV)
				unitLatencyRep = 0.7*(self.resOnRep*(self.capInvInput+self.capInvOutput+self.unitLengthWireCap*self.minDist)+0.5*unitLengthWireResistance*self.minDist*self.unitLengthWireCap*self.minDist+unitLengthWireResistance*self.minDist*self.capInvInput)/self.minDist
				unitLatencyWire = 0.7*unitLengthWireResistance*self.minDist*self.unitLengthWireCap*self.minDist/self.minDist
				numRepeater = math.ceil(wireLengthV/self.minDist)
				if (numRepeater > 0):
					readLatency += wireLengthV*unitLatencyRep
				else:
					readLatency += wireLengthV*unitLatencyWire
				
				#*** horizontal stage ***#
				wireLengthH /= 2   # wire length /2 
				wireWidth, unitLengthWireResistance = self.GetUnitLengthRes(wireLengthH)
				unitLatencyRep = 0.7*(self.resOnRep*(self.capInvInput+self.capInvOutput+self.unitLengthWireCap*self.minDist)+0.5*unitLengthWireResistance*self.minDist*self.unitLengthWireCap*self.minDist+unitLengthWireResistance*self.minDist*self.capInvInput)/self.minDist
				unitLatencyWire = 0.7*unitLengthWireResistance*self.minDist*self.unitLengthWireCap*self.minDist/self.minDist
				numRepeater = math.ceil(wireLengthH/self.minDist)
				if (numRepeater > 0):
					readLatency += wireLengthH*unitLatencyRep
				else:
					readLatency += wireLengthH*unitLatencyWire
			
			#*** main bus ***#
			readLatency += min(self.numCol-self.x_center, self.x_center)*self.unitWidth*unitLatencyRep
		readLatency *= numRead
		self.latency = readLatency
		#####
		# nearly 2e-05 each Transformer layer: from Neurosim 
		# [Desired Conventional Mapped Tile Storage Size: 1024x1024
		# Desired Conventional PE Storage Size: 512x512
		# User-defined SubArray Size: 128x128]
		#####
		return self.latency
	def get_energy(self,
                x_init, y_init, x_end, y_end, numBitToLoadOut,numBitToLoadIn):
		# x_init=0, y_init=0, x_end=0, y_end=0,unitHeight = sqrt(subarray.get_area)
		# unitWidth = sqrt(subarray.get_area)
		# numRead = ceil((numBitToLoadOut+numBitToLoadIn)/GhTree->busWidth)
		numBitAccess = self.busWidth
		numRead = (numBitToLoadOut+numBitToLoadIn)/self.busWidth
		
		# leakage = 0
		readDynamicEnergy = 0
		
		# unitLengthLeakage = CalculateGateLeakage(INV, 1, widthInvN, widthInvP, inputParameter.temperature, tech) * tech.vdd / minDist
		# leakage = unitLengthLeakage * self.totalWireLength
		unitLengthEnergyRep = (self.capInvInput+self.capInvOutput+self.unitLengthWireCap*self.minDist)*self.vdd*self.vdd/self.minDist*0.25
		unitLengthEnergyWire = (self.unitLengthWireCap*self.minDist)*self.vdd*self.vdd/self.minDist*0.25
		wireLengthV = self.unitHeight*pow(2, (self.numStage-1)/2)/2   # first vertical stage
		wireLengthH = self.unitWidth*pow(2, (self.numStage-1)/2)/2    # first horizontal stage (despite of main bus)
		
		if (((not x_init) & (not y_init)) | ((not x_end) & (not y_end))):
      	# root-leaf communicate (fixed addr)
			for i in range(1, (self.numStage - 1) // 2): # ignore main bus here, but need to count until last stage (diff from area calculation)
				#*** vertical stage ***#
				wireLengthV /= 2   # wire length /2 
				numRepeater = math.ceil(wireLengthV/self.minDist)
				if (numRepeater > 0):
					readDynamicEnergy += wireLengthV*unitLengthEnergyRep
				else:
					readDynamicEnergy += wireLengthV*unitLengthEnergyWire
				
				#*** horizontal stage ***#
				wireLengthH /= 2   # wire length /2 
				numRepeater = math.ceil(wireLengthH/self.minDist)
				if (numRepeater > 0):
					readDynamicEnergy += wireLengthH*unitLengthEnergyRep
				else:
					readDynamicEnergy += wireLengthH*unitLengthEnergyWire
	
			#*** main bus ***#
			readDynamicEnergy += min(self.numCol-self.x_center, self.x_center)*self.unitWidth*unitLengthEnergyRep
			readDynamicEnergy *= numBitAccess  
		readDynamicEnergy *= numRead
		self.energy = readDynamicEnergy
		#####
		# nearly 3.5e-07 each Transformer layer: from Neurosim 
		# [Desired Conventional Mapped Tile Storage Size: 1024x1024
		# Desired Conventional PE Storage Size: 512x512
		# User-defined SubArray Size: 128x128]
		#####
		return self.energy

# TODO: factor in, e.g. latency and energy/power is xxx% of total chip.    
class ClkTree:
	def __init__(self,config,technode):
		self.clk_freq = config.clk_freq
		self.power = 0
		self.latency = 0
		self.area = 0
	def get_area(self):
		return self.area

# TODO: factor in, e.g. latency and energy/power is xxx% of total chip.
class Controller:
	def __init__(self,config,technode):
		self.clk_freq = config.clk_freq
		self.power = 0
		self.latency = 0
		self.area = 0
	def get_area(self):
		return self.area
