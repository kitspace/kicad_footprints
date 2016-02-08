#!/usr/bin/env bash

set -e
for path in $(cat paths); do
  git submodule update --init "$path" &
done;

wait

