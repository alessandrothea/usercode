nJobs=15
csvFile="$HOME/higgsWW/samples/R42X_S1_V04_S2_V00_S3_V00.csv"
# optArgs=" summary=1"
optArgs="summary=1"

crab2prawn.py -c $csvFile -j $nJobs    -t ../prawn_stage2and3loose.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 29-37          -p "loose." -a "$optArgs" -g 2011:Summer11:loose:mc
crab2prawn.py -c $csvFile -j $nJobs    -t ../prawn_stage2and3loose.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 101120-101150  -p "loose." -a "$optArgs" -g 2011:Summer11:loose:mc

# # set custom queues
pwn_Update.py -n -g Summer11:loose:mc queue=short.q,all.q

crab2prawn.py -c $csvFile -j 100       -t ../prawn_stage2and3loose.sh -o /shome/thea/higgsWW/Summer11/jobs -w ../../ -i 26             -p "loose." -a "$optargs" -g 2011:Summer11:loose:mc
