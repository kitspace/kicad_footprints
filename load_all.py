import pcbnew
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')

pretties = []
for dirname, dirnames, filenames in os.walk('./'):
    # don't go into any .git directories.
    if '.git' in dirnames:
        dirnames.remove('.git')

    for filename in filenames:
        if (not os.path.isdir(filename)) and (os.path.splitext(filename)[-1] == '.kicad_mod'):
            pretties.append(os.path.realpath(dirname))
            break

src_plugin = pcbnew.IO_MGR.PluginFind(1)

for libpath in pretties:
    print('Loading ' + libpath)
    list_of_footprints = src_plugin.FootprintEnumerate(libpath)
