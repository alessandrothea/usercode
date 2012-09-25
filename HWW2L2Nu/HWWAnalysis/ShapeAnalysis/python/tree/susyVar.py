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


class SusyVarFiller(TreeCloner):

    def __init__(self):
        pass

#     @staticmethod
    def _getMR(self,pA, pzA, pxA, pyA, pB, pzB, pxB, pyB):

        A = pA
        B = pB
        az = pzA
        bz = pzB
        jaT = ROOT.TVector3()
        jbT = ROOT.TVector3()
        jaT.SetXYZ(pxA,pyA,0.0)
        jbT.SetXYZ(pxB,pyB,0.0)
        ATBT = (jaT+jbT).Mag2()
        temp = sqrt((A+B)*(A+B)-(az+bz)*(az+bz)-  (jbT.Dot(jbT)-jaT.Dot(jaT))*(jbT.Dot(jbT)-jaT.Dot(jaT))/(jaT+jbT).Mag2())
        mybeta = (jbT.Dot(jbT)-jaT.Dot(jaT))/sqrt(ATBT*((A+B)*(A+B)-(az+bz)*(az+bz)))
        mygamma = 1./sqrt(1.-mybeta*mybeta)
        # gamma times MRstar                                                                                                                                                         \
        temp *= mygamma
        return temp


#     @staticmethod
    def _getMTR(self, ptA, pxA, pyA, ptB, pxB, pyB, met, metx, mety):
        temp = met * (ptA + ptB) - ( metx*(pxA+pxB) + mety*(pyA+pyB) )
        temp /= 2.
        temp = sqrt(temp)
        return temp


    def help(self):
        return '''Add new variables, mR, MRT, ...'''


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
        newbranches = ['MR2j', 'MTR2j', 'R2j', 'unboostedMR2j', 'dphillRframe2j', 'dphillHRframe2j', 'unboostedMTR2j', 'unboostedR2j'  ]
        self.clone(output,newbranches)

        MR2j  = numpy.ones(1, dtype=numpy.float32)
        MTR2j = numpy.ones(1, dtype=numpy.float32)
        R2j   = numpy.ones(1, dtype=numpy.float32)

        unboostedMR2j    = numpy.ones(1, dtype=numpy.float32)
        dphillRframe2j   = numpy.ones(1, dtype=numpy.float32)
        dphillHRframe2j  = numpy.ones(1, dtype=numpy.float32)
        unboostedMTR2j   = numpy.ones(1, dtype=numpy.float32)
        unboostedR2j     = numpy.ones(1, dtype=numpy.float32)




        self.otree.Branch('MR2j',  MR2j,  'MR2j/F')
        self.otree.Branch('MTR2j', MTR2j, 'MTR2j/F')
        self.otree.Branch('R2j',   R2j,   'R2j/F')

        self.otree.Branch('unboostedMR2j',    unboostedMR2j,    'unboostedMR2j/F')
        self.otree.Branch('dphillRframe2j' ,  dphillRframe2j ,  'dphillRframe2j/F' )
        self.otree.Branch('dphillHRframe2j',  dphillHRframe2j,  'dphillHRframe2j/F')
        self.otree.Branch('unboostedMTR2j',   unboostedMTR2j,   'unboostedMTR2j/F')
        self.otree.Branch('unboostedR2j',     unboostedR2j,     'unboostedR2j/F')



        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree
        getMR     = self._getMR
        getMTR    = self._getMTR


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


                met = itree.pfmet
                metx = met * cos (itree.pfmetphi)
                mety = met * sin (itree.pfmetphi)

                # add lepton contribution as if I did not measure leptons
                metx = metx + px1 + px2
                mety = mety + py1 + py2
                met = sqrt( metx*metx + mety*mety )

                MR2j[0]  = getMR(jetp1, jetpz1, jetpx1, jetpy1, jetp2, jetpz2, jetpx2, jetpy2)
                MTR2j[0]  = getMTR(jetpt1, jetpx1, jetpy1, jetpt2, jetpx2, jetpy2, met, metx, mety)
                R2j[0]   = MTR2j[0] / MR2j[0]


                v1 = ROOT.TLorentzVector()
                v2 = ROOT.TLorentzVector()
                v1.SetPtEtaPhiM(itree.jetpt1, itree.jeteta1, itree.jetphi1, 0)
                v2.SetPtEtaPhiM(itree.jetpt2, itree.jeteta2, itree.jetphi2, 0)

                vmet = ROOT.TVector3()
                # add leptons to met since I consider "unseen" the leptons
                vmet.SetXYZ(metx + px1 + px2, mety + py1 + py2, 0.)

                hwwKin = ROOT.HWWKinematics(v1, v2, vmet)

                unboostedMR2j[0]     = hwwKin.CalcMRNEW()
                dphillRframe2j[0]    = hwwKin.CalcDeltaPhiRFRAME()
                dphillHRframe2j[0]   = hwwKin.CalcDoubleDphiRFRAME()

                unboostedMTR2j[0] = hwwKin.CalcUnboostedMTR(v1, v2, vmet)
                unboostedR2j[0]   = hwwKin.CalcRNEW(v1, v2, vmet)




            else :
                MR2j[0]  = -999.
                MTR2j[0] = -999.
                R2j[0]   = -999.
                unboostedMR2j[0]   = -999.

                unboostedMR2j[0]     = -999.
                dphillRframe2j[0]    = -999.
                dphillHRframe2j[0]   = -999.

                unboostedMTR2j[0] = -999.
                unboostedR2j[0]   = -999.



            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



