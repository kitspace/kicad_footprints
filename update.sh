#!/usr/bin/env bash
set -eu
set -o pipefail

git submodule foreach "git pull origin master&"

wait
