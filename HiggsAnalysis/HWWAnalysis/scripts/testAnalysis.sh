# bin/runHWW.exe config/TestAnalysis.config -UserAnalyzer.nEvents 1

# samples=( DYEE10 DYEE20 DYuu10 DYuu20 H160 TT W2ENu W2MuNu WW WZ ZZ )
samples=( WW H160 El2010 )

for sample in ${samples[@]}
do
#bin/runHWW.exe config/TestAnalysis.config -UserAnalyzer.inputFile ../nTuples/H160.root -UserAnalyzer.outputFile output/hww_H160.root
    bin/runHWW.exe config/TestAnalysis.config -UserAnalyzer.inputFile ../nTuples/${sample}.root -UserAnalyzer.outputFile output/hww_${sample}.root
done

