# -*- Encoding: windows-1251 -*-
import sys
import os
import os.path
import xml.sax
import codecs
import re
import time
import StringIO

class Handler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.__table = {}
        self.reset()

    def reset(self, outPath = None):
        self.__currentTable = {}
        self.__header = False
        self.__output = None
        self.__outPath = outPath
        self.__name = None
        self.__chars = ""
        if outPath != None:
            self.__output = codecs.getwriter("windows-1251")(file(outPath, "wb"), 'xmlcharrefreplace')

    def startDocument(self):
        self.__output.write('<?xml version="1.0" encoding="windows-1251"?>')

    def endDocument(self):
        self.__table[self.__outPath] = self.__currentTable
        self.__output.write("<html><head/><body>%s</body></html>" % xml.sax.saxutils.escape(self.__chars))

    def startElement(self, name, attrs):
        nl = name.lower()
        if nl == "text":
            self.__header = False
            self.__chars = ""
        elif nl == "metatext":
            self.__header = True
            return

        if self.__header:
            self.__name = name
            self.__chars = ""

    def endElement(self, name):
        if self.__header and self.__name != None:
            name = name.lower()
            self.__currentTable[name] = self.__currentTable.get(name, []) + [self.__chars]
            self.__name = None

    def characters(self, content):
        self.__chars += content

    def ignorableWhitespace(self, whitespace):
        self.__chars += whitespace

    def saveTable(self, tablepath, basepath = ""):
        out = codecs.getwriter("windows-1251")(file(tablepath, "wb"), 'xmlcharrefreplace')

        keys = set()
        res = []

        for val in self.__table.values():
            keys.update(val.keys())

        keys = list(keys)
        keys.sort()

        out.write("path;%s\n" % ";".join(keys))

        for (path, val) in self.__table.items():
            if path.startswith(basepath):
                path = path[len(basepath) + 1:]
                res = [path.lstrip().lstrip("\\").lstrip("/")]
            for el in keys:
                res.append("|".join(val.get(el, [])))
            res = map(lambda x: x.replace('"', "'").replace(";", ""), res)
            out.write("%s\n" % ";".join(res).replace("\n", " "))

def convert_directory(indir, outdir, handler, indent = ""):
    curdirname = os.path.basename(indir)
    if outdir != "" and not os.path.exists(outdir):
        os.makedirs(outdir)

    print "%sEntering %s" % (indent, curdirname)
    starttime = time.time()
    nextindent  = indent + "    "

    filelist = os.listdir(indir)
    subdirs = [f for f in filelist if os.path.isdir(os.path.join(indir, f))]
    files = [f for f in filelist if not os.path.isdir(os.path.join(indir, f))]

    for subdir in subdirs:
        inpath = os.path.join(indir, subdir)
        if outdir != "":
            outpath = os.path.join(outdir, subdir)
        else:
            outpath = ""
        convert_directory(inpath, outpath, handler, nextindent)

    for f in files:
        inpath = os.path.join(indir, f)
        if outdir != "":
            outpath = os.path.join(outdir, f)
        else:
            outpath = ""
        convert(inpath, outpath, handler, nextindent)

    print "%sTime: %.2f s" % (indent, time.time() - starttime)

def convert(inpath, outpath, handler, indent=""):
    print "%s%s" % (indent, os.path.basename(inpath)),
    try:
        handler.reset(outpath)
        xml.sax.parseString(convert_file(inpath), handler)
        print " - OK"
    except xml.sax.SAXParseException:
        print " - FAILED"


def convert_file(path):
    res = StringIO.StringIO()
    f = codecs.getreader("utf-8")(file(path, "rb"), 'xmlcharrefreplace')
    for el in f:
        res.write(el.replace("&QUOT;", '"'))
    return codecs.getencoder("utf-8")(res.getvalue(), "replace")[0]

def main():
    if "-convert" in sys.argv:
        handler = Handler()
        convert_directory(sys.argv[1], sys.argv[2], handler)
        handler.saveTable(sys.argv[3], sys.argv[2])

if __name__ == "__main__":
    main()
