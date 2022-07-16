'''
replaces paths for 3d models in the footprints with actual 3d files when we can
find them
'''

import os
import re
from kiutils.footprint import Footprint

mods = []
git_root = None
for dirname, dirnames, filenames in os.walk("./"):
    dirname = os.path.realpath(dirname)

    if ".git" in dirnames:
        # don't go into our root .git directory.
        dirnames.remove(".git")
    elif ".git" in filenames:
        # this is the submodule root
        git_root = dirname

    for filename in filenames:
        is_dir = os.path.isdir(filename)
        is_mod = os.path.splitext(filename)[-1] == ".kicad_mod"
        if not is_dir and is_mod:
            if git_root is None:
                raise Exception("Could not find git root for {}".format(filename))
            mod = os.path.join(dirname, filename)
            mods.append([git_root, mod])


for git_root, mod in mods:
    try:
        footprint = Footprint.from_file(mod)
    except Exception as e:
        print("Could not parse {}: {}".format(mod, e))
    else:
        for model in footprint.models:
            model_filename = os.path.basename(model.path)
            found = False
            for dirname, dirnames, filenames in os.walk(git_root):
                for filename in filenames:
                    if model_filename == filename:
                        found = True
                        model.path = os.path.join(git_root, dirname, filename)
                        break
                if found:
                    break

            if found:
                print("Replacing 3d model path for {}".format(mod))
                footprint.to_file(mod)

