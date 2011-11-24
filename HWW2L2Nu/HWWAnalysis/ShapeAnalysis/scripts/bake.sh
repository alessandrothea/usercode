syst='electronResolution electronScale_down electronScale_up jetEnergyScale_down jetEnergyScale_up leptonEfficiency_down leptonEfficiency_up metResolution muonScale_down muonScale_up' 
for m in $masses;
do
    qexe.py -t mkH_nom_${m} "mkShapes2.py --noSyst -m $m"
    for iSyst in $syst
    do
        qexe.py -t mkH_${iSyst}_${m} "mkShapes2.py --noNoms -m $m --doSyst $iSyst"
    done
done
# qexe.py -t mkH_nom_${m} "mkShapes2.py --noSyst"
# for iSyst in $syst
# do
#     qexe.py -t mkH_${iSyst}_${m} "mkShapes2.py --noNoms --doSyst $iSyst"
# done

watch 'tail -n 30 qexe.log; echo Remaining jobs: `qstat | wc -l`; qstat;'
