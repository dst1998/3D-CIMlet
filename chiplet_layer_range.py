import math
import numpy as np
import re
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
                    print(f"Layer {layer_idx}: Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
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

def get_static_chiplet_layers(config,net_structure,Num_StaticPE_eachLayer,num_static_chiplet_eachLayer):
    static_chiplet_size = config.static_chiplet_height * config.static_chiplet_width

    # get layers in each static chiplet (chiplet_layer_range list :layer?~? in chiplet i)
    chiplet_availability = [static_chiplet_size] * config.num_static_chiplet  # Initialize all chiplets' unmapped PE to 'static_chiplet_size'
    chiplet_layers = [[] for _ in range(config.num_static_chiplet)]
    layer_location_begin_chiplet = [-1 for _ in range(len(Num_StaticPE_eachLayer))] # tell this layer is on which chiplet
    
    last_chiplet_used = 0  # Used to record the index of last used chiplet
    chiplet_index = 0
    num_used_chiplet = 0
    
    # go through static layers
    for layer_idx, layer in enumerate(net_structure):
        # print("layer:", layer)
            
        required_pes = Num_StaticPE_eachLayer[layer_idx]
        # print("required_pes:", required_pes)
        if required_pes == 0:  # is dynamic layer，skip this layer
            continue
        
        # Calculate how many chiplets are needed for this layer
        num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]
        
        if layer[6] == 0: # is static layer
            # Split the PE requirements for this layer equally across multiple chiplets
            if num_static_chiplet_this_layer >1:
                pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
                if last_chiplet_used != 0:
                    chiplet_index = last_chiplet_used + 1 # the layer need more than 1 chiplet, then start with a new chiplet
                for i in range(num_static_chiplet_this_layer):
                    chiplet_availability[chiplet_index + i] -= pe_used_per_chiplet

                    # update chiplet_layers of this chiplet
                    chiplet_layers[chiplet_index + i].append(layer_idx)
                
                layer_location_begin_chiplet[layer_idx] = chiplet_index # tell this layer is on which chiplet
                
                last_chiplet_used = chiplet_index + num_static_chiplet_this_layer-1 # update next chiplet index
                
                num_used_chiplet = last_chiplet_used + 1

            else: # num_static_chiplet_this_layer == 1
                while required_pes > 0 and num_used_chiplet + num_static_chiplet_this_layer <= config.num_static_chiplet:
                    if (layer_idx != 0) and (num_static_chiplet_eachLayer[layer_idx-1]>1):
                        chiplet_index = last_chiplet_used + 1
                    else:
                        chiplet_index = last_chiplet_used
                    available_pe = chiplet_availability[chiplet_index]
                    # print("chiplet_index:", chiplet_index)
                    # print("required_pes:", required_pes)
                    # print("available_pe:", available_pe)
                    
                    if required_pes <= available_pe:
                        chiplet_availability[chiplet_index] -= required_pes
                        required_pes -= required_pes
                        
                        # update chiplet_layers of this chiplet
                        chiplet_layers[chiplet_index].append(layer_idx)
                        
                        # tell this layer is on which chiplet
                        layer_location_begin_chiplet[layer_idx] = chiplet_index
                        
                        # update last_chiplet_used
                        last_chiplet_used = chiplet_index

                    else:
                        print(f"Layer {layer_idx}: Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
                        last_chiplet_used += 1
                        num_used_chiplet += 1
            
            if (last_chiplet_used + 1) > config.num_static_chiplet:
                print(f"Layer {layer_idx} requires more chiplets than available.")
                break
    
    print("num_used_static_chiplet:", num_used_chiplet)
    
    # go through semi-static layers
    for layer_idx, layer in enumerate(net_structure):
        # print("layer:", layer)
            
        required_pes = Num_StaticPE_eachLayer[layer_idx]
        # print("required_pes:", required_pes)
        if required_pes == 0:  # is dynamic layer，skip this layer
            continue
        
        # Calculate how many chiplets are needed for this layer
        num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]
        
        if layer[6] == 2: # is semi-static layer
            # Split the PE requirements for this layer equally across multiple chiplets
            if num_static_chiplet_this_layer >1:
                pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
                if last_chiplet_used != 0:
                    chiplet_index = last_chiplet_used + 1 # the layer need more than 1 chiplet, then start with a new chiplet
                for i in range(num_static_chiplet_this_layer):
                    chiplet_availability[chiplet_index + i] -= pe_used_per_chiplet

                    # update chiplet_layers of this chiplet
                    chiplet_layers[chiplet_index + i].append(layer_idx)
                
                layer_location_begin_chiplet[layer_idx] = chiplet_index # tell this layer is on which chiplet
                
                last_chiplet_used = chiplet_index + num_static_chiplet_this_layer-1 # update next chiplet index
                
                num_used_chiplet = last_chiplet_used + 1

            else: # num_static_chiplet_this_layer == 1
                while required_pes > 0 and num_used_chiplet + num_static_chiplet_this_layer <= config.num_static_chiplet:
                    if (layer_idx != 0) and (num_static_chiplet_eachLayer[layer_idx-1]>1):
                        chiplet_index = last_chiplet_used + 1
                    else:
                        chiplet_index = last_chiplet_used
                    available_pe = chiplet_availability[chiplet_index]
                    # print("chiplet_index:", chiplet_index)
                    # print("required_pes:", required_pes)
                    # print("available_pe:", available_pe)
                    
                    if required_pes <= available_pe:
                        chiplet_availability[chiplet_index] -= required_pes
                        required_pes -= required_pes
                        
                        # update chiplet_layers of this chiplet
                        chiplet_layers[chiplet_index].append(layer_idx)
                        
                        # tell this layer is on which chiplet
                        layer_location_begin_chiplet[layer_idx] = chiplet_index
                        
                        # update last_chiplet_used
                        last_chiplet_used = chiplet_index

                    else:
                        print(f"Layer {layer_idx}: Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
                        last_chiplet_used += 1
                        num_used_chiplet += 1
            
            if (last_chiplet_used + 1) > config.num_static_chiplet:
                print(f"Layer {layer_idx} requires more chiplets than available.")
                break
    
    print("num_used_static_chiplet:", num_used_chiplet)
    
    
    # # go through semi-static layers
    # for layer_idx, layer in enumerate(range(len(Num_StaticPE_eachLayer))):
    #     # print("layer:", layer)
        
    #     required_pes = Num_StaticPE_eachLayer[layer]
    #     # print("required_pes:", required_pes)
    #     if required_pes == 0:  # is dynamic layer，skip this layer
    #         continue
        
    #     # Calculate how many chiplets are needed for this layer
    #     num_static_chiplet_this_layer = num_static_chiplet_eachLayer[layer_idx]
    
    #     if layer[6] == 2: # is semi-static layer
    #         # Split the PE requirements for this layer equally across multiple chiplets
    #         if num_static_chiplet_this_layer >1:
    #             pe_used_per_chiplet = math.ceil(required_pes / num_static_chiplet_this_layer)
    #             last_chiplet_used += 1 # the layer need more than 1 chiplet, then start with a new chiplet
    #             for i in range(num_static_chiplet_this_layer):
    #                 chiplet_availability[last_chiplet_used + i] -= pe_used_per_chiplet

    #                 # update chiplet_layers of this chiplet
    #                 chiplet_layers[last_chiplet_used + i].append(layer)
                
    #             layer_location_begin_chiplet[layer_idx] = last_chiplet_used # tell this layer is on which chiplet
                
    #             last_chiplet_used = last_chiplet_used + num_static_chiplet_this_layer # update next chiplet index

    #         else: # num_static_chiplet_this_layer == 1
    #             while required_pes > 0 and last_chiplet_used + num_static_chiplet_this_layer <= config.num_static_chiplet:
    #                 chiplet_index = last_chiplet_used
    #                 available_pe = chiplet_availability[chiplet_index]
    #                 # print("chiplet_index:", chiplet_index)
    #                 # print("required_pes:", required_pes)
    #                 # print("available_pe:", available_pe)
                    
    #                 if required_pes <= available_pe:
    #                     chiplet_availability[chiplet_index] -= required_pes
    #                     required_pes -= required_pes
                        
    #                     # update chiplet_layers of this chiplet
    #                     chiplet_layers[chiplet_index].append(layer)
                        
    #                     # tell this layer is on which chiplet
    #                     layer_location_begin_chiplet[layer_idx] = last_chiplet_used

    #                 else:
    #                     print(f"Layer {layer_idx}: Not enough space in chiplet {chiplet_index}, moving to the next chiplet.")
    #                     last_chiplet_used += 1
            
    #         if (last_chiplet_used + 1) > config.num_static_chiplet:
    #             print(f"Layer {layer} requires more chiplets than available.")
    #             break
            
            
            
            
    # num_used_chiplet = last_chiplet_used + 1
    # print("num_used_static_chiplet:", num_used_chiplet)
    
    # discard unused chiplets (which are filled with -1)
    chiplet_layers = chiplet_layers[0:num_used_chiplet]
    print("chiplet_layers:", chiplet_layers)
    
    # mark the static chip type to semi-static or not: static:0, semi-static:2.
    chiplet_static_type = [0] * len(chiplet_layers)
    for chiplet_idx in range(len(chiplet_layers)):
        for layer_idx in chiplet_layers[chiplet_idx]:
            if net_structure[layer_idx][6] == 2:
                chiplet_static_type[chiplet_idx] = 2
    print("chiplet_static_type:",chiplet_static_type)
        
    # update each dynamic layer's beginning chiplet from -1 to the first dynamic chiplet.
    for i in range(len(layer_location_begin_chiplet)):
        if layer_location_begin_chiplet[i] == -1:
            layer_location_begin_chiplet[i] = num_used_chiplet  # update the begin chiplet idx of ith layer
            # print("chiplet_idx updated:", layer_location_begin_chiplet[i])
    print("layer_location_begin_chiplet:",layer_location_begin_chiplet)
    
    return chiplet_layers, chiplet_availability, num_used_chiplet,chiplet_static_type,layer_location_begin_chiplet

def get_dest_layers(config,net_structure,netStructure_layer_def):
    num_T_head = config.num_T_head
    if "Transformer_inf" in config.model_filename:
        num_layers_per_T_layer = 3+ num_T_head*2 +3
        dest_layers = [[] for _ in range(len(net_structure))]
        to_bp_dest_layers = [[] for _ in range(len(net_structure))] # only init, not used in adapter_inf
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))] # only init, not used in adapter_inf
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
        to_bp_dest_layers = [[] for _ in range(len(net_structure))] # only init, not used in adapter_inf
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))] # only init, not used in adapter_inf
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
    
    elif "Transformer_adapter_cl" in config.model_filename:
        match = re.search(r'_(\d+)layer', config.model_filename)
        if match:
            T_layer = int(match.group(1))
        else:
            print("No match for T_layer found")
        
        fp_num_layers_per_T_layer = 3+ num_T_head*2 +3 +4
        bp_num_layers_per_T_layer = 12+ num_T_head*2
        dest_layers = [[] for _ in range(len(net_structure))]
        to_bp_dest_layers = [[] for _ in range(len(net_structure))]
        num_to_bp_transfer_byte_to_layer = [0 for _ in range(len(net_structure))]
        for layer in range(len(net_structure)):
            # if src layer is from FP:
            if 'FP' in netStructure_layer_def[layer]:
                # FP: generate K
                if ((layer % fp_num_layers_per_T_layer == 0)and(layer != len(net_structure)-1)):
                    # print("case1:")
                    # print("layer:",layer)
                    for head in range(num_T_head):
                        # print("head:",head)
                        # print("dest:",3+head*2 + math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer)

                        # to FP
                        dest_layers[layer].append(3+head*2 + math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer) 
                # FP: generate Q
                if (layer % fp_num_layers_per_T_layer == 1):
                    # print("case1:")
                    # print("layer:",layer)
                    for head in range(num_T_head):
                        # print("head:",head)
                        # print("dest:",3+head*2 + math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer)
                        
                        # to FP
                        output_dest_layer = 3+head*2 + math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer
                        dest_layers[layer].append(output_dest_layer)
                        # num_transfer_byte_eachLayer[output_dest_layer] = net_structure[output_dest_layer][0] * net_structure[output_dest_layer][1] 
                        
                        # to BP
                        bp_dest_layer = (T_layer * fp_num_layers_per_T_layer+14) + head*2 +(T_layer-math.ceil(layer/fp_num_layers_per_T_layer))*bp_num_layers_per_T_layer
                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                # FP: generate V
                if (layer % fp_num_layers_per_T_layer == 2):
                    # print("case2:")
                    # print("layer:",layer)
                    for head in range(num_T_head):
                        # to FP
                        output_dest_layer = 2+head*2 + layer
                        dest_layers[layer].append(output_dest_layer)
                        # to BP
                        bp_dest_layer = (T_layer * fp_num_layers_per_T_layer+13) + head*2 +(T_layer-math.ceil(layer/fp_num_layers_per_T_layer))*bp_num_layers_per_T_layer
                        to_bp_dest_layers[layer].append(bp_dest_layer) 
                        num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                # FP: K.QT        
                if (0 <= ((layer % fp_num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % fp_num_layers_per_T_layer)-3)%2 ==0):
                    # print("case3:")
                    # print("layer:",layer)
                    dest_layers[layer].append(1 + layer) # to FP
                # FP: K.QT * V
                if (0 <= ((layer % fp_num_layers_per_T_layer)-3)/2 <num_T_head) and ( ((layer % fp_num_layers_per_T_layer)-3)%2 ==1):
                    # print("case4:")
                    # print("layer:",layer)
                    dest_layers[layer].append(math.floor(layer/fp_num_layers_per_T_layer)*fp_num_layers_per_T_layer + fp_num_layers_per_T_layer-7) # to FP
                # FP: head contact
                if (layer % fp_num_layers_per_T_layer == fp_num_layers_per_T_layer-7):
                    # print("case5:")
                    # print("layer:",layer)
                    
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter1-1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                # FP: adapter1-1
                if (layer % fp_num_layers_per_T_layer == fp_num_layers_per_T_layer-6):
                    # print("case5:")
                    # print("layer:",layer)
                    
                    # to FP
                    output_dest_layer = layer+1
                    dest_layers[layer].append(output_dest_layer)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter1-1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter1-2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                # FP: adapter1-2
                if (layer % fp_num_layers_per_T_layer == fp_num_layers_per_T_layer-5):
                    # print("case5:")
                    # print("layer:",layer)
                    
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter1-2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    
                # FP: ff1
                if (layer % fp_num_layers_per_T_layer == fp_num_layers_per_T_layer-4):
                    # print("case5:")
                    # print("layer:",layer)
                    
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # # to BP
                    # indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff1,']
                    # bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    # bp_dest_layer = indexes[bp_idx]
                    # to_bp_dest_layers[layer].append(bp_dest_layer)
                    # num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                # FP: ff2
                if (layer % fp_num_layers_per_T_layer == fp_num_layers_per_T_layer-3):
                    # print("case5:")
                    # print("layer:",layer)
                    
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # # to BP
                    # indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff2,']
                    # bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    # bp_dest_layer = indexes[bp_idx]
                    # to_bp_dest_layers[layer].append(bp_dest_layer)
                    # num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter2-1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                # FP: adapter2-1
                if (layer % fp_num_layers_per_T_layer == fp_num_layers_per_T_layer-2):
                    # print("case5:")
                    # print("layer:",layer)
                    
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter2-1,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter2-2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                # FP: adapter2-2
                if (layer % fp_num_layers_per_T_layer == fp_num_layers_per_T_layer-1):
                    # print("case5:")
                    # print("layer:",layer)
                    
                    # to FP
                    dest_layers[layer].append(layer+1)
                    # to BP
                    indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter2-2,']
                    bp_idx = T_layer - math.ceil(layer / fp_num_layers_per_T_layer)
                    bp_dest_layer = indexes[bp_idx]
                    to_bp_dest_layers[layer].append(bp_dest_layer)
                    num_to_bp_transfer_byte_to_layer[bp_dest_layer] = net_structure[bp_dest_layer][2] * net_structure[bp_dest_layer][3]
                
                # FP: final output classification weight, also last layer of FP, go to the first layer
                if (layer % fp_num_layers_per_T_layer == 0) and (layer == T_layer * fp_num_layers_per_T_layer):
                    # to FP (go to 1st layer of BP)
                    dest_layers[layer].append(layer+1)
            
            # if src layer is from BP:
            elif 'BP' in netStructure_layer_def[layer] or 'W Gradient' in netStructure_layer_def[layer]:
                
                # BP:weight_outputProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_outputProjection,']:
                    dest_layers[layer].append(layer+1)
                    dest_layers[layer].append(layer+2)
                
                # W Gradient:weight_adapter2-2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter2-2,']:
                    dest_layers[layer].append(layer+1)
                
                # BP:weight_adapter2-2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter2-2,']:
                    dest_layers[layer].append(layer+1)
                    dest_layers[layer].append(layer+2)
                
                # W Gradient:weight_adapter2-1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter2-1,']:
                    dest_layers[layer].append(layer+1)

                # BP:weight_adapter2-1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter2-1,']:
                    dest_layers[layer].append(layer+1)
                
                # BP:weight_ff2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff2,']:
                    dest_layers[layer].append(layer+1)
                
                # BP:weight_ff1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_ff1,']:
                    dest_layers[layer].append(layer+1)
                    dest_layers[layer].append(layer+2)
                
                # W Gradient:weight_adapter1-2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter1-2,']:
                    dest_layers[layer].append(layer+1)
                
                # BP:weight_adapter1-2
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter1-2,']:
                    dest_layers[layer].append(layer+1)
                    dest_layers[layer].append(layer+2)
                
                # W Gradient:weight_adapter1-1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'W Gradient:weight_adapter1-1,']:
                    dest_layers[layer].append(layer+1)

                # BP:weight_adapter1-1
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_adapter1-1,']:
                    dest_layers[layer].append(layer+1)

                # BP:weight_headContact ##
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_headContact,'] and layer != max([i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_headContact,']):
                    for head in range(num_T_head):
                        dest_layers[layer].append(layer+1 + head*2)
                
                # BP:V
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:V,']
                largest_num_T_head = sorted(indexes, reverse=True)[:num_T_head]
                remaining_indexes = [i for i in indexes if i not in largest_num_T_head]
                if layer in indexes and layer in remaining_indexes:
                    dest_layers[layer].append(layer+1)
                
                # BP:Q
                indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:Q,']
                largest_num_T_head = sorted(indexes, reverse=True)[:num_T_head]
                remaining_indexes = [i for i in indexes if i not in largest_num_T_head]
                if layer in indexes and layer in remaining_indexes:
                    kProjection_indexes = [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_kProjection,']
                    out_dest_layer = min(index for index in kProjection_indexes if index > layer)
                    dest_layers[layer].append(out_dest_layer)
                
                # BP:weight_kProjection
                if layer in [i for i, item in enumerate(netStructure_layer_def) if item == 'BP:weight_kProjection,'] and (layer != len(net_structure)-1):
                    dest_layers[layer].append(layer+1)
                    dest_layers[layer].append(layer+2)

        print("dest_layers:",dest_layers)
        print("to_bp_dest_layers:",to_bp_dest_layers)
    
    return dest_layers, to_bp_dest_layers, num_to_bp_transfer_byte_to_layer