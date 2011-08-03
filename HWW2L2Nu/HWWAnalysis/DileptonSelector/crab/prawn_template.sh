#!/bin/bash
#$ -N $jobName 
#$ -q $queue
#$ -cwd
#$ -o $stdOutPath
#$ -e $stdErrPath
#source ~/.bashrc

# cmssw interface
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc5_amd64_gcc434

# CMSSW environment
cd $workingDir
eval `scramv1 ru -sh`
# DCAP environment (override CMSSW loaded libraries)
source $HOME/bin/rc/dcap.sh

# cd $workingDir
echo $PWD
cmsRun $optArgs print inputFiles_load=$inputFile outputFile=$outputFile maxEvents=$nEvents skipEvents=$firstEvent

# parameters provided by the framework:
# $$sessionName  = $sessionName
# $$queue        = $queue
# $$jobName      = $jobName
# $$inputFile    = $inputFile
# $$outputFile   = $outputFile
# $$firstEvent   = $firstEvent
# $$eventsPerJob = $eventsPerJob
# $$nEvents      = $nEvents
# $$optArgs      = $optArgs
