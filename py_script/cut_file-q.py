#coding=utf-8
import os
import re
import xlrd
import shutil
import time

main_folder = "./"

def find_xlsx(xlsx):
    files = []
    for (root,dirs,filename) in os.walk(xlsx):
        for f in filename:
            (shotname, extension) = os.path.splitext(f)
            new_file = shotname + extension
            copy_file = os.path.join(xlsx,new_file)
            if not ("~$" in shotname):
                if ( "xlsx" in extension):
                    print(copy_file+os.path.dirname(__file__))
                    # return copy_file
                    files.append(copy_file)
            else:
                continue
    return files
    return False

def XLSX_read(fileName):
    if fileName == False:
        print("未能正确读取xlsx文件")
        os._exit(0)
    bk = xlrd.open_workbook(fileName)
    table_name = bk.sheet_names()
    table = bk.sheet_by_name(table_name[0])
    ncolsH = table.col_values(7)
    return ncolsH

def cut_file_in_folder(folders):
    dir_linked = []
    file_linked = []
    for root,dirs,files in os.walk(main_folder,topdown = True):
        for folder in folders:
            folder = str(folder).strip()
            for d in dirs:
                if folder in d:
                    dst_folder = os.path.join(main_folder,d)
                    dir_linked.append(d)
                    for f in files:
                        if folder in f:
                            file_linked.append(f)
                            src_file = os.path.join(main_folder,f)
                            dst_file = os.path.join(dst_folder,f)
                            print(folder)
                            shutil.move(src_file, dst_folder)
    return True

def create_folder(folders, Img_num):
    for folder in folders:
        print(folder)
        d_num = Img_num[folder]
        new_folder_name = ("%s %s图"%(folder,str(d_num)))
        dirs_folder = os.path.join(main_folder,new_folder_name)
        if not (os.path.exists(dirs_folder)):
            os.mkdir(new_folder_name)
            print(new_folder_name)

if __name__ == "__main__":
    start = time.process_time()
    person_flag = "F5"
    folders = set()
    Img_num = {}
    try:
        for xlsx_f in find_xlsx(main_folder):    
            data = XLSX_read(xlsx_f)
        data_set = set(data)
        for d in data_set:
            d_num = data.count(d)
            print(d+str(d_num))
            if (d_num>= 2) and d != "":
                # print(d_num)
                folders.add(d)
                Img_num[d]=d_num
        create_folder(folders, Img_num)
                
        cut_file_in_folder(folders)
    except Exception as identifier:
        print(identifier)
    end = time.process_time()
    running_time = end-start
    print("运行时间是:%6.3f"%running_time)
    os.system("pause")

