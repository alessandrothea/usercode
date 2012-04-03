#!/usr/bin/env python

## Example:
## ./applyScaleFactors.py -i H140_ll.root -o blu/bla/bli.root -t latino -a leptonEfficiency -d down

import optparse
import os
import ROOT
import numpy
from ROOT import *
import math


verbose = False
## mZ = 91.1876
to = ' -> '

def mitMuEffA(pt, eta):
    if pt <= 15.:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9819
        if abs(eta) >= 1.5 and abs(eta) <2.4:
            return 1.0153
    if 15 < pt and pt <= 20.:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9786
        if abs(eta) >= 1.5 and abs(eta) <2.4:
            return 1.0057
    if 20 < pt:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9986
        if abs(eta) >= 1.5 and abs(eta) <2.4:
            return 1.0140
    else:
        return -1

def mitMuEffB(pt, eta):
    if pt <= 15.:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9190
        if abs(eta) >= 1.5 and abs(eta) <2.4:
            return 0.9620
    if 15 < pt and pt <= 20.:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9352
        if abs(eta) >= 1.5 and abs(eta) <2.4:
            return 0.9546
    if 20 < pt:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9897
        if abs(eta) >= 1.5 and abs(eta) <2.4:
            return 0.9901
    else:
        return -1

def mitEleEffA(pt, eta):
    if pt <= 15.:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 1.0532
        if abs(eta) >= 1.5 and abs(eta) <2.5:
            return 1.0841
    if 15 < pt and pt <= 20.:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9659
        if abs(eta) >= 1.5 and abs(eta) <2.5:
            return 1.0318
    if 20 < pt:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9855
        if abs(eta) >= 1.5 and abs(eta) <2.5:
            return 1.0213
    else:
        return -1

def mitEleEffB(pt, eta):
    if pt <= 15.:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9842
        if abs(eta) >= 1.5 and abs(eta) <2.5:
            return 0.8677
    if 15 < pt and pt <= 20.:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9159
        if abs(eta) >= 1.5 and abs(eta) <2.5:
            return 0.9546
    if 20 < pt:
        if abs(eta) >= 0 and abs(eta) <1.5:
            return 0.9736
        if abs(eta) >= 1.5 and abs(eta) <2.5:
            return 1.0069
    else:
        return -1


def openTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f

def getHist(file, hist):
    h = file.Get(hist)
    if not h.__nonzero__():
        raise NameError('Histogram '+hist+' doesn\'t exist in '+str(file))
    return h




###############################################################################################
###############################################################################################
###############################################################################################


import re
from math import *
from pprint import pprint



#fits = open("/afs/cern.ch/user/g/gpetrucc/scratch0/higgs/CMSSW_4_2_7_patch2/src/WWAnalysis/AnalysisStep/test/tp_lepton_effs/fit_results.txt", "r")
fits = open("/afs/cern.ch/user/j/jueugste/latinos/fit_results.txt", "r")

triggers = []
for line in fits:
    m = re.match(r"201[01][AB]_(\d+)-(\d+)_(\w+)_(barrel|endcap|forward)\s+.*", line)
    if not m: continue
    numbers = [float(x) for x in line.split()[1:]]
    (start, end) = int(m.group(1)), int(m.group(2))
    trigname = m.group(3)
    etarange = m.group(4)
    found = False
    for (trigname2,start2,end2,pars) in triggers:
        if trigname2 == trigname and start2 == start and end2 == end:
            pars[etarange] = numbers
            found = True
            break
    if not found:
        triggers.append((trigname,start,end,{etarange:numbers}))



## Giovannis classes:

class LegEfficiency:
    def __init__(self,name,params):
        self._name    = name
        self._isMu    = ("Mu" in name)
        if self._isMu:
            self._plateau = [params['barrel'][0], params['endcap'][0], params['forward'][0]]
            self._turnon  = [params['barrel'][1], params['endcap'][1], params['forward'][1]]
            self._resol   = [params['barrel'][2], params['endcap'][2], params['forward'][2]]
            self._ptcut   = [params['barrel'][3], params['endcap'][3], params['forward'][3]]
            self._plat2   = [params['barrel'][4], params['endcap'][4], params['forward'][4]]
        else:
            self._plateau = [params['barrel'][0], params['endcap'][0]]
            self._turnon  = [params['barrel'][1], params['endcap'][1]]
            self._resol   = [params['barrel'][2], params['endcap'][2]]
            self._ptcut   = [params['barrel'][3], params['endcap'][3]]
            self._plat2   = [params['barrel'][4], params['endcap'][4]]
    def __call__(self,pt,eta,verbose=0):
        ieta = 0
        if self._isMu:
            if abs(eta) > 1.2: ieta = 1
            if abs(eta) > 2.1: ieta = 2
        else:
            if abs(eta) > 1.5: ieta = 1
        ret = self._plat2[ieta]
        if pt <= self._ptcut[ieta] and self._ptcut[ieta] > 8:
            ret = self._plateau[ieta]/(1 + exp(-(pt - self._turnon[ieta])/self._resol[ieta]))
        if verbose > 0: print  "      %s: for (pt,eta) = (%.1f,%.2f), efficiency is %5.2f%%" % (self._name,pt,eta,ret*100)
        return ret

class ZeroEfficiency:
    def __init__(self, name=None):
        self._name = name
    def __call__(self,pt,eta,verbose=0):
        if verbose > 0 and self._name != None:
            print "Called ZeroEfficiency %s for (pt,eta) = (%.1f,%.2f)" % (self._name,pt,eta)
        return 0.0;

class PerfectEfficiency:
    def __init__(self,threshold=0,plateau=1.0):
        self._threshold = 0
        self._plateau   = 1.0
    def __call__(self,pt,eta,verbose=0): 
        return self._plateau if pt > self._threshold else 0.0;

class DiMuEventEfficiency:
    def __init__(self,legs,mode="default"):
        self._mode   = mode
        if mode != "onlyDouble":
            self._single = legs["SingleMu"]
        else:
            self._single = ZeroEfficiency()
        if "Mu13leg_Mu8" in legs:
            self._doubleHighPt = legs["Mu13leg_Mu8"]
            self._doubleLowPt  = legs["Mu13_Mu8leg"]
        elif "Mu17leg_Mu8" in legs:
            self._doubleHighPt = legs["Mu17leg_Mu8"]
            self._doubleLowPt  = legs["Mu17_Mu8leg"]
        else:
            self._doubleHighPt = ZeroEfficiency()
            self._doubleLowPt  = ZeroEfficiency() 
        if "Mu17_TkMu8_Exclusive" in legs and mode != "noTkMu":
            self._tkMuExclusive = legs["Mu17_TkMu8_Exclusive"]
        else:
            self._tkMuExclusive = ZeroEfficiency()
    def __call__(self,pt1,eta1,pt2,eta2,verbose=0):
        # The event passes the trigger if:
        # - leading lepton passes single mu
        # - or leading passes high pt double leg and sub-leading passes low pt double or tracker double
        # - or leading passes double mu low pt and sub-leanding passes single mu
        # - or leading passes tracker mu and sub-leading passes high pt double leg
        # - or leading passes nothing but sub-leading passes single mu
        # in the above, leading legs are exclusive while sub-leading are inclusive.
        #
        # 1. compute efficiencies for first leg
        effs_leg1 = [x(pt1,eta1,verbose-1) for x in self._single, self._doubleHighPt, self._doubleLowPt, self._tkMuExclusive]
        # 2. make them exclusive, add efficiency of everything failing
        effs_leg1[1] -= effs_leg1[0]
        effs_leg1[2] -= effs_leg1[0] + effs_leg1[1]
        effs_leg1.append(1.0 - sum(effs_leg1))
        # 3. compute efficiencies for second leg
        effs_leg2 = [x(pt2,eta2,verbose-1) for x in self._single, self._doubleHighPt, self._doubleLowPt, self._tkMuExclusive]
        # 4. make them inclusive adding tkMu to low pt double mu
        effs_leg2[3] += effs_leg2[2]
        # 5. do the running sum
        eff = [
            effs_leg1[0] * 1,            # single lead
            effs_leg1[1] * effs_leg2[3], # double with lead high pt leg
            effs_leg1[2] * effs_leg2[0], # single sublead (lead passes low pt leg exclusive)
            effs_leg1[3] * effs_leg2[1], # tracker double with sublead high pt leg          
            effs_leg1[4] * effs_leg2[0], # single sublead (lead fails everything)          
        ]
        if verbose > 0: 
            print "  - %6.2f%% single mu leading" % (100*eff[0])
            print "  - %6.2f%% plus double with lead high pt leg" % (100*sum(eff[0:1]))
            print "  - %6.2f%% plus single sublead (lead passes low pt leg exclusive)" % (100*sum(eff[0:2]))
            print "  - %6.2f%% plus tracker double with sublead high pt leg" % (100*sum(eff[0:3]))
            print "  - %6.2f%% plus single sublead (lead fails everything)" % (100*sum(eff))
        return sum(eff)

class DiElEventEfficiency:
    def __init__(self,legs,mode="default"):
        self._mode   = mode
        if mode != "onlyDouble":
            self._singleEl = legs["SingleEl"] if "SingleEl" in legs else ZeroEfficiency("NoSingleEl")
        else:
            self._singleEl = ZeroEfficiency()
        if "Ele17_Ele8_Ele17Leg_fromEle8" in legs:
            self._doubleElHighPt = legs["Ele17_Ele8_Ele17Leg_fromEle8"]
            self._doubleElLowPt  = legs["Ele17_Ele8_Ele8Leg_fromEle8"]
        elif "Ele17_Ele8_Tighter_Ele17Leg_fromEle8" in legs:
            self._doubleElHighPt = legs["Ele17_Ele8_Tighter_Ele17Leg_fromEle8"]
            self._doubleElLowPt  = legs["Ele17_Ele8_Tighter_Ele8Leg_fromEle8"]
        else:
            self._doubleElHighPt = ZeroEfficiency("NoDoubleEl_HighPt")
            self._doubleElLowPt  = ZeroEfficiency("NoDoubleEl_LowPt") 
    def __call__(self,pt1,eta1,pt2,eta2,verbose=0):
        effs_leg1 = [x(pt1,eta1,verbose-1) for x in self._singleEl, self._doubleElHighPt]
        effs_leg2 = [x(pt2,eta2,verbose-1) for x in self._singleEl, self._doubleElLowPt]
        effs_leg1[1] -= effs_leg1[0]
        effs_leg1.append(1.0 - sum(effs_leg1))
        eff = [
            effs_leg1[0] * 1,            # single leading
            effs_leg1[1] * effs_leg2[1], # double 
            effs_leg1[2] * effs_leg2[0], # single electron          
        ]
        if verbose > 0: 
            print "  - %6.2f%% single el leading" % (100*eff[0])
            print "  - %6.2f%% plus double "      % (100*sum(eff[0:1]))
            print "  - %6.2f%% plus single el subleading" % (100*sum(eff))
        return sum(eff)

class ElMuEventEfficiency:
    def __init__(self,legs,mode="default"):
        self._mode   = mode
        if mode != "onlyDouble":
            self._singleEl = legs["SingleEl"] if "SingleEl" in legs else ZeroEfficiency("NoSingleEl")
            self._singleMu = legs["SingleMu"]
        else:
            self._singleEl = ZeroEfficiency()
            self._singleMu = ZeroEfficiency()
        if "Mu13leg_Mu8" in legs:
            self._doubleMuHighPt = legs["Mu13leg_Mu8"]
            self._doubleMuLowPt  = legs["Mu13_Mu8leg"]
        elif "Mu17leg_Mu8" in legs:
            self._doubleMuHighPt = legs["Mu17leg_Mu8"]
            self._doubleMuLowPt  = legs["Mu17_Mu8leg"]
        else:
            self._doubleMuHighPt = ZeroEfficiency()
            self._doubleMuLowPt  = ZeroEfficiency() 
        if "Ele17_Ele8_Ele17Leg_fromEle8" in legs:
            self._doubleElHighPt = legs["Ele17_Ele8_Ele17Leg_fromEle8"]
            self._doubleElLowPt  = legs["Ele17_Ele8_Ele8Leg_fromEle8"]
        elif "Ele17_Ele8_Tighter_Ele17Leg_fromEle8" in legs:
            self._doubleElHighPt = legs["Ele17_Ele8_Tighter_Ele17Leg_fromEle8"]
            self._doubleElLowPt  = legs["Ele17_Ele8_Tighter_Ele8Leg_fromEle8"]
        else:
            self._doubleElHighPt = ZeroEfficiency("NoDoubleEl_HighPt")
            self._doubleElLowPt  = ZeroEfficiency("NoDoubleEl_LowPt") 
    def __call__(self,ptmu,etamu,ptel,etael,verbose=0):
        effs_leg1 = [x(ptmu,etamu,verbose-1) for x in self._singleMu, self._doubleMuHighPt, self._doubleMuLowPt]
        effs_leg2 = [x(ptel,etael,verbose-1) for x in self._singleEl, self._doubleElHighPt, self._doubleElLowPt]
        # 2. make them exclusive, add efficiency of everything failing
        effs_leg1[1] -= effs_leg1[0]
        effs_leg1[2] -= effs_leg1[0] + effs_leg1[1]
        effs_leg1.append(1.0 - sum(effs_leg1))
        # 5. do the running sum
        eff = [
            effs_leg1[0] * 1,            # single mu
            effs_leg1[1] * effs_leg2[2], # double with lead high pt mu
            effs_leg1[2] * effs_leg2[1], # double with low pt mu (but not high pt mu)
            effs_leg1[3] * effs_leg2[0], # single electron          
        ]
        if verbose > 0: 
            print "  - %6.2f%% single mu" % (100*eff[0])
            print "  - %6.2f%% plus double with lead high pt mu" % (100*sum(eff[0:1]))
            print "  - %6.2f%% plus double with low pt mu" % (100*sum(eff[0:2]))
            print "  - %6.2f%% plus single el" % (100*sum(eff))
        return sum(eff)

class LuminosityWeightedAverage:
    def __init__(self,lumiEffPairs):
        norm = sum([lumi for lumi,eff in lumiEffPairs])
        self._pairs = [ (lumi/norm, eff) for (lumi,eff) in lumiEffPairs]
    def __call__(self,pt1,eta1,pt2,eta2,verbose):
        avg = 0
        for (w,eff) in self._pairs:
            avg += w*eff(pt1,eta1,pt2,eta2,verbose)
        return avg








def getTriggersForRun(run, verbose=0):
    ret = {}
    for (trigname,start,end,pars) in triggers:
        if run >= start and run <= end:
            ret[trigname] = LegEfficiency(trigname,pars)
    if verbose: print "Triggers for run %d: %s" % (run, ", ".join(ret.keys()))
    return ret



def getTriggerEfficiency(eff, tree, signalSelection = lambda x : True, weight = lambda x : 1.0):
    debug_low = 0
    num = 0.0; den = 0.0
    if signalSelection(tree):
        w = weight(tree)
        if tree.channel == 2: # make sure for e+mu the 1 is mu
            e = eff(tree.pt2, tree.eta2, tree.pt1, tree.eta1, verbose=0)
        else:
            e = eff(tree.pt1, tree.eta1, tree.pt2, tree.eta2, verbose=0)
        if e < 0.5 and debug_low > 0:
            debug_low -= 1
            if tree.channel == 2: # make sure for e+mu the 1 is mu
                e = eff(tree.pt2, tree.eta2, tree.pt1, tree.eta1, verbose=2)
            else:
                e = eff(tree.pt1, tree.eta1, tree.pt2, tree.eta2, verbose=2)
        return e



theTriggerMix = []
theTriggerMixA = []
theTriggerMixB = []
##lumis = open("/afs/cern.ch/user/g/gpetrucc/scratch0/higgs/CMSSW_4_2_7_patch2/src/WWAnalysis/AnalysisStep/test/tp_lepton_effs/luminosities.thea.txt", "r")
lumis = open("/afs/cern.ch/user/j/jueugste/latinos/luminosities.thea.txt", "r")
for line in lumis:
    (start,end,lumi) = [ float(x) for x in line.replace("-"," ").split() ]
    print "Considering run range %d-%d (lumi %.1f pb)" % (start, end, lumi)
    myTriggers = getTriggersForRun(0.5*(start+end), verbose=1)
    if "SingleMu" not in myTriggers: continue

    theTriggerMix.append((lumi, myTriggers))
    if end <= 173692:
        theTriggerMixA.append((lumi, myTriggers))
    if end > 173692:
        theTriggerMixB.append((lumi, myTriggers))

effMM = LuminosityWeightedAverage( [ ( lumi, DiMuEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMix ] )
effEE = LuminosityWeightedAverage( [ ( lumi, DiElEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMix ] )
effEM = LuminosityWeightedAverage( [ ( lumi, ElMuEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMix ] )

effMMA = LuminosityWeightedAverage( [ ( lumi, DiMuEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMixA ] )
effEEA = LuminosityWeightedAverage( [ ( lumi, DiElEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMixA ] )
effEMA = LuminosityWeightedAverage( [ ( lumi, ElMuEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMixA ] )

effMMB = LuminosityWeightedAverage( [ ( lumi, DiMuEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMixB ] )
effEEB = LuminosityWeightedAverage( [ ( lumi, DiElEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMixB ] )
effEMB = LuminosityWeightedAverage( [ ( lumi, ElMuEventEfficiency(trigs) ) for (lumi,trigs) in theTriggerMixB ] )





###############################################################################################
###############################################################################################
###############################################################################################



###############################################################################################
##                 _                        _                                 
##                | |                      | |                                
##  ___  ___  __ _| | ___    __ _ _ __   __| |  ___ _ __ ___   ___  __ _ _ __ 
## / __|/ __|/ _` | |/ _ \  / _` | '_ \ / _` | / __| '_ ` _ \ / _ \/ _` | '__|
## \__ \ (__| (_| | |  __/ | (_| | | | | (_| | \__ \ | | | | |  __/ (_| | |   
## |___/\___|\__,_|_|\___|  \__,_|_| |_|\__,_| |___/_| |_| |_|\___|\__,_|_|   
##                                                                           
##                                                                           
class scaleAndSmear:
    def __init__(self):
        self.inputFileName = ''
        self.outputFileName = ''
        self.path = ''
        self.inFile = None
        self.outFile = None
        self.treeDir = ''
        self.ttree = None
        self.oldttree = None
        self.nentries = 0
        self.systArgument = ''
        self.direction = ''

        
    def __del__(self):
        if self.outFile:
            self.outFile.Write()
            self.outFile.Close()



    def openOriginalTFile(self):
        filename = self.inputFileName
        print 'opening file: '+filename
        self.inFile = ROOT.TFile.Open(filename)

    def openOutputTFile(self):
        filename = self.outputFileName
        dir = os.path.dirname(filename)
        if not os.path.exists(dir):
            print 'directory does not exist yet...'
            print 'creating output directory: '+dir
            os.system('mkdir -p '+dir)
        print 'creating output file: '+filename
        self.outFile = ROOT.TFile.Open(filename,'recreate')

###############################################################################################
##  _____ _                    _____             
## /  __ \ |                  |_   _|            
## | /  \/ | ___  _ __   ___    | |_ __ ___  ___ 
## | |   | |/ _ \| '_ \ / _ \   | | '__/ _ \/ _ \
## | \__/\ | (_) | | | |  __/   | | | |  __/  __/
##  \____/_|\___/|_| |_|\___|   \_/_|  \___|\___|
##                                              
    def cloneTree(self):
        ## clone the tree
        self.inFile.ls()
        oldTree = self.inFile.Get(self.treeDir)
        ## do not clone the branches which should be scaled
        ## i.e. set status to 0
            
        if self.systArgument == 'leptonEfficiency':
            oldTree.SetBranchStatus('effW'       ,0)
            oldTree.SetBranchStatus('effAW'      ,0)
            oldTree.SetBranchStatus('effBW'      ,0)
            oldTree.SetBranchStatus('triggW'     ,0)
            oldTree.SetBranchStatus('triggAW'     ,0)
            oldTree.SetBranchStatus('triggBW'     ,0)

            
        newTree = oldTree.CloneTree(0)
        nentries = oldTree.GetEntriesFast()
        print 'Tree with '+str(nentries)+' entries cloned...'
        self.nentries = nentries
        
        self.ttree = newTree
        ## BUT keep all branches "active" in the old tree
        oldTree.SetBranchStatus('*'  ,1)

        self.oldttree = oldTree
        for branch in self.ttree.GetListOfBranches():
            print branch



###############################################################################################
##  _                 _                 _____  __  __ _      _                 _          
## | |               | |               |  ___|/ _|/ _(_)    (_)               (_)         
## | |      ___ _ __ | |_  ___  _ __   | |__ | |_| |_ _  ___ _  ___ _ __   ___ _  ___ ___ 
## | |     / _ \ '_ \| __|/ _ \| '_ \  |  __||  _|  _| |/ __| |/ _ \ '_ \ / __| |/ _ | __|
## | |____|  __/ |_) | |_| (_) | | | | | |___| | | | | | (__| |  __/ | | | (__| |  __|__ \
## \_____/ \___| .__/ \__|\___/|_| |_| \____/|_| |_| |_|\___|_|\___|_| |_|\___|_|\___|___/
##             | |                                                                        
##             |_|                                                                        
##
    def leptonEfficiency(self):
        print 'lepton efficiency'

        effW = numpy.zeros(1, dtype=numpy.float32)
        effAW = numpy.zeros(1, dtype=numpy.float32)
        effBW = numpy.zeros(1, dtype=numpy.float32)
        self.ttree.Branch('effW',effW,'effW/F')
        self.ttree.Branch('effAW',effAW,'effAW/F')
        self.ttree.Branch('effBW',effBW,'effBW/F')


        triggW = numpy.zeros(1, dtype=numpy.float32)
        triggAW = numpy.zeros(1, dtype=numpy.float32)
        triggBW = numpy.zeros(1, dtype=numpy.float32)
        self.ttree.Branch('triggW',triggW,'triggW/F')
        self.ttree.Branch('triggAW',triggAW,'triggAW/F')
        self.ttree.Branch('triggBW',triggBW,'triggBW/F')



## this are the 1stNov efficiency weights:
        base_path = '/afs/cern.ch/user/j/jueugste/latinos/leptonEfficiencies/'
        mA_path = base_path+'m_OutputScaleFactorMap_MC42X_2011AReweighted.root'
        mB_path = base_path+'m_OutputScaleFactorMap_MC42X_2011BReweighted.root'
        eA_path = base_path+'e_OutputScaleFactorMap_MC42X_2011AReweighted.root'
        eB_path = base_path+'e_OutputScaleFactorMap_MC42X_2011BReweighted.root'
        lumiA = 2.118
#        lumiB = 1.841
        lumiB = 2.511
        
##         # open the root files containing the weights and errors...
##         base_path = '/shome/jueugste/HWWSystematics/leptonEfficiencies/'
## ##         m_path = base_path+'Muons_vpvPlusExpo_OutputScaleFactorMap.root'
##         m_path = base_path+'OutputScaleFactorMap_MuonEfficiencies_DataRun2011A_vs_MC42X.root'
## ##        m_path = base_path+'AbsEta-Pt_Histrogram_2011AData_MuonPRcenario2_MAP.root'## ##         e_path = base_path+'Electrons_vpvPlusExpo_OutputScaleFactorMap.root'
##         e_path = base_path+'electronEff_CutID_SFmap_Run2011A.root'
## ##        e_path = base_path+'OutputScaleFactorMap_Scenario4_BDTElectrons_Run2011A_MC42X.root'


        fA_muon = openTFile(mA_path)
        fB_muon = openTFile(mB_path)
        fA_ele  = openTFile(eA_path)
        fB_ele  = openTFile(eB_path)
##         f_muon = openTFile(m_path)
##         f_ele  = openTFile(e_path)
        hA_muon = getHist(fA_muon,'hScaleFactorMap')
        hB_muon = getHist(fB_muon,'hScaleFactorMap')
        hA_ele  = getHist(fA_ele,'hScaleFactorMap')
        hB_ele  = getHist(fB_ele,'hScaleFactorMap')
##         h_muon = getHist(f_muon,'hScaleFactorMap')
##         h_ele  = getHist(f_ele,'pt_abseta_PLOT')

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i = 0
        for ientry in range(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 50000
            if i > 0 and i%step == 0.:
                print str(i)+' events processed.'

##
## ----------------------------------------------------------------
##
##             get the bin coordinates
            cpt1 = 1
            cpt2 = 1
            ceta1 = 1
            ceta2 = 1
            lpt1 = self.oldttree.pt1
            lpt2 = self.oldttree.pt2
            leta1 = self.oldttree.eta1
            leta2 = self.oldttree.eta2
##             if lpt1 < 15:
##                 cpt1 = 1
            if lpt1 >= 15 and lpt1 < 20:
                cpt1 = 2
            if lpt1 >= 20 and lpt1 < 50:
                cpt1 = 3
            if lpt1 >= 50:
                cpt1 = 4
##             if lpt2 < 15:
##                 cpt2 = 1
            if lpt2 >= 15 and lpt2 < 20:
                cpt2 = 2
            if lpt2 >= 20 and lpt2 < 50:
                cpt2 = 3
            if lpt2 >= 50:
                cpt2 = 4
            if abs(leta1) > 1.48:
                ceta1 = 2
            if abs(leta2) > 1.48:
                ceta2 = 2

            ## muon-muon channel
            if self.oldttree.channel == 0:
                valA1 = hA_muon.GetBinContent(cpt1,ceta1)
                valA2 = hA_muon.GetBinContent(cpt2,ceta2)
                errA1 = hA_muon.GetBinError(cpt1,ceta1)
                errA2 = hA_muon.GetBinError(cpt2,ceta2)
                valB1 = hB_muon.GetBinContent(cpt1,ceta1)
                valB2 = hB_muon.GetBinContent(cpt2,ceta2)
                errB1 = hB_muon.GetBinError(cpt1,ceta1)
                errB2 = hB_muon.GetBinError(cpt2,ceta2)
##                 val1 = h_muon.GetBinContent(cpt1,ceta1)
##                 val2 = h_muon.GetBinContent(cpt2,ceta2)
##                 err1 = h_muon.GetBinError(cpt1,ceta1)
##                 err2 = h_muon.GetBinError(cpt2,ceta2)

            ## electron-electron channel    
            if self.oldttree.channel == 1:
                if lpt1 < 15:
                    cpt1 = 1
                if lpt1 >= 15 and lpt1 < 20:
                    cpt1 = 2
                if lpt1 >= 20 and lpt1 < 25:
                    cpt1 = 3
                if lpt1 >= 25 and lpt1 < 50:
                    cpt1 = 4
                if lpt1 >= 50:
                    cpt1 = 5
                if lpt2 < 15:
                    cpt2 = 1
                if lpt2 >= 15 and lpt2 < 20:
                    cpt2 = 2
                if lpt2 >= 20 and lpt2 < 25:
                    cpt2 = 3
                if lpt2 >= 25 and lpt2 < 50:
                    cpt2 = 4
                if lpt2 >= 50:
                    cpt2 = 5
                if abs(leta1) <= 1.4442:
                    ceta1 = 1
                if abs(leta1) > 1.4442 and abs(leta1) <1.556:
                    ceta1 = 2
                if abs(leta1) >= 1.556:
                    ceta1 = 3
                if abs(leta2) <= 1.4442:
                    ceta2 = 1
                if abs(leta2) > 1.4442 and abs(leta2) <1.556:
                    ceta2 = 2
                if abs(leta2) >= 1.556:
                    ceta2 = 3
                
                valA1 = hA_ele.GetBinContent(cpt1,ceta1)
                valA2 = hA_ele.GetBinContent(cpt2,ceta2)
                errA1 = hA_ele.GetBinError(cpt1,ceta1)
                errA2 = hA_ele.GetBinError(cpt2,ceta2)

                valB1 = hB_ele.GetBinContent(cpt1,ceta1)
                valB2 = hB_ele.GetBinContent(cpt2,ceta2)
                errB1 = hB_ele.GetBinError(cpt1,ceta1)
                errB2 = hB_ele.GetBinError(cpt2,ceta2)

##                 val1 = h_ele.GetBinContent(cpt1,ceta1)
##                 val2 = h_ele.GetBinContent(cpt2,ceta2)
##                 err1 = h_ele.GetBinError(cpt1,ceta1)
##                 err2 = h_ele.GetBinError(cpt2,ceta2)

            ## electron-muon channel
            if self.oldttree.channel == 2:
                if lpt1 < 15:
                    cpt1 = 1
                if lpt1 >= 15 and lpt1 < 20:
                    cpt1 = 2
                if lpt1 >= 20 and lpt1 < 25:
                    cpt1 = 3
                if lpt1 >= 25 and lpt1 < 50:
                    cpt1 = 4
                if lpt1 >= 50:
                    cpt1 = 5
                if abs(leta1) <= 1.4442:
                    ceta1 = 1
                if abs(leta1) > 1.4442 and abs(leta1) <1.556:
                    ceta1 = 2
                if abs(leta1) >= 1.556:
                    ceta1 = 3

                valA1 = hA_ele.GetBinContent(cpt1,ceta1)
                valA2 = hA_muon.GetBinContent(cpt2,ceta2)
                errA1 = hA_ele.GetBinError(cpt1,ceta1)
                errA2 = hA_muon.GetBinError(cpt2,ceta2)

                valB1 = hB_ele.GetBinContent(cpt1,ceta1)
                valB2 = hB_muon.GetBinContent(cpt2,ceta2)
                errB1 = hB_ele.GetBinError(cpt1,ceta1)
                errB2 = hB_muon.GetBinError(cpt2,ceta2)

##                 val1 = h_ele.GetBinContent(cpt1,ceta1)
##                 val2 = h_muon.GetBinContent(cpt2,ceta2)
##                 err1 = h_ele.GetBinError(cpt1,ceta1)
##                 err2 = h_muon.GetBinError(cpt2,ceta2)

            ## muon-electron channel    
            if self.oldttree.channel == 3:
                if lpt2 < 15:
                    cpt2 = 1
                if lpt2 >= 15 and lpt2 < 20:
                    cpt2 = 2
                if lpt2 >= 20 and lpt2 < 25:
                    cpt2 = 3
                if lpt2 >= 25 and lpt2 < 50:
                    cpt2 = 4
                if lpt2 >= 50:
                    cpt2 = 5
                if abs(leta2) <= 1.4442:
                    ceta2 = 1
                if abs(leta2) > 1.4442 and abs(leta2) <1.556:
                    ceta2 = 2
                if abs(leta2) >= 1.556:
                    ceta2 = 3                    
                valA1 = hA_muon.GetBinContent(cpt1,ceta1)
                valA2 = hA_ele.GetBinContent(cpt2,ceta2)
                errA1 = hA_muon.GetBinError(cpt1,ceta1)
                errA2 = hA_ele.GetBinError(cpt2,ceta2)

                valB1 = hB_muon.GetBinContent(cpt1,ceta1)
                valB2 = hB_ele.GetBinContent(cpt2,ceta2)
                errB1 = hB_muon.GetBinError(cpt1,ceta1)
                errB2 = hB_ele.GetBinError(cpt2,ceta2)

##                 val1 = h_muon.GetBinContent(cpt1,ceta1)
##                 val2 = h_ele.GetBinContent(cpt2,ceta2)
##                 err1 = h_muon.GetBinError(cpt1,ceta1)
##                 err2 = h_ele.GetBinError(cpt2,ceta2)

##
## ----------------------------------------------------------------
##

##             ## add the statistical error
##             ##effW_sup = (val1+err2)*(val2+err2)
##             ##effW_sdown = (val1-err2)*(val2-err2)
##             effAW_sup = (valA1+errA2)*(valA2+errA2)
##             effAW_sdown = (valA1-errA2)*(valA2-errA2)
##             effBW_sup = (valB1+errB2)*(valB2+errB2)
##             effBW_sdown = (valB1-errB2)*(valB2-errB2)
##             effW_sup   = (effWA_sup*lumiA + effWB_sup*lumiB) / (lumiA + lumiB)
##             effW_sdown = (effWA_sdown*lumiA + effWB_sdown*lumiB) / (lumiA + lumiB) 

##
## ----------------------------------------------------------------
## MIT numbers
## ----------------------------------------------------------------
##

##             # muon-muon channel
##             if self.oldttree.channel == 0:
##                 valA1 = mitMuEffA(lpt1, leta1)
##                 valA2 = mitMuEffA(lpt2, leta2)
##                 valB1 = mitMuEffB(lpt1, leta1)
##                 valB2 = mitMuEffB(lpt2, leta2)

##             if self.oldttree.channel == 1:
##                 valA1 = mitEleEffA(lpt1, leta1)
##                 valA2 = mitEleEffA(lpt2, leta2)
##                 valB1 = mitEleEffB(lpt1, leta1)
##                 valB2 = mitEleEffB(lpt2, leta2)

##             if self.oldttree.channel == 2:
##                 valA1 = mitEleEffA(lpt1, leta1)
##                 valA2 = mitMuEffA(lpt2, leta2)
##                 valB1 = mitEleEffB(lpt1, leta1)
##                 valB2 = mitMuEffB(lpt2, leta2)

##             if self.oldttree.channel == 3:
##                 valA1 = mitMuEffA(lpt1, leta1)
##                 valA2 = mitEleEffA(lpt2, leta2)
##                 valB1 = mitMuEffB(lpt1, leta1)
##                 valB2 = mitEleEffB(lpt2, leta2)


            
                
            ## just replace the "old" value with the one from the root files
            ##effW_sup   = val1*val2
            ##effW_sdown = val1*val2
            effAW_sup   = valA1*valA2
            effAW_sdown = valA1*valA2
            effBW_sup   = valB1*valB2
            effBW_sdown = valB1*valB2

            effW_sup   = (effAW_sup*lumiA + effBW_sup*lumiB) / (lumiA + lumiB)
            effW_sdown = (effAW_sdown*lumiA + effBW_sdown*lumiB) / (lumiA + lumiB) 

##Some printouts to check that I am doing the right thing...        
            print '------------------------'
            print self.oldttree.channel
            print lpt1, leta1, valA1, valB1,'\n' 
            print lpt2, leta2, valA2, valB2,'\n' 
            
##             #print 'up  : '+str(effW_sup)
##             print 'val : '+str(val1*val2)
##             #print 'down: '+str(effW_sdown)
##             print 'effW: '+str(self.oldttree.effW)
            
            if self.direction == 'up':
                effAW[0] = effAW_sup
                effBW[0] = effBW_sup
                effW[0] = effW_sup
            if self.direction == 'down':
                effAW[0] = effAW_sdown
                effBW[0] = effBW_sdown
                effW[0] = effW_sdown

##            print effW[0], effAW[0], effBW[0]

##            print self.direction+' : '+str(effW[0])
            # fill old and new values



###############################################################################################
###############################################################################################
###############################################################################################
            # trigger efficiencies

            # check ordering (muon first!!)
            
            diMu2015 = lambda x: (x.channel == 0)# and x.pt1 > 20 and x.pt2 >= 15)
            diEl2015 = lambda x: (x.channel == 1)# and x.pt1 > 20 and x.pt2 >= 15)
            OF2010   = lambda x: (x.channel >= 2)# and x.pt1 > 20 and x.pt2 >= 10)        
            
##             diMu2015 = lambda x: (self.oldttree.channel == 0)# and x.pt1 > 20 and x.pt2 >= 15)
##             diEl2015 = lambda x: (self.oldttree.channel == 1)# and x.pt1 > 20 and x.pt2 >= 15)
##             OF2010   = lambda x: (self.oldttree.channel >= 2)# and x.pt1 > 20 and x.pt2 >= 10)        

#            print self.oldttree.channel
##             print getTriggerEfficiency(effMM, self.oldttree, diMu2015)
##             print getTriggerEfficiency(effEE, self.oldttree, diEl2015)
##             print getTriggerEfficiency(effEM, self.oldttree, OF2010)

##             if diMu2015:
            if self.oldttree.channel == 0:
                triggW[0] = getTriggerEfficiency(effMM, self.oldttree, diMu2015)
                triggAW[0] = getTriggerEfficiency(effMMA, self.oldttree, diMu2015)
                triggBW[0] = getTriggerEfficiency(effMMB, self.oldttree, diMu2015)
##             elif diEl2015:
            elif self.oldttree.channel == 1:
                triggW[0] = getTriggerEfficiency(effEE, self.oldttree, diEl2015)
                triggAW[0] = getTriggerEfficiency(effEEA, self.oldttree, diEl2015)
                triggBW[0] = getTriggerEfficiency(effEEB, self.oldttree, diEl2015)
##             elif OF2010:
            elif self.oldttree.channel >= 2:
                triggW[0] = getTriggerEfficiency(effEM, self.oldttree, OF2010)
                triggAW[0] = getTriggerEfficiency(effEMA, self.oldttree, OF2010)
                triggBW[0] = getTriggerEfficiency(effEMB, self.oldttree, OF2010)
 ##            print triggW[0]
##             print triggAW[0]
##             print triggBW[0]
                

###############################################################################################
###############################################################################################
###############################################################################################


            self.ttree.Fill()
###############################################################################################
##                  _       
##                 (_)      
##  _ __ ___   __ _ _ _ __  
## | '_ ` _ \ / _` | | '_ \ 
## | | | | | | (_| | | | | |
## |_| |_| |_|\__,_|_|_| |_|
##                         
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    
    parser.set_defaults(overwrite=False)
    
    parser.add_option('-i', '--inputFileName',   dest='inputFileName',   help='Name of the input *.root file',)
    parser.add_option('-o', '--outputFileName',  dest='outputFileName',  help='Name of the output *.root file',)
    parser.add_option('-a', '--systematicArgument', dest='systArgument', help='Argument to specify systematic',)
    parser.add_option('-d', '--direction',          dest='direction',    help='Direction of the scale variation (up/down)',)
    parser.add_option('-t', '--treeDir',            dest='treeDir',      help='TDirectry structure to the tree to scale and smear',)
#    parser.add_option('-n', '--nEvents',           dest='nEvents',     help='Number of events to run over',)


    (opt, args) = parser.parse_args()

    if opt.inputFileName is None:
        parser.error('No input file defined')
    if opt.outputFileName is None:
        parser.error('No output file defined')
    if opt.systArgument is None:
        parser.error('No systematic argument given')
    possibleSystArguments = ['leptonEfficiency']
    if opt.systArgument not in possibleSystArguments:
        parser.error('Wrong systematic argument')        
    possibleDirections = ['up','down']
    if opt.direction not in possibleDirections:
        parser.error('No direction of the systematic variation given')
    if opt.treeDir is None:
        parser.error('No path to the tree specyfied')


##     sys.argv.append('-b')
##     ROOT.gROOT.SetBatch()

    s = scaleAndSmear()
    s.inputFileName = opt.inputFileName
    s.outputFileName = opt.outputFileName
    s.treeDir = opt.treeDir
    s.systArgument = opt.systArgument
    s.direction = opt.direction

    print s.systArgument

    s.openOriginalTFile()
    s.openOutputTFile()
    s.cloneTree()
    
    if s.systArgument == 'muonScale':
        s.muonScale()
    if s.systArgument == 'electronScale':
        s.electronScale()
    if s.systArgument == 'leptonEfficiency':

        s.leptonEfficiency()
    if s.systArgument == 'jetEnergyScale':
        s.jetEnergyScale()
    if s.systArgument == 'metResolution':
        s.metResolution()
    if s.systArgument == 'electronResolution':
        s.electronResolution()
    


    print 'Job finished...'





if __name__ == '__main__':
    main()

