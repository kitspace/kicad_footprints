# KiCAD footprint collection
This is a collection of all the KiCAD footprints I know of. If you know of any more, please let me know!

It's best used with footprint search that is part of kicad "product" (daily) builds.

![](screenshot.png)

This repo uses git submodules.
A submodule is a way of including another git repo in your repo holding it at a particular version until you want to update it.
This is useful as you can easily keep a local copy of all the libraries, freeze them and only update when you want to.

All the official libraries are under the `KiCad/` sub-directory. I will keep
adding to this and updating when the libraries update.

To initialise:

    git clone https://github.com/monostable/kicad_footprints
    cd kicad_footprints && ./init

This downloads all the libraries in parallell but it can still take a while.

If you want to update all libraries to their latest versions do:

    ./update

You can use `generate_table` to generate an fp-lib-table with all these
local repos. You could use this to replace your existing fp-lib-table, e.g. on
Linux:
    
    cp ~/.config/kicad/fp-lib-table ~/.config/kicad/fp-lib-table.backup
    ./generate_table > ~/.config/kicad/fp-lib-table
    
You will need to restart KiCAD for this change to take proper effect. 

If you want to pull in any libraries that have been added since your initial clone:

    git pull 
    ./init
