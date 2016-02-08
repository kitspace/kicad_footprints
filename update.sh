#!/usr/bin/env bash

set -e
echo -n '' > paths
git submodule foreach 'echo "$path" >> $toplevel/paths'

for path in $(cat paths); do
  git submodule update --init "$path" &
done;

wait

