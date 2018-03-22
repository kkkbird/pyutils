#! python3

import os
import argparse
import glob
import re

import hashlib

FLAGS = None

STATE_NONE, STATE_READ_FUNC, STATE_READ_FILE, STATE_READ_CREATE_FILE = range(4)


def parse_goroutine_line(l):
    m = re.match(r'^goroutine \w+ \[(.+)\]:$', l)

    if m:
        l = m.group(1).split(",", 1)
        if len(l) == 2:
            return l[0], l[1].strip()
        return l[0], ""

    return None, ""


def parse_func_line(l):
    m = re.match(r'^goroutine \w+ \[(\w+)\]:$', l)

    if m:
        return m.group(1)

    return None


def getlogs(flist):
    for fname in flist:
        with open(fname) as f:
            for l in f:
                yield l.strip()


def infomd5(info):
    s = info["reason"]
    for cs in info["callstacks"]:
        s += cs[0] + cs[1]
    s += info["createdby"]

    m = hashlib.md5()
    m.update(s.encode("utf8"))
    return m.hexdigest()


def printinfos(infos):
    fatalerrors = infos["fatalerrors"]
    infoMaps = infos["infomaps"]

    if "unfinished" in infos:
        print("="*20)

        unfinished = infos["unfinished"]
        print("unfinished goroutine")
        print(unfinished["reason"], unfinished["callstacks"],
              unfinished["createdby"])

    if len(fatalerrors):
        print("="*20)
        print("%d Fatal error(s):" % len(fatalerrors))
        for e in fatalerrors:
            print(e)

    print("="*20)
    if len(infoMaps) > 0:
        infos = sorted(infoMaps.items(), key=lambda v: v[1]["count"])
        for k, v in infos:
            print(k, v["count"], v["reason"], v["createdby"], len(v["addon"]))

        print("="*20)
        LIST_NUM = FLAGS.showtop
        print("TOP %d routine call stack" % LIST_NUM)

        for i, (k, v) in enumerate(infos[-LIST_NUM:]):
            print("%d, REASON: %s, COUNT: %d, ADDONS:%d" %
                  (LIST_NUM-i, v["reason"], v["count"], len(v["addon"])))
            for sFunc, sFile in v["callstacks"]:
                print(sFunc)
                print("    %s" % sFile)

            print(v["createdby"])
            print("-"*10)
    else:
        print("no goroutine call stack")


def parselog(flist):
    infoMaps = {}
    reason = ""
    callfunc = ""
    callfile = ""
    callstacks = []
    createdby = ""
    addon = ""

    fatalerrors = []

    state = STATE_NONE
    for l in getlogs(flist):
        if len(l) == 0:
            continue

        if state == STATE_NONE:
            if l.startswith('fatal error:'):
                fatalerrors.append(l.split(":", 1)[1])

            reason, addon = parse_goroutine_line(l)
            if reason:
                state = STATE_READ_FUNC
        elif state == STATE_READ_FUNC:
            if l.startswith("created by "):
                createdby = l
                state = STATE_READ_CREATE_FILE
            else:
                callfunc = l.rsplit("(", 1)[0]
                state = STATE_READ_FILE
        elif state == STATE_READ_FILE:
            if l.startswith("created by "):
                createdby = l
                state = STATE_READ_CREATE_FILE
            else:
                callfile = l.rsplit(" ", 1)[0]
                callstacks.append((callfunc, callfile))
                state = STATE_READ_FUNC
        elif state == STATE_READ_CREATE_FILE:
            createdbyfile = l.rsplit(" ", 1)[0]
            createdby = "%s %s" % (createdby, createdbyfile)

            info = {
                "reason": reason,
                "callstacks": callstacks,
                "createdby": createdby,
            }
            md5 = infomd5(info)

            if md5 in infoMaps:
                infoMaps[md5]["count"] += 1
            else:
                infoMaps[md5] = info
                infoMaps[md5]["count"] = 1
                infoMaps[md5]["addon"] = []

            if addon:
                infoMaps[md5]["addon"].append(addon)

            reason = ""
            callfunc = ""
            callfile = ""
            callstacks = []
            createdby = ""
            addon = ""

            state = STATE_NONE

    infos = {
        "fatalerrors": fatalerrors,
        "infomaps": infoMaps,
    }

    if state != STATE_NONE:
        infos["unfinished"] = {
            "reason": reason,
            "callstacks": callstacks,
            "createdby": createdby,
        }

    return infos


def main(args):
    print(FLAGS)

    flist = []
    for f in glob.iglob(FLAGS.errpattern):
        flist.append(f)

    flist.sort(key=lambda f: os.stat(f).st_mtime)

    print("Log files:", flist)

    infos = parselog(flist)

    printinfos(infos)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--errpattern',
        type=str,
        default='err.log*',
        help='Path to folders of labeled images.'
    )
    parser.add_argument(
        '--showtop',
        type=int,
        default=10,
        help='how many top routines will show in detail'
    )

    FLAGS, unparsed = parser.parse_known_args()
    main(unparsed)
