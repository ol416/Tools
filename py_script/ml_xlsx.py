import os
import logging
import shutil
import pandas as pd
import openpyxl
import win32com.client
import time
from bk_xlsx import bk_concat

class ml_xlsx():
    def __init__(self):
        self.count = 0

    def _concat_to_excel(self,data):
        wb = openpyxl.load_workbook('门帘筛选表格.xlsx')
        ws = wb["Sheet2"]
        wb.remove(ws)
        #如果有多个模块可以读写excel文件，这里要指定engine，否则可能会报错
        writer = pd.ExcelWriter('门帘筛选表格.xlsx',engine='openpyxl')
        #没有下面这个语句的话excel表将完全被覆盖
        writer.book = wb
        df = data
        #如果有相同名字的工作表，新添加的将命名为Sheet21，如果Sheet21也有了就命名为Sheet22，不会覆盖原来的工作表
        if self.count == 0:
            df.to_excel(writer,sheet_name = 'Sheet2',index = None)
            self.count = 1
            writer.save()
            writer.close()            
            os.rename('门帘筛选表格.xlsx','门帘筛选表格2.xlsx')
        else:
            df.to_excel(writer,sheet_name = 'Sheet2',index = None)
            writer.save()
            writer.close()

if __name__ == '__main__':
    mark_xlsx = "C:/Users/Administrator/Desktop/excel/门帘筛选表格.xlsx"
    data_source = 'C:/Users/Administrator/Desktop/excel/门帘标品表格.xlsm'
    SrcPath = "./"
    Path = "./"
    ml_xlsx = ml_xlsx()
    bk_concat.exists_file(filename = '门帘筛选表格.xlsx',file_link=mark_xlsx,src_path = SrcPath)
    df = pd.read_excel(data_source,sheet_name=0,dtype = 'str')
    df.loc[df['图数量'].isna(),'图数量'] = 0
    df['图数量']=df['图数量'].astype(int)
    df = df.sort_values(by = ['订单号','地址','店铺'])
    df1 = df[df['整合'].isna() & df['整合2'].isin(['True'])]
    df2 = df[~df['整合'].isna() & df['整合2'].isin(['True'])]
    ml_xlsx._concat_to_excel(df1)
    bk_concat.exists_file(filename = '门帘筛选表格.xlsx',file_link=mark_xlsx,src_path = SrcPath)
    ml_xlsx._concat_to_excel(df2)
    print('已完成')
    time.sleep(1)
