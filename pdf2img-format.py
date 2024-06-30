import os
import re
from PyPDF2 import PdfReader, PdfWriter
from wand.image import Image
from wand.color import Color

# 定义可能的正则表达式模式
patterns = [
    r'(59JF[A-Za-z0-9]+)',
    r'(69G[A-Z0-9]+)',
    r'(XV[A-Z0-9]+)'
]

def radio_size(w, h, x, model):
    '''根据指定模型计算比例尺寸'''
    if model == "w":
        return round(w / h * x)
    elif model == "h":
        return round(h / w * x)
    else:
        return round(w / h * x)

def extract_unique_identifier(page_content, patterns):
    for pattern in patterns:
        match = re.search(pattern, page_content)
        if match:
            return match.group(0).strip()
    return None

def save_page_as_pdf(page, output_path):
    writer = PdfWriter()
    writer.add_page(page)
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

def convert_pdf_to_jpeg(pdf_path, jpeg_path, resolution=300):
    with Image(filename=pdf_path, resolution=resolution) as img:
        img.alpha_channel = 'remove'
        img.compression_quality = 100
        img.units = 'pixelsperinch'
        img.format = 'jpg'
        img.resize(radio_size(img.width, img.height, 1600, "w"), 1600)
        img.crop(height=1550)
        img.extent(width=750, height=1600, gravity="center")
        img.save(filename=jpeg_path)

def split_and_rename_pdfs(input_folder, output_folder):
    # 检查输出文件夹是否存在，如果不存在则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists('img'):
        os.makedirs('img')

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            # 构造输入文件路径
            input_path = os.path.join(input_folder, filename)

            # 打开输入的PDF文件
            with open(input_path, 'rb') as file:
                reader = PdfReader(file)
                pages = reader.pages

                # 遍历每一页
                for page_number, page in enumerate(pages):
                    try:
                        # 获取当前页内容
                        page_content = page.extract_text()
                        # 提取唯一的标识符
                        unique_identifier = extract_unique_identifier(page_content, patterns)
                        if unique_identifier:
                            # 构造输出文件名
                            output_filename = f'{unique_identifier}.pdf'
                            output_path = os.path.join(output_folder, output_filename)
                            # 保存页面
                            save_page_as_pdf(page, output_path)
                            print(f'{output_filename} 已保存')

                            # 构造图像文件路径
                            output_jpeg_filename = f"{os.path.splitext(output_filename)[0]}.jpg"
                            output_jpeg_path = os.path.join('img', output_jpeg_filename)

                            # 转换PDF为JPEG
                            if not os.path.exists(output_jpeg_path):
                                convert_pdf_to_jpeg(output_path, output_jpeg_path)
                                print(f'{output_jpeg_filename} 已保存')
                        else:
                            print(f'{filename}-page:{page_number}>未找到匹配项')
                    except Exception as e:
                        print(f"Error processing page {page_number} of {filename}: {e}")

# 输入文件夹路径和输出文件夹路径
input_folder = 'data'
output_folder = 'output'

# 调用函数进行分页、提取内容和重命名操作
split_and_rename_pdfs(input_folder, output_folder)
