#! /usr/bin/python

import os
import argparse
import codecs
import shutil

from pyquery import PyQuery as pq

FLAGS = None


def getScriptNames(indir):
    libs = []
    srcs = []

    indexhtml = os.path.join(indir, "index.html")
    with codecs.open(indexhtml, 'r', 'utf-8') as fin:
        q = pq(fin.read())
        scripts = q("script")

        for js in scripts:
            src = js.attrib['src']
            if src.startswith("libs"):
                libs.append(src)
            else:
                srcs.append(src)
    return libs, srcs


def createGameJS(indir, jsNames):
    path = os.path.join(indir, "game.js")
    with codecs.open(path, "w", 'utf-8') as outjs:
        outjs.write("require(\"weapp-adapter.js\");\n")
        for js in jsNames:
            outjs.write("require(\"{}\");\n".format(js))

    return


def mergeLayaGameJS(indir, srcs):
    outName = "layagame.js"
    mergedPath = os.path.join(indir, outName)
    with codecs.open(mergedPath, "w", 'utf-8') as fmerged:
        for src in srcs:
            path = os.path.join(indir, src)
            with codecs.open(path, 'r', 'utf-8') as fin:
                fmerged.write(
                    "// By laya minigame creator: merge source {}\n".format(src))
                fmerged.write(fin.read())

    return outName


def copyScripts2Out(indir, scripts, outdir):
    if not (os.path.exists(outdir) and os.path.isdir(outdir)):
        os.mkdir(outdir)

    for f in scripts:
        srcPath = os.path.join(indir, f)
        dstPath = os.path.join(outdir, f)
        dstDir = os.path.split(dstPath)[0]
        if not (os.path.exists(dstDir) and os.path.isdir(dstDir)):
            os.mkdir(dstDir)
        print("copy {} to {}".format(srcPath, dstPath))
        shutil.copy(srcPath, dstPath)


def main(args):
    libs, srcs = getScriptNames(FLAGS.indir)
    merged = mergeLayaGameJS(FLAGS.indir, srcs)
    createGameJS(FLAGS.indir, libs+[merged, ])

    if FLAGS.out:
        copyScripts2Out(FLAGS.indir, libs+[merged, "game.js"], FLAGS.out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("indir", default="./bin",
                        help="input dir path, default [./bin]")

    parser.add_argument("-o", "--out", help="output dir path")

    FLAGS, unparsed = parser.parse_known_args()

    print(FLAGS)

    main(unparsed)
