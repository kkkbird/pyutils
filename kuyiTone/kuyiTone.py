from time import sleep
import winsound
import yaml
import codecs
import sys
import qrcode
import base64
import struct


def parseTone(tone: str):
    baseTone = 25  # C调的do的index
    tone = tone.strip()

    match tone[0]:
        case 'C':
            pass
        case 'D':
            baseTone += 2
        case 'E':
            baseTone += 4
        case 'F':
            baseTone += 5
        case 'G':
            baseTone += 7
        case 'A':
            baseTone += 9
        case 'B':
            baseTone += 11

    if len(tone) > 1:
        match tone[1]:
            case '#':
                baseTone += 1
            case 'b':
                baseTone -= 1

    return baseTone


def parseBeat(beat: str, baseTone: int, bpm: int):
    beat = beat.strip()
    desc = beat[1:]
    tone = baseTone

    b = 1.0

    for d in desc:
        match d:
            case '`':
                tone += 12
            case '.':
                tone -= 12
            case '_':
                b /= 2
            case '-':
                b += 1
            case '#':
                tone += 1
            case 'b':
                tone -= 1
            case ':':
                b += b / 2

    t = int(b * 1000 * 60 / bpm)
    p = 0

    match beat[0]:
        case '0':
            p = 0
        case '1':
            p = tone
        case '2':
            p = tone + 2
        case '3':
            p = tone + 4
        case '4':
            p = tone + 5
        case '5':
            p = tone + 7
        case '6':
            p = tone + 9
        case '7':
            p = tone + 11

    # http://www.360doc.com/content/22/0110/21/111224_1012721857.shtml
    tones = (
        0,
        65, 69, 73, 77, 82, 87, 92, 98, 103, 110, 116, 123,  # 0
        130, 138, 146, 155, 164, 174, 185, 196, 207, 220, 233, 246,  # 1
        261, 277, 293, 311, 326, 349, 370, 392, 415, 440, 466, 493,  # 2
        523, 554, 587, 622, 659, 698, 740, 784, 830, 880, 932, 987,  # 3
        1046, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976  # 4
    )

    return (tones[p], t)


def parseMusic(m):
    print("data:")
    print(m)
    baseTone = parseTone(m['tone'])
    bpm = m['bpm']

    beats = (parseBeat(x, baseTone, bpm) for x in m['music'].split())
    return beats


def playBeats(beats):
    for b in beats:
        print(b)
        if (b[0] == 0):
            sleep(b[1] // 1000)
        else:
            winsound.Beep(b[0], b[1])


def printBeats(beats):
    out = [o for b in beats for o in b]
    print("raw_16bit:")
    print(f'[{",".join([hex(o) for o in out])}]')

    bs = struct.pack('H'*len(out), *out)

    print("raw_8bit:")
    print(f'[{",".join([hex(o) for o in bs])}]')

    b64 = base64.b64encode(bs)

    print("base64:")
    print(b64)
    qr = qrcode.QRCode()
    qr.add_data(b64)
    qr.print_ascii()


def readMusicFile(fname):
    with codecs.open(fname, 'r', 'utf8') as f:
        m = yaml.load(f, Loader=yaml.Loader)

    return m


def printUsage():
    print("kuyiTone [play|gen] <filename>")


def main():
    if len(sys.argv) != 3:
        printUsage()
        return

    fname = sys.argv[2]
    cmd = sys.argv[1]
    try:
        m = readMusicFile(fname)
        beats = parseMusic(m)
        match cmd.lower():
            case 'play':
                playBeats(beats)
            case 'gen':
                printBeats(beats)

    except Exception as e:
        print(e)
        return


if __name__ == '__main__':
    main()
