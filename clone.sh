echo "Initializing $1"
if ! git submodule update --quiet --depth 1 "$1" 2> /dev/null
then
  echo "Submodule out of date: $1"
  pushd "$1" && git fetch --unshallow --quiet
  popd && git submodule update --quiet "$1"
fi
