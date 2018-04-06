#! /bin/python

import os
import argparse
import glob
import re


'''
#confd: {{key||default_value}} - common token
#confd: {{||default_value}} - just a subsitution without key
'''

FLAGS = None

LINE_KEY_CONFD = "#confd:"

T = '''[template]
src = "{src}"
dest = "{dest}"
keys = [
{keys}
]
'''


def matchs(prefix, kvs, subs):
    def _m(m):
        k, v = m.group(1), m.group(2)
        if k == '':
            subs.append(v)
            return v
        if len(prefix) > 0:
            full_key = "%s/%s" % (prefix, k)
        else:
            full_key = k
        kvs[full_key] = v
        return "\"{{getv %s}}\"" % full_key
    return _m


def str_setting_env(k, v):
    k = k[1:]  # omit first "/"
    k = k.replace("/", "_")
    k = k.upper()
    return "%s=%s" % (k, v)


def print_backend_settings(kvs):
    print_maps = {
        "env": str_setting_env,
    }

    if FLAGS.backend in print_maps:
        f = print_maps[FLAGS.backend]
        print("  >> Backend setting for %s:" % FLAGS.backend)
        for k, v in kvs.items():
            print(f(k, v))
    else:
        print("  >> Backend output of %s is not supported now" % FLAGS.backend)


def print_kvs_and_subs(kvs, subs):
    if len(kvs) > 0:
        print("  >> KVS:")
        for k, v in kvs.items():
            print("{:>25} : {}".format(k, v))
    if len(subs) > 0:
        print("  >> SUBS:")
        for s in subs:
            print("      {}".format(s))


def create_confdfiles(f_in):
    basename = os.path.basename(f_in)
    src = basename + '.tmpl'
    src_path = os.path.join(FLAGS.templatesdir, src)

    lines = []
    kvs = {}
    subs = []
    m = matchs(FLAGS.prefix, kvs, subs)

    print("-" * 25)
    print(">> Check %s" % f_in)

    with open(f_in, "rb") as f:
        for l in f.readlines():
            l = l.decode('utf8')
            if l.startswith(LINE_KEY_CONFD):
                lines.pop()
                l = l[len(LINE_KEY_CONFD):]
                l = re.sub(r"\{\{([^\|]*)\|\|([^\}]+)\}\}", m, l)
            lines.append(l.encode('utf8'))

    print_kvs_and_subs(kvs, subs)

    if len(kvs) > 0:
        with open(src_path, "wb") as f:
            f.write(b''.join(lines))

        confd_name = os.path.splitext(basename)[0] + ".toml"
        confd_file = os.path.join(FLAGS.confdir, confd_name)
        with open(confd_file, "wb") as f:
            keys = map(lambda x: "    \"%s\"," % x, kvs.keys())
            f.write(T.format(src=src, dest=f_in,
                             keys="\n".join(keys)).encode('utf8'))

        print_backend_settings(kvs)


def main(args):
    print("FLAGS:")
    for k, v in FLAGS.__dict__.items():
        print("{:>15} : {}".format(k, v))

    if len(FLAGS.prefix) > 0 and not FLAGS.prefix.startswith('/'):
        print("Err: Prefix must start with '/'")
        exit(-1)

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
