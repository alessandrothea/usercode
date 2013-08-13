from tree.gardening import TreeCloner


import optparse
import os
import sys
import ROOT
import numpy
import re
import warnings
import os.path
from math import *
import math


#
#
# \ \     /  __ )   ____|       \  | \ \     /  \
#  \ \   /   __ \   |          |\/ |  \ \   /  _ \
#   \ \ /    |   |  __|        |   |   \ \ /  ___ \
#    \_/    ____/  _|         _|  _|    \_/ _/    _\
#
#

class VbfMVAVarFiller(TreeCloner):

    def __init__(self):
        pass


    def createVbfMVA(self):
        self.getVbfMVA = ROOT.TMVA.Reader();

        self.getVbfMVA.AddVariable("sqrt((jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))*(jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))+(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2))*(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2)))",                  (self.var1))
        self.getVbfMVA.AddVariable("jetpt1",                  (self.var2))
        self.getVbfMVA.AddVariable("jetpt2",                  (self.var3))
        self.getVbfMVA.AddVariable("log(mjj)",                (self.var4))
        self.getVbfMVA.AddVariable("jeteta1*jeteta2",         (self.var5))
        self.getVbfMVA.AddVariable("detajj",                  (self.var6))


  #factory->AddVariable( "sqrt((jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))*(jetpt1*cos(jetphi1)+jetpt2*cos(jetphi2))+(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2))*(jetpt1*sin(jetphi1)+jetpt2*sin(jetphi2)))" , 'F');
  #factory->AddVariable( "jetpt1" , 'F');
  #factory->AddVariable( "jetpt2" , 'F');
  #factory->AddVariable( "log(mjj)" , 'F');
  #factory->AddVariable( "jeteta1*jeteta2" , 'F');
  #factory->AddVariable( "detajj" , 'F');



        baseCMSSW = os.getenv('CMSSW_BASE')
        self.getVbfMVA.BookMVA("Fisher",baseCMSSW+"/src/VBFMvaInCMSSW/GetVBFMVA/data/TMVA_Fisher.weights.xml")


    def help(self):
        return '''Add dy mva variables'''


    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        #group.add_option('-k', '--kindMCDATA',   dest='kindMCDATA', help='kind of sample: MC2011, MC2012, DATA2011, DATA2012', default='MC2012')
        parser.add_option_group(group)
        return group


    def checkOptions(self,opts):
        #if not (hasattr(opts,'kindMCDATA')) :
            #raise RuntimeError('Missing parameter')
        #self.kindMCDATA     = opts.kindMCDATA
        print "it's all ok ..."


    def process(self,**kwargs):

        self.getVbfMVA = None
        self.var1 = numpy.ones(1, dtype=numpy.float32)
        self.var2 = numpy.ones(1, dtype=numpy.float32)
        self.var3 = numpy.ones(1, dtype=numpy.float32)
        self.var4 = numpy.ones(1, dtype=numpy.float32)
        self.var5 = numpy.ones(1, dtype=numpy.float32)
        self.var6 = numpy.ones(1, dtype=numpy.float32)

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)

        newbranches = ['vbfMVAFisher']
        self.clone(output,newbranches)

        vbfMVAFisher = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('vbfMVAFisher',  vbfMVAFisher,  'vbfMVAFisher/F')

        self.createVbfMVA()

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

            ptjj = sqrt((itree.jetpt1*cos(itree.jetphi1)+itree.jetpt2*cos(itree.jetphi2))*(itree.jetpt1*cos(itree.jetphi1)+itree.jetpt2*cos(itree.jetphi2))+(itree.jetpt1*sin(itree.jetphi1)+itree.jetpt2*sin(itree.jetphi2))*(itree.jetpt1*sin(itree.jetphi1)+itree.jetpt2*sin(itree.jetphi2)))

            self.var1[0] =  ptjj
            self.var2[0] =  itree.jetpt1
            self.var3[0] =  itree.jetpt2
            if (itree.mjj>100) :   self.var4[0] =  math.log(itree.mjj)
            else :                 self.var4[0] =  math.log(100)
            self.var5[0] =  itree.jeteta1*itree.jeteta2
            self.var6[0] =  itree.detajj

            if  itree.njet>=2 :
                vbfMVAFisher[0] = self.getVbfMVA.EvaluateMVA("Fisher")
            else :
                vbfMVAFisher[0] = -999.
            #print "~~~"
            #print math.fabs(itree.jeteta1)
            #print math.fabs(itree.jeteta2)
            #print math.copysign(1.0, itree.jeteta1*itree.jeteta2)
            #print vbfMVAFisher[0]

            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



