#!/bin/bash
# set -x



tail="_shape.txt"
cwd=$PWD
# masses="110 115 120 130 140 150 160 170 180 190 200 250 300 350 400 450 500 550 600"

function usage() {
	echo "$( basename $0) -p <prefix>"
}

prefix=
while getopts "hp:" OPTION
do
    case $OPTION in
        h)
            usage
            exit 1
            ;;
        p)
            prefix=$OPTARG
            ;;
    esac
done

echo `shape-config.py`
eval $(shape-config.py)

if [[ $prefix ]]; then
    echo "Running in $prefix"
    cd $prefix
fi

echo "Lumi $lumi"
head="hww-${lumi}fb.mH"
head2j="hww-${lumi}fb.mH"
hline=$(printf '%.0s-' {1..80})
combCmd='combineCards.py -S'
echo $PWD
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
			$combCmd "of_"$jet"="$head$mass".of_"$jet$tail  "sf_"$jet"="$head$mass".sf_"$jet$tail > $head$mass".comb_"$jet$tail 
		fi
	done

	for fl in of sf
	do
		file0="${head}${mass}.${fl}_0j${tail}"
		file1="${head}${mass}.${fl}_1j${tail}"
		cmb="${head}${mass}.comb_${fl}${tail}"

        echo $hline
		echo " Combining cards $mass $fl ( ${file0} + ${file1} )"
        echo $hline
		if [ -e "${file0}" ] && [ -e "${file1}" ] 
		then
			echo " ${mass}: ${fl}_0j ${fl}_1j => comb_${fl}"
			$combCmd "${fl}_0j=${file0}"  "${fl}_1j=${file1}"  > "${cmb}"
		fi
	done

	if [ -e $head$mass".of_0j"$tail ] && [ -e $head$mass".sf_0j"$tail ] && [ -e $head$mass".of_1j"$tail ] && [ -e $head$mass".sf_1j"$tail ]
	then
		echo " $mass: sf_0j of_0j of_1j sf_1j => comb_0j1j "
		$combCmd "of_0j="$head$mass".of_0j"$tail  "sf_0j="$head$mass".sf_0j"$tail "of_1j="$head$mass".of_1j"$tail  "sf_1j="$head$mass".sf_1j"$tail > $head$mass".comb_0j1j"$tail
	fi

	if [ -e $head$mass".comb_0j"$tail ] && [ -e $head$mass".comb_1j"$tail ] && [ -e $head2j$mass".comb_2j_cb.txt" ]
	then
		echo " $mass: comb_0j comb_1j comb_2j_cb => comb_0j1j2j "
		$combCmd HWW_0j=$head$mass".comb_0j"$tail HWW_1j=$head$mass".comb_1j"$tail HWW_2j=$head2j$mass.comb_2j_cb.txt > $head$mass.comb_0j1j2j$tail
fi


done
echo "...Done"


