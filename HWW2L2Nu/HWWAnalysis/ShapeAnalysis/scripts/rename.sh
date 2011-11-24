#!/bin/bash

for jet in 0 1
do 
	
	for chan in of sf 
	do

		rename "_"$jet"jet_mllmtPreSel_"$chan "."$chan"_"$jet"j_shape" histo*root

	done

done

rename 'histo_H' 'hww-2.13fb.mH' histo*root
