from PIL import Image
import os

def get_outfile(infile, outfile):
    if outfile:
        return outfile
    dir, suffix = os.path.splitext(infile)
    outfile = '{}-out{}'.format(dir, suffix)
    return outfile

def resize_image(infile, outfile='', y_s=230,crop=False):
    """修改图片尺寸
    :param infile: 图片源文件
    :param outfile: 重设尺寸文件保存地址
    :param x_s: 设置的宽度
    :return:
    """
    im = Image.open(infile)
    x, y = im.size
    if crop:
        # first crop to a square
        if x > y:
            out = im.crop((int(x/2-y/2), 0, int(x/2+y/2),y))
        else:
            out = im.crop((0,int(y/2-x/2),x,int(y/2+x/2)))
        out = out.resize((230,230), Image.ANTIALIAS)
    else:
        # y_s = int(y * x_s / x)
        x_s = int(x * y_s / y)
        out = im.resize((x_s, y_s), Image.ANTIALIAS)
    # outfile = get_outfile(infile, outfile)
    out.save(outfile)

def get_size(file):
    # 获取文件大小:KB
    size = os.path.getsize(file)
    return size / 1024

def compress_image(infile, outfile='', mb=100, step=10, quality=80):
    """不改变图片尺寸压缩到指定大小
    :param infile: 压缩源文件
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    o_size = get_size(infile)
    if o_size <= mb:
        return infile
    outfile = get_outfile(infile, outfile)
    while o_size > mb:
        im = Image.open(infile)
        im.save(outfile, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        o_size = get_size(outfile)
    return outfile, get_size(outfile)

def folder(f_input, f_output):
    for root,dirs,files in os.walk(f_input): 
        for file in files: 
            if file[0] == ".":
                continue
            if file[0] == "1":
                crop=True
            else:
                crop=False
            i_input = f_input+file
            i_output = f_output+file
            resize_image(i_input,i_output,crop=crop)
            print(i_output, get_size(i_output))
            # compress_image(i_output)

folder("_assets/images/2021-11-09/lecture2/", "_assets/images/2021-11-09/lecture2-small/")
# folder("_assets/images/music-theory-1/normal/","_assets/images/music-theory-1/small/")