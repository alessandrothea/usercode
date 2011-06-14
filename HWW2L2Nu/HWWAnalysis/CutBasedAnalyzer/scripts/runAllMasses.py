#!/usr/bin/env python

import os.path
import os
import sys
import optparse

def sumData(samples,data,path,label):
    newFile = path+'/step3_'+label+'.root' 
    if not os.path.exists( newFile )  or len(set(samples).intersection(set(data))) != 0:
        toMerge=' '.join([path+'/step3_'+d+'.root' for d in data])
        cmd = 'hadd -f '+newFile+' '+toMerge
        print cmd
        code = os.system(cmd)
        if code != 0:
            raise RuntimeError('hadd returned code '+str(code))



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

data2011PromptReco=[
        'id074.SingleMuon2011A',
        'id075.DoubleElectron2011A',
        'id076.DoubleMuon2011A',
        'id077.MuEG2011A',
        'id079.SingleMuon2011Av2',
        'id080.DoubleElectron2011Av2',
        'id081.DoubleMuon2011Av2',
        'id082.MuEG2011Av2',
        ]

data2011ReReco=[
         'id090.SingleMu2011AReRecoMay10',
         'id091.DoubleMu2011AReRecoMay10',
         'id092.DoubleElectron2011AReRecoMay10',
         'id093.MuEG2011AReRecoMay10',
         ]

data2011 = data2011PromptReco

background = []
background.extend(bkg_dy)
background.extend(bkg_top)
background.extend(bkg_dibos)

samples = []
samples.extend(background)
samples.extend(higgs)
# samples.extend(data2011)

# samples = []
samples.extend(data2011ReReco)
samples.extend(data2011PromptReco)
# samples = []

masses = [120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 250, 300, 350, 400, 450, 500, 550, 600]
masses = [ 160 ]
# lumi=133.5
# lumi=146.1
lumi=187.6

usage = 'usage: %prog config.py'
parser = optparse.OptionParser(usage)

parser.add_option('--noRunHWW', dest='runHWW', help='don\'t run step3', action='store_false', default=True )
parser.add_option('--noHadd', dest='hadd', help='don\'t run hadd', action='store_false', default=True )
parser.add_option('--noMakePlots', dest='makePlots', help='don\'t run makePlots', action='store_false', default=True )

(opt, args) = parser.parse_args()


spring11Dir=os.getenv('HOME')+'/higgsWW/Spring11'
workdir=os.getenv('CMSSW_BASE')+'/src/HWWAnalysis/CutBasedAnalyzer'
print 'Working in',workdir
os.chdir(workdir)

skimPath=spring11Dir+'/skimmed'
for mass in masses:
    ntuplePath=spring11Dir+'/step3/h'+str(mass)
    finalPath=spring11Dir+'/final/h'+str(mass)

    os.system('mkdir -p %s' % ntuplePath)
    print 'Running on:'
    print ' -',','.join(samples)

    if opt.runHWW:
        for sample in samples:
            inSample = skimPath+'/'+sample+'.root'
            outSample = ntuplePath+'/step3_'+sample+'.root'
            cmd = 'runHWW.exe test/analysisHWW.config -UserAnalyzer.inputFile '+inSample+' -UserAnalyzer.outputFile '+outSample 
            print cmd
            code = os.system(cmd)
            if code != 0:
                print 'Cazzarola'
                sys.exit(code)

    if opt.hadd:
        sumData(samples,data2011PromptReco,ntuplePath,'Data2011PromptReco')
        sumData(samples,data2011ReReco,ntuplePath,'Data2011ReReco')

    dataTags = ['Data2011PromptReco','Data2011ReReco']
#     dataTags = ['Data2011PromptReco']
    for tag in dataTags:
        if not os.path.exists(ntuplePath+'/step3_'+tag+'.root'):
            print ntuplePath+'/step3_'+tag+'.root  not found'
            continue

    if opt.makePlots:
        print 'Making stack plots for '+tag  
        optVars = 'higgsMass='+str(mass)+' dataTag='+tag+ ' prefix="step3_"'
        cmds = []
        cmds.append(
            'makePlots.py --luminosity='+str(lumi)+' --path='+ntuplePath+' --optVars="'+optVars+'" -p macros/plots/hww_yield.cfg  -s macros/samples/hww_data11.cfg -o '+finalPath+'/h'+str(mass)+'_'+tag+'_yield.root'
        )
        cmds.append(
            'makePlots.py --luminosity='+str(lumi)+' --path='+ntuplePath+' --optVars="'+optVars+'" -p macros/plots/hww_dileptons.cfg  -s macros/samples/hww_data11_vars.cfg -o '+finalPath+'/h'+str(mass)+'_'+tag+'_dileptons.root'
        )
        cmds.append(
            'makePlots.py --luminosity='+str(lumi)+' --path='+ntuplePath+' --optVars="'+optVars+'" -p macros/plots/hww_cuts.cfg  -s macros/samples/hww_data11_vars.cfg -o '+finalPath+'/h'+str(mass)+'_'+tag+'_cuts.root'
        )
        cmds.append(
            'makePlots.py --luminosity='+str(lumi)+' --path='+ntuplePath+' --optVars="'+optVars+'" -p macros/plots/hww_extra.cfg  -s macros/samples/hww_data11.cfg -o '+finalPath+'/h'+str(mass)+'_'+tag+'_extra.root'
        )

        for cmd in cmds:
            print cmd
            os.system(cmd)

