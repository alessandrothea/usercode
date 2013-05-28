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

        cmssw_base = os.getenv('CMSSW_BASE')
        ROOT.gSystem.Load("libFWCoreFWLite.so") 
        ROOT.gSystem.Load("libFWCoreFWLite.so")
        ROOT.gSystem.Load("libQuarkGluonTaggerEightTeV.so")
        ROOT.gROOT.ProcessLine('AutoLibraryLoader::enable()')

        QGLikCalc   = ROOT.QGLikelihoodCalculator("/data2/amassiro/VBF/Summer12/21May2013/CMSSW_5_3_9_patch1/src/QuarkGluonTagger/EightTeV/data/")
        QGLikCalcQC = ROOT.QGLikelihoodCalculator("/data2/amassiro/VBF/Summer12/21May2013/CMSSW_5_3_9_patch1/src/QuarkGluonTagger/EightTeV/data/",True)
        #                       const TString dataDir, Bool_t chs

        QGMLPCalc   = ROOT.QGMLPCalculator("MLP","/data2/amassiro/VBF/Summer12/21May2013/CMSSW_5_3_9_patch1/src/QuarkGluonTagger/EightTeV/data/")

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ['jetQGLik1', 'jetQGLikQC1','jetQGLik2', 'jetQGLikQC2','jetQGLik3', 'jetQGLikQC3','jetQGLik4', 'jetQGLikQC4','jetQGLik5', 'jetQGLikQC5','jetQGLik6', 'jetQGLikQC6','jetQGLik7', 'jetQGLikQC7']
        self.clone(output,newbranches)
        newbranchesM = ['jetQGMLP1', 'jetQGMLPQC1','jetQGMLP2', 'jetQGMLPQC2','jetQGMLP3', 'jetQGMLPQC3','jetQGMLP4', 'jetQGMLPQC4','jetQGMLP5', 'jetQGMLPQC5','jetQGMLP6', 'jetQGMLPQC6','jetQGMLP7', 'jetQGMLPQC7']
        self.clone(output,newbranchesM)

        jetQGLik1       = numpy.ones(1, dtype=numpy.float32)
        jetQGLikQC1     = numpy.ones(1, dtype=numpy.float32)
        jetQGLik2       = numpy.ones(2, dtype=numpy.float32)
        jetQGLikQC2     = numpy.ones(2, dtype=numpy.float32)
        jetQGLik3       = numpy.ones(3, dtype=numpy.float32)
        jetQGLikQC3     = numpy.ones(3, dtype=numpy.float32)
        jetQGLik4       = numpy.ones(4, dtype=numpy.float32)
        jetQGLikQC4     = numpy.ones(4, dtype=numpy.float32)
        jetQGLik5       = numpy.ones(5, dtype=numpy.float32)
        jetQGLikQC5     = numpy.ones(5, dtype=numpy.float32)
        jetQGLik6       = numpy.ones(6, dtype=numpy.float32)
        jetQGLikQC6     = numpy.ones(6, dtype=numpy.float32)
        jetQGLik7       = numpy.ones(7, dtype=numpy.float32)
        jetQGLikQC7     = numpy.ones(7, dtype=numpy.float32)

        self.otree.Branch('jetQGLik1'      ,  jetQGLik1      ,  'jetQGLik1/F'    )
        self.otree.Branch('jetQGLikQC1'    ,  jetQGLikQC1    ,  'jetQGLikQC1/F'    )

        self.otree.Branch('jetQGLik2'      ,  jetQGLik2      ,  'jetQGLik2/F'    )
        self.otree.Branch('jetQGLikQC2'    ,  jetQGLikQC2    ,  'jetQGLikQC2/F'    )

        self.otree.Branch('jetQGLik3'      ,  jetQGLik3      ,  'jetQGLik3/F'    )
        self.otree.Branch('jetQGLikQC3'    ,  jetQGLikQC3    ,  'jetQGLikQC3/F'    )

        self.otree.Branch('jetQGLik4'      ,  jetQGLik4      ,  'jetQGLik4/F'    )
        self.otree.Branch('jetQGLikQC4'    ,  jetQGLikQC4    ,  'jetQGLikQC4/F'    )

        self.otree.Branch('jetQGLik5'      ,  jetQGLik5      ,  'jetQGLik5/F'    )
        self.otree.Branch('jetQGLikQC5'    ,  jetQGLikQC5    ,  'jetQGLikQC5/F'    )

        self.otree.Branch('jetQGLik6'      ,  jetQGLik6      ,  'jetQGLik6/F'    )
        self.otree.Branch('jetQGLikQC6'    ,  jetQGLikQC6    ,  'jetQGLikQC6/F'    )

        self.otree.Branch('jetQGLik7'      ,  jetQGLik7      ,  'jetQGLik7/F'    )
        self.otree.Branch('jetQGLikQC7'    ,  jetQGLikQC7    ,  'jetQGLikQC7/F'    )


        jetQGMLP1       = numpy.ones(1, dtype=numpy.float32)
        jetQGMLPQC1     = numpy.ones(1, dtype=numpy.float32)
        jetQGMLP2       = numpy.ones(2, dtype=numpy.float32)
        jetQGMLPQC2     = numpy.ones(2, dtype=numpy.float32)
        jetQGMLP3       = numpy.ones(3, dtype=numpy.float32)
        jetQGMLPQC3     = numpy.ones(3, dtype=numpy.float32)
        jetQGMLP4       = numpy.ones(4, dtype=numpy.float32)
        jetQGMLPQC4     = numpy.ones(4, dtype=numpy.float32)
        jetQGMLP5       = numpy.ones(5, dtype=numpy.float32)
        jetQGMLPQC5     = numpy.ones(5, dtype=numpy.float32)
        jetQGMLP6       = numpy.ones(6, dtype=numpy.float32)
        jetQGMLPQC6     = numpy.ones(6, dtype=numpy.float32)
        jetQGMLP7       = numpy.ones(7, dtype=numpy.float32)
        jetQGMLPQC7     = numpy.ones(7, dtype=numpy.float32)

        self.otree.Branch('jetQGMLP1'      ,  jetQGMLP1      ,  'jetQGMLP1/F'    )
        self.otree.Branch('jetQGMLPQC1'    ,  jetQGMLPQC1    ,  'jetQGMLPQC1/F'    )

        self.otree.Branch('jetQGMLP2'      ,  jetQGMLP2      ,  'jetQGMLP2/F'    )
        self.otree.Branch('jetQGMLPQC2'    ,  jetQGMLPQC2    ,  'jetQGMLPQC2/F'    )

        self.otree.Branch('jetQGMLP3'      ,  jetQGMLP3      ,  'jetQGMLP3/F'    )
        self.otree.Branch('jetQGMLPQC3'    ,  jetQGMLPQC3    ,  'jetQGMLPQC3/F'    )

        self.otree.Branch('jetQGMLP4'      ,  jetQGMLP4      ,  'jetQGMLP4/F'    )
        self.otree.Branch('jetQGMLPQC4'    ,  jetQGMLPQC4    ,  'jetQGMLPQC4/F'    )

        self.otree.Branch('jetQGMLP5'      ,  jetQGMLP5      ,  'jetQGMLP5/F'    )
        self.otree.Branch('jetQGMLPQC5'    ,  jetQGMLPQC5    ,  'jetQGMLPQC5/F'    )

        self.otree.Branch('jetQGMLP6'      ,  jetQGMLP6      ,  'jetQGMLP6/F'    )
        self.otree.Branch('jetQGMLPQC6'    ,  jetQGMLPQC6    ,  'jetQGMLPQC6/F'    )

        self.otree.Branch('jetQGMLP7'      ,  jetQGMLP7      ,  'jetQGMLP7/F'    )
        self.otree.Branch('jetQGMLPQC7'    ,  jetQGMLPQC7    ,  'jetQGMLPQC7/F'    )



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

            jetRho = itree.jetRho

            if itree.jetpt1>0 :
                number   = int (itree.jetNChgptCut1 + itree.jetNNeutralptCut1)
                jetQGLik1[0]   = QGLikCalc.computeQGLikelihood2012(itree.jetpt1,   itree.jeteta1, jetRho,  number, itree.jetptD1,   itree.jetaxis21)
                numberQC = int (itree.jetNChgQC1 + itree.jetNNeutralptCut1)
                jetQGLikQC1[0] = QGLikCalcQC.computeQGLikelihood2012(itree.jetpt1, itree.jeteta1, jetRho,  number, itree.jetQCptD1, itree.jetQCaxis21)
            else :
                jetQGLik1[0]   = -999.
                jetQGLikQC1[0] = -999.

            if itree.jetpt2>0 :
                number   = int (itree.jetNChgptCut2 + itree.jetNNeutralptCut2)
                jetQGLik2[0]   = QGLikCalc.computeQGLikelihood2012(itree.jetpt2,   itree.jeteta2, jetRho,  number, itree.jetptD2,   itree.jetaxis22)
                numberQC = int (itree.jetNChgQC2 + itree.jetNNeutralptCut2)
                jetQGLikQC2[0] = QGLikCalcQC.computeQGLikelihood2012(itree.jetpt2, itree.jeteta2, jetRho,  number, itree.jetQCptD2, itree.jetQCaxis22)
            else :
                jetQGLik2[0]   = -999.
                jetQGLikQC2[0] = -999.

            if itree.jetpt3>0 :
                number   = int (itree.jetNChgptCut3 + itree.jetNNeutralptCut3)
                jetQGLik3[0]   = QGLikCalc.computeQGLikelihood2012(itree.jetpt3,   itree.jeteta3, jetRho,  number, itree.jetptD3,   itree.jetaxis23)
                numberQC = int (itree.jetNChgQC3 + itree.jetNNeutralptCut3)
                jetQGLikQC3[0] = QGLikCalcQC.computeQGLikelihood2012(itree.jetpt3, itree.jeteta3, jetRho,  number, itree.jetQCptD3, itree.jetQCaxis23)
            else :
                jetQGLik3[0]   = -999.
                jetQGLikQC3[0] = -999.

            if itree.jetpt4>0 :
                number   = int (itree.jetNChgptCut4 + itree.jetNNeutralptCut4)
                jetQGLik4[0]   = QGLikCalc.computeQGLikelihood2012(itree.jetpt4,   itree.jeteta4, jetRho,  number, itree.jetptD4,   itree.jetaxis24)
                numberQC = int (itree.jetNChgQC4 + itree.jetNNeutralptCut4)
                jetQGLikQC4[0] = QGLikCalcQC.computeQGLikelihood2012(itree.jetpt4, itree.jeteta4, jetRho,  number, itree.jetQCptD4, itree.jetQCaxis24)
            else :
                jetQGLik4[0]   = -999.
                jetQGLikQC4[0] = -999.

            if itree.jetpt5>0 :
                number   = int (itree.jetNChgptCut5 + itree.jetNNeutralptCut5)
                jetQGLik5[0]   = QGLikCalc.computeQGLikelihood2012(itree.jetpt5,   itree.jeteta5, jetRho,  number, itree.jetptD5,   itree.jetaxis25)
                numberQC = int (itree.jetNChgQC5 + itree.jetNNeutralptCut5)
                jetQGLikQC5[0] = QGLikCalcQC.computeQGLikelihood2012(itree.jetpt5, itree.jeteta5, jetRho,  number, itree.jetQCptD5, itree.jetQCaxis25)
            else :
                jetQGLik5[0]   = -999.
                jetQGLikQC5[0] = -999.

            if itree.jetpt6>0 :
                number   = int (itree.jetNChgptCut6 + itree.jetNNeutralptCut6)
                jetQGLik6[0]   = QGLikCalc.computeQGLikelihood2012(itree.jetpt6,   itree.jeteta6, jetRho,  number, itree.jetptD6,   itree.jetaxis26)
                numberQC = int (itree.jetNChgQC6 + itree.jetNNeutralptCut6)
                jetQGLikQC6[0] = QGLikCalcQC.computeQGLikelihood2012(itree.jetpt6, itree.jeteta6, jetRho,  number, itree.jetQCptD6, itree.jetQCaxis26)
            else :
                jetQGLik6[0]   = -999.
                jetQGLikQC6[0] = -999.

            if itree.jetpt7>0 :
                number   = int (itree.jetNChgptCut7 + itree.jetNNeutralptCut7)
                jetQGLik7[0]   = QGLikCalc.computeQGLikelihood2012(itree.jetpt7,   itree.jeteta7, jetRho,  number, itree.jetptD7,   itree.jetaxis27)
                numberQC = int (itree.jetNChgQC7 + itree.jetNNeutralptCut7)
                jetQGLikQC7[0] = QGLikCalcQC.computeQGLikelihood2012(itree.jetpt7, itree.jeteta7, jetRho,  number, itree.jetQCptD7, itree.jetQCaxis27)
            else :
                jetQGLik7[0]   = -999.
                jetQGLikQC7[0] = -999.

            # MLP

            if itree.jetpt1>0 :
                number   = int (itree.jetNChgptCut1 + itree.jetNNeutralptCut1)
                jetQGMLP1[0]   = QGMLPCalc.QGvalue(itree.jetpt1,   itree.jeteta1, jetRho,  number, itree.jetptD1,   itree.jetaxis11,   itree.jetaxis21)
                numberQC = int (itree.jetNChgQC1 + itree.jetNNeutralptCut1)
                jetQGMLPQC1[0] = QGMLPCalc.QGvalue(itree.jetpt1, itree.jeteta1, jetRho,  number, itree.jetQCptD1, itree.jetQCaxis11, itree.jetQCaxis21)
            else :
                jetQGMLP1[0]   = -999.
                jetQGMLPQC1[0] = -999.

            if itree.jetpt2>0 :
                number   = int (itree.jetNChgptCut2 + itree.jetNNeutralptCut2)
                jetQGMLP2[0]   = QGMLPCalc.QGvalue(itree.jetpt2,   itree.jeteta2, jetRho,  number, itree.jetptD2,   itree.jetaxis12,   itree.jetaxis22)
                numberQC = int (itree.jetNChgQC2 + itree.jetNNeutralptCut2)
                jetQGMLPQC2[0] = QGMLPCalc.QGvalue(itree.jetpt2, itree.jeteta2, jetRho,  number, itree.jetQCptD2, itree.jetQCaxis12, itree.jetQCaxis22)
            else :
                jetQGMLP2[0]   = -999.
                jetQGMLPQC2[0] = -999.

            if itree.jetpt3>0 :
                number   = int (itree.jetNChgptCut3 + itree.jetNNeutralptCut3)
                jetQGMLP3[0]   = QGMLPCalc.QGvalue(itree.jetpt3,   itree.jeteta3, jetRho,  number, itree.jetptD3,   itree.jetaxis13,   itree.jetaxis23)
                numberQC = int (itree.jetNChgQC3 + itree.jetNNeutralptCut3)
                jetQGMLPQC3[0] = QGMLPCalc.QGvalue(itree.jetpt3, itree.jeteta3, jetRho,  number, itree.jetQCptD3, itree.jetQCaxis13, itree.jetQCaxis23)
            else :
                jetQGMLP3[0]   = -999.
                jetQGMLPQC3[0] = -999.

            if itree.jetpt4>0 :
                number   = int (itree.jetNChgptCut4 + itree.jetNNeutralptCut4)
                jetQGMLP4[0]   = QGMLPCalc.QGvalue(itree.jetpt4,   itree.jeteta4, jetRho,  number, itree.jetptD4,   itree.jetaxis14,   itree.jetaxis24)
                numberQC = int (itree.jetNChgQC4 + itree.jetNNeutralptCut4)
                jetQGMLPQC4[0] = QGMLPCalc.QGvalue(itree.jetpt4, itree.jeteta4, jetRho,  number, itree.jetQCptD4, itree.jetQCaxis14, itree.jetQCaxis24)
            else :
                jetQGMLP4[0]   = -999.
                jetQGMLPQC4[0] = -999.

            if itree.jetpt5>0 :
                number   = int (itree.jetNChgptCut5 + itree.jetNNeutralptCut5)
                jetQGMLP5[0]   = QGMLPCalc.QGvalue(itree.jetpt5,   itree.jeteta5, jetRho,  number, itree.jetptD5,   itree.jetaxis15,   itree.jetaxis25)
                numberQC = int (itree.jetNChgQC5 + itree.jetNNeutralptCut5)
                jetQGMLPQC5[0] = QGMLPCalc.QGvalue(itree.jetpt5, itree.jeteta5, jetRho,  number, itree.jetQCptD5, itree.jetQCaxis15, itree.jetQCaxis25)
            else :
                jetQGMLP5[0]   = -999.
                jetQGMLPQC5[0] = -999.

            if itree.jetpt6>0 :
                number   = int (itree.jetNChgptCut6 + itree.jetNNeutralptCut6)
                jetQGMLP6[0]   = QGMLPCalc.QGvalue(itree.jetpt6,   itree.jeteta6, jetRho,  number, itree.jetptD6,   itree.jetaxis16,   itree.jetaxis26)
                numberQC = int (itree.jetNChgQC6 + itree.jetNNeutralptCut6)
                jetQGMLPQC6[0] = QGMLPCalc.QGvalue(itree.jetpt6, itree.jeteta6, jetRho,  number, itree.jetQCptD6, itree.jetQCaxis16, itree.jetQCaxis26)
            else :
                jetQGMLP6[0]   = -999.
                jetQGMLPQC6[0] = -999.

            if itree.jetpt7>0 :
                number   = int (itree.jetNChgptCut7 + itree.jetNNeutralptCut7)
                jetQGMLP7[0]   = QGMLPCalc.QGvalue(itree.jetpt7,   itree.jeteta7, jetRho,  number, itree.jetptD7,   itree.jetaxis17,   itree.jetaxis27)
                numberQC = int (itree.jetNChgQC7 + itree.jetNNeutralptCut7)
                jetQGMLPQC7[0] = QGMLPCalc.QGvalue(itree.jetpt7, itree.jeteta7, jetRho,  number, itree.jetQCptD7, itree.jetQCaxis17, itree.jetQCaxis27)
            else :
                jetQGMLP7[0]   = -999.
                jetQGMLPQC7[0] = -999.



            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'






