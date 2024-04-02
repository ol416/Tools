# coding=utf-8
import os
import re
import xlrd
import shutil
import time

excel_path = './'
main_folder = "E:/图片库/"
#input_folder = "//共享盘/f/源图/门帘源图/标品图库"
input_folder = "Y:/门帘源图/标品图库"
input_folder_file_dict = {}
reg1 = re.compile("(^[a-zA-Z]+[-]?[0-9]+)")
reg3 = re.compile("([整|分]+)([0-9]+)([x|X]+)([0-9]+)")


def find_xlsx(xlsx):
    files = []
    for (root, dirs, filename) in os.walk(xlsx):
        for f in filename:
            (shotname, extension) = os.path.splitext(f)
            new_file = shotname + extension
            copy_file = os.path.join(xlsx, new_file)
            if not ("~$" in shotname):
                if "xlsx" in extension:
                    print(copy_file + os.path.dirname(__file__))
                    # return copy_file
                    files.append(copy_file)
            else:
                continue
    return files


def XLSX_read(fileName):
    if fileName == False:
        print("未能正确读取xlsx文件")
        os._exit(0)
    bk = xlrd.open_workbook(fileName)
    table_name = bk.sheet_names()
    table = bk.sheet_by_name(table_name[0])
    ncolsP = table.col_values(15)
    ncolsZ = table.col_values(18)
    return [ncolsZ, ncolsP]


def deal_regular(str_name):
    str_name_dict = {}
    # for str in str_name:
    for i in range(len(str_name)):
        str1 = reg1.findall(str_name[i])
        if len(str1) == 0:
            break
        else:
            str1 = str1[0]
        str3 = reg3.findall(str_name[i])[0]
        new_str = str1 + str3[0] + str3[1] + str3[2].upper() + str3[3]
        str_name_dict.update({new_str: str_name[i]})
    return str_name_dict


def read_file(folder):
    str_group = []
    for root, dirs, file in os.walk(folder,topdown=True):
        for f in file:
            (shotname, extension) = os.path.splitext(f)
            if extension == ".jpg":                
                str_group.append(f)
    return deal_regular(str_group)


def cut_file_in_rename(folders):
    already_file = 0
    change_count = 0
    folder_dict = read_file(input_folder)
    for f in folders[1:]:
        format_file = f[0]
        new_name = f[1]
        real_name = folder_dict[format_file]
        new_name_src = new_name + ".jpg"
        src_file = os.path.join(input_folder, real_name)
        main_folder_file = os.path.join(main_folder, real_name)
        if os.path.exists(src_file):
            if os.path.exists(main_folder + new_name_src):
                print("%s文件已存在" % (new_name_src))
                already_file+=1
                continue
            change_count+=1        
            print("------已修改文件%s"%(format_file))
            shutil.copy(src_file,main_folder)
            os.rename(main_folder_file,main_folder+new_name_src)
        else:
            print("跳过%s,%s"%(format_file,new_name))
            continue
    print("在Excel中共读取了%s个文件，实际复制了%d次"%(len(folders)-1,change_count))


if __name__ == "__main__":
    start = time.process_time()
    data_set = []
    try:
        for xlsx_f in find_xlsx(excel_path):
            P, Z = XLSX_read(xlsx_f)
        for i in range(len(P)):
            data_set.append([P[i], Z[i]])
        # for d in data_set:
        #     folders.add(d)
        #     print(folders)
        cut_file_in_rename(data_set)
    except Exception as identifier:
        print("错误")
        print(identifier)
    end = time.process_time()
    running_time = end - start
    print("运行时间是:%6.3f" % running_time)
    os.system("pause")
