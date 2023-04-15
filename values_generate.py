import pandas as pd

# 读取Excel文件
df = pd.read_excel("ZD888-task.xlsx",
                   usecols=["会员订单号", "退供单号", "退供差异单号", "地区", "进度"])

# 筛选进度列为空的数据
df = df[df["进度"].isna()]

# 转换成字典格式并写入文件
for index, row in df.iterrows():
    file_name = str(row["退供单号"]) + ".values"
    with open(file_name, "w", encoding='GBK') as f:
        f.write("A={}\nB={}\nC={}\nD={}\nE={}".format(
            row["会员订单号"], row["退供单号"], row["退供差异单号"], row["退供差异单号"], row["地区"]))
