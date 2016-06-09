#!/usr/bin/env bash

set -e

source ./.submodule_paths.sh

for path in $submodule_paths; do
  cd "./$path" && git pull || echo "ERROR: $path" &
done;

wait
