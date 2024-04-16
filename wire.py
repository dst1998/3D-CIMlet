class Wire():
    def __init__(self,technode):
        self.technode = technode
        self.wireWidth = 0
        self.AR = 0
        self.Rho = 0
        self.unitLengthResistance = 0
        self.unitLengthCap = 0.2e-15/1e-6; # 0.2 fF/mm
    
    def get_wire_properties(self):
        if self.technode == 130:
            self.wireWidth = 175 * 1e-9
            self.AR = 1.60
            self.Rho = 2.20e-8
        elif self.technode == 90:
            self.wireWidth = 110 * 1e-9
            self.AR = 1.60
            self.Rho = 2.52e-8
        elif self.technode == 65:
            self.wireWidth = 105 * 1e-9
            self.AR = 1.70
            self.Rho = 2.68e-8
        elif self.technode == 45:
            self.wireWidth = 80 * 1e-9
            self.AR = 1.70
            self.Rho = 3.31e-8
        elif self.technode == 32:
            self.wireWidth = 56 * 1e-9
            self.AR = 1.80
            self.Rho = 3.70e-8
        elif self.technode == 22:
            self.wireWidth = 40 * 1e-9
            self.AR = 1.90
            self.Rho = 4.03e-8
        elif self.technode == 14:
            self.wireWidth = 25 * 1e-9
            self.AR = 2.00
            self.Rho = 5.08e-8
        elif self.technode in [7, 10]:
            self.wireWidth = 18 * 1e-9
            self.AR = 2.00
            self.Rho = 6.35e-8
        else:
            print("Technode out of range")
            return None
        
    def get_wire_width(self):
        return self.wireWidth
    
    def get_wire_unitLengthResistance(self):
        self.unitLengthResistance =  self.Rho / ( self.wireWidth * self.wireWidth * self.AR )
        return self.unitLengthResistance
    
    def get_wire_unitLengthLatency(self):
        self.unitLengthLatency = 3*self.get_wire_unitLengthResistance() * self.unitLengthCap
        return self.unitLengthLatency 
    
    def get_wire_unitLengthArea(self):
        self.unitArea = self.wireWidth **2
        return self.unitArea
    
    def get_wire_unitLengthDynPower(self):
        self.freq = 1e9
        self.vdd = 1
        self.delta = 0.15 # switching activity of adder, delta = 0.15 by default
        self.StaticWire_unitLengthDynPower = self.unitLengthCap * self.vdd * self.vdd * self.delta * self.freq
        return self.StaticWire_unitLengthDynPower
        


    # wireLength_PE_Row = wireWidth * heightInFeatureSize * PE_size_col
    # wireLength_PE_Col = wireWidth * widthInFeatureSize * PE_size_col

    # temp = 300
    # Rho *= (1+0.00451*abs(temp-300))

    # unitLengthWireResistance =  Rho / ( wireWidth*1e-9 * wireWidth*1e-9 * AR )
    # wireResistanceRow = unitLengthWireResistance * wireLengthRow
    # wireResistanceCol = unitLengthWireResistance * wireLengthCol


# technode = 45
# W = Wire(technode)
# W.get_wire_properties()
# print(W.get_wire_unitLengthLatency())
# print(W.get_wire_unitLengthArea())
