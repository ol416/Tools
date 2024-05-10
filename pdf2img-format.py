# 文件名：split_and_rename_pdfs.py
# 语言：Python

import os
import re
from PyPDF2 import PdfReader, PdfWriter
from wand.image import Image
from wand.color import Color
from PIL import Image as PImage

def radio_size(w, h, x, model):
    '''根据指定模型计算比例尺寸'''
    if model == "w":
        return round(w / h * x)
    elif model == "h":
        return round(h / w * x)
    else:
        return round(w / h * x)

def get_img_size(fn, types=True):
    '''获取图像尺寸'''
    '''types = True cm, types = False pixel'''
    img = PImage.open(fn)
    dpi = img.info['dpi'][0]
    if types:
        width, height = map(lambda x: x/dpi*2.54, img.size)
    else:
        width, height = map(lambda x: x, img.size)
    return round(width), round(height), dpi

def split_and_rename_pdfs(input_folder, output_folder):
    # 检查输出文件夹是否存在，如果不存在则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            # 构造输入文件路径
            input_path = os.path.join(input_folder, filename)

            # 打开输入的PDF文件
            with open(input_path, 'rb') as file:
                reader = PdfReader(file)
                # 遍历每一页
                for page_number, page in enumerate(reader.pages):
                    # 创建一个新的PDF写入器
                    writer = PdfWriter()

                    # 获取当前页内容
                    page_content = page.extract_text()
                    regex_str = r'(59JF[A-Za-z0-9]+)'
                    if "LIU·JO" in page_content:
                        regex_str = r'(69G[A-Z0-9]+)'
                    match = re.findall(regex_str, page_content)

                    if match:
                        match_str = match[0].strip()
                    else:
                        print(f'{file.name}-page:{page_number}>未找到匹配项')
                        continue

                    # 构造输出文件名
                    output_filename = f'{match_str}.pdf'
                    output_path = os.path.join(output_folder, output_filename)
                    if not os.path.exists(output_path):
                        # 将当前页添加到新的PDF文件中
                        writer.add_page(page)
                        # 保存新的PDF文件
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                            print(f'{output_filename} 已保存')

                    # 构造图像文件路径
                    output_jpeg_filename = f"{os.path.splitext(output_filename)[0]}.jpg"
                    output_jpeg_path = os.path.join('img', output_jpeg_filename)

                    # 转换PDF为JPEG
                    if not os.path.exists(output_jpeg_path):
                        if not os.path.exists('img'):
                            os.makedirs('img')
                        with Image(filename=output_path, resolution=300) as img:
                            img.alpha_channel = 'remove'
                            img.compression_quality = 100
                            img.units = 'pixelsperinch'
                            img.format = 'jpg'
                            img.resize(radio_size(img.width, img.height, 1600, "w"), 1600)
                            img.crop(height=1550)
                            img.extent(width=750, height=1600, gravity="center")
                            img.save(filename=output_jpeg_path)
                            print(f'{output_jpeg_filename} 已保存')

# 输入文件夹路径和输出文件夹路径
input_folder = 'data'
output_folder = 'output'

# 调用函数进行分页、提取内容和重命名操作
split_and_rename_pdfs(input_folder, output_folder)
