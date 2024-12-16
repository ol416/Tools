import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def get_all_files(path) -> list:
    allfile = []
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            allfile.append(os.path.join(dirpath, dir))
        for name in filenames:
            allfile.append(os.path.join(dirpath, name))
    return allfile

output_folder = "xlsx"

if not  os.path.exists(output_folder):
    os.mkdir(output_folder)
# 读取 Excel 文件
size_table = [os.path.join("./pdc_info",_) for _ in os.listdir('./pdc_info') if "product_sizetable_export" in _]
df = pd.read_excel(size_table[0], header=None)



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
    # item_data = item_data.dropna(axis=0,how="all")
    
    # item_data = item_data.dropna(axis=1)

    
    # 保存为新的 Excel 文件
    output = os.path.join(output_folder,f'{item_number}.xlsx')
    item_data.to_excel(output, index=False, header=False)


# 获取文件夹内所有xlsx文件路径
all_file = [_ for _ in get_all_files(output_folder) if "xlsx" in os.path.splitext(_)[1]]
df = pd.DataFrame()

# 将数据导入到合并表头的dataframe里。
for i in all_file:
    filename = os.path.splitext(os.path.basename(i))[0]
    xlsx = pd.read_excel(i,header=0)
    if not xlsx.empty:
        xlsx.loc[:,"款号"]=filename
    df = pd.concat([df,xlsx],axis=0,join='outer')
df = df.sort_index(axis=1)
# 去除全是 NaN 的列
df = df.dropna(axis=0,how="all")
# print(df)

#     df = pd.concat(df,xlsx)
df.to_csv('i.csv',encoding='GBK',index=None)