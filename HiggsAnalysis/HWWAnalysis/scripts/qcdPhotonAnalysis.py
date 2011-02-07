#!/bin/env python

from musella.Tools.myopt import options

from sys import argv
import os
import sys
import json

def list2vec(list,type):
    v = std.vector(type)()
    for l in list: v.push_back(l)
    return v

# analyzer options
args = [
      "-optimize", "false",
##      "-ptbins",   "0.,5.,10.,20.,30.,50.,80.,120.,170.,230.,300.",
##      "-ptbins",    "0.,5.,10.,20.,30.,50.,80.,120.,180.,240.,300.",
##      "-ptbins",    "0.,5.,10.,21.,23.,26.,31.,35.,40.,45.,50.,60.,100.,300.",
      "-ptbins", "0.,5.,10.,21.,23.,26.,30.,35.,40.,45.,50.,60.,85.,120.,300.",
##      "-ptbins",    "0.,5.,10.,21.,26.,31.,40.,50.,60.,100.,300.",
      "-maxruns",   "0,0,0,143962,143962",
      ## "-maxruns",   "0,0,0,143962,143962",
##      "-etaregs",  "0,0.9,1.479,2.5",
##      "-etaregs",  "0,1.45,1.7,2.5",
      "-etaregs",  "0,1.45,1.55,2.5",
      "-etabins",
      "-3.1, -2.9, -2.7, -2.5, -2.3, -2.1, -1.9, -1.7, -1.5, -1.3, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1,"
      " 0.1,  0.3,  0.5,  0.7,  0.9,  1.1,  1.3,  1.5,  1.7,  1.9,  2.1,  2.3,  2.5,  2.7,  2.9,  3.1",
      "-maxpho",   "999",
      "-opt_iter_eff", "0.95",

      "-escale", "1.", 
      
      "-templateEB","sigmaIetaIeta",
      ## "-templateEB","etaWidth",
      "-templatebinsEB",
      "0.0005, 0.0010, 0.0015, 0.0020, 0.0025, 0.0030, 0.0035, 0.0040, 0.0045,"
      "0.0050, 0.0055, 0.0060, 0.0065, 0.0070, 0.0075, 0.0080, 0.0085, 0.0090, 0.0095,"
      "0.0100, 0.0105, 0.0110, 0.0115, 0.0120, 0.0125, 0.0130, 0.0135, 0.0140, 0.0145,"
      "0.0150, 0.0155, 0.0160, 0.0165, 0.0170, 0.0175, 0.0180, 0.0185, 0.0190, 0.0195,"
      "0.0200, 0.0205, 0.0210, 0.0215, 0.0220, 0.0225, 0.0230, 0.0235, 0.0240, 0.0245,"
      "0.0250, 0.0255, 0.0260, 0.0265, 0.0270, 0.0275, 0.0280, 0.0285, 0.0290, 0.0295,"
      "0.0300, 0.0305",
      

      ## "-templateEE","abs(ESRatio)",
      ## "-templatebinsEE",
      ## "0.0000, 0.0167, 0.0335, 0.0502, 0.0670, 0.0837, 0.1005, 0.1172, 0.1340, 0.1507,"
      ## "0.1675, 0.1842, 0.2010, 0.2177, 0.2345, 0.2512, 0.2680, 0.2847, 0.3015, 0.3182,"
      ## "0.3350, 0.3517, 0.3685, 0.3852, 0.4020, 0.4187, 0.4355, 0.4522, 0.4690, 0.4857,"
      ## "0.5025, 0.5192, 0.5360, 0.5527, 0.5695, 0.5862, 0.6030, 0.6197, 0.6365, 0.6532,"
      ## "0.6700, 0.6867, 0.7035, 0.7202, 0.7370, 0.7537, 0.7705, 0.7872, 0.8040, 0.8207,"
      ## "0.8375, 0.8542, 0.8710, 0.8877, 0.9045, 0.9212, 0.9380, 0.9547, 0.9715, 0.9882,"
      ## "1.0050",
      
      "-templateEE","sigmaIetaIeta",
      ## "-templateEE","etaWidth",
      "-templatebinsEE",
      "0.0005, 0.0020, 0.0035, 0.0050, 0.0065, 0.0080, 0.0095, 0.0110, 0.0125, 0.0140,"
      "0.0155, 0.0170, 0.0185, 0.0200, 0.0215, 0.0230, 0.0245, 0.0260, 0.0275, 0.0290,"
      "0.0305, 0.0320, 0.0335, 0.0350, 0.0365, 0.0380, 0.0395, 0.0410, 0.0425, 0.0440,"
      "0.0455, 0.0470, 0.0485, 0.0500, 0.0515, 0.0530, 0.0545, 0.0560, 0.0575, 0.0590,"
      "0.0605, 0.0620, 0.0635, 0.0650, 0.0665, 0.0680, 0.0695, 0.0710, 0.0725, 0.0740,"
      "0.0755, 0.0770, 0.0785, 0.0800, 0.0815, 0.0830, 0.0845, 0.0860, 0.0875, 0.0890,"
      "0.0905",
      
      "-autoPlots",
      "run:(2600:132399.5:134999.5):Run number; run; events,"
      "vtxX:(200:-1.01:0.99):Vertex X; vtx_{x} [cm]; Events/0.01 cm,"
      "vtxY:(200:-1.01:0.99):Vertex Y; vtx_{y} [cm]; Events/0.01 cm,"
      "vtxZ:(150:-15.2:14.8):Vertex Z; vtx_{z} [cm]; Events/0.2 cm,"
      "metEt:(200:0:200):MET; MET [GeV]; Events/GeV,"
      "metEt/pt[0]:(100:0:10):MET/leading #gamma p_{T}; MET/Leading #gamma p_{T}; Events/0.1,"
      "metCorSumEt:(200:0:200):sumE_{T}; sumE_{T}  [GeV]; Events/GeV,"
      "metPx:(100:-200:200):METx; MET_{x} [GeV]; Events/ 2 GeV,"
      "metPy:(100:-200:200):METy; MET_{y} [GeV]; Events/ 2 GeV,",
      
      "-nMinusOnePlots",
      "rawEnergy*sin(2*atan(exp(-scEta))):(40:0:200):Photon raw E_{T} ; raw E_{T} [GeV]; #gamma candidates/5GeV,"
      "scEta:(31:-3.1:3.1):Photon #eta; #eta_{SC}; #gamma candidates/0.2,"
      "scPhi:(32:-3.2:3.2):Photon #phi; #phi_{SC}; #gamma candidates/0.2,"
      "pt:(40:0:200):Photon E_{T}; E_{T} [GeV]; #gamma candidates/5GeV,"
      "eta:(31:-3.1:3.1):Photon #eta; #eta; #gamma candidates/0.2,"
      "phi:(32:-3.2:3.2):Photon #phi; #phi; #gamma candidates/0.2,"
      "scSize:(200:0:200):Number of crystals; Num of crystals; N Photons," 
      "clustersSize:(20:0:20):Number of basic clusters; Num of basic clusters; N Photons,"
      "eMax/energy:(60:0:1.2):Photon R19; E_{Max}/E; #gamma candidates/0.02,"
      "e2nd/energy:(60:0:1.2):Photon R19; E_{2}/E  ; #gamma candidates/0.02,"
      "e1x5/e5x5:(60:0:1.2):Photon E_{1x5}/E_{5x5}; E_{1x5}/E_{5x5}; #gamma candidates/0.02,"
      "e2x5/e5x5:(60:0:1.2):Photon E_{2x5}/E_{5x5}; E_{2x5}/E_{5x5}; #gamma candidates/0.02,"
      "sigmaIetaIeta:(100:0:0.1):Photon #sigma_{i#eta i#eta}; #sigma_{i#eta i#eta}; #gamma candidates/0.01,"
      "abs(ESRatio):(50:0:1.):Photon R_{ES}; R_{ES}; #gamma candidates/0.02,"
      "phiWidth/etaWidth:(50:0:10):Photon #phi width / #eta width; #phi witdh/#eta width; #gamma candidates/0.2,"
      "etaWidth:(60:0:0.1):Photon #eta width; #eta width; #gamma candidates/0.0017,"
      "phiWidth:(60:0:0.3):Photon #phi width; #phi width; #gamma candidates/0.0.005,"
      "eMax/e3x3:(60:0:1.2):Photon R19; E_{Max}/E_{3x3}; #gamma candidates/0.02,"
      "r9:(60:0:1.2):Photon E_{3x3}/E ; E_{3x3}/E_{#gamma}; #gamma candidates/0.02,"
      "hasPixelSeed:(2:0:2):Pixel seed match ; Pixel seed match; N Photons,"
      "ecalRecHitSumEtConeDR04+hcalTowerSumEtConeDR04+trkSumPtHollowConeDR04:(62:-1:30.):Total Isolation ; #Sigma E_{T}^{calo}/c + p_{T}^{track} Isolation #Delta R=0.4 [GeV/c]; #gamma candidates/0.5 GeV,"
      "(ecalRecHitSumEtConeDR04+hcalTowerSumEtConeDR04+trkSumPtHollowConeDR04):(24:-1:11.):Total Isolation ; #Sigma E_{T}^{calo}/c + p_{T}^{track} Isolation #Delta R=0.4 [GeV/c]; #gamma candidates/0.5 GeV,"
      "ecalRecHitSumEtConeDR04:(24:-1:11.):ECAL Isolation ; ECAL #Sigma E_{T} Isolation #Delta R=0.4 [GeV]; #gamma candidates/0.5 GeV,"
      "hcalTowerSumEtConeDR04:(24:-1:11.):HCAL Isolation ; HCAL #Sigma E_{T} Isolation #Delta R=0.4 [GeV]; #gamma candidates/0.5 GeV,"
      "trkSumPtHollowConeDR04:(24:-1:11.):Track Isolation ; Track #Sigma p_{T} Isolation #Delta R=0.4 [GeV/c]; #gamma candidates/0.5 GeV/c,"
      "hadronicOverEm:(40:0:0.5):Track Isolation ; H/E; #gamma candidates/0.0125,"
      "sqrt(pt[]*metEt*2*(1-cos(phi[]-atan(metPy/metPx)))):(200:0:200):Photon-MET transverse mass;M_{T}; Entries/GeV,"
      ]

goodruns = [ ]

# python options   
o = options( [
    ("prescale",0,"prescale"),
    ("keep","1",""),
    ("refLumi",1./6.81141,""),
    ("isdata",False,""),
    ("noweight",False,""),
    ("source","mpantuples",""),
    ("maxPtHat",1.e+10,""),
    ("selection",
     "!vtxIsFake && vtxNdof > 4 && abs(vtxZ) <= 18:vtx,"
     ##"! (TTBit[36] || TTBit[37] || TTBit[38] || TTBit[39]):halo veto,"
     ,""),
    ("selectionData",
     "TTBit0:bptx,"
     "1:HLT_Photon10_OR_15_OR_20_OR_25_OR_30,"
     ## "HLT_Photon10_L1R || HLT_Photon15_L1R || HLT_Photon15_Cleaned_L1R || HLT_Photon20_Cleaned_L1R || ((HLTBit[89] || HLTBit[90] ) && run>=144010):HLT_Photon10_OR_15_OR_20_OR_25_OR_30,"
     ,""),
    ("selectionMc","HLT_Photon15_L1R:HLT_Photon15_L1R",""),
    ("maxEvent",-1,""),
    ("mpa",True,""),
    ("tracks",False,""),
    ("outfile","",""),
    ("goodlumis","",""),
    ("datasets","",""),
    ("splitbins",False,""),
    ("dsinname",False,"")
    ]
             )

# parse options
o.parse(args)
o.parse(argv)

argv.pop(0)
for a in argv : args.append(a)

print "------------------------------------------------------------"
o.dump()

# make sure ROOT doesn't parse the command line options
sys.argv = []

# load libraries
from ROOT import gSystem, TFile
TFile.Open(o.outfile,"recreate").Close()

# prescale
keep = []
if( o.prescale != 0 ):
    keep = [ int(i) for i in o.keep.split(',') ]
    o.refLumi *= float(o.prescale)/float(len(keep))

# load trees
import mpantuples
import pkgutil
i = pkgutil.ImpImporter(".")
l = i.find_module(o.source)
source = l.load_module(o.source)
mpantuples.maxPtHat=o.maxPtHat
datasets = source.datasets
alldatasets = datasets
source.loadTrees(o.refLumi,datasets,o.splitbins)

# split jobs per dataset
merge = False
if o.datasets != "":
    ds = [ datasets[int(i)] for i in o.datasets.strip().split(',') ]
    datasets = ds

    if o.dsinname: 
        target = str(o.outfile)
        o.outfile = o.outfile.split('.')[0]
        for d in datasets: o.outfile += "_"+str(d.GetTitle()).replace('#','').replace(" ","_")
        o.outfile += ".root"

# unweight if required
if o.noweight:
    for d in datasets:
        d.SetWeight(1.,"global")

# synchronize options
for i in range(0,len(args)):
    if( args[i] == "-outfile" ): args[i+1] = o.outfile

gSystem.Load('${CMSSW_BASE}/lib/${SCRAM_ARCH}/libmusellaTools.so')
gSystem.Load('${CMSSW_BASE}/lib/${SCRAM_ARCH}/libmusellaQCDPhotons.so')

from ROOT import NtupleAnalyzer, QcdPhotonAnalyzer, QcdPhotonEvent, std

# instantiate Event class
ev = QcdPhotonEvent(0,o.tracks,o.mpa,o.isdata)
if( o.prescale != 0 ):
    ev.prescale(o.prescale,list2vec(keep,'int'))

# instantiate analyzer
analyzer = QcdPhotonAnalyzer(list2vec(args,'string'))
analyzer.config(str(o))

# pass event selection to analyzer
print o.selectionData
for sel in o.selectionData.split(","):
    if sel != "":
        s = [ str(x) for x in sel.split(":") ]
        analyzer.selectionData(s[0],s[1])

for sel in o.selectionMc.split(","):
    if sel != "":
        s = [ str(x) for x in sel.split(":") ]
        analyzer.selectionMc(s[0],s[1])

for sel in o.selection.split(","):
    if sel != "":
        s = [ str(x) for x in sel.split(":") ]
        analyzer.selection(s[0],s[1])

# run analysis
NtupleAnalyzer.analyze(analyzer,list2vec(datasets,'Dataset *'),ev,o.maxEvent)

# fix crash in TChain destructor when using TNetFiles 
for d in alldatasets : d.Reset()

