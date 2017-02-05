import os
import sys
import kicad_schlib

PCBLIB_PATH = "../../pcblib" # Path relative to the library directory in a mock project

test_functions = []

def register(f):
    test_functions.append(f)
    return f

@register
def fields_50mil(part):
    """field text size must be 50mil"""
    for i in part.fields:
        if i.visible and i.value != "" and not part.is_power:
            assert i.size == 50, "field name: %r, value: %r" % (i.name, i.value)


@register
def footprint_exists(part):
    """Footprint must either be blank or valid and existent"""
    fp = part.footprint.split(":")
    assert not part.footprint or len(fp) == 2, "Invalid footprint '%s'" % part.footprint
    if part.footprint:
        libname = fp[0] + ".pretty"
        fpname = fp[1] + ".kicad_mod"
        fppath = os.path.join(PCBLIB_PATH, libname, fpname)
        assert os.path.isfile(fppath), "Footprint file '%s' does not exist" % fppath


def main(argv):
    global PCBLIB_PATH
    if len(argv) == 2:
        path = argv[1]
    elif len(argv) == 1:
        path = '.'
    else:
        print("usage: test.py [path]", file=sys.stderr)
        return 1

    PCBLIB_PATH = os.path.join(path, PCBLIB_PATH)

    for fn in os.listdir(path):
        if not fn.endswith(".lib"):
            continue

        full_fn = os.path.join(path, fn)

        with open(full_fn) as f:
            reader = kicad_schlib.FileReader(f)

            try:
                lib = kicad_schlib.Library.parse(reader)
            except kicad_schlib.KiSyntaxError as e:
                print("[FAIL][    ]  %s - cannot parse" % full_fn)
                print(str(e))
                continue

            success = True
            for each_part in lib.parts:
                for each_fxn in test_functions:
                    try:
                        each_fxn(each_part)
                    except Exception as e:
                        print("[    ][FAIL] %s / %s" % (full_fn, each_part.name))
                        print(each_fxn.__doc__)
                        print(str(e))
                        success = False
                        break

            if success:
                print("[PASS][    ] %s" % full_fn)
            else:
                print("[FAIL][    ] %s" % full_fn)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
