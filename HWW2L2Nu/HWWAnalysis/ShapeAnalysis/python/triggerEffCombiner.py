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
            m = re.match(r"2012[AB]?_(\d+)-(\d+)_(\w+)_(barrel|endcap|forward)\s+.*", line)
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
            self._single = legs["SingleMu"] if "SingleMu" in legs else ZeroEfficiency("NoSingleMu")
        else:
            self._single = ZeroEfficiency()
        if "Mu13leg_Mu8" in legs:
            self._doubleHighPt = legs["Mu13leg_Mu8"]
            self._doubleLowPt  = legs["Mu13_Mu8leg"]
        elif "Mu17_Mu8_Mu17Leg" in legs:
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
            print "  - %6.2f%% plus double with lead high pt mu" % (100*sum(eff[0:2]))
            print "  - %6.2f%% plus double with low pt mu" % (100*sum(eff[0:3]))
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


