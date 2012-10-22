#!/bin/env python

# import modules for regular expressions, math, and printing
import re
from math import *
from pprint import pprint


triggers = []

class TriggerEff:

    def __init__(self,path):
        
        # open file (TODO: replace with config option)
        fits = open(path, "r")

        # read every line
        for line in fits:
            m = re.match(r"2012[ABC]?_(\d+)-(\d+)_(\w+)_(barrel|endcap|forward|absetabin[0123])\s+.*", line)
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


    def getMMeff(self):
        # works only with 2012 data for the moment
        triggers = self.getTriggersForRun(190456)
        return DiMuEventEfficiency(triggers)

    def getEEeff(self):
        # works only with 2012 data for the moment
        triggers = self.getTriggersForRun(190456)
        return DiElEventEfficiency(triggers)

    def getEMeff(self):
        # works only with 2012 data for the moment
        triggers = self.getTriggersForRun(190456)
        return ElMuEventEfficiency(triggers)

    def getTriggersForRun(self, run, verbose=0):
        ret = {}
        for (trigname,start,end,pars) in triggers:
            if run >= start and run <= end:
                ret[trigname] = LegEfficiency(trigname,pars)
        if verbose: print "Triggers for run %d: %s" % (run, ", ".join(ret.keys()))
        return ret


    def getTriggerEfficiency(self, eff, tree, signalSelection = lambda x : True, weight = lambda x : 1.0):
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


## Giovannis classes:

class LegEfficiency:
    def __init__(self,name,params):
        self._name    = name
        self._isMu    = ("Mu" in name)
        self._isSingleMu = ("SingleMu" in name)
        if self._isSingleMu:
            self._plateau = [params['absetabin0'][0], params['absetabin1'][0], params['absetabin2'][0], params['absetabin3'][0]]
            self._turnon  = [params['absetabin0'][1], params['absetabin1'][1], params['absetabin2'][1], params['absetabin3'][1]]
            self._resol   = [params['absetabin0'][2], params['absetabin1'][2], params['absetabin2'][2], params['absetabin3'][2]]
            self._ptcut   = [params['absetabin0'][3], params['absetabin1'][3], params['absetabin2'][3], params['absetabin3'][3]]
            self._plat2   = [params['absetabin0'][4], params['absetabin1'][4], params['absetabin2'][4], params['absetabin3'][4]]            
        elif self._isMu:
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
        if self._isSingleMu:
            if abs(eta) > 0.8: ieta = 1
            if abs(eta) > 1.2: ieta = 2
            if abs(eta) > 2.1: ieta = 3
        elif self._isMu:
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
            self._single = legs["SingleMu"] if "SingleMu" in legs else ZeroEfficiency("NoSingleMu")
        else:
            self._single = ZeroEfficiency()
        if "Mu17_Mu8_Mu17Leg" in legs:
            self._doubleHighPt = legs["Mu17_Mu8_Mu17Leg"]
            self._doubleLowPt  = legs["Mu17_Mu8_Mu8Leg"]
        else:
            self._doubleHighPt = ZeroEfficiency()
            self._doubleLowPt  = ZeroEfficiency() 
        if "Mu17_TkMu8_Exclusive" in legs and mode != "noTkMu":
            self._tkMuExclusive = legs["Mu17_TkMu8_Exclusive"]
        else:
            self._tkMuExclusive = ZeroEfficiency()
    def __call__(self,pt1,eta1,pt2,eta2,verbose=0):
        effs_leg1 = [x(pt1,eta1,verbose-1) for x in self._single, self._doubleHighPt, self._doubleLowPt, self._tkMuExclusive]
        effs_leg2 = [x(pt2,eta2,verbose-1) for x in self._single, self._doubleHighPt, self._doubleLowPt, self._tkMuExclusive]
        p0 = effs_leg1[0]
        p1 = effs_leg1[1]
        p2 = effs_leg1[2]
        q0 = effs_leg2[0]
        q1 = effs_leg2[1]
        q2 = effs_leg2[2]
        eff = p0 + (1-p0)*q0 + (1-p0)*(1-q0)*(p1*q2 + (1-p1*q2)*p2*q1)
        return eff

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
        else:
            self._doubleElHighPt = ZeroEfficiency("NoDoubleEl_HighPt")
            self._doubleElLowPt  = ZeroEfficiency("NoDoubleEl_LowPt") 
    def __call__(self,pt1,eta1,pt2,eta2,verbose=0):
        effs_leg1 = [x(pt1,eta1,verbose-1) for x in self._singleEl, self._doubleElHighPt, self._doubleElLowPt]
        effs_leg2 = [x(pt2,eta2,verbose-1) for x in self._singleEl, self._doubleElHighPt, self._doubleElLowPt]
        p0 = effs_leg1[0]
        p1 = effs_leg1[1]
        p2 = effs_leg1[2]
        q0 = effs_leg2[0]
        q1 = effs_leg2[1]
        q2 = effs_leg2[2]
        eff = p0 + (1-p0)*q0 + (1-p0)*(1-q0)*(p1*q2 + (1-p1*q2)*p2*q1)
        return eff

class ElMuEventEfficiency:
    def __init__(self,legs,mode="default"):
        self._mode   = mode
        if mode != "onlyDouble":
            self._singleEl = legs["SingleEl"] if "SingleEl" in legs else ZeroEfficiency("NoSingleEl")
            self._singleMu = legs["SingleMu"] if "SingleMu" in legs else ZeroEfficiency("NoSingleMu")
        else:
            self._singleEl = ZeroEfficiency()
            self._singleMu = ZeroEfficiency()
        if "Mu13leg_Mu8" in legs:
            self._doubleMuHighPt = legs["Mu13leg_Mu8"]
            self._doubleMuLowPt  = legs["Mu13_Mu8leg"]
        elif "Mu17_Mu8_Mu17Leg" in legs:
            self._doubleMuHighPt = legs["Mu17_Mu8_Mu17Leg"]
            self._doubleMuLowPt  = legs["Mu17_Mu8_Mu8Leg"]
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
        p0 = effs_leg1[0]
        p1 = effs_leg1[1]
        p2 = effs_leg1[2]
        q0 = effs_leg2[0]
        q1 = effs_leg2[1]
        q2 = effs_leg2[2]
        eff = p0 + (1-p0)*q0 + (1-p0)*(1-q0)*(p1*q2 + (1-p1*q2)*p2*q1)
        return eff

class LuminosityWeightedAverage:
    def __init__(self,lumiEffPairs):
        norm = sum([lumi for lumi,eff in lumiEffPairs])
        self._pairs = [ (lumi/norm, eff) for (lumi,eff) in lumiEffPairs]
    def __call__(self,pt1,eta1,pt2,eta2,verbose):
        avg = 0
        for (w,eff) in self._pairs:
            avg += w*eff(pt1,eta1,pt2,eta2,verbose)
        return avg


