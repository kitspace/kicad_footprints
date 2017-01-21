echo "Cloning $1"
if ! git submodule update --quiet --depth 1 "$1"
then
  echo "falling back to deep clone for $1"
  if ! git submodule update --quiet "$1"
  then 
      echo "** FAILED ** $1"
  fi
fi
