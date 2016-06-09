This is a repo of KiCad footprint libraries as submodules. A submodule is a way of including another git repo in your repo holding it at a particular version until you want to update it. This is useful as you can easily keep a local copy of all the libraries, freeze them and only update when you want to. 

All the official libraries are under the `KiCad/` sub-directory. I will keep adding to this and updating when the libraries update.

To initialise:

    git clone https://github.com/kasbah/kicad_footprints
    cd kicad_footprints && ./init.sh 

This downloads all the libraries asyncronously but it can still take a while. If you want to update all libraries to their latest versions do:

    ./update.sh

You can use `generate_table.py` to generate an fp-lib-table with all
these local repos. You could use this to replace your existing fp-lib-table, e.g. on Linux:
    
    cp ~/.config/kicad/fp-lib-table ~/.config/kicad/fp-lib-table.backup
    ./generate_table.py > ~/.config/kicad/fp-lib-table
