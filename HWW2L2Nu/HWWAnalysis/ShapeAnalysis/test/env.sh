SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

export PATH="$DIR/scripts:$PATH"
export PYTHONPATH="$DIR/scripts:$PYTHONPATH"
echo "$DIR/scripts added to PATH"
export masses="110 115 120 130 140 150 160 170 180 190 200 250 300 350 400 450 500 550 600"
export jets="0 1"
