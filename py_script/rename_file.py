import os
import shutil
import time

main_folder = "E:\\加框"
del_folder = "C:\\Users\\Administrator\\Desktop\\原图"
person_flag = "F5"

def find_file():
    # file_list = []
    error_flags = set()
    count_num = 0
    for root, dirs, filename in os.walk(main_folder):
        filename = set(filename)
        for f in filename:
            split_file_name = f.split("$")
            split_final_name = split_file_name[0]
            real_path = os.path.join(root, f)
            # print(f)
            new_path = os.path.join(root, split_final_name)+os.path.splitext(f)[1] 
            if ("$" in f):
                rename_file(real_path,new_path)
                count_num +=1
            if ".jpg" in os.path.splitext(real_path)[1]:
                if (person_flag not in split_final_name):
                    error_flags.add(split_final_name)
            # filename.remove(f)
    print("总计完成：%d，错误数量：%d"%(count_num, len(error_flags)))

def rename_file(src_name,dst_name):
    try:
        new_name = os.rename(src_name,dst_name)
        return new_name
    except Exception as identifier:
        # os.remove(src_name)
        shutil.move(src_name, del_folder)
        print("已删除%s"%(os.path.splitext(src_name)[0]))
    

if __name__ == "__main__":
    start = time.process_time()
    find_file()    
    end = time.process_time()
    running_time = end-start
    print("运行时间是:%6.3f"%running_time)
    os.system("pause")

