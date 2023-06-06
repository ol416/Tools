#先根据文件名创建对应文件夹
#如果存在则不跳过
#将对应文件放入同名文件夹内
#检查是否有826.jpg，如果有则删除再命名成826

import os
import shutil

def getallfiles(path) -> list:
    if not os.path.exists(path):
        return -1
    path = os.path.abspath(path)
    allfile = []
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            allfile.append(os.path.join(dirpath, dir))
        for name in filenames:
            allfile.append(os.path.join(dirpath, name))
    return allfile

# 创建文件同名的文件夹
def create_filename_folder(filename_list):
    for f in filename_list:
        # 将文件拆分成文件名和文件后缀
        filename = os.path.splitext(f)[0]
        if not os.path.exists(filename):
            os.mkdir(filename)
        shutil.move(f,filename)

path = './img'

if __name__ == '__main__':
    file_path = getallfiles(path)
    path_list = filter(lambda x: '.jpg' in x, file_path)
    create_filename_folder(path_list)
    print(path_list)

