#!/bin/bash
# set -x

lumi=4.63
head="hww-${lumi}fb.mH"
head2j="hww-${lumi}fb.mH"
tail="_shape.txt"
masses="110 115 120 130 140 150 160 170 180 190 200 250 300 350 400 450 500 550 600"
hline=$(printf '%.0s-' {1..80})
for mass in $masses
do

	for jet in 0j 1j
	do
        echo $hline
        echo " Combining cards $mass $jet"
        echo $hline
		if [ -e $head$mass".of_"$jet$tail ] && [ -e $head$mass".sf_"$jet$tail ] 
		then
			echo " ${mass}: of_${jet} sf_${jet} => comb_${jet}"
			combineCards.py  "of_"$jet"="$head$mass".of_"$jet$tail  "sf_"$jet"="$head$mass".sf_"$jet$tail > $head$mass".comb_"$jet$tail 
		fi
	done

	if [ -e $head$mass".of_0j"$tail ] && [ -e $head$mass".sf_0j"$tail ] && [ -e $head$mass".of_1j"$tail ] && [ -e $head$mass".sf_1j"$tail ]
	then
		echo " $mass: sf_0j of_0j of_1j sf_1j => comb_0j1j "
		combineCards.py  "of_0j="$head$mass".of_0j"$tail  "sf_0j="$head$mass".sf_0j"$tail "of_1j="$head$mass".of_1j"$tail  "sf_1j="$head$mass".sf_1j"$tail > $head$mass".comb_0j1j"$tail
	fi

	if [ -e $head$mass".comb_0j"$tail ] && [ -e $head$mass".comb_1j"$tail ] && [ -e $head2j$mass".comb_2j_cb.txt" ]
	then
		echo " $mass: comb_0j comb_1j comb_2j_cb => comb_0j1j2j "
		combineCards.py HWW_0j=$head$mass".comb_0j"$tail HWW_1j=$head$mass".comb_1j"$tail HWW_2j=$head2j$mass.comb_2j_cb.txt > $head$mass.comb_0j1j2j$tail
fi

done


