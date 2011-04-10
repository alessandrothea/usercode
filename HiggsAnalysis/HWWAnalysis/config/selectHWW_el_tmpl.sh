#!/bin/bash
#$ -N $jobName 
#$ -l s_rt=01:30:00,h_rt=04:00:00
#$ -q $queue
#$ -cwd
#$ -o $stdOutPath
#$ -e $stdErrPath
#source ~/.bashrc

# cmssw interface
source $VO_CMS_SW_DIR/cmsset_default.sh

# CMSSW environment
cd ~/HWW/CMSSW_3_8_6
eval `scramv1 ru -sh`
# DCAP environment (override CMSSW loaded libraries)
source $HOME/bin/rc/dcap.sh

cd $workingDir
echo $PWD
./bin/selectHWW.exe config/selectHWW_qsub.config -HWWSelector.hltMode el -Selector.inputFile $inputFile -Selector.outputFile $outputFile -Selector.firstEvent $firstEvent -Selector.nEvents $nEvents

# parameters provided by the framework:
# $$sessionName  = $sessionName
# $$queue        = $queue
# $$jobName      = $jobName
# $$inputFile    = $inputFile
# $$outputFile   = $outputFile
# $$firstEvent   = $firstEvent
# $$eventsPerJob = $eventsPerJob
# $$nEvents      = $nEvents
