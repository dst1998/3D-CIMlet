import pandas as pd
import math

model_layer = 12
head = 12
# token_len = 128
# token_len = 196 # for gpt2
token_len = (224//16)*(224//16) # 196 for DeiT
dim = 768
dim_ff = dim*4
dim_head = math.ceil(dim/head)
# dim_out = 2 # final classification #where did you get this for bert base, there are a lot of task and output depends on task to task
dim_out = 1000 # final classification for gpt2
num_onelayer_row = 3+ head*2 +3
num_file_row = (3+ head*2 +3) * model_layer +1 # +1: final output weight after all layers
# model_type = 'Transformer_inf'
model_type = 'DeiT_inf'
# Define the first line of customization
first_row = ['model_type', model_type] + [0] * 7

# Initialize an empty list for storing all rows
data = [first_row]
row = [token_len, dim, dim, dim, token_len, dim, 0, 0, "Token Generation,"]
data.append(row)
for i in range(1, num_file_row+1):
    # if ((i%num_onelayer_row == 1 and i != num_file_row) or i%num_onelayer_row == 2 or i%num_onelayer_row == 3 ):  # K,Q,V projection
    if ((i%num_onelayer_row == 1 and i != num_file_row) or i%num_onelayer_row == 2 or i%num_onelayer_row == 3):  # K, V projection
        row = [token_len, dim, dim, dim, token_len, dim, 0, 0, "K,Q,V projection,"]  ## 3 of these multiplications right? 
    # elif (i%num_onelayer_row == 3):
    #     if 'Gpt2' in model_type:
    #         row = [1, dim, dim, dim, 1, dim, 0, 0, "Q projection,"]
    elif ((3 < i%num_onelayer_row < num_onelayer_row-2) and (i%2 == 0)):  # KQ softmax
        row = [token_len, dim_head, dim_head, token_len, token_len, token_len, 1, 1,"K.Q,"]
    elif ((3 < i%num_onelayer_row < num_onelayer_row-2) and (i%2 == 1)):  # KQ softmax * V
        row = [token_len, token_len, token_len, dim_head, token_len, dim_head, 1, 0,"KQT softmax * V,"]
    elif (i%num_onelayer_row == num_onelayer_row-2):  # head contact
        row = [token_len, dim, dim, dim, token_len, dim, 0, 0,"head contact,"]
    elif (i%num_onelayer_row == num_onelayer_row-1):  # ff1
        row = [token_len, dim, dim, dim_ff, token_len, dim_ff, 0, 0, "ff1,"]
    elif (i%num_onelayer_row == 0 and i !=0):  # ff2
        row = [token_len, dim_ff, dim_ff, dim, token_len, dim, 0, 0, "ff2,"]
    elif (i%num_onelayer_row == 1 and i == num_file_row):  # final output weight projection
        row = [token_len, dim, dim, dim_out, token_len, dim_out, 0, 1, "output weight projection,"]
    data.append(row)

df = pd.DataFrame(data)

df.iloc[1:, :-1] = df.iloc[1:, :-1].astype(int)

# Saved as a new CSV file
output_file_path = '/home/du335/simulator/' + model_type + '_' + str(model_layer) + 'layer' + '_' + str(head) + 'head' + '_' + str(token_len) + 'token' + '.csv'
df.to_csv(output_file_path, index=False, header=False)

print(f"New file generated: {output_file_path}")