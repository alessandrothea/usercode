from tree.gardening import TreeCloner


import optparse
import sys
import ROOT
import numpy
import re
import warnings
import os.path
from math import *
from array import array;



#
#
#                    __ )                       |              |     \ \     /            _)         |      |
#      |   |  __ \   __ \    _ \    _ \    __|  __|   _ \   _` |      \ \   /  _` |   __|  |   _` |  __ \   |   _ \   __|
#      |   |  |   |  |   |  (   |  (   | \__ \  |     __/  (   |       \ \ /  (   |  |     |  (   |  |   |  |   __/ \__ \
#     \__,_| _|  _| ____/  \___/  \___/  ____/ \__| \___| \__,_|        \_/  \__,_| _|    _| \__,_| _.__/  _| \___| ____/
#
#



#
# Examples:
#
#  cd /HWWAnalysis/ShapeAnalysis
# source test/env.sh
#
# gardener.py  unBoostedVar  /data2/amassiro/VBF/Data/All21Aug2012_temp_1/latino_085_WgammaToLNuG.root  /data2/amassiro/VBF/Data/All21Aug2012_temp_2/latino_085_WgammaToLNuG_TESTIFITWORKS.root 
#
#


class UnBoostedVarFiller(TreeCloner):


    def __init__(self):
        pass

#     @staticmethod
    def _getMT2(self, pxl1, pyl1, pxl2, pyl2, metx, mety):

        mt2 = ROOT.mT2(pxl1, pyl1, pxl2, pyl2, metx, mety)

        return mt2


    def help(self):
        return '''Add new unboosted variables'''


    def addOptions(self,parser):
        #description = self.help()
        #group = optparse.OptionGroup(parser,self.label, description)
        #group.add_option('-b', '--branch',   dest='branch', help='Name of something that is not used ... ', default='boh')
        #parser.add_option_group(group)
        #return group
        pass


    def checkOptions(self,opts):
        pass

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ['boostedMR', 'unboostedMR', 'dphillRframe','dphillHRframe']
        self.clone(output,newbranches)

        boostedMR      = numpy.ones(1, dtype=numpy.float32)
        unboostedMR    = numpy.ones(1, dtype=numpy.float32)
        dphillRframe   = numpy.ones(1, dtype=numpy.float32)
        dphillHRframe  = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('boostedMR'    ,  boostedMR    ,  'boostedMR/F'    )
        self.otree.Branch('unboostedMR'  ,  unboostedMR  ,  'unboostedMR/F'  )
        self.otree.Branch('dphillRframe' ,  dphillRframe ,  'dphillRframe/F' )
        self.otree.Branch('dphillHRframe',  dphillHRframe,  'dphillHRframe/F')


        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree
        getMT2     = self._getMT2


        cmssw_base = os.getenv('CMSSW_BASE')
        try:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/unBoostedVar.C+g')
        except RuntimeError:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/unBoostedVar.C++g')


        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(itree.pt1, itree.eta1, itree.phi1, 0)
            l2.SetPtEtaPhiM(itree.pt2, itree.eta2, itree.phi2, 0)

            modmet = itree.pfmet
            metx = modmet * cos (itree.pfmetphi)
            mety = modmet * sin (itree.pfmetphi)
            met = ROOT.TVector3()
            met.SetXYZ(metx, mety, 0.)


            hwwKin = ROOT.HWWKinematics(l1, l2, met)


            boostedMR[0]     = hwwKin.CalcMR()
            unboostedMR[0]   = hwwKin.CalcMRNEW()
            dphillRframe[0]  = hwwKin.CalcDeltaPhiRFRAME()
            dphillHRframe[0] = hwwKin.CalcDoubleDphiRFRAME()


            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'






