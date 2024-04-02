import os
import re
import xlrd
import shutil
import time

ZPS = "整片式"
FPS = "分片式"
IMG_PATH = "E:\\图片库"
IMG_ROOT_PATH = "Other"


def find_file(serial, name, types, Img_num, width, height, store):
    path = "E:/图片库"
    global person_flag
    global file_linked_name
    global rename_file_num
    files = file_linked_name
    types = types[0:3]
    for f in files:
        src_path = os.path.join(path, f)
        f = f.strip()
        if not (person_flag in f):
            if (
                f.upper().endswith(".TIF")
                or f.upper().endswith(".JPG")
                or f.endswith(".png")
            ):
                print((name in f and types in f ))
                if (serial in f and name in f and types in f and Img_num in f) and store in f:
                    if width + "X" + height in f.upper():
                        count = 0
                        # print("Found it! " + f)
                        rename_file_num += 1
                        print(
                            "%u Found it! %s-%s %s"
                            % (rename_file_num, name, types, Img_num)
                        )
                        # print(os.path.splitext(src_path)[0])
                        new_file_name = (
                            #serial
                            #+ "-"
                            #+
                            os.path.splitext(f)[0]
                            + "-"
                            + person_flag
                            + "$"
                            + name
                            + "-"
                            + serial
                            + "-"
                            + width
                            + "X"
                            + height
                            + "-"
                            + Img_num
                            + types
                            + os.path.splitext(f)[1]
                        )
                        new_file_path = os.path.join(path, new_file_name)
                        if count < 1:
                            count += 1
                            os.rename(src_path, new_file_path)
                        find_types_file(IMG_PATH, new_file_name)
                        file_linked_name.remove(f)
                        break
                    else:
                        print(width + "X" + height)
                        print("尺寸匹配错误")
                        continue
                else:
                    #print("非匹配")
                    continue
            else:
                # print("No Found! " + f)
                continue
        else:
            continue


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
    return False


def XLSX_read(fileName):
    if fileName == False:
        print("未能正确读取xlsx文件")
        os._exit(0)
    #     fileName = "C:/Users/Administrator/Desktop/files/小南豆门帘订单模板新新.xlsx"
    bk = xlrd.open_workbook(fileName)
    table_name = bk.sheet_names()
    table = bk.sheet_by_name(table_name[0])
    ncolsG = table.col_values(6)
    ncolsH = table.col_values(7)
    ncolsM = table.col_values(12)
    store = table.col_values(13)
    ncolsQ = table.col_values(15)
    width = table.col_values(23)
    height = table.col_values(25)
    data = []
    for n in range(table.nrows):
        data.append(
            [ncolsG[n], ncolsH[n], ncolsM[n], ncolsQ[n], width[n], height[n], store[n]]
        )
    return data


def del_all_file(path):
    for i in os.listdir(path):
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            continue

def path_exist_mkdir(path):
    if not os.path.exists(path):#如果路径不存在
        os.makedirs(path)

def find_types_file(path, fileName):
    global ZPS
    global FPS
    global IMG_ROOT_PATH
    global ZPS_num
    global FPS_num
    file_path = os.path.join(path, fileName)
    ZPS_new_path = os.path.join(ZPS, fileName)
    FPS_new_path = os.path.join(FPS, fileName)
    another_path = os.path.join(IMG_ROOT_PATH, fileName)
    if "整片" in fileName:
        ZPS_num += 1
        shutil.copy2(file_path, ZPS_new_path)
    elif "分片" in fileName:
        FPS_num += 1
        shutil.copy2(file_path, FPS_new_path)
    else:
        shutil.copy2(file_path, another_path)
    os.remove(file_path)


if __name__ == "__main__":
    start = time.process_time()
    ZPS_num = 0
    FPS_num = 0
    #     find_file("", "", "")
    file_linked_name = os.listdir(IMG_PATH)
    # print(data)
    person_flag = "F5"
    rename_file_num = 0
    path_exist_mkdir(ZPS)
    path_exist_mkdir(FPS)
    path_exist_mkdir(IMG_ROOT_PATH)
    if not os.listdir(IMG_PATH):
        print("删除所有文件")
        del_all_file(ZPS)
        del_all_file(FPS)
    try:
        for xlsx_f in find_xlsx("./"):
            data = XLSX_read(xlsx_f)
        for d in data[1:]:
            serial = d[0]
            name = d[1]
            types = d[2]
            Img_num = d[3]
            width = d[4]
            height = d[5]
            store = d[6]
            print(d)
            find_file(
                str(serial).strip(),
                str(name).strip(),
                str(types).strip(),
                str(Img_num).strip(),
                str(int(round(int(width)))).strip(),
                str(int(round(int(height)))).strip(),
                str(store).strip(),
            )
    except Exception as identifier:
        print(identifier)
        # print(name+types+Img_num)
    print("整片式：%u\n分片式：%u\n共有：%u个文件\n" % (ZPS_num, FPS_num, (ZPS_num + FPS_num)))
    end = time.process_time()
    running_time = end - start
    print("运行时间是:%6.3f" % running_time)
    os.system("pause")
