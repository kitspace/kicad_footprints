#!/usr/bin/env bash

submodule_paths=$(git config --file .gitmodules --get-regexp path | awk '{ print $2 }')
