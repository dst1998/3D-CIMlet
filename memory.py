from abc import ABC, abstractmethod

class Memory(ABC):

    @abstractmethod
    def CalculateMemArea(self):
        pass

    @abstractmethod
    def CalculateMemLatency(self):
        pass

    @abstractmethod
    def CalculateMemPower(self):
        pass

class SRAM(Memory):
    def __init__(
                self,
                width,
                height,
                technode,
                cell_read_cycle, cell_write_cycle,
                cell_read_latency=1*1e-6, cell_read_energy=1*1e-6, # 2 random value: should be replaced by (# of clk)
                cell_write_latency=1*1e-6, cell_write_energy=1*1e-6,  # 2 random value: should be replaced by (# of clk)
                cell_leak_power = 1*1e-6 # random value
                ):
        self.width = width
        self.height = height
        self.technode = technode
        self.cell_read_cycle = cell_read_cycle
        self.cell_read_latency = cell_read_latency
        self.cell_read_energy = cell_read_energy
        self.cell_write_cycle = cell_write_cycle
        self.cell_write_latency = cell_write_latency
        self.cell_write_energy = cell_write_energy
        self.cell_leak_power = cell_leak_power
        
    def CalculateMemArea(self):
        technode = self.technode * 1e-9 # change to nm
        area = self.width * self.height * (technode **2)
        return area
    def CalculateMemLatency(self):
        read_latency = self.cell_read_cycle * self.cell_read_latency # depends on ADC read-out pipeline. assume sequential read-out here.
        write_latency = self.cell_write_cycle * self.cell_write_latency
        return read_latency, write_latency
    def CalculateMemPower(self):
        read_energy = self.cell_read_cycle * self.cell_read_energy
        write_energy = self.cell_write_cycle * self.cell_write_energy
        leak_power = self.cell_leak_power * self.width * self.height 
        # SRAM: leak_energy = leak_power * whole_latency, whole_latency is generated after 1 inference/ 1 module
        return read_energy, write_energy, leak_power

class eDRAM(Memory):
    def __init__(self) -> None:
        super().__init__()
        pass
    def CalculateMemArea(self):
        pass
    def CalculateMemLatency(self):
        pass
    def CalculateMemPower(self):
        pass

class Regfile(Memory):
    def __init__(self) -> None:
        super().__init__()
        pass
    def CalculateMemArea(self):
        pass
    def CalculateMemLatency(self):
        pass
    def CalculateMemPower(self):
        pass

class NVM(Memory): # subclass: 2d/3d FeFET,RRAM,PCM
    def __init__(self) -> None:
        super().__init__()
        pass
    def CalculateMemArea(self):
        pass
    def CalculateMemLatency(self):
        pass
    def CalculateMemPower(self):
        pass