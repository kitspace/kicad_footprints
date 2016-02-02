This is an entire repo of KiCad footprint libraries as submodules. A submodule is a way of including another git repo in your repo holding it at a particular version until you want to update it. All the official libraries are under the `Kicad/` sub-directory.

This is useful as you can easily keep a local copy of all the libraries, freeze them and only update when you want to. 

All the official libraries are under the `Kicad/` sub-directory.

To clone all the repos 

    git clone --recursive https://github.com/kasbah/kicad_footprints

If you want to update all libraries 

    git pull && git submodule update 

