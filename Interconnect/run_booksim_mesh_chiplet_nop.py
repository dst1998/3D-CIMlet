import os, re, glob, sys, math
import numpy

def run_booksim_mesh_chiplet_nop(config, nop_clk_freq, trace_file_dir, bus_width):


    #os.chdir(trace_file_dir)
    #mesh_sizes_per_layer = pd.readcsv('mesh_sizes_per_layer.csv')
    mesh_size_file_name = trace_file_dir + '/nop_mesh_size.csv'
    mesh_size = int(numpy.loadtxt(mesh_size_file_name))
    #os.chdir('..')
    
    
    # Initialize file counter
    file_counter = 0
    
    # Create directory to store config files
    os.system('mkdir -p /home/du335/simulator/Interconnect/logs_NoP/configs')

    # Open the file and check if it has content
    area_file_path = '/home/du335/simulator/Interconnect/logs_NoP/Area_chiplet.csv'
    # Check if the file exists and if it is empty
    if os.path.exists(area_file_path):
        with open(area_file_path, 'r+') as area_file:
            content = area_file.read()
            if content:  # If the file has content
                area_file.seek(0)  # Move the pointer to the beginning of the file
                area_file.truncate()  # Clear the file

    # Open the file and check if it has content
    latency_file_path = '/home/du335/simulator/Interconnect/logs_NoP/Latency_chiplet.csv'
    # Check if the file exists and if it is empty
    if os.path.exists(latency_file_path):
        with open(latency_file_path, 'r+') as latency_file:
            content = latency_file.read()
            if content:  # If the file has content
                latency_file.seek(0)  # Move the pointer to the beginning of the file
                latency_file.truncate()  # Clear the file
    
    # Open the file and check if it has content
    latencyCycle_eachlayer_file_path = '/home/du335/simulator/Interconnect/logs_NoP/NoP_LatencyCycle_eachLayer.csv'
    # Check if the file exists and if it is empty
    if os.path.exists(latencyCycle_eachlayer_file_path):
        with open(latencyCycle_eachlayer_file_path, 'r+') as latencyCycle_eachlayer_file:
            content = latencyCycle_eachlayer_file.read()
            if content:  # If the file has content
                latencyCycle_eachlayer_file.seek(0)  # Move the pointer to the beginning of the file
                latencyCycle_eachlayer_file.truncate()  # Clear the file
    
    # Open the file and check if it has content
    power_file_path = '/home/du335/simulator/Interconnect/logs_NoP/Energy_chiplet.csv'
    # Check if the file exists and if it is empty
    if os.path.exists(power_file_path):
        with open(power_file_path, 'r+') as power_file:
            content = power_file.read()
            if content:  # If the file has content
                power_file.seek(0)  # Move the pointer to the beginning of the file
                power_file.truncate()  # Clear the file
    
        
    # Get a list of all files in directory
    files = glob.glob(trace_file_dir + '/*.txt')
    file_counter = 0
    total_latency = 0
    total_area = 0
    total_power = 0
    
    # Iterate over all files
    for file in files :
    
        # print('[ INFO] Processing file ' + file + ' ...')
    
        # Extract file name without extension and absolute path from filename
        run_name = os.path.splitext(os.path.basename(file))[0]
        # run_id = run_name.strip('trace_file_chiplet_')
        match = re.search(r'trace_file_srcL_(\d+)_destL_(\d+)', run_name)
        if match:
            src_layer_idx = match.group(1)
            dest_layer_idx = match.group(2)
            run_id = f'{str(src_layer_idx)}_to_{str(dest_layer_idx)}'
    
    
        # trace file
        # trace_file_name = 'trace_file_chiplet_' + str(file_counter) + '.txt'
    
    
        # Open read file handle of config file
        fp = open('/home/du335/simulator/Interconnect/mesh_config_trace_based_nop', 'r')
    
        # Set path to config file
        # config_file = '/home/du335/simulator/Interconnect/logs_NoP/configs/chiplet_' + str(file_counter) + '_mesh_config'
        config_file = '/home/du335/simulator/Interconnect/logs_NoP/configs/chiplets' + '_mesh_config'
    
        # Open write file handle for config file
        outfile = open(config_file, 'w')

        # Iterate over file and set size of mesh in config file
        for line in fp :
    
            line = line.strip()
    
            # Search for pattern
            matchobj = re.match(r'^k=', line)
    
            # Set size of mesh if line in file corresponds to mesh size
            if matchobj :
                line = 'k=' + str(mesh_size) + ';'
    
            # Search for pattern
            matchobj1 = re.match(r'^channel_width = ', line)
    
            # Set size of mesh if line in file corresponds to mesh size
            if matchobj1 :
                line = 'channel_width = ' + str(bus_width) + ';'
            
            # Write config to file
            outfile.write(line + '\n')
    
        # Close file handles
        fp.close()
        outfile.close()
    
        # Set path to log file for trace files
        log_file = '/home/du335/simulator/Interconnect/logs_NoP/layer_'  + str(run_id) + '.log'
    
        # Copy trace file ( to ' trace_file.txt' as input of Booksim??)
        os.system('cp ' + file + ' trace_file.txt')
    
        # Run Booksim with config file and save log
        os.system('chmod +x /home/du335/simulator/Interconnect/booksim')
        booksim_command = '/home/du335/simulator/Interconnect/booksim ' + config_file + ' > ' + log_file
        os.system(booksim_command)
    
        # Grep for packet latency average from log file
        latency = os.popen('grep "Trace is finished in" ' + log_file + ' | tail -1 | awk \'{print $5}\'').read().strip()
    
        print('[ INFO] Latency for Layer : ' + str(run_id) + ' is ' + latency + '\t' + 'cycles' +'\n')
        total_latency = total_latency + int(latency)
        
        # NoP latency for each two layers
        latencyCycle_eachlayer_file = open('/home/du335/simulator/Interconnect/logs_NoP/NoP_LatencyCycle_eachLayer.csv', 'a')
        latencyCycle_eachlayer_file.write('NoP latency for layer' +'\t' + str(run_id) + '\t'+'is' +'\t' + str(latency) +'\t' + 'cycles' + '\n')
        latencyCycle_eachlayer_file.close()
    
    
        # power = os.popen('grep "Total Power" ' + log_file + ' | tail -1 | awk \'{print $4}\'').read().strip()
        # Find the last line in the log file that contains “Total Power”.
        grep_power_result = os.popen('grep "Total Power" ' + log_file + ' | tail -1').read().strip()

        if grep_power_result:  # If a matching line is found
            # Extracts the value of the fourth field and converts it to a floating point number
            power = os.popen('echo "' + grep_power_result + '" | awk \'{print $4}\'').read().strip()
        else:  # If not found
            power = "0"
    
        print('[ INFO] Power for Layer : '  + str(run_id) + ' is ' + power + '\t' + 'mW' +'\n')
        total_power = total_power + float(power)
    
    
        # area = os.popen('grep "Total Area" ' + log_file + ' | tail -1 | awk \'{print $4}\'').read().strip()
        grep_area_result = os.popen('grep "Total Area" ' + log_file + ' | tail -1').read().strip()

        if grep_area_result:  # If a matching line is found
            # Extracts the value of the fourth field and converts it to a floating point number
            area = os.popen('echo "' + grep_area_result + '" | awk \'{print $4}\'').read().strip()
        else:  # If not found
            area = "0"
    
        # print('[ INFO] Area for Chiplet : ' + str(run_id) + ' is ' + area + '\t' + 'um^2' +'\n')
    
        total_area = total_area + float(area)

        # Increment file counter
        file_counter += 1
    
    # Open output file handle to write area
    outfile_area = open('/home/du335/simulator/Interconnect/logs_NoP/booksim_area.csv', 'a')
    # outfile_area.write(str(total_area/file_counter) + '\n')
    # outfile_area.close()

    # area_file = open('/home/du335/simulator/Interconnect/logs_NoP/Area_chiplet.csv', 'a')
    # area_file.write('Total NoP area is' + '\t' + str(total_area/file_counter) + '\t' + 'um^2' + '\n')
    # area_file.close()
    
    if file_counter == 0:
        # print('No NoP for this Chiplet.')
        outfile_area.write(str(0) + '\n')
        outfile_area.close()
        area_file = open('/home/du335/simulator/Interconnect/logs_NoP/Area_chiplet.csv', 'a')
        area_file.write('Total NoP area is' + '\t' + str(0) +  '\t' + 'um^2' + '\n')
        area_file.close()
    else:    
        outfile_area.write(str(total_area/file_counter) + '\n')
        outfile_area.close()
        area_file = open('/home/du335/simulator/Interconnect/logs_NoP/Area_chiplet.csv', 'a')
        area_file.write('Total NoP area is' + '\t' + str(total_area/file_counter) +  '\t' + 'um^2' + '\n')
        area_file.close()
        
    # Open output file handle to write latency
    outfile_latency = open('./logs_NoP/booksim_latency.csv', 'a')
    outfile_latency.write(str(total_latency) + '\n')
    outfile_latency.close()

    latency_file = open('/home/du335/simulator/Interconnect/logs_NoP/Latency_chiplet.csv', 'a')
    latency_file.write('Total NoP latency is' +'\t' + str(total_latency*1/nop_clk_freq) +'\t' + 's' + '\n')
    latency_file.close()
    
    # Open output file handle to write power
    outfile_power = open('./logs_NoP/booksim_power.csv', 'a')
    # outfile_power.write(str(total_power/file_counter) + '\n')
    # outfile_power.close()

    # power_file = open('/home/du335/simulator/Interconnect/logs_NoP/Energy_chiplet.csv', 'a')
    # power_file.write('Total NoP power is' +'\t' + str(total_power/file_counter) +'\t' + 'mW' + '\n')
    # power_file.close()
    
    if file_counter == 0:
        outfile_power.write(str(0) + '\n')
        outfile_power.close()
        power_file = open('/home/du335/simulator/Interconnect/logs_NoP/Energy_chiplet.csv', 'a')
        power_file.write('Total NoP power is' + '\t' + str(0) + '\t' + 'W' + '\n')
        power_file.close()
    else:
        outfile_power.write(str(total_power/file_counter) + '\n')
        outfile_power.close()
        power_file = open('/home/du335/simulator/Interconnect/logs_NoP/Energy_chiplet.csv', 'a')
        # power_file.write('Total NoP power is' + '\t' + str(total_power/file_counter) + '\t' + 'mW' + '\n')
        power_file.write('Total NoP power is' + '\t' + str(total_power/file_counter *1e-03) + '\t' + 'W' + '\n')
        power_file.close()  