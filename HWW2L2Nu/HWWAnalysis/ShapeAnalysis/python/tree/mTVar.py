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




#              __ __| ___ \
#      __ `__ \   |      ) |
#      |   |   |  |     __/
#     _|  _|  _| _|   _____|
#


class MTVarFiller(TreeCloner):


    def __init__(self):
        pass

#     @staticmethod
    def _getMT2(self, pxl1, pyl1, pxl2, pyl2, metx, mety):

        mt2 = ROOT.mT2(pxl1, pyl1, pxl2, pyl2, metx, mety)

        return mt2


    def help(self):
        return '''Add new variables, MT2, ...'''


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
        newbranches = ['MT2']
        self.clone(output,newbranches)

        MT2  = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('MT2',  MT2,  'MT2/F')


        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree
        getMT2     = self._getMT2


        cmssw_base = os.getenv('CMSSW_BASE')
        try:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/mT2.C+g')
        except RuntimeError:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/mT2.C++g')

        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            pl1  = itree.pt1 / sin ( 2. * atan ( exp ( -  itree.eta1) ))
            pxl1 = itree.pt1 * cos (itree.phi1)
            pyl1 = itree.pt1 * sin (itree.phi1)

            pl2  = itree.pt2 / sin ( 2. * atan ( exp ( -  itree.eta2) ))
            pxl2 = itree.pt2 * cos (itree.phi2)
            pyl2 = itree.pt2 * sin (itree.phi2)

            met = itree.pfmet
            metx = met * cos (itree.pfmetphi)
            mety = met * sin (itree.pfmetphi)

            MT2[0] = ROOT.mT2(pxl1, pyl1, pxl2, pyl2, metx, mety)

            #getMT2(pxl1, pyl1, pxl2, pyl2, metx, mety)

            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



