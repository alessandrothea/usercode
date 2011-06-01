nJobs=25
csvFile="$HOME/higgsWW/samples/R42X_S1_V00_S2_V00_S3_V00_ReRecoMay10.csv"
optArgs="useLumi=$HOME/higgsWW/lumi/ReRecoMay10/currentLumi.json"

crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_template.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 90 -a "$optArgs dataType=SingleMu" -g 2011:ReRecoMay10:$CMSSW_VERSION:Spring11:data:SingleMu
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_template.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 91 -a "$optArgs dataType=DoubleMu" -g 2011:ReRecoMay10:$CMSSW_VERSION:Spring11:data:DoubleMu 
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_template.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 92 -a "$optArgs dataType=DoubleEl" -g 2011:ReRecoMay10:$CMSSW_VERSION:Spring11:data:DoubleEl 
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_template.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 93 -a "$optArgs dataType=MuEg"     -g 2011:ReRecoMay10:$CMSSW_VERSION:Spring11:data:MuEg 
pwn_Update.py -n -g ReRecoMay10 queue=short.q,all.q
