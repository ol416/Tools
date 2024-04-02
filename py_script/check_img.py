import PIL.ExifTags
from PIL import Image
import sys,os

# 不检查图片大小
Image.MAX_IMAGE_PIXELS = None
addr = "./"
total_counter = 0
fail_counter = 0

def get_img_size(fn):
    img = Image.open(fn)
    dpi = img.info['dpi'][0]
    size = img.size
    width = size[0]/dpi*2.54
    height = size[1]/dpi*2.54
    return round(width),round(height)

if __name__ == "__main__":
    for root,dirs,filename in os.walk(addr,topdown=True):
        filelen = len(filename)
        for f in filename:            
            (shotname, extension) = os.path.splitext(f)
            if "tif" in extension or "jpg" in extension:
                total_counter+=1                              
                path = os.path.join(root,f)
                (width,height) = get_img_size(path)
                size_format = "(%sX%s)"%(str(width),str(height))
                if str(width-1) in (shotname) and str(height-1) in (shotname):
                    # print("%s - %s true"%(shotname,size_format))
                    continue
                else:
                    fail_counter+=1
                    print("%d   %s - %s false"%(fail_counter,shotname,size_format))
                    
    print("\n总共测试%d张图片，其中有%d张尺寸错误的图片\n"%(total_counter,fail_counter))
    os.system("pause")