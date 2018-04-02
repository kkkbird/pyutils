#! /bin/python

import os
import argparse

INDENT = ' ' * 4
FLAGS = None


def indent(contents):
    lines = list(map(str.strip, contents.splitlines()))
    current_indent = 0
    for index, line in enumerate(lines):
        if (line.endswith('}')):
            current_indent -= 1

        lines[index] = current_indent * INDENT + line

        if (line.endswith('{')):
            current_indent += 1

    return ('\n').join(lines)


def main(args):

    for fname in os.listdir(FLAGS.path):
        if os.path.isfile(fname) and fname.endswith(".conf"):
            o = ""
            fullname = os.path.join(FLAGS.path, fname)
            
            with open(fullname, "rb") as fin:
                o = indent(fin.read().decode('utf8'))
            
            with open(fullname, "wb") as fout:
                fout.write(o.encode('utf8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Path to folders nginx.conf'
    )

    FLAGS, unparsed = parser.parse_known_args()
    main(unparsed)
