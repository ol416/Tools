import re
import PIL.ExifTags
from PIL import Image
import sys,os

# 不检查图片大小
Image.MAX_IMAGE_PIXELS = None
addr = "./"
total_counter = 0
fail_counter = 0
reg1 = re.compile('\(([0-9]+)([×|x|X]+)([0-9]+)\)')
reg_str = re.compile("^((.+)?)(-)([a-zA-Z]+-[0-9]+)([分|整])+(\d+[×|x|X]\d+)")

def get_img_size(fn):
    img = Image.open(fn)
    dpi = img.info['dpi'][0]
    size = img.size
    width = size[0]/dpi*2.54
    height = size[1]/dpi*2.54
    return round(width),round(height)

def regex_str(reg, strs):
    ret = re.findall(reg, strs)
    if len(ret) > 0:
        ret = ret[0]
    else:
        ret = False
    return ret

def regex_dict_format(reg_str,list_str):
    true_dict = {}
    reg_result = [regex_str(reg_str,_.replace('.jpg','')) for _ in list_str]
    i = 0
    for _ in reg_result:
        if _:
            if '片式' in _:
                format_str = '{0[1]}{0[2]}{0[3]}{0[4]}({0[5]})'.format(_)
            else:
                format_str = '{0[1]}{0[2]}{0[3]}{0[4]}片式({0[5]})'.format(_)
            true_dict[list_str[i]] = format_str
        else:
            true_dict[list_str[i]] = _
        i+=1

    # for _ in list_str:
        # print(f'[{_}] {true_dict[_]}')
    return true_dict

if __name__ == "__main__":
    for root,dirs,filename in os.walk(addr,topdown=True):
        format_dict = regex_dict_format(reg_str,filename)
        filelen = len(filename)
        for f in filename:            
            (shotname, extension) = os.path.splitext(f)
            # if reg1.findall(shotname):
            #     break
            if "tif" in extension or "jpg" in extension:
                total_counter+=1                              
                path = os.path.join(root,f)
                tmp_str = format_dict.get(f)
                if tmp_str:
                    os.rename(f,f'{tmp_str}{extension}')
                    fail_counter +=1
                else:
                    print(f'failure:{f}')

                # (width,height) = get_img_size(path)
                # size_format = "(%sX%s)"%(str(width-1),str(height-1))
                # complexs_str = '{}{}{}'.format(shotname,size_format,extension)
                # os.rename(f,complexs_str)
                # fail_counter+=1
                # print(complexs_str)

                # if str(width-1) in (shotname) and str(height-1) in (shotname):
                #     # print("%s - %s true"%(shotname,size_format))
                #     continue
                # else:
                #     fail_counter+=1
                #     print("%d   %s - %s false"%(fail_counter,shotname,size_format))
                    
    # print("\n总共测试%d张图片，其中有%d张尺寸错误的图片\n"%(total_counter,fail_counter))
    print('有{0}张图片,修改{1}张图'.format(total_counter,fail_counter))
    os.system("pause")