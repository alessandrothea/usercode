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
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        group.add_option('-b', '--branch',   dest='branch', help='Name of something that is not used ... ', default='boh')
        parser.add_option_group(group)
        return group


    def checkOptions(self,opts):
        pass

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ['MR2j', 'MTR2j', 'R2j']
        self.clone(output,newbranches)

        MR2j  = numpy.ones(1, dtype=numpy.float32)
        MTR2j = numpy.ones(1, dtype=numpy.float32)
        R2j   = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('MR2j',  MR2j,  'MR2j/F')
        self.otree.Branch('MTR2j', MTR2j, 'MTR2j/F')
        self.otree.Branch('R2j',   R2j,   'R2j/F')


        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree
        getMR     = self._getMR
        getMTR    = self._getMTR

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

                met = itree.pfmet
                metx = met * cos (itree.pfmetphi)
                mety = met * sin (itree.pfmetphi)

                MR2j[0]  = getMR(jetp1, jetpz1, jetpx1, jetpy1, jetp2, jetpz2, jetpx2, jetpy2)
                MTR2j[0]  = getMTR(jetpt1, jetpx1, jetpy1, jetpt2, jetpx2, jetpy2, met, metx, mety)
                R2j[0]   = MTR2j[0] / MR2j[0]
            else :
                MR2j[0]  = -999.
                MTR2j[0] = -999.
                R2j[0]   = -999.
            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



