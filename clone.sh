echo "Cloning $1"
if ! git submodule update --quiet --depth 1 "$1"
then
  echo "Submodule out of date: $1"
  sh check.sh "$1"
fi
