import pandas as pd
import math

model_layer = 2
head = 12
token_len = 16
dim = 768
dim_ff = dim*4
dim_head = math.ceil(dim/head)
dim_out = 32 # final classification
num_onelayer_row = 3+ head*2 +3
num_file_row = (3+ head*2 +3) * model_layer +1 # +1: final output weight after all layers
model_type = 'Transformer_inf'
# 定义第一行自定义内容
first_row = ['model_type', model_type] + [0] * 7

# 初始化一个空列表用于存储所有行
data = [first_row]  # 第一行自定义的内容

# 使用for loop来根据行的index生成内容
for i in range(1, num_file_row+1):  # 这里我们生成10行数据，第一行是自定义行，其他从1到9
    if ((i%num_onelayer_row == 1 and i != num_file_row) or i%num_onelayer_row == 2 or i%num_onelayer_row == 3 ):  # K,Q,V projection
        row = [token_len, dim, dim, dim, token_len, dim, 0, 0, "K,Q,V projection,"]
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
        row = [token_len, dim, dim, dim_out, token_len, dim_out, 0, 0, "output weight projection,"]
    data.append(row)

# 将数据转换为DataFrame
df = pd.DataFrame(data)

df.iloc[1:, :-1] = df.iloc[1:, :-1].astype(int)

# 保存为新的CSV文件
output_file_path = '/home/du335/simulator/' + model_type + '_' + str(model_layer) + 'layer' + '_' + str(head) + 'head' + '_' + str(token_len) + 'token' + '.csv'
df.to_csv(output_file_path, index=False, header=False)

print(f"New file generated: {output_file_path}")