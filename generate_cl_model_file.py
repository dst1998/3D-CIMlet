import pandas as pd

# 读取现有的CSV文件
file_path = '/home/du335/simulator/example_onelayer.csv'  # 替换为你的文件路径
df = pd.read_csv(file_path, header=None)

# 初始化一个空列表，用于存储新数据
new_data = []

# 遍历源文件的倒数行生成对应的新行
for i in range(len(df)):
    # 取得倒数第i+1行的数据
    row = df.iloc[-(i+1)]
    
    # 生成新行的逻辑：你可以根据倒数的行进行操作
    new_row = [
        row[-2],  # 例如，倒数第二项
        row[-3],  # 倒数第三项
        row[1] * 2,  # 例如，第二项乘以2
        row[2] * 2,  # 第三项乘以2
        row[4],  # 复制第5项
        row[5] * 2,  # 第6项乘以2
        1 if row[6] == 0 else 0,  # 取反第7项
        row[7],  # 复制第8项
        row[8]  # 复制第9项
    ]
    
    # 将新行添加到new_data列表中
    new_data.append(new_row)

    # 可以再根据需求生成额外的行
    extra_row = [
        row[-2] * 2,  # 比如，倒数第二项乘以2
        row[-3] * 2,  # 倒数第三项乘以2
        row[1] + 100,  # 第二项加上100
        row[2] + 100,  # 第三项加上100
        row[4],  # 复制第5项
        row[5] + 100,  # 第6项加上100
        row[6],  # 复制第7项
        row[7],  # 复制第8项
        row[8]  # 复制第9项
    ]
    
    # 添加额外的行
    new_data.append(extra_row)

# 将new_data转换为DataFrame并与原始DataFrame合并
new_df = pd.DataFrame(new_data)
df = pd.concat([df, new_df], ignore_index=True)

# 保存为新的CSV文件
output_file_path = 'new_file.csv'  # 替换为你想保存的新文件路径
df.to_csv(output_file_path, index=False, header=False)

print(f"新CSV文件已保存到: {output_file_path}")

