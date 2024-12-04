import os
import shutil
from multiprocessing import Pool, cpu_count

def move_files(args):
    """单个文件/文件夹移动的任务"""
    item_path, target_folder = args
    try:
        shutil.move(item_path, os.path.join(target_folder, os.path.basename(item_path)))
    except Exception as e:
        print(f"移动 {item_path} 时出错: {e}")

def split_folder_parallel(input_folder, output_base, limit=50000):
    # 确保输出基路径存在
    if not os.path.exists(output_base):
        os.makedirs(output_base)

    # 获取输入文件夹中的所有项目
    items = os.listdir(input_folder)
    total_items = len(items)

    # 计算批次数量
    num_batches = (total_items + limit - 1) // limit
    print(f"总共有 {total_items} 个项目，将分成 {num_batches} 个文件夹。")

    # 生成目标文件夹路径
    batches = []
    for batch_number in range(1, num_batches + 1):
        batch_folder = os.path.join(output_base, f"batch_{batch_number}")
        if not os.path.exists(batch_folder):
            os.makedirs(batch_folder)
        batches.append(batch_folder)

    # 为每个项目分配目标文件夹
    tasks = []
    for i, item in enumerate(items):
        batch_index = i // limit
        target_folder = batches[batch_index]
        item_path = os.path.join(input_folder, item)
        tasks.append((item_path, target_folder))

    # 使用多进程移动文件
    print(f"开始使用 {cpu_count()} 个核心处理...")
    with Pool(processes=cpu_count()) as pool:
        pool.map(move_files, tasks)

    print("文件夹拆分完成！")

if __name__ == "__main__":
    # 参数设置
    input_folder = "./batch_image"  # 输入文件夹路径
    output_base = "./split_folders"  # 输出基路径
    limit = 50000  # 每个文件夹最多包含的项目数

    # 调用拆分函数
    split_folder_parallel(input_folder, output_base, limit)
