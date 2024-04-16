import numpy as np
import math
import os
import shutil

#Take all below parameters as argument
#quantization_bit = 8
#bus_width = 32
#netname = 'VGG-19_45.3M'
#xbar_size = 256
#chiplet_size = 9
#num_chiplets = 144
#type = 'Homogeneous Design'
#scale = 100

def generate_trace_noc(Num_StaticPE_eachLayer, Num_DynamicPE_eachLayer, Num_Output_eachLayer, Num_Weight_eachLayer,
                        BitWidth_in, BitWidth_weight, bus_width):
    
    num_layer = len(Num_StaticPE_eachLayer)

    # num_StaticPE_each_layer = []
    # num_DynamicPE_each_layer = []    
    # num_activations_each_layer = []
    # num_weights_each_layer = []
    
    PE_begin_array = [] # 0, 72, 。。。
    PE_end_array = []  # 71, 144, 。。。
        
        
    # begin_layer = tile_begin_array[chiplet_idx]
    # # print("Begin Layer: ", begin_layer)
    # end_layer = tile_end_array[chiplet_idx]
    # # print("End Layer: ", end_layer)
    
    
    # if (begin_layer == 0):
    #     first_tile_number = 0
    # else:
    #     first_tile_number = sum(num_tiles_each_layer[0:begin_layer])
    # # print("Begin Layer is: ", begin_layer)
    # # print("first_tile_number: ", first_tile_number)
    # chiplet_dir_name = 'Chiplet_' + str(chiplet_idx)
    
    # os.mkdir(chiplet_dir_name)
    trace_all_layers = []
    
    for layer_idx in range(num_layer-1): # 100 layers, layer_idx = 0~98
        
        # if (layer_idx+1) < num_layer:
        trace = np.array([[0,0,0]])
        timestamp = 1

        num_output_bits_this_layer = Num_Output_eachLayer[layer_idx] * BitWidth_in
        num_PE_this_layer = Num_StaticPE_eachLayer[layer_idx] + Num_DynamicPE_eachLayer[layer_idx]
        num_output_bits_perPE_this_layer = math.ceil(num_output_bits_this_layer / num_PE_this_layer)
        num_outputPackets_perPE_this_layer= math.ceil(num_output_bits_perPE_this_layer / bus_width)

        # num_packets_this_layer = math.ceil(num_output_bits_this_layer / bus_width)

        if Num_StaticPE_eachLayer[layer_idx]: # this layer is static layer
            if Num_StaticPE_eachLayer[layer_idx+1]==0: # next layer is dynamic
                if (layer_idx == 0):
                    src_PE_begin = 0
                else:
                    src_PE_begin = sum(Num_StaticPE_eachLayer[0:layer_idx])

                src_PE_end = src_PE_begin + Num_StaticPE_eachLayer[layer_idx] - 1

                dest_PE_begin =  sum(Num_StaticPE_eachLayer) + sum(Num_DynamicPE_eachLayer[0:layer_idx+1])
                dest_PE_end = dest_PE_begin + Num_DynamicPE_eachLayer[layer_idx+1] - 1

                # print("sta to dyn")
                # print("src_PE_begin:",src_PE_begin)
                # print("src_PE_end:",src_PE_end)
                # print("dest_PE_begin:",dest_PE_begin)
                # print("dest_PE_end:",dest_PE_end)
            
            else: # next layer is static layer
                if (layer_idx == 0):
                    src_PE_begin = 0
                else:
                    src_PE_begin = sum(Num_StaticPE_eachLayer[0:layer_idx])

                src_PE_end = src_PE_begin + Num_StaticPE_eachLayer[layer_idx] - 1

                dest_PE_begin = src_PE_end + 1
                dest_PE_end = dest_PE_begin + Num_StaticPE_eachLayer[layer_idx+1] - 1

                # print("sta to sta")
                # print("src_PE_begin:",src_PE_begin)
                # print("src_PE_end:",src_PE_end)
                # print("dest_PE_begin:",dest_PE_begin)
                # print("dest_PE_end:",dest_PE_end)

        else: # Num_StaticPE_eachLayer[layer_idx]==0: # this layer is dynamic layer
            if Num_StaticPE_eachLayer[layer_idx+1]==0: # next layer is dynamic
                if (layer_idx == 0):
                    src_PE_begin = sum(Num_StaticPE_eachLayer)
                else:
                    src_PE_begin = sum(Num_StaticPE_eachLayer) + sum(Num_DynamicPE_eachLayer[0:layer_idx])

                src_PE_end = src_PE_begin + Num_DynamicPE_eachLayer[layer_idx] - 1
    
                dest_PE_begin = src_PE_end + 1
                dest_PE_end = dest_PE_begin + Num_DynamicPE_eachLayer[layer_idx+1] - 1
                # print("dyn to dyn")
                # print("src_PE_begin:",src_PE_begin)
                # print("src_PE_end:",src_PE_end)
                # print("dest_PE_begin:",dest_PE_begin)
                # print("dest_PE_end:",dest_PE_end)
            
            else: # next layer is static layer
                if (layer_idx == 0):
                    src_PE_begin = sum(Num_StaticPE_eachLayer)
                else:
                    src_PE_begin = sum(Num_StaticPE_eachLayer) + sum(Num_DynamicPE_eachLayer[0:layer_idx])
    
                src_PE_end = src_PE_begin + Num_DynamicPE_eachLayer[layer_idx] - 1
                
                dest_PE_begin =  sum(Num_StaticPE_eachLayer[0:layer_idx+1])
                dest_PE_end = dest_PE_begin + Num_StaticPE_eachLayer[layer_idx+1] - 1 
                # print("dyn to sta")
                # print("src_PE_begin:",src_PE_begin)
                # print("src_PE_end:",src_PE_end)
                # print("dest_PE_begin:",dest_PE_begin)
                # print("dest_PE_end:",dest_PE_end)
        
        # # from SIAM:
        # print("num_packets_this_layer",num_packets_this_layer)
        # for packet_idx in range(0, num_packets_this_layer):
        #     for dest_PE_idx in range(dest_PE_begin, dest_PE_end+1):
        #         for src_PE_idx in range(src_PE_begin, src_PE_end+1):
        #             trace = np.append(trace, [[src_PE_idx, dest_PE_idx, timestamp]], axis=0)
                    
        #         if (dest_PE_idx != dest_PE_end):
        #             timestamp = timestamp + 1
        #     timestamp = timestamp + 1
        #     print("timestamp",timestamp)
        
        for src_PE_idx in range(src_PE_begin, src_PE_end+1):
            for packet_idx in range(0, math.ceil(num_outputPackets_perPE_this_layer/ (dest_PE_end - dest_PE_begin + 1))):
                for dest_PE_idx in range(dest_PE_begin, dest_PE_end+1):
                    trace = np.append(trace, [[src_PE_idx, dest_PE_idx, timestamp]], axis=0)
                    
                if (packet_idx != num_outputPackets_perPE_this_layer-1):
                    timestamp = timestamp + 1
            timestamp = timestamp + 1
        
        # print("timestamp",timestamp)
        
        
        trace = np.delete(trace, 0, 0)
        # print("layer = ",layer_idx)
        # print(trace)
        trace_all_layers.append(trace)
    
    # print(trace)
    return trace_all_layers