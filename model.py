import csv
# for Transformer model, save data like: T,d,h,dff,num_en,num_de,if_mem,T_mem...
# for User-defined model, save to NetStructure[][], 
#      each row: [0]input_row_num, [1]input_column_num, [2]weight_row_num, [3]weight_column_num, 
#                [4]output_row_num, [5]output_column_num, [6]dynamic(1)/ static(0), [7]have_softmax(1)/or not(0), [8] head_num (only for Q*KT and A'*V)
class GetData:
    def __init__(
                self,
                model_filename:str,
                hw_config_filename:str
                ):
        self.model_data = {}  # to store the model data dictionary from csv file
        self.hw_config = {}  # to store the hw config dictionary from py file
        self.model_filename = model_filename
        self.hw_config_filename = hw_config_filename
        self.NetStructure = []  # to store the network structure for User-defined model

    def load_model(self):
        try:
            with open(self.model_filename, mode='r', newline='') as file:
                csv_reader = csv.reader(file)
                first_row = next(csv_reader)  # Read the first line to determine the model type
                if first_row[1] == "Transformer":
                    for row in csv_reader:
                        if len(row) == 2:  # check if there's a key-value pair in each row
                            key, value = row[0], int(row[1])
                            self.model_data[key] = value
                        else:
                            print(f"Ignoring invalid row: {row}")
                    return self.model_data
                elif first_row[1] == "User-defined":
                    for row in csv_reader:
                        converted_row = [int(item) for item in row]
                        self.NetStructure.append(converted_row)  # Add each row to the NetStructure list
                    return self.NetStructure
        
        except FileNotFoundError:
            print(f"File '{self.model_filename}' not found.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    
    def load_hardware_config(self): # add try/except later
        with open(self.hw_config_filename, 'r') as file:
            for line in file:
                # remove spaces at the beginning and end of the line and remove the comment section
                line = line.strip().split('#')[0].strip()
            
                # ignore blank line
                if not line:
                    continue

                key, value = line.split('=')
            
                # remove spaces from the ends of keys and values
                key = key.strip()
                value = value.strip()
            
                self.hw_config[key] = value

        return self.hw_config





# # e.g.
# csv_file = "/home/nanoxing/a/du335/purdue-glibreth-server/simulator/user_defined_example.csv" 
# config_file = "/home/nanoxing/a/du335/purdue-glibreth-server/simulator/hw_config.txt" 
# model_data_loader = GetData(csv_file, config_file)
# model_data_loader.load_model()
# for row in model_data_loader.NetStructure:
#     print(row)
# hw_config = GetData(csv_file,config_file).load_hardware_config()
# print(hw_config)



