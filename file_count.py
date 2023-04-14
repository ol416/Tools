import os

target_path='./'

if os.name == 'nt':
    import win32api, win32con

# 判断文件夹是否为隐藏文件夹（仅在Windows平台下使用）
def folder_is_hidden(p):
    if os.name == 'nt':
        attribute = win32api.GetFileAttributes(p)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    else:
        return p.startswith('.') # 在Linux和macOS平台下判断文件夹是否以"."开头

# 获取目标路径下的所有文件夹
all_content=[_ for _ in os.listdir(target_path) if os.path.isdir(_) and not folder_is_hidden(_) ]
all_content.sort()

# 获取指定路径下的所有文件和文件夹
def getallfiles(path) -> list:
    allfile = []
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            allfile.append(os.path.join(dirpath, dir))
        for name in filenames:
            allfile.append(os.path.join(dirpath, name))
    return allfile

count_num=1
for content in all_content:
    all_sub_content=os.listdir(target_path+content)
    if len(all_sub_content)!=1024:
        file_count = len(all_sub_content)
        if "Thumbs.db" in all_sub_content:
            file_count-=1
        print('No.{0}|Name：{1}|Total：{2}'.format(count_num,content,file_count))
        count_num=count_num+1

# 获取目标路径下的所有jpg文件的数量
file_count = 0
for file in getallfiles(target_path):
    shortname, extension = os.path.splitext(os.path.basename(file))
    if extension.lower() in ['.jpg']:
        file_count+=1

print('jpg文件数量：{0}'.format(file_count))
os.system("pause")
