import os
import re
from PyPDF2 import PdfReader, PdfWriter
from wand.image import Image
from wand.color import Color
from PIL import Image as PImage

def radio_size(w,h,x,model):
    if model == "w":
        return round(w / h * x)
    elif model == "h":
        return round(h / w * x)
    else:
        return round(w / h * x)

def get_img_size(fn, types=True):
    '''
        types = True cm
        types = False pixel
    '''
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
                for page_number in range(len(reader.pages)):
                    # 创建一个新的PDF写入器
                    writer = PdfWriter()

                    # 获取当前页
                    page = reader.pages[page_number]

                    regex_str = r'限公司(59JF(.?)*)'
                    page_content = page.extract_text()
                    match = re.search(regex_str, page_content)
                    match_str = match.group(1).strip()

                    # 构造输出文件名
                    # output_filename = f"{os.path.splitext(filename)[0]}_page{page_number + 1}.pdf"
                    output_filename = f'{match.group(1).strip()}.pdf'
                    output_path = os.path.join(output_folder, output_filename)
                    if not os.path.exists(output_path):
                        
                        # 将当前页添加到新的PDF文件中
                        writer.add_page(page)

                        # 保存新的PDF文件
                        # if not os.path.exists(output_path):
                        with open(output_path, 'wb') as output_file:
                                writer.write(output_file)  
                                            
                    
                    if match:
                        extracted_content = match_str

                        # 构造新的文件路径
                        new_filename = f"{extracted_content}.pdf"
                        new_path = os.path.join(output_folder, new_filename)

                        # 重命名文件
                        # Construct the output JPEG filename
                        output_jpeg_filename = f"{os.path.splitext(new_filename)[0]}.jpg"
                        output_jpeg_path = os.path.join('img', output_jpeg_filename)  

                        if not os.path.exists(new_path):
                            os.rename(output_path, new_path)
                        

                        if not os.path.exists(output_jpeg_path):
                            # Convert PDF file to JPEG
                            if not os.path.exists('img'):
                                os.makedirs('img')         

                            with Image(filename=new_path,resolution = 300) as img:
                                # img.background_color = Color("white")
                                img.alpha_channel = 'remove'
                                img.compression_quality = 100
                                img.resolution = 300
                                img.units = 'pixelsperinch'
                                img.format = 'jpg'

                                img.resize(radio_size(img.width,img.height,1600,"w"),1600)
                                img.crop(height=1500)
                                img.resize(radio_size(img.width,img.height,1600,"w"),1600)

                                # 扩展画布
                                img.extent(width=750,height=1600,gravity="center")
                                
                                # 图片裁切
                                # img.crop(height=1600,top=60)

                                # Save the JPEG image
                                img.save(filename=output_jpeg_path)

                            print(match_str)
                            


# 输入文件夹路径和输出文件夹路径
input_folder = 'data'
output_folder = 'output'

# 调用函数进行分页、提取内容和重命名操作
split_and_rename_pdfs(input_folder, output_folder)
