import openpyxl
import os
import shutil

def batch_operation_from_excel(excel_file, operation='copy'):
    """
    根据 Excel 表格中的规则批量复制或移动/重命名文件或文件夹。
    表格中 A 列为源路径，B 列为目标路径，从第二行开始读取。

    Args:
        excel_file (str): Excel 文件路径。
        operation (str, optional): 要执行的操作, 'copy' (复制) 或 'move' (移动/重命名)。
                                   默认为 'copy'。
    """
    # 打开Excel文件
    try:
        workbook = openpyxl.load_workbook(excel_file, read_only=True)
    except FileNotFoundError:
        print(f"错误: Excel文件 '{excel_file}' 未找到。")
        return
    sheet = workbook.active

    print(f"开始执行 '{operation}' 操作...")
    # 遍历每一行（从第二行开始，因为第一行是标题）
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        # 跳过空行或路径不完整的行
        if not row or not row[0] or not row[1]:
            continue

        source_path = str(row[0])
        destination_path = str(row[1])

        # 检查源路径是否存在
        if not os.path.exists(source_path):
            print(f"第 {row_idx} 行: 源路径不存在，跳过: {source_path}")
            continue

        try:
            if operation.lower() == 'copy':
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                    print(f"已复制目录: {source_path} -> {destination_path}")
                else:
                    # 确保目标目录存在
                    dest_dir = os.path.dirname(destination_path)
                    if dest_dir:
                        os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy2(source_path, destination_path)
                    print(f"已复制文件: {source_path} -> {destination_path}")
            elif operation.lower() == 'move':
                # 确保目标目录存在
                dest_dir = os.path.dirname(destination_path)
                if dest_dir:
                    os.makedirs(dest_dir, exist_ok=True)
                shutil.move(source_path, destination_path)
                print(f"已移动/重命名: {source_path} -> {destination_path}")
            else:
                print(f"不支持的操作: '{operation}'。请使用 'copy' 或 'move'。")
                break
        except Exception as e:
            print(f"第 {row_idx} 行: 处理 '{source_path}' -> '{destination_path}' 时出错: {e}")

    print(f"\n完成 '{operation}' 操作。")

if __name__ == "__main__":
    # --- 配置 ---
    # 指定Excel文件路径
    excel_file_path = "sheet.xlsx"
    # --- 配置结束 ---

    # 交互式选择操作类型
    operation_type = ''
    while operation_type not in ['copy', 'move']:
        choice = input("请选择要执行的操作: [1] 复制 (copy)  [2] 移动/重命名 (move)\n请输入选项数字或英文单词: ").lower().strip()
        if choice in ['1', 'copy']:
            operation_type = 'copy'
        elif choice in ['2', 'move']:
            operation_type = 'move'
        else:
            print("\n无效输入，请重新选择。\n")

    # 调用函数执行操作
    print("-" * 30)
    batch_operation_from_excel(excel_file_path, operation=operation_type)
    os.system("pause") # 在Windows上运行时暂停，方便查看结果
