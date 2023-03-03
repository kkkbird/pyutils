import argparse
import os
import codecs


def printfiles(files, outname, codec):
    with codecs.open(outname, "wb", encoding=codec) as fh:
        for f in files:
            fh.write("[{}]\n".format(f))
            with open(f, "rb") as infile:
                try:
                    fh.write(infile.read().decode(codec))
                except UnicodeDecodeError:
                    print(f)                
                fh.write("\n")


def main(args):
    indir = args.indir
    outname = args.outfile
    codec = args.codec

    infiles = []

    for root, dirs, files in os.walk(indir):
        for name in files:
            infiles.append(os.path.join(root, name))

    printfiles(infiles, outname, codec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i',
        '--indir',
        type=str,
        default='.',
        help='Path for input'
    )

    parser.add_argument(
        '-o',
        '--outfile',
        type=str,
        default='output.txt',
        help='output file'
    )

    parser.add_argument(
        '-c',
        '--codec',
        type=str,
        default='utf8',
        help='file encodig'
    )

    args = parser.parse_args()
    main(args)
