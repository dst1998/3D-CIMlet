from abc import ABC, abstractmethod

class Pack(ABC):

    @abstractmethod    
    def CalculateArea(self):
        pass

    @abstractmethod
    def CalculateLatency(self):
        pass

    @abstractmethod
    def CalculatePower(self):
        pass

class Pack2D(Pack):
    def __init__(
                self,
                mems
                ):
        
        self.mac = 
        self.memory[] = mems

    def CalculateArea(self):
        sum = 0
        for item in thid.memory:
            sum = sum + item.calculation1()
        
        pass
    def CalculateLatency(self):
        pass
    def CalculatePower(self):
        pass

class Pack2_5D(Pack):
    def __init__(self):
        pass
    def CalculateArea(self):
        pass
    def CalculateLatency(self):
        pass
    def CalculatePower(self):
        pass

class Pack3D(Pack):
    def __init__(self):
        pass
    def CalculateArea(self):
        pass
    def CalculateLatency(self):
        pass
    def CalculatePower(self):
        pass
