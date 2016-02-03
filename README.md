This is a repo of KiCad footprint libraries as submodules. A submodule is a way of including another git repo in your repo holding it at a particular version until you want to update it. This is useful as you can easily keep a local copy of all the libraries, freeze them and only update when you want to. 

All the official libraries are under the `Kicad/` sub-directory. I will keep adding to this and updating when the libraries update.

To clone all the repos 

    git clone --recursive https://github.com/kasbah/kicad_footprints

If you want to update all libraries 

    cd kicad_footprints && git pull && git submodule update 

You can use `generate_fp-lib-table.py` to generate an fp-lib-table with all
these local repos. You could use this to replace your existing fp-lib-table, e.g. on Linux:
    
    cp ~/.config/kicad/fp-lib-table ~/.config/kicad/fp-lib-table.backup
    ./generate_fp-lib-table.py > ~/.config/kicad/fp-lib-table


