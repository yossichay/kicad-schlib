#!/usr/bin/python3
import os
import subprocess
import sys

md5sums = {}

dirname = sys.argv[1]

for fn in os.listdir(dirname):
    md5sum = subprocess.check_output(['md5sum', os.path.join(dirname, fn)]).decode('ascii').partition(" ")[0]

    if md5sum in md5sums:
        # This blob already exists. Symlink it
        os.unlink(os.path.join(dirname, fn))
        os.symlink(md5sums[md5sum], os.path.join(dirname, fn))

    else:
        md5sums[md5sum] = fn
