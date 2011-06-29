nJobs=10
csvFile="$HOME/higgsWW/samples/R414_S1_V07_S2_V04_S3_V00.csv"
optArgs="useLumi=$HOME/higgsWW/lumi/currentLumi.json"

crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_template.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 74,79 -a "$optArgs dataType=SingleMu" -g 2011:PromptReco:$CMSSW_VERSION:Spring11:data:SingleMu
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_template.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 75,80 -a "$optArgs dataType=DoubleEl" -g 2011:PromptReco:$CMSSW_VERSION:Spring11:data:DoubleEl 
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_template.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 76,81 -a "$optArgs dataType=DoubleMu" -g 2011:PromptReco:$CMSSW_VERSION:Spring11:data:DoubleMu 
crab2prawn.py -c $csvFile -j $nJobs -t ../prawn_template.sh -o /shome/thea/higgsWW/Spring11/jobs -w ../../ -i 77,82 -a "$optArgs dataType=MuEg"     -g 2011:PromptReco:$CMSSW_VERSION:Spring11:data:MuEg 
pwn_Update.py -n -g Spring11:data queue=short.q,all.q
