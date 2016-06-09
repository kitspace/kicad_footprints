#!/usr/bin/env bash

submodule_paths=$(git submodule | awk '{ print $2 }')
