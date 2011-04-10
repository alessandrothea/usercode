# bin/runHWW.exe config/TestAnalysis.config -UserAnalyzer.nEvents 1


bkg_dy=( DYEE10 DYEE20 DYuu10 DYuu20 DYtt10 DYtt20 )
bkg_top=( TTJets TT T2BLNu-t T2BLNu-s T2BLNu-tW )
bkg_dibos=( VVJets WW WZ ZZ )
bkg_bos=( PhV W2ENu W2MuNu WJets )

background=( ${bkg_dy[@]} ${bkg_top[@]} ${bkg_dibos[@]} ${bkg_bos[@]}  )
higgs=( H160 )
data2010=( El2010B El2010A Mu2010A Mu2010B )
samples=( "${data2010[@]}" ) 
# samples=( "${higgs[@]}" ) 
# samples=( "${bkg_dibos[@]}" ) 
# samples=( "${background[@]}" "${higgs[@]}" "${data2010[@]}" )
samples=( Mu2010B )
 
echo "Running on:"
echo "   ${samples[@]}"
for sample in ${samples[@]}
do
#bin/runHWW.exe config/TestAnalysis.config -UserAnalyzer.inputFile ../nTuples/H160.root -UserAnalyzer.outputFile output/hww_H160.root
    cmd="bin/runHWW.exe config/TestAnalysis.config -UserAnalyzer.inputFile ../nTuples/${sample}.root -UserAnalyzer.outputFile output/hww_${sample}.root"
    echo $cmd
    $cmd
done

