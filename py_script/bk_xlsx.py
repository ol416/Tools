import os
import logging
import shutil
import pandas as pd
import openpyxl
import win32com.client
import time

class bk_concat():
    def __init__(self):
        pass
    @classmethod
    def just_open(self, filename):
        xlApp = win32com.client.DispatchEx("Excel.Application")
        xlApp.Visible = False
        xlBook = xlApp.Workbooks.Open(filename)
        xlBook.RefreshAll()
        print("0")
        xlApp.CalculateUntilAsyncQueriesDone()
        # time.sleep(5)
        print("1")
        xlBook.Save()
        print("2")
        print("3")
        xlBook.Close()
        print("4")
        
    @classmethod
    def concat_to_excel(self,data):
        wb = openpyxl.load_workbook('备注.xlsx')
        df2 = pd.read_excel('备注.xlsx',dtype=str,sheet_name='Sheet4')
        ws = wb["Sheet2"]
        ws2 = wb["Sheet4"]
        wb.remove(ws)
        wb.remove(ws2)
        #如果有多个模块可以读写excel文件，这里要指定engine，否则可能会报错
        writer = pd.ExcelWriter('备注.xlsx',engine='openpyxl')
        #没有下面这个语句的话excel表将完全被覆盖
        writer.book = wb

        df = data
        #如果有相同名字的工作表，新添加的将命名为Sheet21，如果Sheet21也有了就命名为Sheet22，不会覆盖原来的工作表
        df.to_excel(writer,sheet_name = 'Sheet2',index = None)
        df2.to_excel(writer,sheet_name = 'Sheet4',index = None)
        writer.save()
        writer.close()
    @classmethod
    def exists_file(self,filename,file_link,src_path):
        if not os.path.exists(filename):
            shutil.copy2(file_link,src_path)

if __name__ == '__main__':
    mark_xlsx = "C:/Users/Administrator/Desktop/excel/备注.xlsx"
    SrcPath = "./"
    Path = "./"
    dfs = []
    new_file_name = 0
    bk_concat.just_open(mark_xlsx)    
    for (root,dirs,filename) in os.walk(SrcPath):
        root_depth = len(root.split(os.path.sep))
        bk_concat.exists_file(filename = '备注.xlsx',file_link=mark_xlsx,src_path = SrcPath)
        for f in filename:
            # new_root = os.path.join(Path, f)
            src_file = os.path.join(root, f)
            # print(root_depth)
            if (root_depth == 1):
                (shotname, extension) = os.path.splitext(f)
                new_file = shotname +"-"+str(new_file_name) + extension
                copy_file = os.path.join(Path,new_file)
                if not ("~$" in shotname) and "副本" in shotname:
                    if ( "xlsx" in extension):
                        new_file_name+=1
                        if not (os.path.exists(copy_file)):
                            dfs.append(pd.read_excel(src_file,dtype=str))
                            print(src_file)
                            # shutil.copy2(src_file, copy_file)
    df = pd.concat(dfs)
    bk_concat.concat_to_excel(df)

    print(f'总共找到 {new_file_name} 个相关文件')
    time.sleep(2)
    # df.to_excel('result.xlsx', index=False)
