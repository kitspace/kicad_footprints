#!/usr/bin/env bash

set -e

git submodule init

for path in $(cat .submodule_paths); do
  git submodule update "$path" &
done;

wait

for path in $(cat .submodule_paths); do
  cd "$path" && git pull &
done;

wait

