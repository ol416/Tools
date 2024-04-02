import os
import re
import shutil
import hashlib
from win32com.client import DispatchEx, GetActiveObject, GetObject

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

color = {
    'Black': (255, 255, 255),
    'White': (0, 0, 0)
}

TEXT_TYPE_LOCATION = {
    '整片式': (43, 2),
    '分片式': (43, 2),
    '空调罩': (43, 2)
}

#!/usr/bin/env python
# -*- coding: utf-8 -*-
TMP_csv = 'E:/Temp/tmp.csv'

def get_file_md5(file_name):
    """
    计算文件的md5
    :param file_name:
    :return:
    """
    m = hashlib.md5()  # 创建md5对象
    with open(file_name, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  # 更新md5对象
    return m.hexdigest()  # 返回md5对象

def get_str_md5(content):
    """
    计算字符串md5
    :param content:
    :return:
    """
    m = hashlib.md5(content)  # 创建md5对象
    return m.hexdigest()

def get_img_size(fn, types=True):
    '''
        types = True cm
        types = False pixel
    '''
    img = Image.open(fn)
    dpi = img.info['dpi'][0]
    if types:
        width, height = map(lambda x: x/dpi*2.54, img.size)
    else:
        width, height = map(lambda x: x, img.size)
    return round(width), round(height), dpi

# image: 图片  text：要添加的文本 font：字体
def add_text_to_image(img_source_link, text, location, dpi=100, fonts='font/simsun.ttc', font_size=25, color=(255, 255, 255)):
    name, ext = os.path.splitext(img_source_link)
    format_filename = f"{name}{ext}"

    width, height = location
    # 打开图片
    img = Image.open(img_source_link)
    # 添加文字
    draw = ImageDraw.Draw(img)
    # 参数：位置、文本、填充、字体
    font = ImageFont.truetype(font=fonts, size=font_size)
    textWidth, textHeight = draw.textsize(text, font)
    locations = add_text_type(img_source_link, width,
                              height, textWidth, textHeight)
    if isinstance(locations, list):
        draw.text(xy=locations[0], text=text, fill=color, font=font)
        draw.text(xy=locations[1], text=text, fill=color, font=font)
    else:
        draw.text(xy=locations, text=text, fill=color, font=font)
    # 保存
    img.save(format_filename, dpi=(dpi, dpi), quality=100,subsampling=0, icc_profile=img.info.get(
        'icc_profile'), optimize=True, exif=img.info.get('exif'))
    check_md5(TMP_csv,get_file_md5(f),writer=True)
    print(text)

def regex_str(reg, strs):
    ret = re.findall(reg, strs)
    if len(ret) > 0:
        ret = ret[0]
    else:
        ret = strs
    return ret

def create_today_folder(url, identifier_text):
    now = datetime.now()
    date_format_str = '{}-{} {}'.format(now.month, now.day, identifier_text)
    folder_path = os.path.join(url, date_format_str)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def getallfiles(path) -> list:
    allfile = []
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            allfile.append(os.path.join(dirpath, dir))
        for name in filenames:
            allfile.append(os.path.join(dirpath, name))
    return allfile

def add_text_type(filepaths, width, height, textwidth=0, textheight=0):
    shortname, extension = os.path.splitext(os.path.basename(filepaths))
    img_type = ()
    if '整片式' in filepaths:
        # img_type = TEXT_TYPE_LOCATION['整片式']
        img_type = (width-textwidth-82, 4)
    elif '分片式' in filepaths:
        img_type = [(width-textwidth-82, 4), (80, height/2+4)]
    elif '空调罩' in filepaths:
        img_type = TEXT_TYPE_LOCATION['空调罩']
    else:
        print(f'未知格式|{shortname}')
        return False
    return img_type

def check_md5(csv_file,md5_code,writer = False):
    is_check:bool
    df = pd.read_csv(csv_file)
    df_select = df[df['f'] == md5_code]
    if len(df_select):
        is_check = True
    else:
        is_check = False
        data = [md5_code]
        df = pd.DataFrame(data=data,index=[0])
        if writer:
            df.to_csv(csv_file,mode='a')
    return is_check

def run_PS(imglist):
    if len(imglist):
        try:
            app = GetActiveObject("Photoshop.Application")
        except:
            app = DispatchEx("Photoshop.Application")

    for index,imgpath in enumerate(imglist):
        # imgname = os.path.splitext(os.path.basename(imgpath))[0]
        imgpath = os.path.abspath(imgpath)
        print(f'{index}->{imgpath}')
        docRef = app.Open(imgpath)
        app.DoAction('批量拼合', '焕动作')
        # img = Image.open(imgpath)
        # img.save("new"+imgpath, dpi=(dpi, dpi), quality=100,subsampling=0)

if __name__ == '__main__':
    reg_str = "\d{4}([a-zA-Z]+\d?)\d{3}"
    url = './'
    font = 'font/simsun.ttc'
    new_path = []
    tmp_list = []
    location = (43, 2)
    path_list = filter(lambda x: '.jpg' in x, getallfiles(url))
    path_list = list(path_list)
    if not len(path_list):
        print('没有相关格式的图片')
        os.system('pause')
        raise ValueError('没有相关格式的图片')
    # else:
    #     dst_path = create_today_folder(url,regex_str(reg_str,path_list[0]))
    for f in path_list:
        dst_path = os.path.join("./",os.path.basename(f))
        shutil.move(f,dst_path)
        if not "空调罩" in os.path.basename(f):
            new_path.append(dst_path)
        else:
            tmp_list.append(dst_path)
    run_PS(new_path)
    path_list = new_path
    path_list = path_list+tmp_list

    for f in path_list:
        shortname, extension = os.path.splitext(os.path.basename(f))
        if '.jpg' in extension:
            if check_md5(TMP_csv,get_file_md5(f)):
                print(f'{shortname}已存在')
                continue                   
            filepath = f
            width, height, dpi = get_img_size(filepath, types=False)
            location = add_text_type(filepath, width, height)
            if not location:
                continue
            add_text_to_image(img_source_link=filepath, text=shortname, location=[
                              width, height], fonts='simhei.ttf', dpi=dpi,font_size=28)
            # shutil.move(filepath,dst_path)
    for f in path_list:
        command_str = 'convert -verbose "{}" -strip -colorspace CMYK "{}"'
        os.system(command_str.format(f,f))
    os.system("pause")
    # img_data = Image.open('bcca.jpg')
    # add_text_to_image(img_data,'号啊',font=font)
    # img = cv2.imread("map.png")
    # data = "DS041: 88;DS048: 800;DS049: 64;DS098: 0.00;DS123: 0.00"
    # layer1_show(img, data)
    # add_text_to_image(img_data,'号啊',font=font)
    # img = cv2.imread("map.png")
    # data = "DS041: 88;DS048: 800;DS049: 64;DS098: 0.00;DS123: 0.00"
    # layer1_show(img, data)
