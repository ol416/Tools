import os
import pandas as pd

def rename_items_by_table(table_path):
    """
    根据表格中的规则批量重命名文件或文件夹。
    表格中 A 列为旧路径，B 列为新路径，忽略标题行。

    :param table_path: 表格文件路径（支持 .csv 或 .xlsx）。
    """
    # 读取表格数据
    if table_path.endswith('.csv'):
        table = pd.read_csv(table_path, header=0)  # 忽略标题行
    elif table_path.endswith('.xlsx'):
        table = pd.read_excel(table_path, header=0)  # 忽略标题行
    else:
        print("仅支持 .csv 或 .xlsx 格式的表格！")
        return

    # 检查表格中是否存在 A 和 B 列
    required_columns = ["A", "B"]
    if len(table.columns) < 2:
        print("表格中至少需要两列：A 列（旧路径）和 B 列（新路径）！")
        return

    # 遍历表格中的规则
    for index, row in table.iterrows():
        old_path = row[0]  # 假设第一列为旧路径
        new_path = row[1]  # 假设第二列为新路径

        # 检查旧路径是否存在
        if not os.path.exists(old_path):
            print(f"旧路径不存在：{old_path}")
            continue

        # 避免新路径重名
        counter = 1
        base_name, ext = os.path.splitext(new_path)
        while os.path.exists(new_path):
            new_path = f"{base_name}_{counter}{ext}"
            counter += 1

        # 重命名文件或文件夹
        try:
            os.rename(old_path, new_path)
            print(f"重命名成功: {old_path} -> {new_path}")
        except Exception as e:
            print(f"重命名失败: {old_path} -> {new_path}, 错误: {e}")

# 示例用法
if __name__ == "__main__":
    # 表格文件路径（支持 .csv 或 .xlsx）
    rules_table = r"./sheet.xlsx"

    # 执行批量重命名
    rename_items_by_table(rules_table)
