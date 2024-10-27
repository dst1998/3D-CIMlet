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
Created on Fri Sep 24 17:22:09 2021

"""


import os, re, glob, sys, math
import timeit

from Interconnect.generate_traces_nop import generate_traces_nop
from Interconnect.run_booksim_mesh_chiplet_nop import run_booksim_mesh_chiplet_nop

start = timeit.default_timer()

# chiplet_size = 25
# num_chiplet = 144
# scale = 1
# bus_width = 4
# netname = 'VGG19_homogeneous_NoP_traces'

def nop_interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet, num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, num_in_eachLayer, netname, chiplet_size, nop_clk_freq):
    
    type = config.type
    scale = config.scale_nop
    bus_width = config.chiplet_bus_width_2D
    num_chiplets = num_used_static_chiplet_all_layers + num_used_dynamic_chiplet
    
    num_bits_nop_eachLayer = generate_traces_nop(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet,num_chiplet_eachLayer, dest_layers, layer_location_begin_chiplet, num_in_eachLayer, bus_width, netname, chiplet_size, type, scale)

    print('Trace generation for NoP is finished')
    print('Starting to simulate the NoP trace')
    
    trace_directory_name = str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '_bus_width_' + str(bus_width)
    trace_directory_full_path = '/home/du335/simulator/Interconnect/' + netname + '_NoP_traces' + '/' + trace_directory_name
    
    # results_directory_name = 'results_' + trace_directory_name
    results_directory_name = trace_directory_name
    # results_directory_full_path = '/home/du335/simulator/Final_Results/NoP_Results_' + 'results_' + netname + '/' + results_directory_name
    results_directory_full_path = '/home/du335/simulator/Final_Results/NoP_Results_' + netname + '/' + results_directory_name
    
    # os.system('pwd')
    
    # os.system('python3 run_booksim_mesh_chiplet_nop.py ' + trace_directory_full_path + ' ' + str(bus_width))
    run_booksim_mesh_chiplet_nop(config,nop_clk_freq,trace_directory_full_path, bus_width)
    
    if (not os.path.exists(results_directory_full_path)):
        os.makedirs(results_directory_full_path)
    
    os.system('rm -rf ' + results_directory_full_path + '/logs_NoP') #
    os.system('mv /home/du335/simulator/Interconnect/logs_NoP/ ' + results_directory_full_path) #
    
    print('finish simulate the NoP trace')

    # return area (not used)
    area = 0.0
    nop_area_file_path = '/home/du335/simulator/Final_Results/NoP_Results_' + netname + '/' + str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '_bus_width_' + str(bus_width) + '/logs_NoP/Area_chiplet.csv'

    with open(nop_area_file_path, 'r') as file:
        for line in file:
            # Remove surrounding whitespaces and split the line
            line = line.strip()
        
            # Check if the line starts with the expected prefix
            if line.startswith("Total NoP area is"):
                # Split the line and extract the numeric part
                parts = line.split('\t')  # Split by tab character
                if len(parts) > 1:
                    area += float(parts[1])  # Convert the second part to a float and add to the total
    area *= 1e-12 # get m2

    print("Total area from booksim nop_area_file_path:", area)

    # return latency (not used)
    latency_list = []
    nop_latency_file_path = '/home/du335/simulator/Final_Results/NoP_Results_' + netname + '/' + str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '_bus_width_' + str(bus_width) + '/logs_NoP/Latency_chiplet.csv'

    with open(nop_latency_file_path, 'r') as file:
        for line in file:
            # Remove surrounding whitespaces and split the line
            line = line.strip()
        
            # Check if the line starts with the expected prefix
            if line.startswith("Total NoP latency is"):
                # Split the line and extract the numeric part
                parts = line.split('\t')  # Split by tab character
                if len(parts) > 1:
                    latency_list.append(float(parts[1]))  # Convert the second part to a float and add to the total
    latency_list = [latency * scale for latency in latency_list]
    total_latency = sum(latency_list)

    print("Total latency from booksim nop_latency_file_path:", total_latency)
    

    # return latencyCycle_eachLayer (used)
    # NoP_LatencyCycle_eachLayer.csv
    # ('NoP latency for layer' +'\t' + str(run_id) + '\t'+'is' +'\t' + str(latency) +'\t' + 'cycles' + '\n')
    num_layers = len(num_in_eachLayer)
    latencyCycle_eachLayer_list = [[0 for _ in range(num_layers)] for _ in range(num_layers)]
    nop_latency_eachlayer_file_path = '/home/du335/simulator/Final_Results/NoP_Results_' + netname + '/' + str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '_bus_width_' + str(bus_width) + '/logs_NoP/NoP_LatencyCycle_eachLayer.csv'

    with open(nop_latency_eachlayer_file_path, 'r') as file:
        for line in file:
            # Remove surrounding whitespaces and split the line
            line = line.strip()
        
            # Check if the line starts with the expected prefix
            if line.startswith("NoP latency for layer"):
                # Split the line and extract the numeric part
                parts = line.split('\t')  # Split by tab character
                if len(parts) > 4:
                    latency = int(parts[3])
                    # extract src_layer_idx and dest_layer_idx
                    run_info = parts[1]  # e.g.'3_to_5'
                    src_layer_idx, dest_layer_idx = map(int, run_info.split('_to_'))
                    
                    latencyCycle_eachLayer_list[src_layer_idx][dest_layer_idx] = latency
    latencyCycle_eachLayer_list = [latency * scale for latency in latencyCycle_eachLayer_list]
    # print("NoP latencyCycle_eachLayer_list:", latencyCycle_eachLayer_list)

    # return energy (not used)
    power_list = []
    nop_power_file_path = '/home/du335/simulator/Final_Results/NoP_Results_' + netname + '/' + str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '_bus_width_' + str(bus_width) + '/logs_NoP/Energy_chiplet.csv'

    with open(nop_power_file_path, 'r') as file:
        for line in file:
            # Remove surrounding whitespaces and split the line
            line = line.strip()
        
            # Check if the line starts with the expected prefix
            if line.startswith("Total NoP power is"):
                # Split the line and extract the numeric part
                parts = line.split('\t')  # Split by tab character
                if len(parts) > 1:
                    power_list.append(float(parts[1]))  # Convert the second part to a float and add to the total
    
    if len(latency_list) != len(power_list):
        raise ValueError("The length of latency_list and power_list must be the same.")
    energy = sum(l * p for l, p in zip(latency_list, power_list))

    print("Total energy from booksim nop_energy_file_path:", energy)

    return area, total_latency, energy, num_bits_nop_eachLayer, latencyCycle_eachLayer_list
    
    
    # os.system('mv /home/gkrish19/SIAM_Integration/Interconnect/logs_NoP/ ' + results_directory_full_path)
            
    
                    
