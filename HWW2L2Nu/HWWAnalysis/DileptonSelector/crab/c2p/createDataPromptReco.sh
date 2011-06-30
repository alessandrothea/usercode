nJobs=40
csvFile="$HOME/higgsWW/samples/R42X_S1_V04_S2_V00_S3_V00.csv"
optArgs="useLumi=$HOME/higgsWW/lumi/currentLumi.json"

crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 84 -a "$optArgs triggerFilter=singleMu" -g 2011:PromptRecov4:42X:data:singleMu
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 85 -a "$optArgs triggerFilter=doubleEl" -g 2011:PromptRecov4:42X:data:doubleEl 
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 86 -a "$optArgs triggerFilter=doubleMu" -g 2011:PromptRecov4:42X:data:doubleMu 
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_step2.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 87 -a "$optArgs triggerFilter=muEg"     -g 2011:PromptRecov4:42X:data:muEg 
pwn_Update.py -n -g PromptRecov4:data queue=short.q,all.q
