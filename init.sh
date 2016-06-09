#!/usr/bin/env bash

set -e

source ./.submodule_paths.sh

git submodule init

for path in $submodule_paths; do
  git submodule $1 update "$path" && git submodule foreach "git checkout master" &
done

wait

./update.sh
