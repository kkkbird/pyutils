import qrcode
from PIL import Image
import os
 
#生成二维码图片
def make_qr(data, save_path, logo=""):
    qr=qrcode.QRCode(
        version=4,  #生成二维码尺寸的大小 1-40  1:21*21（21+(n-1)*4）
        error_correction=qrcode.constants.ERROR_CORRECT_Q, #L:7% M:15% Q:25% H:30%
        box_size=20, #每个格子的像素大小
        border=2, #边框的格子宽度大小
    )
    qr.add_data(data)
    qr.make(fit=True)    
 
    img=qr.make_image()

    if len(logo) > 0 and os.path.exists(logo):
        img=img.convert("RGBA")
 
        #添加logo
        icon=Image.open(logo)
        #获取二维码图片的大小
        img_w,img_h=img.size

        factor=4
        size_w=int(img_w/factor)
        size_h=int(img_h/factor)

        #logo图片的大小不能超过二维码图片的1/4
        icon_w,icon_h=icon.size
        if icon_w>size_w:
            icon_w=size_w
        if icon_h>size_h:
            icon_h=size_h
        icon=icon.resize((icon_w,icon_h),Image.ANTIALIAS)
        #详见：http://pillow.readthedocs.org/handbook/tutorial.html

        #计算logo在二维码图中的位置
        w=int((img_w-icon_w)/2)
        h=int((img_h-icon_h)/2)
        icon=icon.convert("RGBA")
        img.paste(icon,(w,h),icon)
        #详见：http://pillow.readthedocs.org/reference/Image.html#PIL.Image.Image.paste
    
    #保存处理后图片
    img.save(save_path)
    
if __name__=='__main__':
    for i in range(1, 61):
        bikeNo = "021%05d" % i
        url = "https://apitest.lieqishare.cn/bike/scancode?id=0001%s" % bikeNo
        save_path = "./qr/%s.jpg" % bikeNo
        make_qr(url, save_path, "./p5_1.png")