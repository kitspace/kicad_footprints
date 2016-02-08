#!/usr/bin/env bash

echo -n '' > .submodule_paths
git submodule foreach 'echo "$path" >> $toplevel/.submodule_paths'
