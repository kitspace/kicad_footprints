#!/usr/bin/env bash
set -eu
set -o pipefail

git submodule init

submodule_paths=$(git submodule | awk '{ print $2 }')

pids=()
for path in $submodule_paths; do
  git submodule update --depth 1 "$path" &
  pids+=($!)
done

for pid in "${pids[@]}"; do
  wait $pid
done
