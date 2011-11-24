#!/bin/bash
LUMI=$1; if [[ "$LUMI" == "" ]]; then echo "$0 lumi"; exit 1; fi;
for m in $(cat ./masses); do 
    test -f hww-$LUMI.mH$m.comb_0j_shape.txt || continue;
    test -f hww-$LUMI.mH$m.comb_1j_shape.txt || continue;
    test -f hww-$LUMI-cuts.mH$m.comb2j.txt || echo "No 2-jets datacards for m(H) = $m, lumi $LUMI (hww-$LUMI-cuts.mH$m.comb2j.txt)";
    test -f hww-$LUMI-cuts.mH$m.comb2j.txt || break;
    echo " make hww-$LUMI.mH$m.allcomb.txt"
    combineCards.py HWW_0j=hww-$LUMI.mH$m.comb_0j_shape.txt HWW_1j=hww-$LUMI.mH$m.comb_1j_shape.txt HWW_2j=hww-$LUMI-cuts.mH$m.comb2j.txt > hww-$LUMI.mH$m.allcomb_shape.txt
done
