import csv
# Just only consider Transformer model, save data like: T,d,h,dff,num_en,num_de,if_mem,T_mem...
# Add DNN later? save to NetStructure[][] for multi-layer DNN, change in load_model
class GetData:
    def __init__(
                self,
                model_filename:str,
                hw_config_filename:str,
                ):
        self.model_data = {}  # to store the model data dictionary from csv file
        self.hw_config = {}  # to store the hw config dictionary from py file
        self.model_filename = model_filename
        self.hw_config_filename = hw_config_filename

    def load_model(self):
        try:
            with open(self.model_filename, mode='r', newline='') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) == 2:  # check if there's a key-value pair in each row
                        key, value = row
                        self.model_data[key] = value
                    else:
                        print(f"Ignoring invalid row: {row}")
            return self.model_data
        
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





# e.g.
csv_file = "/home/du335/simulator/model_bert_base.csv" 
config_file = "/home/du335/simulator/hw_config.txt" 
model_data = GetData(csv_file, config_file).load_model()
print(model_data)
hw_config = GetData(csv_file,config_file).load_hardware_config()
print(hw_config)



