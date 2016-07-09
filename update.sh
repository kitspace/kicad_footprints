#!/usr/bin/env bash
set -eu
set -o pipefail

submodule_paths=$(git submodule | awk '{ print $2 }')

for path in $submodule_paths; do
  cd "$path" && git pull origin master &
done

wait
