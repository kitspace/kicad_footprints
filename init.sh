#!/usr/bin/env bash

set -eu
set -o pipefail

git submodule init

submodule_paths=$(git submodule | awk '{ print $2 }')

for path in $submodule_paths; do
  git submodule update "$path" &
done

wait
