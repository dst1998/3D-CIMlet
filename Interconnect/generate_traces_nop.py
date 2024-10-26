#*******************************************************************************
# Copyright (c) 2021-2025
# School of Electrical, Computer and Energy Engineering, Arizona State University
# Department of Electrical and Computer Engineering, University of Wisconsin-Madison
# PI: Prof. Yu Cao, Prof. Umit Y. Ogras, Prof. Jae-sun Seo, Prof. Chaitali Chakrabrati
# All rights reserved.
#
# This source code is part of SIAM - a framework to benchmark chiplet-based IMC 
# architectures with synaptic devices(e.g., SRAM and RRAM).
# Copyright of the model is maintained by the developers, and the model is distributed under
# the terms of the Creative Commons Attribution-NonCommercial 4.0 International Public License
# http://creativecommons.org/licenses/by-nc/4.0/legalcode.
# The source code is free and you can redistribute and/or modify it
# by providing that the following conditions are met:
#
#  1) Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2) Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Developer list:
#		Gokul Krishnan Email: gkrish19@asu.edu
#		Sumit K. Mandal Email: skmandal@wisc.edu
#
# Acknowledgements: Prof.Shimeng Yu and his research group for NeuroSim
#*******************************************************************************/

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 09:57:35 2021

"""

import pandas as pd
import numpy as np
import math
import os
import shutil

#Take all below parameters as argument
# quantization_bit = 8
# bus_width = 32
# netname = 'ResNet110' #'VGG-19_45.3M'
# xbar_size = 256
# chiplet_size = 16
# num_chiplets = 25
# type = 'Homogeneous Design'
# scale = 1

def generate_traces_nop(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet,num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, num_in_eachLayer, bus_width, netname, chiplet_size, type, scale):

    # directory_name = netname + '/' + type + '/' + str(num_chiplets) + '_Chiplets_' + str(chiplet_size) + '_Pes/to_interconnect'
    directory_name = '/home/du335/simulator/to_interconnect'
    # tiles_csv_file_name = directory_name + '/num_tiles_per_layer_chiplet.csv'
    # num_tiles_each_layer = pd.read_csv(tiles_csv_file_name, header=None)
    # num_tiles_each_layer = num_tiles_each_layer.to_numpy()
    # num_tiles_each_layer = num_tiles_each_layer[:, 2]
    
    # activation_csv_file_name = directory_name + '/ip_activation.csv'
    # num_activations_per_layer = pd.read_csv(activation_csv_file_name, header=None)
    # num_activations_per_layer = num_activations_per_layer.to_numpy()
    
    # chiplet_breakup_file_name = directory_name + '/chiplet_breakup.csv'
    # data = pd.read_csv(chiplet_breakup_file_name, header=None)
    # data = data.to_numpy()
    
    num_bits_nop_eachLayer = [0] * len(num_in_eachLayer)

    num_chiplets_used = num_used_static_chiplet_all_layers + num_used_dynamic_chiplet
    nop_mesh_size = math.ceil(math.sqrt(num_chiplets_used))
    
    dir_name = '/home/du335/simulator/Interconnect/' +  netname + '_NoP_traces' + '/' + type + '_' + str(num_chiplets_used) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '_bus_width_' + str(bus_width)
            
    if (os.path.isdir(dir_name)):
        shutil.rmtree(dir_name)
    
    os.makedirs(dir_name)
    # os.chdir(dir_name);
    
    # loop: src_layer, find if the dest_layers of each src_layer need NoP
    for layer_idx in range(len(num_chiplet_eachLayer)):
        # print("layer_idx:",layer_idx)
        for dest_layer in dest_layers[layer_idx]:
            
            # if layer_idx == 102:
            #         print("dest_layer=",dest_layer)
            #         print("layer_location_begin_chiplet[dest_layer]", layer_location_begin_chiplet[dest_layer])
            #         print("layer_location_begin_chiplet[layer_idx]", layer_location_begin_chiplet[layer_idx])
            #         print("num_used_static_chiplet_all_layers", num_used_static_chiplet_all_layers)
                    
            #         print("num_chiplet_eachLayer[layer_idx]", num_chiplet_eachLayer[layer_idx])
            #         print("num_chiplet_eachLayer[dest_layer]", num_chiplet_eachLayer[dest_layer])
            
            
            # if the src_layer_begin_chip and dest_layer_begin_chip are not on same chip -> need NoP, or 
            # if src_layer_begin_chip and dest_layer_begin_chip are on same chip, and src_layer and dest_layer are both dynamic layers, and two layers need diff num of chips -> need NoP
            if ((layer_location_begin_chiplet[dest_layer] != layer_location_begin_chiplet[layer_idx]) | ((layer_location_begin_chiplet[dest_layer] == num_used_static_chiplet_all_layers) & (layer_location_begin_chiplet[layer_idx] == num_used_static_chiplet_all_layers) & (num_chiplet_eachLayer[layer_idx] != num_chiplet_eachLayer[dest_layer]))):
                # print("dest_layer:",dest_layer)
                trace = np.array([[0,0,0]])
                
                num_src_chiplet = num_chiplet_eachLayer[layer_idx]
                num_dst_chiplet = num_chiplet_eachLayer[dest_layer]
                # print("num_src_chiplet:",num_src_chiplet)
                # print("num_dst_chiplet:",num_dst_chiplet)
                
                src_chiplet_begin = layer_location_begin_chiplet[layer_idx]
                src_chiplet_end = src_chiplet_begin + num_src_chiplet - 1
                # print("src_chiplet_begin:",src_chiplet_begin)
                # print("src_chiplet_end:",src_chiplet_end)
                
                dst_chiplet_begin = layer_location_begin_chiplet[dest_layer]
                dst_chiplet_end = dst_chiplet_begin + num_dst_chiplet - 1
                # print("dst_chiplet_begin:",dst_chiplet_begin)
                # print("dst_chiplet_end:",dst_chiplet_end)
                
                num_activations_per_chiplet = math.ceil(num_in_eachLayer[dest_layer]*config.BitWidth_in/(num_src_chiplet*num_dst_chiplet*scale*bus_width))
                
                # if layer_idx == 102 and dest_layer == 104:
                # if layer_idx == 102:
                #     print("dest_layer",dest_layer)
                #     print("layer 102 to this layer num_activations_per_chiplet", num_activations_per_chiplet)
                
                num_bits_nop_eachLayer[dest_layer] += num_in_eachLayer[dest_layer]*config.BitWidth_in

                timestamp = 1

                for packet_idx in range(1, num_activations_per_chiplet):
                    for dest_chiplet_idx in range(dst_chiplet_begin, dst_chiplet_end+1):
                        for src_chiplet_idx in range(src_chiplet_begin, src_chiplet_end+1):
                            # trace = [trace; src_chiplet_idx-1 dest_chiplet_idx-1 timestamp]
                            if src_chiplet_idx != dest_chiplet_idx: 
                                # if src_chip is dest_chip, then no need for nop
                                trace = np.append(trace, [[src_chiplet_idx, dest_chiplet_idx, timestamp]], axis=0)
                                # print("5")
                        if (dest_chiplet_idx != dst_chiplet_end):
                            timestamp = timestamp + 1
                        
                    timestamp = timestamp + 1
                    
                filename = 'trace_file_srcL_' + str(layer_idx) +'_destL_' + str(dest_layer) + '.txt'
                
                trace = np.delete(trace, 0, 0)
                os.chdir(dir_name)
                np.savetxt(filename, trace, fmt='%i')
                os.chdir("../..")
    
    os.chdir(dir_name)
    np.savetxt('nop_mesh_size.csv', [nop_mesh_size], fmt='%i')
    os.chdir("../..")
    
    return num_bits_nop_eachLayer