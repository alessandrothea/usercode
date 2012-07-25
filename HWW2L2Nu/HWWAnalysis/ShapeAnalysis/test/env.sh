SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
SCRIPTS="$(dirname $SOURCE)/../scripts"
PYTHON="$(dirname $SOURCE)/../python"
DIRS="$( cd -P $SCRIPTS && pwd )"
DIRP="$( cd -P $PYTHON && pwd )"

export PATH="$DIRS:$PATH"
export PYTHONPATH="$DIRS:$PYTHONPATH"
echo "$DIRS added to PATH and PYTHONPATH"
export PYTHONPATH="$DIRP:$PYTHONPATH"
echo "$DIRP added to PATH"
