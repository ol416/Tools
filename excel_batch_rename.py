import openpyxl
import os
import shutil

def copy_and_rename_images_from_excel(excel_file, image_folder, destination_folder):
    # 打开Excel文件
    workbook = openpyxl.load_workbook(excel_file,read_only=True)
    sheet = workbook.active

    # 遍历每一行（从第二行开始，因为第一行是标题）
    for row in sheet.iter_rows(min_row=2, values_only=True):
        item_number = row[0]  # 货号
        style_number = row[1]  # 款号

        # # 在图片文件夹中搜索以.jpg结尾的文件
        # for filename in os.listdir(image_folder):
        #     if filename.endswith('.jpg'):
        #         # 检查文件名是否包含款号
        #         if style_number in filename:
        #             # 构建新的文件名
        #             new_filename = f"{item_number}.jpg"

        #             # 构建源文件路径和目标文件路径
        #             source_path = os.path.join(image_folder, filename)
        #             destination_path = os.path.join(destination_folder, new_filename)

        # 复制文件并重命名
        if not os.path.isdir(item_number):
            dirname = os.path.dirname(style_number)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            shutil.copy(item_number, style_number)
            print(style_number)
        else:
            shutil.copytree(item_number, style_number)
            print(style_number)
        # print(f"已复制并重命名文件 {filename} 到 {destination_path}")

    print("完成复制和重命名。")

# 指定Excel文件路径、图片文件夹路径和目标文件夹路径
excel_file = "./sheet.xlsx"
image_folder = "./input"
destination_folder = "./output"

# 调用函数执行复制和重命名操作
copy_and_rename_images_from_excel(excel_file, image_folder, destination_folder)
