#!/bin/bash
# set -x

head="hww-4.63fb.mH"
head2j="hww-4.63fb-cuts.mH"
tail="_shape.txt"
masses="110 115 120 130 140 150 160 170 180 190 200 250 300 350 400 450 500 550 600"
for mass in $masses
do

	for jet in 0j 1j
	do
		echo $mass $jet 
		if [ -e $head$mass".of_"$jet$tail ] && [ -e $head$mass".sf_"$jet$tail ] 
		then
			echo combining $mass $jet datacards 
			combineCards.py  "of_"$jet"="$head$mass".of_"$jet$tail  "sf_"$jet"="$head$mass".sf_"$jet$tail > $head$mass".comb_"$jet$tail 
		fi
	done

	if [ -e $head$mass".of_0j"$tail ] && [ -e $head$mass".sf_0j"$tail ] && [ -e $head$mass".of_1j"$tail ] && [ -e $head$mass".sf_1j"$tail ]
	then
		echo "Combining the 0j and 1j shape cards for $mass"
		combineCards.py  "of_0j="$head$mass".of_0j"$tail  "sf_0j="$head$mass".sf_0j"$tail "of_1j="$head$mass".of_1j"$tail  "sf_1j="$head$mass".sf_1j"$tail > $head$mass".comb"$tail
	fi

	if [ -e $head$mass".of_0j"$tail ] && [ -e $head$mass".sf_0j"$tail ] && [ -e $head$mass".of_1j"$tail ] && [ -e $head$mass".sf_1j"$tail ] && [ -e $head2j$mass".comb2j.txt" ]
	then
		echo "Combining 0j 1j shape and 2j cut"
		combineCards.py HWW_0j=$head$mass".comb_0j"$tail HWW_1j=$head$mass".comb_1j"$tail HWW_2j=$head2j$mass.comb2j.txt > $head$mass.allcomb_shape.txt
	fi

done


