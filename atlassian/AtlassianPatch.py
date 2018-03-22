import os
import base64
import sys
import struct
import zipfile

ori_key_list = [b'MIIBuDCCASwGByqGSM44BAEwggEfAoGBAP1/U4EddRIpUt9KnC7s5Of2EbdSPO9EAMMeP4C2USZpRV1AIlH7WT2NWPq/xfW6MPbLm1Vs14E7gB00b/JmYLdrmVClpJ+f6AR7ECLCT7up1/63xhv4O1fnxqimFQ8E+4P208UewwI1VBNaFpEy9nXzrith1yrv8iIDGZ3RSAHHAhUAl2BQjxUjC8yykrmCouuEC/BYHPUCgYEA9+GghdabPd7LvKtcNrhXuXmUr7v6OuqC+VdMCz0HgmdRWVeOutRZT+ZxBxCBgLRJFnEj6EwoFhO3zwkyjMim4TwWeotUfI0o4KOuHiuzpnWRbqN/C/ohNWLx+2J6ASQ7zKTxvqhRkImog9/hWuWfBpKLZl6Ae1UlZAFMO/7PSSoDgYUAAoGBAIvfweZvmGo5otwawI3no7Udanxal3hX2haw962KL/nHQrnC4FG2PvUFf34OecSK1KtHDPQoSQ+DHrfdf6vKUJphw0Kn3gXm4LS8VK/LrY7on/wh2iUobS2XlhuIqEc5mLAUu9Hd+1qxsQkQ50d0lzKrnDqPsM0WA9htkdJJw2nS', ]

crack_key = b'MIIBtjCCASsGByqGSM44BAEwggEeAoGBAIAAAAAAAANbJyV1TeD8Fg1mRpH9WAzgEVSHEuEhbvnKJEffhzkQ7Z4OsFMntpt+W77s8d4lhvg0WlrIZyCc4xmD1qyOgbHeuvSdnMdc9ST4Nhcfc16bTKGlCb7MSWNd/4cFKhLje+6UD/UjwHtzqfTWsFaybNBujpo7T/lj1z6xAhUAhF+jYrmnGey79BjtpVuaRsAPNV0CgYAFfsRbCaBLfU0JurZePmOy1IAd1ZLYrHA1eEDyH3fudu/IOZg1BW3YW5+OXzMBOMxKWGazbvKPiW/wldy33478ZniVxmjrE/hVDkYtNevw8KMEcQ+Pkx1KEBgnVhRhPDFl9HUFn2MwJlOcz4PB5AzePolLe3AxTecQ8kf1ulKRvwOBhAACgYAOVYItLOHRR3CYJm1iHl/QVWfotLE3je3IH9F5YxV6T4/1/p7/kbGBGgR9wFLn5b+pnMxZfeYGud6H6yrLTs4tcsddAulsqSdyxp0FgMa1DOYK+BGtEr5NiXWxCXYX4atdbm1b8HPplo+8sh2XwA+N8aEl6UUL41PmPiQJmRBRNg=='

crack_list = ('com/atlassian/extras/decoder/v2/Version2LicenseDecoder.class', )

# def patch_lic_file(fname):
#     with open(fname, 'rb+') as f:
#         content = f.read()
#         f.seek(0)
#         f.write(content.replace(ori_key, crack_key))


def crack_jar(fname):

    tmpname = fname + 'tmp'
    with zipfile.ZipFile(fname, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment
            for item in zin.infolist():
                content = zin.read(item.filename)
                if item.filename in crack_list:
                    for ori_key in ori_key_list:
                        if content.find(ori_key) < 0:
                            print('cannot find the ori_key in %s' %
                                  item.filename)
                        else:
                            print('%s is cracked' % item.filename)
                            content = content.replace(ori_key, crack_key)
                zout.writestr(item, content)

    os.remove(fname)
    os.rename(tmpname, fname)


def find_cracked_jar(path):
    cracked_jars = []
    for root, dirnames, filenames in os.walk(path):
        for fname in filenames:
            full_path = os.path.join(root, fname)
            if full_path.endswith('.jar'):
                with zipfile.ZipFile(full_path, 'r') as zin:
                    for item in zin.infolist():
                        if item.filename in crack_list:
                            cracked_jars.append(full_path)
                            break
    return cracked_jars


def main():
    if len(sys.argv) == 1:
        dst_path = os.path.dirname(__file__)
    else:
        dst_path = os.path.abspath(sys.argv[1])

    patched_files = find_cracked_jar(dst_path)

    for f in patched_files:
        print('cracking %s' % f)
        crack_jar(f)

    print('done')


if __name__ == '__main__':
    main()
