nJobs=15

csvFile="$HOME/higgsWW/samples/R42X_S1_V04_S2_V00_S3_V00.csv"

 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 1-25,27-50    -g 2011:Spring11:bkg
 crab2prawn.py -c $csvFile -j 100    -t ../prawn_step2.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 26            -g 2011:Spring11:bkg
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 101120-101600 -g 2011:Spring11:ggH:2l2v
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 102120-102600 -g 2011:Spring11:ggH:lvtau
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 103120-103600 -g 2011:Spring11:ggH:tautau
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 104120-104600 -g 2011:Spring11:vbf:2l2v
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 105120-105600 -g 2011:Spring11:vbf:lvtau
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 106120-106600 -g 2011:Spring11:vbf:tautau

# # set custom queues
pwn_Update.py -n -g Spring11:bkg queue=short.q,all.q
# pwn_Update.py -n -s WJetsToLNuMad queue=all.q

#add the 
masses=( 115 120 130 140 150 160 170 180 190 200 210 220 230 250 300 350 400 450 500 550 600 )
for mass in "${masses[@]}"
do
    pwn_Update.py -n -s id101${mass}.ggToH${mass}toWWto2L2Nu optArgs="higgsPtWeights=${mass}" 
    pwn_Update.py -n -s id102${mass}.ggToH${mass}toWWtoLNuTauNu optArgs="higgsPtWeights=${mass}" 
    pwn_Update.py -n -s id103${mass}.ggToH${mass}toWWto2Tau2Nu optArgs="higgsPtWeights=${mass}" 
done
