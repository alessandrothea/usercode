# syst='electronResolution electronScale_down electronScale_up jetEnergyScale_down jetEnergyScale_up leptonEfficiency_down leptonEfficiency_up metResolution muonScale_down muonScale_up' 
# -- v0 -- 
# for m in $masses;
# do
#     qexe.py -t mkH_nom_${m} "mkShapes2.py --noSyst -m $m"
#     for iSyst in $syst
#     do
#         qexe.py -t mkH_${iSyst}_${m} "mkShapes2.py --noNoms -m $m --doSyst $iSyst"
#     done
# done

# -- v1 --
# qexe.py -t mkH_nom_${m} "mkShapes2.py --noSyst"
# for iSyst in $syst
# do
#     qexe.py -t mkH_${iSyst}_${m} "mkShapes2.py --noNoms --doSyst $iSyst"
# done

# -- v3 -- 

HLINE=`printf '%.0s-' {1..100}`
echo $HLINE >> qexe.log
echo "  Baking " `date` >> qexe.log
echo $HLINE >> qexe.log

eval `shape-config.py`

for m in $masses;
do
    CMD="qexe.py -t mkShapes_${m} -- mkShapes.py -m $m $@"
    echo "Baking: $CMD"
    $CMD
done

watch 'tail -n 30 qexe.log; echo Remaining jobs: `qstat | wc -l`; qstat;'
