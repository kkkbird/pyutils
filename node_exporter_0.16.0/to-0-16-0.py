import yaml
import argparse
import sys


def readRules(fname):
    with open(fname, "r") as f:
        return yaml.load(f)


def convertByRule(rules, finName, foutName):
    with open(finName, "r") as fin, open(foutName, "w") as fout:
        for l in fin.readlines():
            for r in rules:
                l = l.replace(r["expr"], r["record"])

            fout.write(l)


def main(args):
    rules = readRules(args.rule)

    all_rules = rules["groups"]

    rules = None

    for r in all_rules:
        if r["name"] == args.rulename:
            rules = r["rules"]
            break

    if rules is None:
        print("Err: cannot find node-exporter-16.rules in rule file")
        sys.exit(-1)

    convertByRule(rules, args.input, args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r', '--rule',
        type=str,
        default='convertrules.yml',
        help='convertion rule file, default: convertrules.yml'
    )

    parser.add_argument(
        '--rulename',
        type=str,
        default='node-exporter-16.rules',
        help='rule name for convertion'
    )

    parser.add_argument(
        '-i', "--input",
        type=str,
        required=True,
        help='input grafana dashborad json'
    )

    parser.add_argument(
        '-o', "--output",
        type=str,
        required=True,
        help='output grafana dashboard json'
    )

    main(parser.parse_args())
