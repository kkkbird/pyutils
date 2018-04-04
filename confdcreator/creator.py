#! /bin/python

import os
import argparse
import glob
import re

'''
key pattern: {{key||default_value}}
'''

FLAGS = None

T = '''[template]
src = "{src}"
dest = "{dest}"
keys = [
{keys}
]
'''


def matchs(prefix, kvs):
    def _m(m):
        k, v = m.group(1), m.group(2)
        full_key = "%s/%s" % (prefix, k)
        kvs[full_key] = v
        return "\"{{getv %s}}\"" % full_key
    return _m


def create_confdfiles(f_in):
    basename = os.path.basename(f_in)
    src = basename + '.tmpl'
    src_path = os.path.join(FLAGS.templatesdir, src)

    lines = []
    kvs = {}
    m = matchs(FLAGS.prefix, kvs)
    with open(f_in, "rb") as f:
        for l in f.readlines():
            l = l.decode('utf8')
            l = re.sub(r"\{\{/confd/(\S+)\|\|(.+)\}\}", m, l)

            lines.append(l.encode('utf8'))

    if len(kvs) > 0:
        with open(src_path, "wb") as f:
            f.write(b''.join(lines))

        print(os.path.splitext(basename), basename)
        confd_name = os.path.splitext(basename)[0] + ".toml"
        confd_file = os.path.join(FLAGS.confdir, confd_name)
        with open(confd_file, "wb") as f:
            keys = map(lambda x: "    \"%s\"," % x, kvs.keys())
            f.write(T.format(src=src, dest=f_in,
                             keys="\n".join(keys)).encode('utf8'))


def main(args):
    for p in [FLAGS.outdir, FLAGS.confdir, FLAGS.templatesdir]:
        if not os.path.exists(p):
            os.mkdir(p)

    for fname in glob.iglob(FLAGS.inputpattern):
        create_confdfiles(fname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i',
        '--inputpattern',
        type=str,
        default=r'./conf/*.conf',
        help='input file pattern'
    )

    parser.add_argument(
        '-o',
        '--outdir',
        type=str,
        default='./confd',
        help='Path for output confd dir'
    )

    parser.add_argument(
        '-p',
        '--prefix',
        type=str,
        default='',
        help='Prefix for confd key'
    )

    parser.add_argument(
        '-b',
        '--backend',
        type=str,
        default='env',
        help='backend type for confd output'
    )

    FLAGS, unparsed = parser.parse_known_args()

    FLAGS.confdir = os.path.join(FLAGS.outdir, "conf.d")
    FLAGS.templatesdir = os.path.join(FLAGS.outdir, "templates")
    main(unparsed)
