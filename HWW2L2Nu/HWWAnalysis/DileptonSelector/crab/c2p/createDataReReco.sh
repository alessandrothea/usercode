nJobs=25
csvFile="$HOME/higgsWW/samples/R42X_S1_V04_S2_V00_S3_V00.csv"
optArgs="summary=1 useLumi=$HOME/higgsWW/lumi/currentLumi.json"

crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 90 -a "$optArgs dataPath=singleMu" -g 2011:ReRecoMay10:42X:data:singleMu
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 91 -a "$optArgs dataPath=doubleMu" -g 2011:ReRecoMay10:42X:data:doubleMu 
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 92 -a "$optArgs dataPath=doubleEl" -g 2011:ReRecoMay10:42X:data:doubleEl 
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 93 -a "$optArgs dataPath=muEG"     -g 2011:ReRecoMay10:42X:data:muEG 
pwn_Update.py -n -g ReRecoMay10 queue=short.q,all.q
