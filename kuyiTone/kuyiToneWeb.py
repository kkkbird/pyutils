from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import info as session_info
from kuyiTone import parseMusic
import re
import struct
import base64
import qrcode


def validTone(tone):
    if re.match(r'^[A-G][#b]?$', tone):
        return None

    return '曲调格式不正确'


def put_music(beats):
    out = [o for b in beats for o in b]
    bs = struct.pack('H'*len(out), *out)
    b64 = base64.b64encode(bs)
    qr = qrcode.make(b64)

    put_table([
        ['raw_16bit', f'[{",".join([hex(o) for o in out])}]'],
        ['raw_8bit', f'[{",".join([hex(o) for o in bs])}]'],
        ['base64', b64],
        ['qr', put_image(qr.get_image())]
    ])

def main():
    put_markdown("""
    ## kuyi simple music generator

    ### 音符标识

    * 每个音符之间间隔一个空格
    * '-' 延长一拍
    * '_' 时值减半
    * '`' 升高1个八度
    * '.' 降低1个八度
    * ':' 延音， 延音符号要放在最后
    * '#' 升半音
    * 'b' 降半音
    """)

    info = input_group("乐曲信息", [
        input("输入曲调(C D E F G A B, 升调加#，降调加b)", name="tone",
              type=TEXT, value='C', validate=validTone, required=True),
        input("输入BPM(每分钟多少拍)", name="bpm", type=NUMBER, value=90,
              help_text="", required=True),
        textarea("简谱（具体内容见上方说明)", name="music", value='1 2 3', rows=5)
    ])    
    try:
        beats = parseMusic(info)
        put_music(beats)
    except Exception as e:
        put_error("输入解析错误"+e)


if __name__ == '__main__':
    start_server(main, debug=True, port=8080)
