#!/usr/bin/env python

import os.path
import os
import sys
import optparse



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

# data2011=[
#         'id090.SingleMu2011AReRecoMay10',
#         'id091.DoubleMu2011AReRecoMay10',
#         'id092.DoubleElectron2011AReRecoMay10',
#         'id093.MuEG2011AReRecoMay10',
#         ]

background = []
background.extend(bkg_dy)
background.extend(bkg_top)
background.extend(bkg_dibos)

samples = []
samples.extend(background)
samples.extend(higgs)
samples.extend(data2011)

# samples = data2011
# samples = []

masses = [120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 250, 300, 350, 400, 450, 500, 550, 600]
masses = [ 160 ]
lumi=146.1
#lumi=168.9

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)


(opt, args) = parser.parse_args()

spring11Dir=os.getenv('HOME')+'/higgsWW/Spring11'
workdir=os.getenv('CMSSW_BASE')+'/src/HWWAnalysis/CutBasedAnalyzer'
print 'Working in',workdir
os.chdir(workdir)

skimPath=spring11Dir+'/skimmed'
for mass in masses:
    ntuplePath=spring11Dir+'/ntuples/h'+str(mass)
    finalPath=spring11Dir+'/final/h'+str(mass)

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
    if not os.path.exists(ntuplePath+'/hww_Data2011.root')  or len(set(samples).intersection(set(data2011))) != 0:
        toMerge=' '.join([ntuplePath+'/hww_'+d+'.root' for d in data2011])
        merged = ntuplePath+'/hww_Data2011.root'
        cmd = 'hadd -f '+merged+' '+toMerge
        print cmd
        code = os.system(cmd)

    print 'Making stack plots'  
    cmds = []
    cmds.append(
        'makePlots.py --luminosity='+str(lumi)+' --path='+ntuplePath+' --optVars="higgsMass='+str(mass)+'" -p macros/plots/hww_yield.cfg  -s macros/samples/hww_data11.cfg -o '+finalPath+'/h'+str(mass)+'_yield.root'
    )
    cmds.append(
        'makePlots.py --luminosity='+str(lumi)+' --path='+ntuplePath+' --optVars="higgsMass='+str(mass)+'" -p macros/plots/hww_dileptons.cfg  -s macros/samples/hww_data11_vars.cfg -o '+finalPath+'/h'+str(mass)+'_dileptons.root'
    )
    cmds.append(
        'makePlots.py --luminosity='+str(lumi)+' --path='+ntuplePath+' --optVars="higgsMass='+str(mass)+'" -p macros/plots/hww_cuts.cfg  -s macros/samples/hww_data11_vars.cfg -o '+finalPath+'/h'+str(mass)+'_cuts.root'
    )
    cmds.append(
        'makePlots.py --luminosity='+str(lumi)+' --path='+ntuplePath+' --optVars="higgsMass='+str(mass)+'" -p macros/plots/hww_extra.cfg  -s macros/samples/hww_data11.cfg -o '+finalPath+'/h'+str(mass)+'_extra.root'
    )

    for cmd in cmds:
        print cmd
        os.system(cmd)

