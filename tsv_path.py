import math

class TSVPath():
    def __init__(self):
        self.tsvPitch = 1.7e-6
        self.tsvRes = 0.3
        self.tsvCap = 20e-15

    def CalculateArea(self):
        self.area = (pow(self.tsvPitch, 2))
        return self.area

        # hInv, wInv = CalculateGateArea(self.INV, 1, self.MIN_NMOS_SIZE*self.tech.featureSize, self.tech.pnSizeRatio*self.MIN_NMOS_SIZE*self.tech.featureSize, self.tech.featureSize*self.MAX_TRANSISTOR_HEIGHT, self.tech)
        # self.area = (2*hInv*wInv + pow(self.tsvPitch, 2))
        
        # self.capInvInput, self.capInvOutput = CalculateGateCapacitance(self.INV, 1, self.widthInvN, self.widthInvP, hInv, self.tech)

    def CalculateLatency(self):
        self.latency = 3 * self.tsvRes * self.tsvCap # 3~5 tau
        return self.latency
        
        # self.readLatency = 0
        # rampInput = 1e20
        
        # resPullUp = CalculateOnResistance(self.widthInvP, self.PMOS, self.inputParameter.temperature, self.tech)
        # tr = resPullUp * (self.capInvOutput + self.tsvCap*numTSV)
        # gm = self.CalculateTransconductance(self.widthInvP, self.PMOS, self.tech)
        # beta = 1 / (resPullUp * gm)
        # self.readLatency += horowitz(tr, beta, rampInput)
        
        # resPullDown = self.tsvRes*numTSV
        # tr = resPullDown * self.capInvInput
        # self.readLatency += horowitz(tr, beta, rampInput)
        
        # if self.inputParameter.synchronous:
        #     self.readLatency = math.ceil(self.readLatency * self.clkFreq)  # #cycles
        # self.readLatency *= numRead

    def CalculatePower(self):
        self.freq = 1e9
        self.vdd = 1
        self.delta = 0.15 # switching activity of adder, delta = 0.15 by default
        self.i_leak = 1e-9 # [need change] e-9~e-6?
        self.leakPower = self.i_leak * self.vdd
        self.dynamicPower = self.tsvCap * self.vdd * self.vdd * self.delta * self.freq
        return self.dynamicPower

        
        # self.leakage = 0
        # self.readDynamicEnergy = 0
        
        # self.leakage += CalculateGateLeakage(self.INV, 1, self.widthInvN, self.widthInvP, self.inputParameter.temperature, self.tech) * self.tech.vdd * (self.inputParameter.numRowSubArray+self.inputParameter.numColSubArray)
        
        # self.readDynamicEnergy += (self.capInvInput + self.capInvOutput + self.inputParameter.tsvCap) * self.tech.vdd ** 2
        # self.readDynamicEnergy *= numRead
        # if self.inputParameter.validated:
        #     self.readDynamicEnergy *= self.inputParameter.delta  # switching activity of adder, delta = 0.15 by default


# def horowitz(tr, beta, rampInput, rampOutput=None):
#     alpha = 1 / rampInput / tr
#     vs = 0.5  # Normalized switching voltage
#     beta = 0.5  # Just use beta=0.5 as CACTI because we do not want to consider gm anymore
#     result = tr * math.sqrt(math.log(vs) ** 2 + 2 * alpha * beta * (1 - vs))
#     if rampOutput is not None:
#         rampOutput = (1 - vs) / result
#     return result