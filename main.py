def main():
    model_data = GetData(model_file, config_file).load_model()
    hw_configs = GetData(model_file, config_file).load_hardware_config()

    for hw_config in hw_configs:
        for data_flow in data_flows:
            mem_instance_list[], PE_instance  = analytical_model(model_data, hw_config)
            #data flow: read and write cycles for each memory, mac operation cycles for PE

            # memory
            for i in len(mem_instance_list[]):
                mem_instance_list[i].energy = memorySubClass(mem_instance_list[i]).getEnergy
                mem_instance_list[i].latency = memorySubClass(mem_instance_list[i]).getLatency
                mem_instance_list[i].area = memorySubClass(mem_instance_list[i]).getArea

            # PE
            PE_instance.energy = PESubClass(PE_instance).getEnergy
            PE_instance.latency = PESubClass(PE_instance).getLatency
            PE_instance.area = PESubClass(PE_instance).getArea
            if (PE_instance.type == CIM):
                for ADC in ADCType[]:
                # ADC chosen from provided list or user-definition info    
                    PE_instance.energy += (hTree.energy + ADC.energy)
                    PE_instance.latency += (hTree.latency + ADC.latency)
                    PE_instance.area += (hTree.area + ADC.area)
            
            # Now get all attributes of mem and PE instances.

            # go through packaing cases loop
            for pack in pack_list[3]:
                chips[]
                if pack == 2:
                    new chip()
                    # area
                    chip.Area = sum(memArea, PEArea)
                    # energy, latency
                    if noPipeline:
                        chip.energy = sum(memEnergy, PEEnergy)
                        chip.latency = sum(memLatency,PELatency) 
                    else:
                        ...
                    #no factor in data transferring 
                    
                    chips[].append(chip)
                
                if pack == 2.5:
                   for option in stack_options:
                        # area
                        chip.Area = sum(memArea, PEArea)
                        # energy, latency
                        ...

                        # data transferring, for loop of all mem and PE components
                        for i in iloop:
                            for j in jloop:
                                if data_trasnfer[][] != 0: # transfer betwwen m-m or m-c
                                    chip.energy +=  data_transfer.energy
                                    chip.latency += data_transfer.latency

        
                else if pack ==3:
                    for option in stack_options:
                        # area
                        chip.Area = max(eachLayer.area)
                        # energy, latency



        mems = [] #list of used memory instances
    for i in input.len:
        if(key==MemoryCellType_SRAM){
            num = value[1]
            w = value[2]
            h = value[3]
            new sRAM =(value1,value2,value3)
            mems.push(sRAM)
        }elif(key==...){
            same
            mems.push(bRAM)
        }...

    Pack2D(mems)