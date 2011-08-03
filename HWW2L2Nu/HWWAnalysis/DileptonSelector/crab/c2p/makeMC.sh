nJobs=50
csvFile="$HOME/higgsWW/samples/R42X_S1_V04_S2_V00_S3_V00.csv"
# optArgs=" summary=1"
optArgs="test/stage2and3.py summary=true"

 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 1-2,7-25,27-50  -a "$optArgs" -p primary. -g primary:414:2011:Summer11:bkg
 crab2prawn.py -c $csvFile -j 100    -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 26              -a "$optArgs" -p primary. -g primary:414:2011:Summer11:bkg
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 101120-101600   -a "$optArgs" -p primary. -g primary:414:2011:Summer11:ggH:2l2v
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 102120-102600   -a "$optArgs" -p primary. -g primary:414:2011:Summer11:ggH:lvtau
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 103120-103600   -a "$optArgs" -p primary. -g primary:414:2011:Summer11:ggH:tautau
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 104120-104600   -a "$optArgs" -p primary. -g primary:414:2011:Summer11:vbf:2l2v
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 105120-105600   -a "$optArgs" -p primary. -g primary:414:2011:Summer11:vbf:lvtau
 crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 106120-106600   -a "$optArgs" -p primary. -g primary:414:2011:Summer11:vbf:tautau

# # set custom queues
pwn_Update.py -n -g Summer11 queue=short.q,all.q

#add the 
masses=( 115 120 130 140 150 160 170 180 190 200 210 220 230 250 300 350 400 450 500 550 600 )
for mass in "${masses[@]}"
do
    pwn_Update.py -n -s id101${mass}.ggToH${mass}toWWto2L2Nu    optArgs="higgsPtWeights=${mass}" 
    pwn_Update.py -n -s id102${mass}.ggToH${mass}toWWtoLNuTauNu optArgs="higgsPtWeights=${mass}" 
    pwn_Update.py -n -s id103${mass}.ggToH${mass}toWWto2Tau2Nu  optArgs="higgsPtWeights=${mass}" 
done
