#!/usr/bin/env bash
set -eu
set -o pipefail

submodule_paths=$(git submodule | awk '{ print $2 }')

pids=()
for path in $submodule_paths; do
  cd "$path" && git pull origin master &
  pids+=($!)
done

for pid in "${pids[@]}"; do
  wait $pid
done
