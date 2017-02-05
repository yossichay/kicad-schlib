#!/usr/bin/env python3

import os
import sys
import argparse
import kicad_schlib

PCBLIB_PATH = "../../pcblib" # Path relative to the library directory in a mock project

test_functions = []
test_notpl_functions = []

def register(f):
    test_functions.append(f)
    return f

def register_notpl(f):
    test_notpl_functions.append(f)
    return f

@register
def fields_50mil(part):
    """Field text size must be 50mil"""
    for i in part.fields:
        if i.visible and i.value != "" and not part.is_power:
            assert i.size == 50, "field name: %r, value: %r" % (i.name, i.value)


@register_notpl
def footprint_check(part):
    """Footprint check"""
    fp = part.footprint.split(":")
    assert not part.footprint or len(fp) == 2, "Invalid footprint '%s'" % part.footprint
    if part.footprint:
        libname = fp[0] + ".pretty"
        fpname = fp[1] + ".kicad_mod"
        fppath = os.path.join(PCBLIB_PATH, libname, fpname)
        assert os.path.isfile(fppath), "Footprint file '%s' does not exist" % fppath


def main(args):
    retcode = 0

    for fn in os.listdir(args.path):
        if not fn.endswith(".lib"):
            continue

        full_fn = os.path.join(args.path, fn)

        with open(full_fn) as f:
            reader = kicad_schlib.FileReader(f)

            try:
                lib = kicad_schlib.Library.parse(reader)
            except kicad_schlib.KiSyntaxError as e:
                print("[FAIL][    ]  %s - cannot parse" % full_fn)
                print(str(e))
                continue

            success = True
            tests = test_functions + test_notpl_functions if not fn.startswith("_") else []
            for each_part in lib.parts:
                for each_fxn in tests:
                    try:
                        each_fxn(each_part)
                    except Exception as e:
                        print("[    ][FAIL] %s / %s" % (full_fn, each_part.name))
                        print(each_fxn.__doc__ + ": " + str(e))
                        success = False
                        break

            if success:
                print("[PASS][    ] %s" % full_fn)
            else:
                print("[FAIL][    ] %s" % full_fn)
                retcode = 2
                if not args.keep_going: return(retcode)
    return(retcode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-k","--keep-going", action="store_true", help="Keep testing even if failed")
    parser.add_argument("--pcblib-path", type=str, help="Path to the PCB library")
    parser.add_argument("path", help="Path where the schematic libraries are stored")
    args = parser.parse_args()

    if args.pcblib_path:
        PCBLIB_PATH = args.pcblib_path
    else:
        PCBLIB_PATH = os.path.join(args.path, PCBLIB_PATH)

    sys.exit(main(args))
