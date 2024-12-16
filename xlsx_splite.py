import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

output_folder = "xlsx"

if not  os.path.exists(output_folder):
    os.mkdir(output_folder)
# 读取 Excel 文件
df = pd.read_excel('test.xlsx', header=None)



# 找到每个款号的索引
item_indices = df[df[0] == '款号'].index

# 循环处理每个款号及其对应的尺码表
for i in range(len(item_indices)):
    start_index = item_indices[i]
    end_index = item_indices[i+1] if i+1 < len(item_indices) else df.shape[0]
    
    # 获取款号及其对应的尺码表部分
    item_data = df.iloc[start_index:end_index]
       
    # 提取款号
    item_number = item_data.iloc[0, 1]
    
    # 去除前两行
    item_data = item_data.iloc[2:]
    
    # 去除全是 NaN 的列
    item_data = item_data.dropna(axis=0,how="all")
    
    item_data = item_data.dropna(axis=1)

    
    # 保存为新的 Excel 文件
    output = os.path.join(output_folder,f'{item_number}.xlsx')
    item_data.to_excel(output, index=False, header=False)
