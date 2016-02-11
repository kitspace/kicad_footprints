#!/usr/bin/env bash

set -e

git submodule init

for path in $(cat .submodule_paths); do
  cd "$path" && git pull &
done;

wait

