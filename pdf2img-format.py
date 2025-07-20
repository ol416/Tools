import os
import re
import blake3
import json
from PyPDF2 import PdfReader, PdfWriter
from wand.image import Image
from wand.color import Color

# 定义可能的正则表达式模式
patterns = [
    r'(59JF[A-Za-z0-9]+)',
    r'(69G[A-Z0-9]+)',
    r'(XV[A-Z0-9]+)',
    r'(WP-XY[A-Z0-9]+)',
    r'(59FV[A-Za-z0-9]+)'
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

def add_bottom_background_and_shadow(image, background_color='#f1f1f1', padding=30, shadow_offset=10):
    """
    給圖片加上底部背景和陰影，模仿卡片懸浮效果
    """
    # 計算新圖片尺寸
    new_width = image.width + padding * 2
    new_height = image.height + padding * 2 + 20  # 底部再加一點額外空間

    # 建立底層背景
    with Image(width=new_width, height=new_height, background=Color(background_color)) as bg:
        # 加入陰影
        with image.clone() as shadow:
            shadow.background_color = Color('black')
            shadow.alpha_channel = 'activate'
            shadow.shadow(0, shadow_offset, 10, 0)  # blur強度 & y軸位移
            bg.composite(shadow, left=padding + 4, top=padding + 4)

        # 貼上原圖
        bg.composite(image, left=padding, top=padding)
        return bg.clone()


def convert_pdf_to_jpeg(pdf_path, jpeg_path, resolution=300):
    with Image(filename=pdf_path, resolution=resolution) as img:
        img.alpha_channel = 'remove'
        img.compression_quality = 100
        img.units = 'pixelsperinch'
        img.format = 'jpg'
        img.resize(radio_size(img.width, img.height, 1600, "w"), 1600)
        img.crop(height=1550)
        img.extent(width=750, height=1600, gravity="center")

        if re.search(r'(WP-XY[A-Z0-9]+)', jpeg_path):
            with add_bottom_background_and_shadow(img, '#f1f1f1') as final_img:
                final_img.save(filename=jpeg_path)
        elif re.search(r'(59FV[A-Za-z0-9]+)', jpeg_path):
            with add_bottom_background_and_shadow(img, '#f8f8f8',padding = 50) as final_img:
                final_img.save(filename=jpeg_path)
        else:
            img.save(filename=jpeg_path)


def compute_blake3_hash(data, data_type="content"):
    if data_type == "path":
        hasher = blake3.blake3()
        with open(data, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    elif data_type == "content":
        return blake3.blake3(data.encode()).hexdigest()
    elif data_type == "binary":
        return blake3.blake3(data).hexdigest()

def save_blake3_hashes(output_folder, page_hashes):
    if page_hashes:
        hash_file_path = os.path.join(output_folder, 'blake3_hashes.json')
        with open(hash_file_path, 'w') as hash_file:
            json.dump(page_hashes, hash_file)
    else:
        hash_file_path = os.path.join(output_folder, 'blake3_hashes.json')
        hashes = {}
        for filename in os.listdir(output_folder):
            if filename.endswith('.pdf'):
                file_path = os.path.join(output_folder, filename)
                file_hash = compute_blake3_hash(file_path)
                hashes[os.path.splitext(filename)[0]] = file_hash  # 去掉 .pdf 后缀
        with open(hash_file_path, 'w') as hash_file:
            json.dump(hashes, hash_file)

def load_blake3_hashes(output_folder):
    hash_file_path = os.path.join(output_folder, 'blake3_hashes.json')
    if os.path.exists(hash_file_path):
        with open(hash_file_path, 'r') as hash_file:
            return json.load(hash_file)
    return {}

def split_and_rename_pdfs(input_folder, output_folder):
    # 检查输出文件夹是否存在，如果不存在则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists('img'):
        os.makedirs('img')

    # 加载已有的 Blake3 哈希值
    existing_hashes = load_blake3_hashes(output_folder)
    page_hashes = existing_hashes.copy()

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            # 构造输入文件路径
            input_path = os.path.join(input_folder, filename)

            # 打开输入的PDF文件
            with open(input_path, 'rb') as file:
                reader = PdfReader(file)
                pages = reader.pages
                
                all_success = True

                # 遍历每一页
                for page_number, page in enumerate(pages):
                    try:
                        # 获取当前页内容
                        page_content = page.extract_text()
                        # 获取页面的原始字节数据
                        page_binary_data = page.get_contents().get_data() if page.get_contents() else b''
                        # 计算当前页的 Blake3 哈希值（优先使用字节数据）
                        page_binary_hash = compute_blake3_hash(page_binary_data, "binary") if page_binary_data else None
                        page_content_hash = compute_blake3_hash(page_content) if page_content else None

                        # 提取唯一的标识符
                        unique_identifier = extract_unique_identifier(page_content, patterns)
                        if unique_identifier:
                            # 构造输出文件名
                            output_filename = f'{unique_identifier}.pdf'
                            output_path = os.path.join(output_folder, output_filename)

                            # 检查是否已有相同哈希值的文件
                            if unique_identifier in existing_hashes:
                                stored_hash = existing_hashes[unique_identifier]
                                # 优先使用二进制哈希
                                if page_binary_hash and stored_hash == page_binary_hash:
                                    print(f'{unique_identifier} 已存在并匹配，跳过保存')

                                    # 如果 PDF 文件已经存在，则直接进行图片转换
                                    if os.path.exists(output_path):
                                        # 构造图像文件路径
                                        output_jpeg_filename = f"{unique_identifier}.jpg"
                                        output_jpeg_path = os.path.join('img', output_jpeg_filename)

                                        # 生成JPEG文件
                                        if not os.path.exists(output_jpeg_path):
                                            convert_pdf_to_jpeg(output_path, output_jpeg_path)
                                            print(f'{output_jpeg_filename} 已保存')
                                    else:
                                        # 如果 PDF 文件不存在（理论上不会发生），则重新保存并转换
                                        save_page_as_pdf(page, output_path)
                                        print(f'{output_filename} 已保存')

                                        # 转换PDF为JPEG
                                        convert_pdf_to_jpeg(output_path, output_jpeg_path)
                                        print(f'{output_jpeg_filename} 已保存')
                                elif not page_binary_hash and page_content_hash == stored_hash:
                                    print(f'{unique_identifier} 文本哈希匹配，跳过保存')
                                else:
                                    # 哈希不一致，重新处理
                                    save_page_as_pdf(page, output_path)
                                    print(f'{output_filename} 已保存')

                                    # 构造图像文件路径
                                    output_jpeg_filename = f"{unique_identifier}.jpg"
                                    output_jpeg_path = os.path.join('img', output_jpeg_filename)

                                    # 转换PDF为JPEG
                                    if not os.path.exists(output_jpeg_path):
                                        convert_pdf_to_jpeg(output_path, output_jpeg_path)
                                        print(f'{output_jpeg_filename} 已保存')
                                    
                                    # 保存当前页的哈希值
                                    page_hashes[unique_identifier] = page_binary_hash or page_content_hash
                            else:
                                # 哈希不存在，直接处理
                                save_page_as_pdf(page, output_path)
                                print(f'{output_filename} 已保存')

                                # 构造图像文件路径
                                output_jpeg_filename = f"{unique_identifier}.jpg"
                                output_jpeg_path = os.path.join('img', output_jpeg_filename)

                                # 转换PDF为JPEG
                                if not os.path.exists(output_jpeg_path):
                                    convert_pdf_to_jpeg(output_path, output_jpeg_path)
                                    print(f'{output_jpeg_filename} 已保存')
                                
                                # 保存当前页的哈希值
                                page_hashes[unique_identifier] = page_binary_hash or page_content_hash
                        else:
                            print(f'{filename}-page:{page_number}>未找到匹配项')
                            all_success = False
                    except Exception as e:
                        print(f"Error processing page {page_number} of {filename}: {e}")
                        all_success = False

                # 如果所有页面都成功处理，删除原始PDF文件
                if all_success:
                    file.close()
                    os.remove(input_path)
                    print(f'{input_path} 已删除')

    # 保存所有文件的 Blake3 哈希值
    save_blake3_hashes(output_folder, page_hashes)

# 输入文件夹路径和输出文件夹路径
input_folder = 'data'
output_folder = 'output'

# 调用函数进行分页、提取内容和重命名操作
split_and_rename_pdfs(input_folder, output_folder)
