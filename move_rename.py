import os
import shutil
import zipfile

def getallfiles(path) -> list:
    if not os.path.exists(path):
        return []
    path = os.path.abspath(path)
    allfile = []
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            allfile.append(os.path.join(dirpath, dir))
        for name in filenames:
            allfile.append(os.path.join(dirpath, name))
    return allfile

def create_filename_folder(filename_list):
    for f in filename_list:
        filename, ext = os.path.splitext(f)
        if ext.lower() == '.jpg':
            folder_name = filename
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)
            new_path = os.path.join(folder_name, '826.jpg')
            shutil.move(f, new_path)

def rename_files_in_folders(path, original_name, new_name):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == original_name:
                original_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)
                os.rename(original_path, new_path)

def compress_to_zip(path, output_filename):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=path)
                zipf.write(file_path, arcname=arcname)

def clean_up_folder(path):
    shutil.rmtree(path)
    os.mkdir(path)

def main(path):
    file_path = getallfiles(path)
    path_list = list(filter(lambda x: x.lower().endswith('.jpg'), file_path))
    create_filename_folder(path_list)
    
    # 第一次压缩
    compress_to_zip(path, 'all_folders.zip')
    
    # # 重命名 826.jpg 为 826-共用款图.jpg
    # rename_files_in_folders(path, '826.jpg', '826-共用款图.jpg')
    
    # # 第二次压缩
    # compress_to_zip(path, 'all_folders_renamed.zip')
    
    # 清理文件夹
    clean_up_folder(path)

    print("初始文件列表：", path_list)
    print("所有操作已完成并生成两个压缩文件：all_folders.zip 和 all_folders_renamed.zip")

if __name__ == '__main__':
    main('./img')
