import pandas as pd
import numpy as np
import math
import os
import shutil

def generate_traces_noc(config, num_pes_each_layer, num_in_eachLayer, chiplet_layers, dest_layers,  layer_location_begin_chiplet, netname, chiplet_size, num_chiplets, type, scale):

    # print("dest_layers:",dest_layers)
    # print("num_pes_each_layer:",num_pes_each_layer)

    dir_name = os.path.join(
    'Interconnect', 
    f'{netname}_NoC_traces', 
    f'{type}_{num_chiplets}_chiplet_size_{chiplet_size}_scale_{scale}'
    )         
    
    if (os.path.isdir(dir_name)):
        shutil.rmtree(dir_name)
    
    os.makedirs(dir_name)
    os.chdir(dir_name)
    
    num_chiplets_used = len(chiplet_layers)
    mesh_size = np.zeros([num_chiplets_used, 1])
    
    for chiplet_idx in range(0, num_chiplets_used):
        
        
        begin_layer = chiplet_layers[chiplet_idx][0]
        
        num_pes_this_chiplet = sum(num_pes_each_layer[layer] for layer in chiplet_layers[chiplet_idx])
        mesh_size[chiplet_idx] = math.ceil(math.sqrt(num_pes_this_chiplet))
        
        
        if (begin_layer == 0):
            first_pe_number = 0
        else:
            first_pe_number = sum(num_pes_each_layer[0:begin_layer])
        # print("Begin Layer is: ", begin_layer)
        # print("first_pe_number: ", first_pe_number)
        chiplet_dir_name = 'Chiplet_' + str(chiplet_idx)
        
        os.mkdir(chiplet_dir_name)
              
        for layer_idx in chiplet_layers[chiplet_idx]:
            
            for dest_layer in dest_layers[layer_idx]:
                if (layer_location_begin_chiplet[dest_layer] == chiplet_idx):
            
                    trace = np.array([[0,0,0]])
                    timestamp = 1
            
                    ip_activation_dest_layer = num_in_eachLayer[dest_layer] #
                    num_packets_this_layer = math.ceil(ip_activation_dest_layer*config.BitWidth_in/(config.pe_bus_width_2D)) #
                    num_packets_this_layer = math.ceil(num_packets_this_layer/scale) #
            
                    if (layer_idx == 0):
                        src_pe_begin = 0
                    else:
                        # src_pe_begin = sum(num_pes_each_layer[0:layer_idx-1])
                        # src_pe_begin = sum(num_pes_each_layer[0:layer_idx])
                        # src_pe_begin = sum(num_pes_each_layer[i] for i in range(layer_idx) if i in chiplet_layers[chiplet_idx])
                        src_pe_begin = math.floor(sum(num_pes_each_layer[i] for i in range(layer_idx) if i in chiplet_layers[chiplet_idx]))
                    
                    # src_pe_end = src_pe_begin + num_pes_each_layer[layer_idx] - 1
                    if (sum(num_pes_each_layer[i] for i in range(layer_idx+1) if i in chiplet_layers[chiplet_idx])) == (math.floor(sum(num_pes_each_layer[i] for i in range(layer_idx+1) if i in chiplet_layers[chiplet_idx]))):
                        src_pe_end = math.floor(sum(num_pes_each_layer[i] for i in range(layer_idx+1) if i in chiplet_layers[chiplet_idx])) - 1
                    else:
                        src_pe_end = math.floor(sum(num_pes_each_layer[i] for i in range(layer_idx+1) if i in chiplet_layers[chiplet_idx]))
            
                    # dest_pe_begin = sum(num_pes_each_layer[0:dest_layer])
                    # dest_pe_begin = sum(num_pes_each_layer[i] for i in range(dest_layer) if i in chiplet_layers[chiplet_idx])
                    dest_pe_begin = math.floor(sum(num_pes_each_layer[i] for i in range(dest_layer) if i in chiplet_layers[chiplet_idx]))
                    # dest_pe_end = dest_pe_begin + num_pes_each_layer[dest_layer] - 1
                    if (sum(num_pes_each_layer[i] for i in range(dest_layer+1) if i in chiplet_layers[chiplet_idx])) == (math.floor((sum(num_pes_each_layer[i] for i in range(dest_layer+1) if i in chiplet_layers[chiplet_idx])))):
                        dest_pe_end = math.floor(sum(num_pes_each_layer[i] for i in range(dest_layer+1) if i in chiplet_layers[chiplet_idx])) - 1
                    else:
                        dest_pe_end = math.floor(sum(num_pes_each_layer[i] for i in range(dest_layer+1) if i in chiplet_layers[chiplet_idx]))
                    
                    # if layer_idx == 404 or layer_idx == 405:
                    #     print("layer_idx:",layer_idx)
                    #     print("src_pe_begin:",src_pe_begin)
                    #     print("src_pe_end:",src_pe_end)
                    #     print("dest_pe_begin:",dest_pe_begin)
                    #     print("dest_pe_end:",dest_pe_end)
                    #     print("num_packets_this_layer:",num_packets_this_layer)
                    #     print("num_pes_each_layer[404]",num_pes_each_layer[404])
            
                    # Normalize the number to first_pe_number
                    # print("src_pe_begin before subtraction with first pe number: ", src_pe_begin)
                    # print("first_pe_number: ", first_pe_number)
                    # src_pe_begin = src_pe_begin - first_pe_number
                    # print("src_pe_begin: ", src_pe_begin)
                    # src_pe_end = src_pe_end - first_pe_number
                    # dest_pe_begin = dest_pe_begin - first_pe_number
                    # dest_pe_end = dest_pe_end - first_pe_number
            
                    for packet_idx in range(0, num_packets_this_layer):
                        for dest_pe_idx in range(dest_pe_begin, dest_pe_end+1):
                            for src_pe_idx in range(src_pe_begin, src_pe_end+1):
                                if src_pe_idx != dest_pe_idx:
                                    trace = np.append(trace, [[src_pe_idx, dest_pe_idx, timestamp]], axis=0)
                                
                            if (dest_pe_idx != dest_pe_end):
                                timestamp = timestamp + 1
                        timestamp = timestamp + 1
                    
                    trace = np.delete(trace, 0, 0)
                    filename = 'trace_file_layer_' + str(layer_idx) + '.txt'
                    os.chdir(chiplet_dir_name)
                    np.savetxt(filename, trace, fmt='%i')
                    os.chdir("..")
    
    np.savetxt('mesh_size.csv', mesh_size, fmt='%i')
    os.chdir("..")
    os.chdir("..")
