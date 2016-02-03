#! /usr/bin/env python

from __future__ import print_function
import os

print('(fp_lib_table')
for dirname, dirnames, filenames in os.walk('.'):
    # editing the 'dirnames' list will stop os.walk() from recursing into there.
    if '.git' in dirnames:
        # don't go into any .git directories.
        dirnames.remove('.git')

    for filename in filenames:
        if os.path.splitext(filename)[-1] == '.kicad_mod':
            print('  (lib (name %s)(type KiCad) (uri %s) (options "") (descr ""))'
                    % (os.path.relpath(dirname, os.path.curdir), os.path.realpath(dirname)))
print(')')
