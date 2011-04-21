# bin/runHWW.exe config/TestAnalysis.config -UserAnalyzer.nEvents 1

bkg_dy=( DYEE10 DYEE20 DYuu10 DYuu20 DYtt10 DYtt20 )
bkg_top=( TTJets T2BLNu-t T2BLNu-s T2BLNu-tW )
bkg_dibos=( VVJets WW WZ ZZ )
bkg_bos=( PhV W2ENu W2MuNu WJets )

background=( ${bkg_dy[@]} ${bkg_top[@]} ${bkg_dibos[@]} ${bkg_bos[@]}  )
higgs=( H160 )
# higgs2011=( H160pu )
data2010=( El2010B El2010A Mu2010A Mu2010B )
samples=( "${data2010[@]}" ) 
# samples=( "${higgs[@]}" ) 
# samples=( "${bkg_dibos[@]}" ) 
samples=( "${background[@]}" "${higgs[@]}" "${data2010[@]}" "${higgs2011[@]}" )
# samples=( "${bkg_top[@]}" )


workdir="."
outdir="$workdir/output"
echo "Running on:"
echo "   ${samples[@]}"
for sample in ${samples[@]}
do
    cmd="bin/runHWW.exe config/analysisHWW.config -UserAnalyzer.inputFile ../Ntuples/${sample}.root -UserAnalyzer.outputFile output/hww_${sample}.root"
    echo $cmd
    $cmd
    if (( $? != 0 )); then
        exit $?
    fi
done

#final touch
cd $outdir
hadd -f hww_Data2010A.root hww_El2010A.root hww_Mu2010A.root
hadd -f hww_Data2010B.root hww_El2010B.root hww_Mu2010B.root

