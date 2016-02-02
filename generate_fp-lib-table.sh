#!/usr/bin/env bash

set -e
echo "(fp_lib_table"
for dir in */*; do
  echo "  (lib (name $dir)(type KiCad) (uri $(pwd)/$dir) (options \"\") (descr \"\"))";
done
echo ")"
