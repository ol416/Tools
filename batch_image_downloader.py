import os
import time
import requests
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置参数
EXCEL_FILE = "./所有图片缩略图.xlsx"  # Excel文件名
SAVE_DIR = './batch_image'  # 保存图片的文件夹
BATCH_SIZE = 2000  # 每批下载的数量
THREAD_COUNT = 25  # 同时下载的线程数
BATCH_SLEEP_TIME = 3  # 每批下载完成后休眠的时间（秒）
RETRY_TIMES = 5  # 每个文件的最大重试次数
DOWNLOADED_LOG = 'downloaded_files.txt'  # 已下载文件的记录日志

# 创建保存目录
os.makedirs(SAVE_DIR, exist_ok=True)

# 读取Excel文件
print("正在加载Excel数据...")
data = pd.read_excel(EXCEL_FILE, usecols=[0, 1], header=0, names=['url', 'filename'])
total_files = len(data)
print(f"总文件数量：{total_files}")

# 加载已下载文件记录
if os.path.exists(DOWNLOADED_LOG):
    with open(DOWNLOADED_LOG, 'r') as f:
        downloaded_files = set(f.read().splitlines())
else:
    downloaded_files = set()

# 下载函数
def download_file(url, save_path):
    for attempt in range(RETRY_TIMES):
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
        except Exception as e:
            print(f"下载失败: {url}，重试 {attempt + 1}/{RETRY_TIMES}，错误: {e}")
        time.sleep(1)
    return False

# 分批并发下载
failed_links = []

def download_batch(batch):
    """处理一批次下载"""
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = {}
        for _, row in batch.iterrows():
            url = row['url']
            filename = row['filename']
            save_path = os.path.join(SAVE_DIR, filename)
            
            # 如果文件已存在或已记录，则跳过
            if os.path.exists(save_path) or filename in downloaded_files:
                continue
            
            # 提交任务
            futures[executor.submit(download_file, url, save_path)] = filename
        
        # 等待任务完成
        for future in tqdm(as_completed(futures), total=len(futures), desc="批次下载进度"):
            filename = futures[future]
            if future.result():  # 下载成功
                downloaded_files.add(filename)
                with open(DOWNLOADED_LOG, 'a') as log:
                    log.write(filename + '\n')
            else:
                failed_links.append(filename)

print("开始下载...")
for start in range(0, total_files, BATCH_SIZE):
    end = min(start + BATCH_SIZE, total_files)
    batch = data.iloc[start:end]
    print(f"正在处理第 {start + 1}-{end} 个文件...")
    
    download_batch(batch)  # 并发处理一批文件

    # 批次休眠
    print(f"第 {start + 1}-{end} 批次下载完成，休眠 {BATCH_SLEEP_TIME} 秒...")
    time.sleep(BATCH_SLEEP_TIME)

# 保存失败链接
if failed_links:
    failed_file = os.path.join(SAVE_DIR, 'failed_links.txt')
    with open(failed_file, 'w') as f:
        f.writelines([link + '\n' for link in failed_links])
    print(f"下载失败的链接已保存到 {failed_file}")

print("下载完成！")
