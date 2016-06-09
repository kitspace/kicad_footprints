#! /usr/bin/env python

from __future__ import print_function
import os

print('(fp_lib_table')
#look for all folders with .kicad_mod files and add those folders as libraries
for dirname, dirnames, filenames in os.walk(os.path.curdir):
    # don't go into any .git directories.
    if '.git' in dirnames:
        dirnames.remove('.git')

    for filename in filenames:
        if os.path.splitext(filename)[-1] == '.kicad_mod':
            print('  (lib (name %s)(type KiCad) (uri %s) (options "") (descr ""))'
                    % (os.path.relpath(dirname, os.path.curdir), os.path.realpath(dirname)))
            break
print(')')
