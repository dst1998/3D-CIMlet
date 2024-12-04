import csv
# for Transformer model, save data like: T,d,h,dff,num_en,num_de,if_mem,T_mem...
# for Transformer_NetStructure model, save to NetStructure[][], 
#      each row: [0]input_row_num, [1]input_column_num, [2]weight_row_num, [3]weight_column_num, 
#                [4]output_row_num, [5]output_column_num, [6]dynamic(1)/ static(0), [7]have_softmax(1)/or not(0), [8] head_num (only for Q*KT and A'*V)
class GetData:
    def __init__(
                self,
                model_filename:str,
                hw_config_filename:str
                ):
        self.model_data = {}  # to store the model data dictionary from csv file
        # self.hw_config = {}  # to store the hw config dictionary from py file
        self.model_filename = model_filename
        # self.hw_config_filename = hw_config_filename
        self.NetStructure = []  # to store the network structure for Transformer_NetStructure model

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
                elif first_row[1] == "Transformer_NetStructure":
                    for row in csv_reader:
                        converted_row = [int(item) for item in row]
                        self.NetStructure.append(converted_row)  # Add each row to the NetStructure list
                    return self.NetStructure
        
        except FileNotFoundError:
            print(f"File '{self.model_filename}' not found.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")



