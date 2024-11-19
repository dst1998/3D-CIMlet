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
Created on Sat Sep  4 08:38:16 2021

"""

import pandas as pd
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

def generate_traces_noc(config, num_pes_each_layer, num_in_eachLayer, chiplet_layers, dest_layers,  layer_location_begin_chiplet, netname, chiplet_size, num_chiplets, type, scale):

    # print("dest_layers:",dest_layers)
    # print("num_pes_each_layer:",num_pes_each_layer)

    # directory_name = netname + '/' + type + '/' + str(num_chiplets) + '_Chiplets_' + str(chiplet_size) + '_Pes/to_interconnect'
    directory_name = '/home/du335/simulator/to_interconnect'
    # pes_csv_file_name = directory_name + '/num_pes_per_layer_chiplet.csv'
    # num_pes_each_layer = pd.read_csv(pes_csv_file_name, header=None)
    # num_pes_each_layer = num_pes_each_layer.to_numpy()
    # num_pes_each_layer = num_pes_each_layer[:, 2]

    
    # activation_csv_file_name = directory_name + '/ip_activation.csv' #
    # num_activations_per_layer = pd.read_csv(activation_csv_file_name, header=None)#
    # num_activations_per_layer = num_activations_per_layer.to_numpy()#
    
    # chiplet_breakup_file_name = directory_name + '/chiplet_breakup.csv'
    # data = pd.read_csv(chiplet_breakup_file_name, header=None)
    # data = data.to_numpy()
    
    # pe_begin_array = data[:, 0]
    # pe_end_array = data[:, 1]
    
    # pe_begin_array = chiplet_layer_range[:, 0]
    # pe_end_array = chiplet_layer_range[:, 1]
    
    dir_name = '/home/du335/simulator/Interconnect/' + netname + '_NoC_traces' + '/' + type + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale)
            
    
    if (os.path.isdir(dir_name)):
        shutil.rmtree(dir_name)
    
    os.makedirs(dir_name)
    os.chdir(dir_name)
    
    num_chiplets_used = len(chiplet_layers)
    mesh_size = np.zeros([num_chiplets_used, 1])
    
    for chiplet_idx in range(0, num_chiplets_used):
        
        
        begin_layer = chiplet_layers[chiplet_idx][0]
        # print("Begin Layer: ", begin_layer)
        # end_layer = pe_end_array[chiplet_idx]
        # print("End Layer: ", end_layer)
        
        # if (begin_layer == -1) & (end_layer == -1):
        #     continue 
        
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
        
        # for layer_idx in chiplet_layers[chiplet_idx]:    
        #     # noc trace: in learning, weight and intermidiate activations generated in FP, transfer as weights in BP
        #     for dest_layer in to_bp_dest_layers[layer_idx]:
        #         if (layer_location_begin_chiplet[dest_layer] == chiplet_idx):
            
        #             trace = np.array([[0,0,0]])
        #             timestamp = 1
            
        #             ip_activation_dest_layer = num_to_bp_transfer_byte_to_layer[dest_layer] #
        #             num_packets_this_layer = math.ceil(ip_activation_dest_layer*config.BitWidth_in/(config.pe_bus_width_2D)) #
        #             num_packets_this_layer = math.ceil(num_packets_this_layer/scale) #
            
        #             if (layer_idx == 0):
        #                 src_pe_begin = 0
        #             else:
        #                 # src_pe_begin = sum(num_pes_each_layer[0:layer_idx-1])
        #                 src_pe_begin = sum(num_pes_each_layer[0:layer_idx])
                    
        #             src_pe_end = src_pe_begin + num_pes_each_layer[layer_idx] - 1
            
        #             dest_pe_begin = sum(num_pes_each_layer[0:dest_layer])
        #             dest_pe_end = dest_pe_begin + num_pes_each_layer[dest_layer] - 1
            
        #             # Normalize the number to first_pe_number
        #             # print("src_pe_begin before subtraction with first pe number: ", src_pe_begin)
        #             # print("first_pe_number: ", first_pe_number)
        #             src_pe_begin = src_pe_begin - first_pe_number
        #             # print("src_pe_begin: ", src_pe_begin)
        #             src_pe_end = src_pe_end - first_pe_number
        #             dest_pe_begin = dest_pe_begin - first_pe_number
        #             dest_pe_end = dest_pe_end - first_pe_number
            
        #             for packet_idx in range(0, num_packets_this_layer):
        #                 for dest_pe_idx in range(dest_pe_begin, dest_pe_end+1):
        #                     for src_pe_idx in range(src_pe_begin, src_pe_end+1):
        #                         trace = np.append(trace, [[src_pe_idx, dest_pe_idx, timestamp]], axis=0)
                                
        #                     if (dest_pe_idx != dest_pe_end):
        #                         timestamp = timestamp + 1
        #                 timestamp = timestamp + 1
                  
        #             trace = np.delete(trace, 0, 0)
        #             filename = 'trace_file_layer_' + str(layer_idx) + '.txt'
        #             os.chdir(chiplet_dir_name)
        #             # 以追加模式打开文件，并保存trace
        #             with open(filename, 'a') as f:  # 'a' 表示追加模式
        #                 np.savetxt(f, trace, fmt='%i')
        #             os.chdir("..")
    
    np.savetxt('mesh_size.csv', mesh_size, fmt='%i')
    os.chdir("..")
    os.chdir("..")
