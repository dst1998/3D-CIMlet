# MAC Macro
from abc import ABC, abstractmethod

class Mac(ABC):

    @abstractmethod    
    def CalculateMacArea(self):
        pass

    @abstractmethod
    def CalculateMacLatency(self):
        pass

    @abstractmethod
    def CalculateMacPower(self):
        pass

class InMemoryCompute(Mac):
    def __init__(
                self,
                width,
                height,
                technode
                ):
        self.width = width
        self.height = height
        self.technode = technode

    def CalculateMacArea(self):
        pass # get from Neurosim
    def CalculateMacLatency(self):
        pass
    def CalculateMacPower(self):
        pass

class NearMemoryCompute(Mac):
    def __init__(self):
        pass
    def CalculateMacArea(self):
        pass
    def CalculateMacLatency(self):
        pass
    def CalculateMacPower(self):
        pass

class DigitalPE(Mac):
    def __init__(self):
        pass
    def CalculateMacArea(self):
        pass
    def CalculateMacLatency(self):
        pass
    def CalculateMacPower(self):
        pass