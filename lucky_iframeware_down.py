import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

def find_links(url, session):
    """
    通过 HTTP 请求获取网页内容并使用 BeautifulSoup 解析，返回所有链接。
    """
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return []

def download_file(url, session, save_path):
    """
    下载指定 URL 的文件并保存到本地指定路径。
    """
    try:
        with session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            print(f"开始下载: {url} 到 {save_path}")
            
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"下载完成: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")

def main():
    base_url = "https://release.66666.host/"
    download_dir = "downloaded_firmware"

    with requests.Session() as session:
        print("正在遍历主目录...")
        # 查找所有一级目录链接
        top_level_links = find_links(base_url, session)

        for dir_link in top_level_links:
            if dir_link.endswith('/'):
                dir_url = urljoin(base_url, dir_link)
                print(f"正在检查一级目录: {dir_url}")

                # 获取二级目录链接
                second_level_links = find_links(dir_url, session)

                # 找到wanji和lucky目录
                wanji_dirs = [link for link in second_level_links if link.endswith('/') and "wanji" in link]
                lucky_dirs = [link for link in second_level_links if link.endswith('/') and "lucky" in link]

                for wanji_link in wanji_dirs:
                    wanji_url = urljoin(dir_url, wanji_link)
                    print(f"找到wanji目录: {wanji_url}")

                    # 在wanji目录中下载wanji文件
                    file_links = find_links(wanji_url, session)
                    for file_link in file_links:
                        if "_Linux_arm64_wanji.tar.gz" in file_link:
                            file_url = urljoin(wanji_url, file_link)
                            clean_dir_link = dir_link.rstrip('/')
                            clean_wanji_link = wanji_link.rstrip('/')
                            relative_path = os.path.join(clean_dir_link, clean_wanji_link, file_link)
                            save_path = os.path.join(download_dir, relative_path)

                            if os.path.exists(save_path):
                                print(f"文件已存在，跳过: {save_path}")
                                continue
                            download_file(file_url, session, save_path)

                for lucky_link in lucky_dirs:
                    lucky_url = urljoin(dir_url, lucky_link)
                    print(f"找到lucky目录: {lucky_url}")

                    # 在lucky目录中下载Linux_arm64文件
                    file_links = find_links(lucky_url, session)
                    for file_link in file_links:
                        if "_Linux_arm64.tar.gz" in file_link and "wanji" not in file_link:
                            file_url = urljoin(lucky_url, file_link)
                            clean_dir_link = dir_link.rstrip('/')
                            clean_lucky_link = lucky_link.rstrip('/')
                            relative_path = os.path.join(clean_dir_link, clean_lucky_link, file_link)
                            save_path = os.path.join(download_dir, relative_path)

                            if os.path.exists(save_path):
                                print(f"文件已存在，跳过: {save_path}")
                                continue
                            download_file(file_url, session, save_path)
                        
if __name__ == "__main__":
    main()
