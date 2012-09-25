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
#       _ \                       |          ___|  |                           | _)  |           | _)  |                        |
#      |   |  |   |   _` |   __|  |  /      |      |  |   |   _ \   __ \       |  |  |  /   _ \  |  |  __ \    _ \    _ \    _` |
#      |   |  |   |  (   |  |       <       |   |  |  |   |  (   |  |   |      |  |    <    __/  |  |  | | |  (   |  (   |  (   |
#     \__\_\ \__,_| \__,_| _|    _|\_\     \____| _| \__,_| \___/  _|  _|     _| _| _|\_\ \___| _| _| _| |_| \___/  \___/  \__,_|
#
#
#



#
# Examples:
#
#  cd /HWWAnalysis/ShapeAnalysis
# source test/env.sh
#
# gardener.py  likelihoodQGVar  /data2/amassiro/VBF/Data/All21Aug2012_temp_1/latino_990_T2tt.root    /data2/amassiro/VBF/Data/All21Aug2012_temp_2/latino_990_T2tt_TESTIFITWORKS.root
#
#


class likelihoodQGVarFiller(TreeCloner):


    def __init__(self):
        pass

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
        newbranches = ['jetQGLik1', 'jetQGLik2', 'jetQGLik3', 'jetQGLik4']
        self.clone(output,newbranches)

        jetQGLik1       = numpy.ones(1, dtype=numpy.float32)
        jetQGLik2       = numpy.ones(1, dtype=numpy.float32)
        jetQGLik3       = numpy.ones(1, dtype=numpy.float32)
        jetQGLik4       = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('jetQGLik1'      ,  jetQGLik1      ,  'jetQGLik1/F'    )
        self.otree.Branch('jetQGLik2'      ,  jetQGLik2      ,  'jetQGLik2/F'    )
        self.otree.Branch('jetQGLik3'      ,  jetQGLik3      ,  'jetQGLik3/F'    )
        self.otree.Branch('jetQGLik4'      ,  jetQGLik4      ,  'jetQGLik4/F'    )



        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree


        cmssw_base = os.getenv('CMSSW_BASE')
        ROOT.gSystem.Load("libFWCoreFWLite.so") 
        #ROOT.gROOT.ProcessLine('.L '+cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/likelihoodQG.C+')
        ROOT.gSystem.Load("libFWCoreFWLite.so")
        ROOT.gSystem.Load("libHWWAnalysisQuarkGluonTagger.so")
        # try ROOT.AutoLibraryLoader.enable()
        ROOT.gROOT.ProcessLine('AutoLibraryLoader::enable()')


        QGLikCalc = ROOT.QGLikelihoodCalculator("data/QGTaggerConfig_nCharged_AK5PF.txt","data/QGTaggerConfig_nNeutral_AK5PF.txt","data/QGTaggerConfig_ptD_AK5PF.txt")

        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            jetRho = itree.jetRho

            jetpt1 = itree.jetpt1
            jetCHM1 = int(itree.jetCHM1)
            jetPhM1 = int(itree.jetPhM1)
            jetNHM1 = int(itree.jetNHM1)
            jetptd1 = itree.jetptd1

            if jetpt1>0 :
                jetQGLik1[0] = QGLikCalc.computeQGLikelihood ( jetpt1, jetRho, jetCHM1, jetNHM1+jetPhM1, jetptd1 )
                #jetQGLik1[0] = QGLikCalc.computeQGLikelihood ( (float) jetpt1, (float) jetRho, (int) jetCHM1, (int) (jetNHM1+jetPhM1), (float) jetptd1 )            
            else :
                jetQGLik1[0] = -999.



            jetpt2 = itree.jetpt2
            jetCHM2 = int(itree.jetCHM2)
            jetPhM2 = int(itree.jetPhM2)
            jetNHM2 = int(itree.jetNHM2)
            jetptd2 = itree.jetptd2

            if jetpt2>0 :
                jetQGLik2[0] = QGLikCalc.computeQGLikelihood ( jetpt2, jetRho, jetCHM2, jetNHM2+jetPhM2, jetptd2 )
            else :
                jetQGLik2[0] = -999.




            jetpt3  = itree.jetpt3
            jetCHM3 = int(itree.jetCHM3)
            jetPhM3 = int(itree.jetPhM3)
            jetNHM3 = int(itree.jetNHM3)
            jetptd3 = itree.jetptd3

            if jetpt3>0 :
                jetQGLik3[0] = QGLikCalc.computeQGLikelihood ( jetpt3, jetRho, jetCHM3, jetNHM3+jetPhM3, jetptd3 )
            else :
                jetQGLik3[0] = -999.




            jetpt4 = itree.jetpt4
            jetCHM4 = int(itree.jetCHM4)
            jetPhM4 = int(itree.jetPhM4)
            jetNHM4 = int(itree.jetNHM4)
            jetptd4 = itree.jetptd4

            if jetpt4>0 :
                jetQGLik4[0] = QGLikCalc.computeQGLikelihood ( jetpt4, jetRho, jetCHM4, jetNHM4+jetPhM4, jetptd4 )
            else :
                jetQGLik4[0] = -999.




            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'






