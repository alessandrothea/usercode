#!/bin/bash
#$ -N $jobName 
#$ -l s_rt=01:30:00,h_rt=04:00:00
#$ -q $queue
#$ -cwd
#$ -o $stdOutPath
#$ -e $stdErrPath
source ~/.bashrc
cd $workingDir
echo $PWD
eval `scramv1 ru -sh`
echo ./bin/selectHWW.exe  config/Test.config -Selector.inputFile=$inputFile -Selector.outputFile=$outputFile
sleep 60
echo 'good Morning!'

# parameters provided by the framework:
# $$sessionName  = $sessionName
# $$queue        = $queue
# $$jobName      = $jobName
# $$inputFile    = $inputFile
# $$outputFile   = $outputFile
# $$firstEvent   = $firstEvent
# $$eventsPerJob = $eventsPerJob
