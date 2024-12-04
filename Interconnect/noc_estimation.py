import os, re, glob, sys, math, shutil
import numpy as np
import pandas as pd
from subprocess import call
from pathlib import Path
import math

from Interconnect.generate_traces_noc import generate_traces_noc
from Interconnect.run_booksim_noc import run_booksim_noc

def interconnect_estimation(config, num_used_static_chiplet_all_layers, num_used_dynamic_chiplet,chiplet_static_type,num_pes_each_layer, num_in_eachLayer, chiplet_layers, dest_layers, layer_location_begin_chiplet, netname, chiplet_size):
    
    type = config.type
    scale = config.scale_noc
    
    num_chiplets = num_used_static_chiplet_all_layers + num_used_dynamic_chiplet
 
    generate_traces_noc(config, num_pes_each_layer, num_in_eachLayer, chiplet_layers, dest_layers, layer_location_begin_chiplet, netname, chiplet_size, num_chiplets, type, scale)

    print('Trace generation for NoC is finished')
    print('Starting to simulate the NoC trace')


    trace_directory_name = str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '/'
    trace_directory_full_path = '/home/du335/simulator/Interconnect/' + netname + '_NoC_traces' + '/' + trace_directory_name
    
    results_directory_name = trace_directory_name
    results_directory_full_path = '/home/du335/simulator/Final_Results/NoC_Results_' + netname + '/' + results_directory_name
                
    run_booksim_noc(config,trace_directory_full_path,num_used_static_chiplet_all_layers, num_used_dynamic_chiplet,chiplet_static_type)
    if (not os.path.exists(results_directory_full_path)):
        os.makedirs(results_directory_full_path)
    
    os.system('rm -rf ' + results_directory_full_path + '/logs')
    os.system('mv /home/du335/simulator/Interconnect/logs/ ' + results_directory_full_path)

    print('finish simulate the NoC trace')

    # return area
    area = 0.0
    noc_area_file_path = '/home/du335/simulator/Final_Results/NoC_Results_' + netname + '/' + str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '/logs/Area_chiplet.csv'

    with open(noc_area_file_path, 'r') as file:
        for line in file:
            # Remove surrounding whitespaces and split the line
            line = line.strip()
        
            # Check if the line starts with the expected prefix
            if line.startswith("Total NoC area is"):
                # Split the line and extract the numeric part
                parts = line.split('\t')  # Split by tab character
                if len(parts) > 1:
                    area += float(parts[1])  # Convert the second part to a float and add to the total
    area *= 1e-12 # get m2

    print("Total area from booksim noc_area_file_path:", area)

    # return latency
    latency_list = []
    noc_latency_file_path = '/home/du335/simulator/Final_Results/NoC_Results_' + netname + '/' + str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '/logs/Latency_chiplet.csv'

    with open(noc_latency_file_path, 'r') as file:
        for line in file:
            # Remove surrounding whitespaces and split the line
            line = line.strip()
        
            # Check if the line starts with the expected prefix
            if line.startswith("Total NoC latency is"):
                # Split the line and extract the numeric part
                parts = line.split('\t')  # Split by tab character
                if len(parts) > 1:
                    latency_list.append(float(parts[1]))  # Convert the second part to a float and add to the total
    latency_list = [latency * scale for latency in latency_list]
    latency = sum(latency_list)

    print("Total latency from booksim noc_latency_file_path:", latency)

    # return energy
    power_list = []
    noc_power_file_path = '/home/du335/simulator/Final_Results/NoC_Results_' + netname + '/' + str(type) + '_' + str(num_chiplets) + '_chiplet_size_' + str(chiplet_size) + '_scale_' + str(scale) + '/logs/Energy_chiplet.csv'

    with open(noc_power_file_path, 'r') as file:
        for line in file:
            # Remove surrounding whitespaces and split the line
            line = line.strip()
        
            # Check if the line starts with the expected prefix
            if line.startswith("Total NoC power is"):
                # Split the line and extract the numeric part
                parts = line.split('\t')  # Split by tab character
                if len(parts) > 1:
                    power_list.append(float(parts[1]))  # Convert the second part to a float and add to the total
    
    if len(latency_list) != len(power_list):
        print("latency_list len:",latency_list)
        print("power_list len:",power_list)
        raise ValueError("The length of latency_list and power_list must be the same.")
    energy = sum(l * p for l, p in zip(latency_list, power_list))

    print("Total energy from booksim noc_energy_file_path:", energy)

    return area, latency, energy



# interconnect_estimation(quantization_bit, bus_width, netname, xbar_size, chiplet_size, num_chiplets, type, scale)
