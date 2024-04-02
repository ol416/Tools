import os
import time
import re
import chardet
import win32com.client
import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
import openpyxl
import xlsxwriter
import requests
import urllib.parse as urlparse
import tqdm
from bk_xlsx import bk_concat

url='C:/Users/Administrator/Desktop/'
excel_temp = 'E:\Temp'
SrcPath = "./"
Path = './'
bb = ['订单报表','宝贝报表']
ml_xlsx = "C:/Users/Administrator/Desktop/excel/门帘标品表格.xlsm"
blt_xlsx = "C:/Users/Administrator/Desktop/excel/玻璃贴标品表格.xlsm"
compose_data_path = 'C:/Users/Administrator/Desktop/excel/compose_data.xlsx'
# lists=os.listdir(url)
# # print(lists)
# lists.sort(key=lambda fn: os.path.getctime(url+'\\'+fn))
# filepath=os.path.join(url,lists[-1])
# # print(filepath)

def get_code(code):
    url = "http://47.114.168.112:23333/TestServer"
    headers = {
        'Content-Type': "text/plain",
        'User-Agent': "PostmanRuntime/7.15.0",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "d5639969-8fbd-4531-9ad5-9a1bbe99089a,0c1fee63-a3e2-4a81-89ea-8b8861a0aa61",
        'Host': "192.168.1.108:8080",
        'accept-encoding': "gzip, deflate",
        'content-length': "12",
        'Connection': "keep-alive",
        'cache-control': "no-cache",
        'Authorization': "Basic dGVzdDp0ZXN0"
        }
    payload = 'get_code={}'.format(code)
    print(code)
    try:
        response = requests.request("POST", url, data=urlparse.quote(payload), headers=headers)
        response_text = urlparse.unquote(response.text)
        print(response_text)
        if response_text == 'authenticated!':
            passwd_code = input('请输入正确的密码:')
            response_text = passwd_code        
        return response_text
    except Exception as e:
            print(e)

def pwd_xlsx(old_filename,new_filename,pwd_str='',pw_str=''):
    print(pw_str)
    xcl = win32com.client.DispatchEx("Excel.Application")
    # pw_str为打开密码, 若无 访问密码, 则设为 ''
    wb = xcl.Workbooks.Open(old_filename, False, False, None, pw_str)
    xcl.DisplayAlerts = False

    # 保存时可设置访问密码.
    wb.SaveAs(new_filename, None, pwd_str, '')

    xcl.Quit()
    return pd.read_excel(new_filename,dtype=str)

def timestamp_to_str(timestamp, format='%Y-%m-%d %H') -> str:
    time_tuple = time.localtime(timestamp)  # 把时间戳转换成时间元祖
    result = time.strftime(format, time_tuple)  # 把时间元祖转换成格式化好的时间
    return result

def is_today_motified(filename) -> bool:
    modified_time = timestamp_to_str(os.path.getmtime(filename))
    now_date = timestamp_to_str(time.time())
    if now_date == modified_time:
        return True
    else:
        return False

def get_file_list(file_path,num=2, del_old_file = True):
    '''
    ::list
    f_xlsx,f_csv
    订单报表，宝贝报表
    '''
    if num == 0:
        bk_concat().just_open(ml_xlsx)
        print('等待两秒')
        time.sleep(2)
        bk_concat().just_open(blt_xlsx)
        print('打开完成！')
        os.system('pause')
        os._exit(0)
    dir_list = os.listdir(file_path)
    f_xlsx = []
    f_csv = []
    if not dir_list:
        return
    else:
        for f in dir_list:
            (shotname, extension) = os.path.splitext(f)
            file_name = os.path.join(file_path,f)
            is_today = is_today_motified(file_name)
            if ".xlsx" in extension:
                if del_old_file and not is_today:
                    os.remove(file_name)
                else:
                    f_xlsx.append(file_name)
            elif ".csv" in extension:
                if del_old_file and not is_today:
                    os.remove(file_name)
                else:
                    f_csv.append(file_name)
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        f_xlsx_list = sorted(f_xlsx,key=lambda x: os.path.getctime(os.path.join(file_path, x)))
        f_csv_list = sorted(f_csv,key=lambda x: os.path.getctime(os.path.join(file_path, x)))
        # dir_list.reverse()
        # print(dir_list)
        return (f_xlsx_list[-num:],f_csv_list[-num:])

def input_num(prompt = 2, retries=4, complaint='Yes or no, please!'):
    while True:
        ok = input(complaint)
        if ok.isnumeric():
            return int(ok)
        elif ok == '':
            return prompt
        else:
            print("请输入正确的数字")

def concat_to_excel(data,sheet_names):
    # data = data.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
    data = data.applymap(
               lambda x: ILLEGAL_CHARACTERS_RE.sub('?', x)
               if isinstance(x, str) else x)
    wb = openpyxl.load_workbook(compose_data_path)
    ws = wb[sheet_names]
    wb.remove(ws)
    #如果有多个模块可以读写excel文件，这里要指定engine，否则可能会报错
    writer = pd.ExcelWriter(compose_data_path,engine='openpyxl')
    #没有下面这个语句的话excel表将完全被覆盖
    writer.book = wb
    df = data
    #如果有相同名字的工作表，新添加的将命名为Sheet21，如果Sheet21也有了就命名为Sheet22，不会覆盖原来的工作表
    df.to_excel(writer, engine='xlsxwriter',sheet_name = sheet_names,index = None)
    writer.save()
    writer.close()

def concat_list(data_list,dtype=0):
    dfss = []
    for data in data_list:
        if dtype == 0:
            (shotname, extension) = os.path.splitext(data)
            dfss.append(pwd_xlsx(data,os.path.join(excel_temp,'tmp.xlsx'),pwd_str='',pw_str=get_code(shotname[-4:])))
        else:
            dfss.append(pd.read_csv(data,dtype=str,encoding='gbk'))
    return pd.concat(dfss)
if __name__ == "__main__":
    dfs = []
    inum = input_num(complaint='请输入导出表格的数量:\n')
    f_xlsx,f_csv = get_file_list(url,inum)
    df_xlsx = concat_list(f_xlsx)
    df_csv = concat_list(f_csv,dtype=1)
    concat_to_excel(df_xlsx,bb[0])
    concat_to_excel(df_csv,bb[1])
    bk_concat.just_open(compose_data_path)
    get_file_list(url,num=0)
    # print('{}\n{}'.format(f_xlsx,f_csv))
    # print(get_datafram(url+'ExportOrderList8049942018.xlsx','i55H1Aah'))
    os.system("pause")
