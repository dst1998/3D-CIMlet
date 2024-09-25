import math
import numpy as np
from config import Config

def get_static_chiplet_layer_range(config,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer):
    static_chiplet_size = config.static_chiplet_height * config.static_chiplet_width

    # get layers in each static chiplet (chiplet_layer_range list :layer?~? in chiplet i)
    chiplet_availability = [static_chiplet_size] * config.num_static_chiplet  # Initialize all chiplets' unmapped PE to be static_chiplet_size
    chiplet_layer_range = np.full((config.num_static_chiplet, 2), -1)  # Initialize to be -1，have not placed any layer
    layer_location_begin_chiplet = [-1 for _ in range(len(Num_StaticPE_eachLayer))] # tell this layer is on which chiplet
    
    last_chiplet_used = 0  # 用于记录最后一个使用的chiplet索引

    for layer_idx, layer in enumerate(range(len(Num_StaticPE_eachLayer))):
        print("layer:", layer)
        required_pes = Num_StaticPE_eachLayer[layer]
        print("required_pes:", required_pes)
        if required_pes == 0:  # is dynamic layer，skip layer
            continue
        
        # 计算这一层需要多少个chiplet
        # num_static_chiplet_this_layer = ceil(required_pes / static_chiplet_size)
        num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]

        
        # if (last_chiplet_used + 1) + num_static_chiplet_this_layer > config.num_static_chiplet:
        #     print(f"Layer {layer} requires more chiplets than available.")
        #     break
        
        # 在多个chiplet间平分这一层的PE需求
        if num_static_chiplet_this_layer >1:
            pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
            last_chiplet_used += 1 # the layer need more than 1 chiplet, then start with a new chiplet
            for i in range(num_static_chiplet_this_layer):
                chiplet_availability[last_chiplet_used + i] -= pe_used_per_chiplet

                # update chiplet_layer_range list
                if chiplet_layer_range[last_chiplet_used + i, 0] == -1:
                    chiplet_layer_range[last_chiplet_used + i, 0] = layer
                chiplet_layer_range[last_chiplet_used + i, 1] = layer
            
            layer_location_begin_chiplet[layer_idx] = last_chiplet_used # tell this layer is on which chiplet
            
            last_chiplet_used = last_chiplet_used + num_static_chiplet_this_layer # update next chiplet index

        else: # num_static_chiplet_this_layer ==1
            while required_pes > 0 and last_chiplet_used + num_static_chiplet_this_layer <= config.num_static_chiplet:
                chiplet_index = last_chiplet_used
                available_pe = chiplet_availability[chiplet_index]
                print("chiplet_index:", chiplet_index)
                print("required_pes:", required_pes)
                print("available_pe:", available_pe)
                
                if required_pes <= available_pe:
                    chiplet_availability[chiplet_index] -= required_pes
                    required_pes -= required_pes
                    
                    # 更新chiplet_layer_range
                    if chiplet_layer_range[chiplet_index, 0] == -1:
                        chiplet_layer_range[chiplet_index, 0] = layer
                    chiplet_layer_range[chiplet_index, 1] = layer
                    
                    # tell this layer is on which chiplet
                    layer_location_begin_chiplet[layer_idx] = last_chiplet_used

                else:
                    print(f"Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
                    last_chiplet_used += 1
        
        if (last_chiplet_used + 1) > config.num_static_chiplet:
            print(f"Layer {layer} requires more chiplets than available.")
            break
    
    num_used_chiplet = last_chiplet_used + 1
    # print("last_chiplet_used:", last_chiplet_used)
    
    # discard unused chiplets (which are filled with -1)
    chiplet_layer_range = chiplet_layer_range[0:num_used_chiplet]
    
    # discard chiplets without inner-chip NoC (will fill with -1)
    for chip_idx in range(len(chiplet_layer_range)):
        # if in this chip, only have 1 layer or have 2 consecutive layer, no discard.
        if (chiplet_layer_range[chip_idx][0]==chiplet_layer_range[chip_idx][1])|((chiplet_layer_range[chip_idx][1]==chiplet_layer_range[chip_idx][0]+1)):
            continue
        # if in this chip, only have more than 2 layers, and if any of the layers is on dynamic chip or is not on this static chip, discard (fill this chip's begin_layer and end_layer with -1, and process in generate_noc_trace).
        else:
            for layer in range(chiplet_layer_range[chip_idx][0],chiplet_layer_range[chip_idx][1]):
                if (layer_location_begin_chiplet[layer] == -1)|(layer_location_begin_chiplet[layer]!= chip_idx):
                    chiplet_layer_range[chip_idx][0] = -1
                    chiplet_layer_range[chip_idx][1] = -1
        
    
    print("chiplet_layer_range:", chiplet_layer_range)
    
    print("layer_location_begin_chiplet:",layer_location_begin_chiplet)
    # print("layer29_location_begin_chiplet:",layer_location_begin_chiplet[29])
    
    return chiplet_layer_range, chiplet_availability, num_used_chiplet,layer_location_begin_chiplet

def get_static_chiplet_layers(config,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer):
    static_chiplet_size = config.static_chiplet_height * config.static_chiplet_width

    # get layers in each static chiplet (chiplet_layer_range list :layer?~? in chiplet i)
    chiplet_availability = [static_chiplet_size] * config.num_static_chiplet  # Initialize all chiplets' unmapped PE to be static_chiplet_size
    chiplet_layers = chiplet_layers = [[] for _ in range(config.num_static_chiplet)]
    layer_location_begin_chiplet = [-1 for _ in range(len(Num_StaticPE_eachLayer))] # tell this layer is on which chiplet
    
    last_chiplet_used = 0  # 用于记录最后一个使用的chiplet索引

    for layer_idx, layer in enumerate(range(len(Num_StaticPE_eachLayer))):
        # print("layer:", layer)
        required_pes = Num_StaticPE_eachLayer[layer]
        # print("required_pes:", required_pes)
        if required_pes == 0:  # is dynamic layer，skip layer
            continue
        
        # 计算这一层需要多少个chiplet
        # num_static_chiplet_this_layer = ceil(required_pes / static_chiplet_size)
        num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]
        
        # 在多个chiplet间平分这一层的PE需求
        if num_static_chiplet_this_layer >1:
            pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
            last_chiplet_used += 1 # the layer need more than 1 chiplet, then start with a new chiplet
            for i in range(num_static_chiplet_this_layer):
                chiplet_availability[last_chiplet_used + i] -= pe_used_per_chiplet

                # update chiplet_layers of this chiplet
                chiplet_layers[last_chiplet_used + i].append(layer)
            
            layer_location_begin_chiplet[layer_idx] = last_chiplet_used # tell this layer is on which chiplet
            
            last_chiplet_used = last_chiplet_used + num_static_chiplet_this_layer # update next chiplet index

        else: # num_static_chiplet_this_layer ==1
            while required_pes > 0 and last_chiplet_used + num_static_chiplet_this_layer <= config.num_static_chiplet:
                chiplet_index = last_chiplet_used
                available_pe = chiplet_availability[chiplet_index]
                # print("chiplet_index:", chiplet_index)
                # print("required_pes:", required_pes)
                # print("available_pe:", available_pe)
                
                if required_pes <= available_pe:
                    chiplet_availability[chiplet_index] -= required_pes
                    required_pes -= required_pes
                    
                    # 更新chiplet_layers of this chiplet
                    chiplet_layers[chiplet_index].append(layer)
                    
                    # tell this layer is on which chiplet
                    layer_location_begin_chiplet[layer_idx] = last_chiplet_used

                else:
                    print(f"Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
                    last_chiplet_used += 1
        
        if (last_chiplet_used + 1) > config.num_static_chiplet:
            print(f"Layer {layer} requires more chiplets than available.")
            break
    
    num_used_chiplet = last_chiplet_used + 1
    print("num_used_chiplet:", num_used_chiplet)
    
    # discard unused chiplets (which are filled with -1)
    chiplet_layers = chiplet_layers[0:num_used_chiplet]
    
    print("chiplet_layers:", chiplet_layers)
    
    # update each dynamic layer's beginning chiplet from -1 to the first dynamic chiplet.
    for i in range(len(layer_location_begin_chiplet)):
        if layer_location_begin_chiplet[i] == -1:
            layer_location_begin_chiplet[i] = num_used_chiplet  # 更新列表中的值
            # print("chiplet_idx updated:", layer_location_begin_chiplet[i])
    print("layer_location_begin_chiplet:",layer_location_begin_chiplet)
    # print("layer29_location_begin_chiplet:",layer_location_begin_chiplet[29])
    
    return chiplet_layers, chiplet_availability, num_used_chiplet,layer_location_begin_chiplet

def get_dest_layers(config,net_structure):
    num_T_head = config.num_T_head
    if "Transformer_inf" in config.model_filename:
        num_layers_per_T_layer = 3+ num_T_head*2 +3
        dest_layers = [[] for _ in range(len(net_structure))]
        for layer in range(len(net_structure)):
            # generate K,Q
            if ((layer % num_layers_per_T_layer == 0)and(layer != len(net_structure)-1)) or (layer % num_layers_per_T_layer == 1):
                # print("case1:")
                # print("layer:",layer)
                for head in range(num_T_head):
                    # print("head:",head)
                    # print("dest:",3+head*2 + math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer)
                    dest_layers[layer].append(3+head*2 + math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer)
            # generate V
            if (layer % num_layers_per_T_layer == 2):
                # print("case2:")
                # print("layer:",layer)
                for head in range(num_T_head):
                    dest_layers[layer].append(2+head*2 + layer)      
            # K.QT        
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==0):
                # print("case3:")
                # print("layer:",layer)
                dest_layers[layer].append(1 + layer)
            # K.QT * V
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==1):
                # print("case4:")
                # print("layer:",layer)
                dest_layers[layer].append(math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer + num_layers_per_T_layer-3)
            # head contact, ff1
            if (layer % num_layers_per_T_layer == num_layers_per_T_layer-3) or (layer % num_layers_per_T_layer == num_layers_per_T_layer-2):
                # print("case5:")
                # print("layer:",layer)
                dest_layers[layer].append(layer+1)
            # ff2, then to next Transformer layer or final output classification
            if (layer % num_layers_per_T_layer == num_layers_per_T_layer-1):
                dest_layers[layer].append(layer+1)
            # final output classification weight, also last layer of whole model, go to the first layer
            if (layer % num_layers_per_T_layer == 0) and (layer == len(net_structure)-1):
                dest_layers[layer].append(0)
        
        print("dest_layers:",dest_layers)
    
    elif "Transformer_adapter_inf" in config.model_filename:
        num_layers_per_T_layer = 3+ num_T_head*2 +3 +4
        dest_layers = [[] for _ in range(len(net_structure))]
        for layer in range(len(net_structure)):
            # generate K,Q
            if ((layer % num_layers_per_T_layer == 0)and(layer != len(net_structure)-1)) or (layer % num_layers_per_T_layer == 1):
                # print("case1:")
                # print("layer:",layer)
                for head in range(num_T_head):
                    # print("head:",head)
                    # print("dest:",3+head*2 + math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer)
                    dest_layers[layer].append(3+head*2 + math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer)
            # generate V
            if (layer % num_layers_per_T_layer == 2):
                # print("case2:")
                # print("layer:",layer)
                for head in range(num_T_head):
                    dest_layers[layer].append(2+head*2 + layer)      
            # K.QT        
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==0):
                # print("case3:")
                # print("layer:",layer)
                dest_layers[layer].append(1 + layer)
            # K.QT * V
            if (0 <= ((layer % num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % num_layers_per_T_layer)-3)%2 ==1):
                # print("case4:")
                # print("layer:",layer)
                dest_layers[layer].append(math.floor(layer/num_layers_per_T_layer)*num_layers_per_T_layer + num_layers_per_T_layer-7)
            # head contact, adapter1-1,adapter1-2,ff1,ff2,adapter2-1,adapter2-2,
            if ( num_layers_per_T_layer-7 <= layer % num_layers_per_T_layer <= num_layers_per_T_layer-1):
                # print("case5:")
                # print("layer:",layer)
                dest_layers[layer].append(layer+1)
            # final output classification weight, also last layer of whole model, go to the first layer
            if (layer % num_layers_per_T_layer == 0) and (layer == len(net_structure)-1):
                dest_layers[layer].append(0)
        
        print("dest_layers:",dest_layers)
    
    return dest_layers