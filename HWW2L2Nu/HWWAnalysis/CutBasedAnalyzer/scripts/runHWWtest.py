#!/usr/bin/env python

import os.path
import os
import sys



bkg_dy=[
'id017B.DY10toElElZ2',
'id018B.DY10toMuMuZ2',
'id019.DY10toTauTau',
'id003.DYtoElEl',
'id004.DYtoMuMu',
'id005.DYtoTauTau',
]

bkg_top=[
'id010.sTtoBLNu',
'id011.tTtoBLNu',
'id012.tWTtoBLNu',
'id023.TTJetsMad',
]

bkg_dibos=[
'id022.GluGluToWWTo4L',
'id014.VVJetsTo4L',
'id021.PhotonVJets',
'id026.WJetsToLNuMad',
'id002.ZZtoAny',
'id001.WZtoAny',
]

higgs=[
'id101160.ggToH160toWWto2L2Nu',
]

data2011=[
'id074.SingleMuon2011A',
'id075.DoubleElectron2011A',
'id076.DoubleMuon2011A',
'id077.MuEG2011A',

'id079.SingleMuon2011Av2',
'id080.DoubleElectron2011Av2',
'id081.DoubleMuon2011Av2',
'id082.MuEG2011Av2',
]

background = []
background.extend(bkg_dy)
background.extend(bkg_top)
background.extend(bkg_dibos)

samples = []
samples.extend(background)
samples.extend(higgs)
samples.extend(data2011)

samples = ['id023.TTJetsMad','id101160.ggToH160toWWto2L2Nu']

spring11Dir=os.getenv('HOME')+'/higgsWW/Spring11'
workdir=os.getenv('CMSSW_BASE')+'/src/HWWAnalysis/CutBasedAnalyzer'
print 'Working in',workdir
os.chdir(workdir)

skimPath=spring11Dir+'/skimmed'
ntuplePath=spring11Dir+'/ntuples/test'

os.system('mkdir -p %s' % ntuplePath)
print 'Running on:'
print ' -',','.join(samples)

for sample in samples:
    inSample = skimPath+'/'+sample+'.root'
    outSample = ntuplePath+'/hww_'+sample+'.root'
    cmd = 'runHWW.exe test/analysisHWW.config -UserAnalyzer.inputFile '+inSample+' -UserAnalyzer.outputFile '+outSample 
    print cmd
    code = os.system(cmd)
    if code != 0:
        print 'Cazzarola'
        sys.exit(code)

#check if I have processed some data
if len(set(samples).intersection(set(data2011))) != 0:
    toMerge=' '.join(data2011)
    cmd = 'hadd -f hww_Data2011 %s' % toMerge
    print cmd



# for sample in ${samples[@]}
# do
#     cmd='runHWW.exe test/analysisHWW.config -UserAnalyzer.inputFile $skimPath/${sample}.root -UserAnalyzer.outputFile $ntuplePath/hww_${sample}.root'
#     echo $cmd
#     $cmd
#     continue
#     if (( $? != 0 )); then
#         exit $?
#     fi
# done

# #final touch
# cd $ntuplePath
# for s in '${data2011[@]}'
# do
#     toMerge='$toMerge hww_$s.root'
# done
# echo Merging $toMerge
# hadd -f hww_Data2011.root $toMerge

