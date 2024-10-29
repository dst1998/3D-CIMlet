import pandas as pd
import re

# read original inference file path
file_path = '/home/du335/simulator/BERT_base_adapter_inf_12layer_12head_128token.csv' 
df = pd.read_csv(file_path, header=None)

# Use regex to extract the part before "_<number>layer"
match = re.match(r'(.*)_\d+layer', file_path.split('/')[-1])

if match:
    model_type = match.group(1)  # Extract "Transformer_adapter_inf"
    
    # Replace "inf" with "cl"
    new_model_type = model_type.replace("inf", "cl_semi_static")
    
    # Generate the new file path
    output_file_path = file_path.replace(model_type, new_model_type)

# Initialize a new list to store bp data
new_data = []
first_row = ['model_type', new_model_type] + [0] * 7
new_data.append(first_row)
# print("len(df):",len(df))
# Iterate over the penultimate line of the source file to generate the corresponding new line
# for new generated rows, if weights are stored in dynamic chip, row[6] is 2.
for i in range(len(df)):
    # Get the data of the penultimate i+1 row
    row = df.iloc[-(i+1)]
    if (row[8] == "output weight projection,"):
        new_row_1 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_outputProjection,"]
        new_row_2 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_outputProjection,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "adapter 2-2,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_adapter2-2,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_adapter2-2,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "adapter 2-1,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_adapter2-1,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_adapter2-1,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "ff2,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],0,0,"BP:weight_ff2,"]
        new_data.append(new_row_1)
    elif (row[8] == "ff1,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],0,0,"BP:weight_ff1,"]
        new_data.append(new_row_1)
    elif (row[8] == "adapter 1-2,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_adapter1-2,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_adapter1-2,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "adapter 1-1,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:weight_adapter1-1,"]
        new_row_2 = [row[5],row[4],row[0],row[1],row[3],row[2],2,0,"W Gradient:weight_adapter1-1,"]
        new_data.append(new_row_1)
        new_data.append(new_row_2)
    elif (row[8] == "head contact,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],0,0,"BP:weight_headContact,"]
        new_data.append(new_row_1)
    elif (row[8] == "KQT softmax * V,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:V,"]
        new_data.append(new_row_1)
    elif (row[8] == "K.Q,"):
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],2,0,"BP:Q,"]
        new_data.append(new_row_1)
    elif (row[8] == "K,Q,V projection,") and ((i+2)<=len(df)) and (df.iloc[-(i+2)][8] == "adapter 2-2,"):# only Wk, which is the first "K,Q,V projection,"
        new_row_1 = [row[4],row[5],row[3],row[2],row[0],row[1],0,0,"BP:weight_kProjection,"]
        new_data.append(new_row_1)
    else:
        continue

bp_df = pd.DataFrame(new_data)
bp_df = bp_df.iloc[1:].reset_index(drop=True) # delete bp_df first row ("model_type,...")

# add "FP:" to 8th term of each row
df.iloc[1:, 8] = df.iloc[1:, 8].apply(lambda x: f"FP:{x}" if isinstance(x, str) else x) 
# Modify the 6th column (static/dynamic) based on adapter conditions in the 8th column
adapter_conditions = ["FP:adapter 1-1,", "FP:adapter 1-2,", "FP:adapter 2-1,", "FP:adapter 2-2,","FP:output weight projection,"]
df.iloc[1:, 6] = df.iloc[1:].apply(lambda row: 1 if row[8] in adapter_conditions else row[6], axis=1)

cl_df = pd.concat([df, bp_df], axis=0, ignore_index=True)
cl_df.iloc[0, 1] = cl_df.iloc[0, 1].replace('inf', 'cl') # change the first row (model type) of whole new file 
# save to new csv file
cl_df.to_csv(output_file_path, index=False, header=False)

print(f"New file generated: {output_file_path}")

