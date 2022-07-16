"""
replaces paths for 3d models in the footprints with actual 3d files when we can
find them
"""

import os
import re

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
    model_paths = []
    try:
        with open(mod, "r") as f:
            text = f.read()
            new_text = text
            model_paths = re.findall(r"\(model \"?(.+?)\"?\n", text)
            for path in model_paths:
                model_filename = os.path.basename(path)
                new_path = None
                for dirname, dirnames, filenames in os.walk(git_root):
                    for filename in filenames:
                        if model_filename == filename:
                            new_path = os.path.join(git_root, dirname, filename)
                            new_text = new_text.replace(path, new_path)
                            break
                    if new_path is not None:
                        break

        if new_text != text:
            print("Replacing 3d model path for {}".format(mod))
            with open(mod, "w") as f:
                f.write(new_text)

    except Exception as e:
        print("Could not parse {}: {}".format(mod, e))
