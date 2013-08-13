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
#
#             |        |        |   | _)
#             |   _ \  __|      |   |  |   _` |   _` |   __|
#         \   |   __/  |        ___ |  |  (   |  (   | \__ \
#        \___/  \___| \__|     _|  _| _| \__, | \__, | ____/
#                                        |___/  |___/
#
#
#



#
# Examples:
#
#  cd /HWWAnalysis/ShapeAnalysis
# source test/env.sh
#
# gardener.py  jetHiggsVar  /data2/amassiro/VBF/Data/All21Aug2012_temp_1/latino_2000_ggToH1000toWWTo2LAndTau2Nu.root    /data2/amassiro/VBF/Data/All21Aug2012_temp_2/latino_2000_ggToH1000toWWTo2LAndTau2Nu_TESTISITWORKING.root
#
#


class JetHiggsVarFiller(TreeCloner):


    def __init__(self):
        pass

    def help(self):
        return '''Add new jet system - Higgs variables'''


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
        newbranches = ['dphiHj', 'dphiHjj', 'ptJoptH', 'ptJJoptH', 'ptllmet']
        self.clone(output,newbranches)

        dphiHj         = numpy.ones(1, dtype=numpy.float32)
        dphiHjj        = numpy.ones(1, dtype=numpy.float32)
        ptJoptH        = numpy.ones(1, dtype=numpy.float32)
        ptJJoptH       = numpy.ones(1, dtype=numpy.float32)
        ptllmet        = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('dphiHj'        ,  dphiHj        ,  'dphiHj/F'      )
        self.otree.Branch('dphiHjj'       ,  dphiHjj       ,  'dphiHjj/F'     )
        self.otree.Branch('ptJoptH'       ,  ptJoptH       ,  'ptJoptH/F'     )
        self.otree.Branch('ptJJoptH'      ,  ptJJoptH      ,  'ptJJoptH/F'    )
        self.otree.Branch('ptllmet'       ,  ptllmet       ,  'ptllmet/F'     )



        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree

        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            jetpt1 = itree.jetpt1
            jetphi1 = itree.jetphi1

            pt1 = itree.pt1
            phi1 = itree.phi1

            pfmet = itree.pfmet
            pfmetphi = itree.pfmetphi

            jetpt2 = itree.jetpt2
            jetphi2 = itree.jetphi2

            pt2 = itree.pt2
            phi2 = itree.phi2


            ptjj = -999
            if jetpt1>0 and jetpt2>0 :
                ptjj = sqrt((jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))*(jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))+(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2))*(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2)))

            ptH = sqrt((pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi))*(pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi))+(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi))*(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi)))

            ptllmet[0] = ptH
            ptJJoptH[0] = -999
            if jetpt1>0 and jetpt2>0 :
                if ptH != 0:
                   ptJJoptH[0] = ptjj / ptH
                else :
                   ptJJoptH[0] = -1

            ptJoptH[0] = -999
            if jetpt1>0:
                if ptH != 0:
                   ptJoptH[0] = jetpt1 / ptH
                else :
                   ptJoptH[0] = -1


# (abs(UNO-DUE)>3.14159266)*(2*3.14159265-abs(UNO-DUE))+(abs(UNO-DUE)<3.14159266)*(abs(UNO-DUE))
#

            pi = ROOT.TMath.Pi()
            dphiHjj[0] = -999
            if jetpt1>0 and jetpt2>0 :
               dphiHjj[0] = (abs(atan2(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2),jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))-atan2(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi),pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi)))>pi)*(2*pi-abs(atan2(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2),jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))-atan2(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi),pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi))))+(abs(atan2(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2),jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))-atan2(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi),pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi)))<pi)*(abs(atan2(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2),jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))-atan2(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi),pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi))))

            dphiHj[0] = -999
            if jetpt1>0 :
               dphiHj[0] = (abs(atan2(sin(jetphi1),cos(jetphi1))-atan2(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi),pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi)))>pi)*(2*pi-abs(atan2(sin(jetphi1),cos(jetphi1))-atan2(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi),pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi))))+(abs(atan2(sin(jetphi1),cos(jetphi1))-atan2(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi),pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi)))<pi)*(abs(atan2(sin(jetphi1),cos(jetphi1))-atan2(pt1*sin(phi1)+pt2*sin(phi2)+pfmet*sin(pfmetphi),pt1*cos(phi1)+pt2*cos(phi2)+pfmet*cos(pfmetphi))))


            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'






