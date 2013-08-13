from tree.gardening import TreeCloner


import optparse
import sys
import ROOT
import numpy
import re
import os.path
import math
from math import *
from array import array;


#
#
#   \  |                               |        |        |   | _)
#  |\/ |   _` |  __ \   |   |          |   _ \  __|      |   |  |   _` |   _` |   __|
#  |   |  (   |  |   |  |   |      \   |   __/  |        ___ |  |  (   |  (   | \__ \
# _|  _| \__,_| _|  _| \__, |     \___/  \___| \__|     _|  _| _| \__, | \__, | ____/
#                      ____/                                      |___/  |___/ 
#
#



#
# Examples:
#
#  cd /HWWAnalysis/ShapeAnalysis
# source test/env.sh
#
# gardener.py  manyJetHiggsVar  /data2/amassiro/VBF/Data/All21Aug2012_temp_1/latino_2000_ggToH1000toWWTo2LAndTau2Nu.root    /data2/amassiro/VBF/Data/All21Aug2012_temp_2/latino_2000_ggToH1000toWWTo2LAndTau2Nu_TESTISITWORKING.root
#
#


class ManyJetsHiggsVarFiller(TreeCloner):

    
    def __init__(self):
        pass

    def help(self):
        return '''Add new many jets system - Higgs variables'''


    def addOptions(self,parser):
        #description = self.help()
        #group = optparse.OptionGroup(parser,self.label, description)
        #group.add_option('-b', '--branch',   dest='branch', help='Name of something that is not used ... ', default='boh')
        #parser.add_option_group(group)
        #return group
        pass


    def checkOptions(self,opts):
        pass

    @staticmethod
    def _deltamassw( jets ):
        mW = 80.385
        return math.fabs( mW - (jets[0] + jets[1]).M() )
        

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ['m4j', 'm3j', 'mW1jj', 'mW2jj', 'pt4j', 'pt3j', 'eta4j', 'eta3j', 'phi4j', 'phi3j', 'dphill4j',  'dphill3j', 'best1', 'best2']
        self.clone(output,newbranches)



        m4j           = numpy.ones(1, dtype=numpy.float32)
        m3j           = numpy.ones(1, dtype=numpy.float32)
        mW1jj         = numpy.ones(1, dtype=numpy.float32)
        mW2jj         = numpy.ones(1, dtype=numpy.float32)
        pt4j          = numpy.ones(1, dtype=numpy.float32)
        pt3j          = numpy.ones(1, dtype=numpy.float32)
        eta4j         = numpy.ones(1, dtype=numpy.float32)
        eta3j         = numpy.ones(1, dtype=numpy.float32)
        phi4j         = numpy.ones(1, dtype=numpy.float32)
        phi3j         = numpy.ones(1, dtype=numpy.float32)
        dphill4j      = numpy.ones(1, dtype=numpy.float32)
        dphill3j      = numpy.ones(1, dtype=numpy.float32)

        best1         = numpy.ones(1, dtype=numpy.float32)
        best2         = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('m4j'             ,  m4j           ,  'm4j/F'        )
        self.otree.Branch('m3j'             ,  m3j           ,  'm3j/F'        )
        self.otree.Branch('mW1jj'           ,  mW1jj         ,  'mW1jj/F'      )
        self.otree.Branch('mW2jj'           ,  mW2jj         ,  'mW2jj/F'      )
        self.otree.Branch('pt4j'            ,  pt4j          ,  'pt4j/F'       )
        self.otree.Branch('pt3j'            ,  pt3j          ,  'pt3j/F'       )
        self.otree.Branch('eta4j'           ,  eta4j         ,  'eta4j/F'      )
        self.otree.Branch('eta3j'           ,  eta3j         ,  'eta3j/F'      )
        self.otree.Branch('phi4j'           ,  phi4j         ,  'phi4j/F'      )
        self.otree.Branch('phi3j'           ,  phi3j         ,  'phi3j/F'      )
        self.otree.Branch('dphill4j'        ,  dphill4j      ,  'dphill4j/F'   )
        self.otree.Branch('dphill3j'        ,  dphill3j      ,  'dphill3j/F'   )

        self.otree.Branch('best1'           ,  best1         ,  'best1/F'   )
        self.otree.Branch('best2'           ,  best2         ,  'best2/F'   )

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
            jeteta1 = itree.jeteta1

            jetpt2 = itree.jetpt2
            jetphi2 = itree.jetphi2
            jeteta2 = itree.jeteta2

            jetpt3 = itree.jetpt3
            jetphi3 = itree.jetphi3
            jeteta3 = itree.jeteta3

            jetpt4 = itree.jetpt4
            jetphi4 = itree.jetphi4
            jeteta4 = itree.jeteta4

            jet1 = ROOT.TLorentzVector()
            jet1.SetPtEtaPhiM(itree.jetpt1, itree.jeteta1, itree.jetphi1, 0)
            jet2 = ROOT.TLorentzVector()
            jet2.SetPtEtaPhiM(itree.jetpt2, itree.jeteta2, itree.jetphi2, 0)
            jet3 = ROOT.TLorentzVector()
            jet3.SetPtEtaPhiM(itree.jetpt3, itree.jeteta3, itree.jetphi3, 0)
            jet4 = ROOT.TLorentzVector()
            jet4.SetPtEtaPhiM(itree.jetpt4, itree.jeteta4, itree.jetphi4, 0)

            jets = [jet1,jet2,jet3,jet4]

            jetSum4 = jet1 + jet2 + jet3 + jet4

            jetSum3 = jet1 + jet2 + jet3

            l1 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiE(itree.pt1, itree.eta1, itree.phi1, itree.pt1/sin(2*atan(exp(-itree.eta1))))

            l2 = ROOT.TLorentzVector()
            l2.SetPtEtaPhiE(itree.pt2, itree.eta2, itree.phi2, itree.pt2/sin(2*atan(exp(-itree.eta2))))

            ll = ROOT.TLorentzVector()
            ll = l1+l2;


            mW1jj[0]    = -999
            mW2jj[0]    = -999
            m4j[0]      = -999
            m3j[0]      = -999
            pt4j[0]     = -999
            pt3j[0]     = -999
            eta4j[0]    = -999
            eta3j[0]    = -999
            phi4j[0]    = -999
            phi3j[0]    = -999
            dphill4j[0] = -999
            dphill3j[0] = -999

            best1[0]    = -999
            best2[0]    = -999

            if (jetpt4 > 0) :
                m4j[0]      = jetSum4.M()
                pt4j[0]     = jetSum4.Pt()
                eta4j[0]    = jetSum4.Eta()
                phi4j[0]    = jetSum4.Phi()
                dphill4j[0] = jetSum4.DeltaPhi(ll)

                # list of all possible couples
                sjets = sorted([ (jets[i],jets[j]) for i in xrange(4) for j in xrange(4) if i<j], key=self._deltamassw)

#                 for jA,jB in sjets:
#                     print (jA+jB).M(),'->', self._deltamassw( (jA,jB) )

                # choose best pair: the pair with one of the two W-candidates nearest to MW 
                best = sjets[0]
                # the companion is made of the other 2 jets
                other = tuple( [j for j in jets if j not in best] )

                W1 = best[0] + best[1]
                W2 = other[0]+other[1]

                best1[0] = jets.index(best[0])
                best2[0] = jets.index(best[1])

                if W1.Pt() > W2.Pt() :
                    mW1jj[0] = W1.M()
                    mW2jj[0] = W2.M()
                else :
                    mW1jj[0] = W2.M()
                    mW2jj[0] = W1.M()


            if (jetpt3 > 0) :
                m3j[0]      = jetSum3.M()
                pt3j[0]     = jetSum3.Pt()
                eta3j[0]    = jetSum3.Eta()
                phi3j[0]    = jetSum3.Phi()
                dphill3j[0] = jetSum3.DeltaPhi(ll)


            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'






