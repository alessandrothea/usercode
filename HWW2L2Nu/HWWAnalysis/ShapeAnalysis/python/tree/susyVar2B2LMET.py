from tree.gardening import TreeCloner


import optparse
import sys
import ROOT
import numpy
import re
import warnings
import os.path
from math import *



#     ___|                          \ \     /            _)         |      |                             |      |
#   \___ \   |   |   __|  |   |      \ \   /  _` |   __|  |   _` |  __ \   |   _ \   __|       _` |   _` |   _` |   _ \   __|
#         |  |   | \__ \  |   |       \ \ /  (   |  |     |  (   |  |   |  |   __/ \__ \      (   |  (   |  (   |   __/  |
#   _____/  \__,_| ____/ \__, |        \_/  \__,_| _|    _| \__,_| _.__/  _| \___| ____/     \__,_| \__,_| \__,_| \___| _|
#                        ____/


class SusyVar2B2LMETFiller(TreeCloner):

    def __init__(self):
        pass

    def help(self):
        return '''Add new variables, mR, ... for 2jet + 2 leptons + met case '''


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
        newbranches = ['MR2B2LMET', 'deltaPhiR2B2LMET', 'deltaPhiBoostR2B2LMET'  ]

        self.clone(output,newbranches)

        MR2B2LMET               = numpy.ones(1, dtype=numpy.float32)
        deltaPhiR2B2LMET        = numpy.ones(1, dtype=numpy.float32)
        deltaPhiBoostR2B2LMET   = numpy.ones(1, dtype=numpy.float32)



        self.otree.Branch('MR2B2LMET',               MR2B2LMET,               'MR2B2LMET/F')
        self.otree.Branch('deltaPhiR2B2LMET',        deltaPhiR2B2LMET,        'deltaPhiR2B2LMET/F')
        self.otree.Branch('deltaPhiBoostR2B2LMET',   deltaPhiBoostR2B2LMET,   'deltaPhiBoostR2B2LMET/F')


        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree


        cmssw_base = os.getenv('CMSSW_BASE')
        #ROOT.gROOT.ProcessLine('.L '+cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/Razor_for_2B_2L_MET.C+')
        try:
             ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/Razor_for_2B_2L_MET.C+g')
        except RuntimeError:
             ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/Razor_for_2B_2L_MET.C++g')



        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            njet    = itree.njet

            if njet >= 2:

                jetpx1 = itree.jetpt1 * cos (itree.jetphi1)
                jetpy1 = itree.jetpt1 * sin (itree.jetphi1)
                jetpt1 = itree.jetpt1
                jetpz1 = itree.jetpt1 / tan ( 2. * atan ( exp ( -  itree.jeteta1) ))
                jetp1  = sqrt (jetpx1*jetpx1 + jetpy1*jetpy1 + jetpz1*jetpz1)

                jetpx2 = itree.jetpt2 * cos (itree.jetphi2)
                jetpy2 = itree.jetpt2 * sin (itree.jetphi2)
                jetpt2 = itree.jetpt2
                jetpz2 = itree.jetpt2 / tan ( 2. * atan ( exp ( -  itree.jeteta2) ))
                jetp2  = sqrt (jetpx2*jetpx2 + jetpy2*jetpy2 + jetpz2*jetpz2)


                px1 = itree.pt1 * cos (itree.phi1)
                py1 = itree.pt1 * sin (itree.phi1)
                pt1 = itree.pt1
                pz1 = itree.pt1 / tan ( 2. * atan ( exp ( -  itree.eta1) ))
                p1  = sqrt (px1*px1 + py1*py1 + pz1*pz1)

                px2 = itree.pt2 * cos (itree.phi2)
                py2 = itree.pt2 * sin (itree.phi2)
                pt2 = itree.pt2
                pz2 = itree.pt2 / tan ( 2. * atan ( exp ( -  itree.eta2) ))
                p2  = sqrt (px2*px2 + py2*py2 + pz2*pz2)


                #met = itree.pfmet
                #metx = met * cos (itree.pfmetphi)
                #mety = met * sin (itree.pfmetphi)

                # create 4-vectors & 3 vectors
                B1 = ROOT.TLorentzVector()
                B2 = ROOT.TLorentzVector()
                B1.SetPtEtaPhiM(itree.jetpt1, itree.jeteta1, itree.jetphi1, 0)
                B2.SetPtEtaPhiM(itree.jetpt2, itree.jeteta2, itree.jetphi2, 0)

                LA = ROOT.TLorentzVector()
                LB = ROOT.TLorentzVector()
                LA.SetPtEtaPhiM(itree.pt1, itree.eta1, itree.phi1, 0)
                LB.SetPtEtaPhiM(itree.pt2, itree.eta2, itree.phi2, 0)


                # jet 1 --> lepton A
                # jet 2 --> lepton B
                #
                # combination with squared sum of invariant mass of "lepton-jet" system smaller
                #

                massAB = ((B1+LA).Mag2() + (B2+LB).Mag2())
                massBA = ((B1+LB).Mag2() + (B2+LA).Mag2())


                L1 = ROOT.TLorentzVector()
                L2 = ROOT.TLorentzVector()

                if (massAB < massBA) :
                    L1.SetPtEtaPhiM(itree.pt1, itree.eta1, itree.phi1, 0)
                    L2.SetPtEtaPhiM(itree.pt2, itree.eta2, itree.phi2, 0)
                else :
                    L1.SetPtEtaPhiM(itree.pt2, itree.eta2, itree.phi2, 0)
                    L2.SetPtEtaPhiM(itree.pt1, itree.eta1, itree.phi1, 0)


                MET = ROOT.TVector3()
                MET.SetPtEtaPhi(itree.pfmet, 0, itree.pfmetphi)

                # now calculate variavbles
                MR2B2LMET[0] = ROOT.CalcMRNEW(B1,  B2,  L1,  L2,  MET)
                deltaPhiR2B2LMET[0] = ROOT.CalcDeltaPhiRFRAME( B1,  B2,  L1,  L2,  MET)
                deltaPhiBoostR2B2LMET[0] = ROOT.CalcDoubleDphiRFRAME( B1,  B2,  L1,  L2,  MET)

            else :
                MR2B2LMET[0] = -999.
                deltaPhiR2B2LMET[0] = -999.
                deltaPhiBoostR2B2LMET[0]   = -999.

            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



