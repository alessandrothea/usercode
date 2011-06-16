#!/usr/bin/env python

import os.path
import os
import sys
import optparse

def sumData(samples,data,path,label):
    newFile = path+'/plot_'+label+'.root' 
    print label,set(samples).intersection(set(data)) 
    if not os.path.exists( newFile )  or len(set(samples).intersection(set(data))) != 0:
        toMerge=' '.join([path+'/plot_'+d+'.root' for d in data])
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

signals=[
'id101%(mass)d.ggToH160toWWto2L2Nu',
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
# samples.extend(higgs)
# samples.extend(data2011)

# samples = []
samples.extend(data2011ReReco)
samples.extend(data2011PromptReco)
# samples = []

masses = [120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 250, 300, 350, 400, 450, 500, 550, 600]
masses = [ 160 ]

for mass in masses:
    xxx = [ signal % { 'mass' : mass } for signal in signals ]
#     print '-'.join(xxx)
    samples.extend(xxx)

mass=160
# lumi=133.5
lumi=187.6

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)

parser.add_option('--noSimple', dest='runSimple', help='don\'t run hww', action='store_false', default=True )
parser.add_option('--noHadd', dest='hadd', help='don\'t run hadd', action='store_false', default=True )
parser.add_option('--noMakePlots', dest='makePlots', help='don\'t run makePlots', action='store_false', default=True )
 

(opt, args) = parser.parse_args()

if len(args) == 0:
    parser.error('Define the config file')
cfg = args[0] 
# use the cfg basename to define the output
(basename,ext) = os.path.splitext( os.path.basename(cfg) )

spring11Dir=os.getenv('HOME')+'/higgsWW/Spring11'
workdir=os.getenv('CMSSW_BASE')+'/src/HWWAnalysis/CutBasedAnalyzer'
print 'Working in',workdir
os.chdir(workdir)


# the ntuples don't depend on the specific cuts. We're using the 160 ones
ntuplePath = spring11Dir+'/step3/h160'
outputPath = spring11Dir+'/other'

plotPath   = outputPath+'/plots/'+basename
stackPath  = outputPath+'/stacks/'+basename

os.system('mkdir -p %s' % stackPath)
os.system('mkdir -p %s' % plotPath)
print 'Running on:'
print ' -',','.join(samples)

if opt.runSimple: 
    for sample in samples:
            
        inSample = ntuplePath+'/step3_'+sample+'.root'
        plotFile = plotPath+'/plot_'+sample+'.root'

        cmd = 'simpleCutter.exe '+cfg+' inputFiles='+inSample+' outputFile='+plotFile
        print cmd
        code = os.system(cmd)
        if code != 0:
            print 'Cazzarola'
            sys.exit(code)

if opt.hadd:    
    sumData(samples,data2011PromptReco,plotPath,'Data2011PromptReco')
    sumData(samples,data2011ReReco,plotPath,'Data2011ReReco')

if opt.makePlots:
    dataTags = ['Data2011PromptReco','Data2011ReReco']
    for tag in dataTags:
        if not os.path.exists(plotPath+'/plot_'+tag+'.root'):
            print plotPath+'/plot_'+tag+'.root  not found'
            continue

        for mass in masses:
            print 'Making stack plots for '+tag  
            optVars = 'higgsMass='+str(mass)+' dataTag='+tag+' prefix=plot_'
            cmds = []
            cmds.append(
                './scripts/makePlots.py --luminosity='+str(lumi)+' --path='+plotPath+' --optVars="'+optVars+'" -p macros/plots/all.cfg  -s macros/samples/hww_data11.cfg -o '+stackPath+'/stack_'+tag+'_all.root'
            )
            for cmd in cmds:
                print cmd
                os.system(cmd)

