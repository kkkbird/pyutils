import etcd3
import etcd3.etcdrpc as etcdrpc
import etcd3.exceptions as exceptions
import argparse
from datetime import datetime


def get_prefix(host, port, prefix):
    kvs = []
    try:
        ec = etcd3.client(host=host, port=port)
        rsp = ec.get_prefix(prefix, sort_order='ascend')

        for v, meta in rsp:
            if v.startswith(b"etcdv3_dir"):  # it is a e3w dir key, ignore
                continue

            kvs.append((meta.key, v))

    except exceptions.Etcd3Exception as e:
        print("get_prefix fail:", type(e).__name__)
    except Exception as e:
        print("exception:", e)
    return kvs


def main():
    parser = argparse.ArgumentParser(
        description='read etcd3 by prefix and convert to put')
    parser.add_argument('prefix', type=str, help='etcd server prefix')
    parser.add_argument('-e', '--host', type=str,
                        default="localhost", help='etcd server url')
    parser.add_argument('-p', '--port', type=int,
                        default=2379, help='etcd server port')

    args = parser.parse_args()

    kvs = get_prefix(args.host, args.port, args.prefix)

    if len(kvs) > 0:
        nowTime = datetime.now().strftime('%Y%m%d%H%M%S')
        prefix = args.prefix.replace("/", "_")
        with open("%s_%d_%s_%s.etcd" % (args.host, args.port, prefix, nowTime), "wb") as f:
            for kv in kvs:
                f.write(b"ETCDCTL_API=3 etcdctl put %s %s\n" % (kv[0], kv[1]))


if __name__ == '__main__':
    main()
