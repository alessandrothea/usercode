#!/bin/bash

scriptPath=${PWD}/$(dirname $0)
scriptName=$(basename -s .sh $0)
destSrc=${scriptPath}/../src
destInc=${scriptPath}/../include


while getopts t:p: opt
do case "$opt" in
	t) TreeName=$OPTARG;;
	p) PathName=$OPTARG;;
	?)echo "Usage: -r <TreeName> "
      echo "	   -p <PathName>"
esac
done
if [[ -z $TreeName ]]; then
    echo "No Tree"
    exit 1
fi
if [[ -z $PathName ]]; then
    echo "No Path"
    exit 1
fi
echo "TreeName $TreeName - PathName $PathName"

root -b -q -l "${scriptPath}/${scriptName}.C(\"${TreeName}\", \"${PathName}\")"

[[ -f ETHZNtupleReader.h ]] && mv ETHZNtupleReader.h ${destInc}
[[ -f ETHZNtupleReader.C ]] && mv ETHZNtupleReader.C ${destSrc}/ETHZNtupleReader.cc 

