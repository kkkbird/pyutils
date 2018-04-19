#! /usr/bin/python3

import os
import argparse
import glob
import re


'''
#confd: {{key||default_value}} - common token
#confd: {{||default_value}} - just a subsitution without key
'''


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
        if len(prefix) > 0 and (not k.startswith('/')):
            full_key = "%s/%s" % (prefix, k)
        else:
            full_key = k
        kvs[full_key] = v
        return "{{getv \"%s\"}}" % full_key
    return _m


def str_setting_env(k, v):
    k = k[1:]  # omit first "/"
    k = k.replace("/", "_")
    k = k.upper()
    #v = v.replace("$", "$$")
    return "%s=%s" % (k, v)


def str_setting_etcd(k, v):
    return "etcdctl set {k} {v}".format(k=k, v=v)


def str_setting_redis(k, v):
    return "redis-cli set {k} {v}".format(k=k, v=v)


def str_setting_consul(k, v):
    return "curl -X PUT -d '{v}' http://localhost:8500/v1/kv{k}".format(k=k, v=v)


def str_setting_rancher(k, v):
    return ""


def print_kvs_and_subs(kvs, subs):
    if len(kvs) > 0:
        print("  >> KVS:")
        for k in sorted(kvs.keys()):
            print("{:>25} : {}".format(k, kvs[k]))
    if len(subs) > 0:
        print("  >> SUBS:")
        for s in sorted(subs):
            print("      {}".format(s))


def create_backend_setttings(options, kvs):
    b = []
    backend_maps = {
        "env": str_setting_env,
        "etcd": str_setting_etcd,
        "redis": str_setting_redis,
        "consul": str_setting_consul,
    }

    if 'fmt' in options and options['fmt'] != "":
        for k, v in kvs.items():
            b.append(options['fmt'].format(k=k, v=v))
        return sorted(b)

    if options["backend"] in backend_maps:
        f = backend_maps[options["backend"]]
        for k, v in kvs.items():
            b.append(f(k, v))
        return sorted(b)
            
    return b


def create_confdfile(options, f_in):
    global LINE_KEY_CONFD, T

    basename = os.path.basename(f_in)
    src = basename + '.tmpl'
    src_path = os.path.join(options["templatesdir"], src)

    lines = []
    kvs = {}
    subs = []
    m = matchs(options["prefix"], kvs, subs)

    with open(f_in, "rb") as f:
        for l in f.readlines():
            l = l.decode('utf8')
            if l.startswith(LINE_KEY_CONFD):
                lines.pop()
                l = l[len(LINE_KEY_CONFD):]
                l = re.sub(r"\{\{([^\|]*)\|\|([^\}]+)\}\}", m, l)
            lines.append(l.encode('utf8'))

    if len(kvs) > 0:
        with open(src_path, "wb") as f:
            f.write(b''.join(lines))

        confd_name = os.path.splitext(basename)[0] + ".toml"
        confd_file = os.path.join(options["confdir"], confd_name)
        with open(confd_file, "wb") as f:
            keys = map(lambda x: "    \"%s\"," % x, sorted(kvs.keys()))
            f.write(T.format(src=src, dest=f_in,
                             keys="\n".join(keys)).encode('utf8'))

    return {
        "kvs": kvs,
        "subs": subs,
    }


def create_confdfiles(options):
    if not os.path.isdir(options['srcdir']):
        print("Err: cannot find %s" % options['srcdir'])
        return

    for p in (options['outdir'], options['confdir'], options['templatesdir']):
        if not os.path.exists(p):
            os.mkdir(p)

    for fname in glob.iglob(options['inputpattern']):
        print("-" * 25)
        print(">> Check %s" % fname)
        out = create_confdfile(options, fname)
        print_kvs_and_subs(out['kvs'], out['subs'])

        if len(out['kvs']) > 0:
            backends = create_backend_setttings(options, out['kvs'])
            print("  >> Backend setting for %s:" % options["backend"])
            for b in backends:
                print(b)


def _main(args):
    options = args.__dict__

    for k, v in options.items():
        print("{:>15} : {}".format(k, v))

    if len(options['prefix']) > 0 and not options["prefix"].startswith('/'):
        print("Err: Prefix must start with '/'")
        exit(-1)

    create_confdfiles(options)


def main():
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

    parser.add_argument(
        '-f',
        '--fmt',
        type=str,
        default="",
        help='backend output format'
    )

    args = parser.parse_args()

    args.srcdir = os.path.dirname(args.inputpattern)
    args.confdir = os.path.join(args.outdir, "conf.d")
    args.templatesdir = os.path.join(args.outdir, "templates")

    _main(args)


if __name__ == "__main__":
    main()
