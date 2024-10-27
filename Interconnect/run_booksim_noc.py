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

#!/usr/bin/python
# python run_booksim.py <directory to injection file>


import os, re, glob, sys, math
import numpy as np

def run_booksim_noc(config,trace_file_dir,num_used_static_chiplet_all_layers, num_used_dynamic_chiplet,chiplet_static_type):

    #os.chdir(trace_file_dir)
    #mesh_sizes_per_layer = pd.readcsv('mesh_sizes_per_layer.csv')
    mesh_size_file_name = trace_file_dir + 'mesh_size.csv'
    mesh_sizes_per_chiplet = np.loadtxt(mesh_size_file_name)
    # make sure even if only 1 value can be returned as a 1d array
    mesh_sizes_per_chiplet = np.atleast_1d(mesh_sizes_per_chiplet)
    #os.chdir('..')
    
    num_chiplets = len(mesh_sizes_per_chiplet)
    
    
    # Initialize file counter
    file_counter = 0
    
    # Create directory to store config files
    os.system('mkdir -p /home/du335/simulator/Interconnect/logs/configs')

    # Open the file and check if it has content
    area_file_path = '/home/du335/simulator/Interconnect/logs/Area_chiplet.csv'
    # Check if the file exists and if it is empty
    if os.path.exists(area_file_path):
        with open(area_file_path, 'r+') as area_file:
            content = area_file.read()
            if content:  # If the file has content
                area_file.seek(0)  # Move the pointer to the beginning of the file
                area_file.truncate()  # Clear the file

    # Open the file and check if it has content
    latency_file_path = '/home/du335/simulator/Interconnect/logs/Latency_chiplet.csv'
    # Check if the file exists and if it is empty
    if os.path.exists(latency_file_path):
        with open(latency_file_path, 'r+') as latency_file:
            content = latency_file.read()
            if content:  # If the file has content
                latency_file.seek(0)  # Move the pointer to the beginning of the file
                latency_file.truncate()  # Clear the file
    
    # Open the file and check if it has content
    power_file_path = '/home/du335/simulator/Interconnect/logs/Energy_chiplet.csv'
    # Check if the file exists and if it is empty
    if os.path.exists(power_file_path):
        with open(power_file_path, 'r+') as power_file:
            content = power_file.read()
            if content:  # If the file has content
                power_file.seek(0)  # Move the pointer to the beginning of the file
                power_file.truncate()  # Clear the file
    
    for chiplet_idx in range(0, num_chiplets):
    
        if (chiplet_idx < num_used_static_chiplet_all_layers) and (chiplet_static_type[chiplet_idx] == 0): # is static chip
            chip_technode = config.static_chiplet_technode
            chip_memory_cell_type = getattr(config, f'static_chiplet_memory_cell_type')
            chip_clk_freq = getattr(config, f'{chip_memory_cell_type}_clk_freq')
        else: # is dynamic chip or semi-static chip
            chip_technode = config.dynamic_chiplet_technode
            chip_memory_cell_type = getattr(config, f'dynamic_chiplet_memory_cell_type')
            chip_clk_freq = getattr(config, f'{chip_memory_cell_type}_clk_freq')
            
        chiplet_directory_name = trace_file_dir + 'Chiplet_' + str(chiplet_idx)
        
        # Get a list of all files in directory
        files = glob.glob(chiplet_directory_name + '/*txt')
        file_counter = 0
        total_latency = 0
        total_area = 0
        total_power = 0
        
        # Iterate over all files
        for file in files:
    
            # Increment file counter
            file_counter += 1
    
            # print('[ INFO] Processing file ' + file + ' ...')
    
            # Extract file name without extension and absolute path from filename
            run_name = os.path.splitext(os.path.basename(file))[0]
            run_id = run_name.strip('trace_file_layer_')
    
    
            # trace file
            trace_file_name = 'trace_file_chiplet_' + str(chiplet_idx) + '.txt'
    
            # mesh size
            mesh_size = int(mesh_sizes_per_chiplet[chiplet_idx])
    
            # Open read file handle of config file
            fp = open('/home/du335/simulator/Interconnect/mesh_config_trace_based', 'r')
            # fp = open('/home/du335/simulator/Interconnect/meshtraceconfig', 'r')
    
            # Set path to config file
            config_file = '/home/du335/simulator/Interconnect/logs/configs/chiplet_' + str(chiplet_idx) + '_mesh_config'
    
            # Open write file handle for config file
            outfile = open(config_file, 'w')
            
            # Set the new tech file name
            new_tech_file = 'techfile_' + str(chip_technode) + 'nm.txt'
    
            # Iterate over file and set size of mesh in config file
            for line in fp :
    
                line = line.strip()
    
                # Search for pattern
                matchobj1 = re.match(r'^k=', line)
    
                # Set size of mesh if line in file corresponds to mesh size
                if matchobj1 :
                    line = 'k=' + str(mesh_size) + ';'
                
                # Search for pattern: tech_file =
                matchobj2 = re.match(r'^tech_file = ', line)
    
                # Replace tech file if line in file corresponds to tech file
                if matchobj2:
                    line = f'tech_file = {new_tech_file};'
    
                # Write config to file
                outfile.write(line + '\n')
    
            # Close file handles
            fp.close()
            outfile.close()
    
            # Set path to log file for trace files
            log_file = '/home/du335/simulator/Interconnect/logs/chiplet_' + str(chiplet_idx) + '_layer_' + str(run_id) + '.log'
    
            # Copy trace file
            os.system('cp ' + file + ' ./trace_file.txt')
    
            # Run Booksim with config file and save log
            os.system('chmod +x /home/du335/simulator/Interconnect/booksim')
            booksim_command = '/home/du335/simulator/Interconnect/booksim ' + config_file + ' > ' + log_file
            # booksim_command = '/home/du335/BOOKSIM2_trace_based/src/booksim ' + config_file + ' > ' + log_file
            os.system(booksim_command)
    
            # Grep for packet latency average from log file
            latency = os.popen('grep "Trace is finished in" ' + log_file + ' | tail -1 | awk \'{print $5}\'').read().strip()
    
            print('[ INFO] Latency for Chiplet : ' + str(chiplet_idx) + ' Layer : ' + str(run_id) + ' is ' + latency  +'\t' + 'cycles' +'\n')
            total_latency = total_latency + int(latency)
    
    
            power = os.popen('grep "Total Power" ' + log_file + ' | tail -1 | awk \'{print $4}\'').read().strip()
    
            print('[ INFO] Power for Chiplet : ' + str(chiplet_idx)  + ' Layer : ' + str(run_id) + ' is ' + power + '\t' + 'mW' +'\n')
            
            total_power = total_power + float(power)
    
    
            area = os.popen('grep "Total Area" ' + log_file + ' | tail -1 | awk \'{print $4}\'').read().strip()
    
            # print('[ INFO] Area for Chiplet : ' + str(chiplet_idx)  + ' Layer : ' + str(run_id) + ' is ' + area + '\t' + 'um^2' + '\n')
    
            total_area = total_area + float(area)
    
        # Open output file handle to write area
        outfile_area = open('/home/du335/simulator/Interconnect/logs/booksim_area.csv', 'a')
    
        if file_counter == 0:
            # print('No NoC for this Chiplet.')
            outfile_area.write(str(0) + '\n')
            outfile_area.close()
            area_file = open('/home/du335/simulator/Interconnect/logs/Area_chiplet.csv', 'a')
            area_file.write('Total NoC area is' + '\t' + str(0) +  '\t' + 'um^2' + '\n')
            area_file.close()
        else:    
            outfile_area.write(str(total_area/file_counter) + '\n')
            outfile_area.close()
            area_file = open('/home/du335/simulator/Interconnect/logs/Area_chiplet.csv', 'a')
            area_file.write('Total NoC area is' + '\t' + str(total_area/file_counter) +  '\t' + 'um^2' + '\n')
            area_file.close()
            
        # Open output file handle to write latency
        outfile_latency = open('/home/du335/simulator/Interconnect/logs/booksim_latency.csv', 'a')
        outfile_latency.write(str(total_latency) + '\n')
        outfile_latency.close()
        latency_file = open('/home/du335/simulator/Interconnect/logs/Latency_chiplet.csv', 'a')
        latency_file.write('Total NoC latency is' + '\t' + str(total_latency*1/chip_clk_freq) + '\t' + 's' + '\n')
        latency_file.close()
    
        # Open output file handle to write power
        outfile_power = open('/home/du335/simulator/Interconnect/logs/booksim_power.csv', 'a')
        
        if file_counter == 0:
            outfile_power.write(str(0) + '\n')
            outfile_power.close()
            power_file = open('/home/du335/simulator/Interconnect/logs/Energy_chiplet.csv', 'a')
            power_file.write('Total NoC power is' + '\t' + str(0) + '\t' + 'W' + '\n')
            power_file.close()
        else:
            outfile_power.write(str(total_power/file_counter) + '\n')
            outfile_power.close()
            power_file = open('/home/du335/simulator/Interconnect/logs/Energy_chiplet.csv', 'a')
            # power_file.write('Total NoC power is' + '\t' + str(total_power/file_counter) + '\t' + 'mW' + '\n')
            power_file.write('Total NoC power is' + '\t' + str(total_power/file_counter *1e-03) + '\t' + 'W' + '\n')
            power_file.close()
    
