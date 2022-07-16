# KiCad footprint collection

- This is a collection of all the KiCad footprints I know of. If you know of any more, please let me know! (Ideally by opening a pull-request or at least an issue on this repo.)
- These footprints are regularily checked with [the Github Action workflow](.github/workflows/load_into_kicad.yml) to make sure KiCad can load them.
- After you [register them with KiCad](#registering-with-kicad) you can use the footprint filter in the footprint assignment tool to find what you want.

![](screenshot.png)

This repo uses git submodules.
A submodule is a way of including another git repo in your repo holding it at a particular version until you want to update it.
This is useful as you can keep a local copy of all the libraries and only update them when you want to.

## Usage

### Initialization


    git clone https://github.com/kitspace/kicad_footprints
    cd kicad_footprints && ./init

This downloads all the libraries in parallel but it can still take a while.

If you are stuck on KiCad version 4 or version 5 can use the `kicad-4` or the `kicad-5` branch. These branches are not being updated though.

### Updating

If you want to update all libraries to their latest versions do:

    ./update

_Warning: `./update` will [`git reset --hard`](http://manpages.ubuntu.com/manpages/xenial/en/man1/git-reset.1.html) the submodules so don't make changes in these folders that you want to keep. Make a separate clone of the submodule respository for that._

If you want to pull in any libraries that have been added since your initial clone:

    git pull && ./init

### Registering with KiCad

You can add these libraries manually through the KiCad GUI of course.
You could also use `generate_table` to generate an fp-lib-table, the file KiCad uses as a footprint registry, with all the footprints from this repository.
You can use this to replace your existing fp-lib-table.
You will need to restart KiCad for this change to take effect.

_Warning: This will overwrite your existing fp-lib-table, discard any customization you made to it and also switch to using our copy of the "official" libraries included with KiCad (these are henceforth prefixed with `kicad-official/`). In our instructions below we make a backup copy of the fp-lib-table so can restore it if you need to._

#### Linux

    cp ~/.config/kicad/6.0/fp-lib-table ~/.config/kicad/6.0/fp-lib-table.backup
    ./generate_table ~/.config/kicad/6.0/fp-lib-table


#### Mac OS

    cp ~/Library/Preferences/kicad/6.0/fp-lib-table ~/Library/Preferences/kicad/6.0/fp-lib-table.backup
    ./generate_table ~/Library/Preferences/kicad/6.0/fp-lib-table

#### Windows (using [git-bash](https://git-scm.com/download))

    cp ~/AppData/Roaming/kicad/6.0/fp-lib-table ~/AppData/Roaming/kicad/6.0/fp-lib-table.backup
    ./generate_table ~/AppData/Roaming/kicad/6.0/fp-lib-table

#### Restoring original

If you don't like the new way of organizing footprint libs and want to restore your original fp-lib-table:

##### Linux

    cp ~/.config/kicad/6.0/fp-lib-table.backup ~/.config/kicad/6.0/fp-lib-table

##### Mac OS

    cp ~/Library/Preferences/kicad/6.0/fp-lib-table.backup ~/Library/Preferences/kicad/6.0/fp-lib-table

##### Windows

    cp ~/AppData/Roaming/kicad/6.0/fp-lib-table.backup ~/AppData/Roaming/kicad/6.0/fp-lib-table


### 3D models

You can try and hack the 3D models to be correctly associated to the footprints through absolute paths by running this script:

```
python3 rewrite_3d_model_paths.py
```

- This script uses dirty regexes to re-write the paths when it finds models of the same name in the same sub-module repository.
- It can take up to 5 minutes on my machine.
- If you ever run `./update` you have to run `rewrite_3d_model_paths.py` again.


### Adding submodules

If you know of any KiCad footprint repositories that have not been added please [file an issue](https://github.com/kitspace/kicad_footprints/issues) and I will add them.

If you want to maintain a private fork of this repository with some private submodules you can add them simply by:

```
git submodule add <git url> <folder>
git commit
```

They should work fine with the rest of the scripts once they are added.

## License

Any scripts in this repository are MIT licensed. All the footprints have their own licenses of course.
