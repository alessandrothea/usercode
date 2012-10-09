#!/bin/bash

if (( $#==0 )); then
    echo "Usage $0 <dir1> <dir2> <dir3>..."
    exit -1
fi

for d in $@
do
    if [[ -d $d ]]; then
    cp -v $CMSSW_BASE/src/HWWAnalysis/Misc/goodies/index.php $d
    fi
done
