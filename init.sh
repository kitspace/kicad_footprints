#!/usr/bin/env bash

set -e

git submodule init

submodule_paths=$(git submodule | awk '{ print $2 }')

for path in $submodule_paths; do
  git submodule $1 update "$path" &
done

wait

./update.sh
