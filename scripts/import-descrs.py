#!/usr/bin/python3

# usage: import-descrs.py LIBFILE.lib BOMTOOL_DB_FILES... <original.dcm >new.dcm

import shlex
import sys

def printerr(s):
    """Print to stderr"""
    sys.stderr.write(s)
    sys.stderr.write('\n')
    sys.stderr.flush()

def read_bomlines(libfile):
    """Parse a kicad library file, returning a dict of part name to BOM line.

    The BOM line will be returned as a list of split words, normalized to all-caps.
    """

    bomlines = {}
    this_cmp = None
    bomline = None

    for line in libfile:
        line = line.strip()
        if line.startswith("F"):
            cols = shlex.split(line)
        if line.startswith("F1"):
            this_cmp = cols[1]
        elif line.startswith("F") and cols[-1] == "BOM":
            bomline = tuple(i.upper() for i in cols[1].split())
        elif line == "ENDDEF":
            assert this_cmp is not None
            if bomline is not None:
                bomlines[this_cmp] = bomline
            this_cmp = None
            bomline = None

    return bomlines

def read_descriptions(dbfile):
    """Parse a DB file, returning a dict of BOM line to description.
    """

    descriptions = {}
    this_bomline = None
    description = None

    for line in dbfile:
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        if this_bomline is None:
            this_bomline = tuple(i.upper() for i in line.split())
            continue

        head, space, tail = line.partition(" ")
        if head.upper() == "DESCR":
            assert description is None
            description = tail

        elif head.upper() == "END":
            assert this_bomline is not None
            if description is not None:
                descriptions[this_bomline] = description
            this_bomline = None
            description = None

    return descriptions

def filter_dcmfile(bomlines, descriptions, infile, outfile):
    """Read a DCM file, and use the given component->bomline and bomline->description
    dicts to substitute in new description lines."""

    this_component = None
    for line in infile:
        if line.startswith("$CMP "):
            this_component = line.strip().partition(" ")[2]
            outfile.write(line)
        elif line.startswith("D "):
            bomline = bomlines.get(this_component)
            if bomline is None:
                printerr("No BOM line for part %s" % this_component)
            description = descriptions.get(bomline)
            if description is not None:
                outfile.write("D %s\n" % description)
            else:
                outfile.write(line)
        elif line.startswith("K "):
            # TODO: implement keywords
            # for now, remove these lines. the existing keywords are crufty.
            pass
        elif line.strip() == "$ENDCMP":
            this_component = None
            outfile.write(line)
        else:
            outfile.write(line)

def main(argv):
    # usage: import-descrs.py LIBFILE.lib BOMTOOL_DB_FILES... <original.dcm >new.dcm
    lib_filename = argv[1]
    db_filenames = argv[2:]

    with open(lib_filename) as f:
        bomlines = read_bomlines(f)

    descriptions = {}
    for fn in db_filenames:
        with open(fn) as f:
            thisfn_descriptions = read_descriptions(f)
        for key in thisfn_descriptions:
            descriptions[key] = thisfn_descriptions[key]

    filter_dcmfile(bomlines, descriptions, sys.stdin, sys.stdout)

if __name__ == "__main__":
    main(sys.argv)
