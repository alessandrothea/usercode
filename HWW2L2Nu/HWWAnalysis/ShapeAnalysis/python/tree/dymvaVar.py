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
#  __ \ \ \   /                                                     _)         |      |
#  |   | \   /       __ `__ \ \ \   /  _` |     \ \   /  _` |   __|  |   _` |  __ \   |   _ \
#  |   |    |        |   |   | \ \ /  (   |      \ \ /  (   |  |     |  (   |  |   |  |   __/
# ____/    _|       _|  _|  _|  \_/  \__,_|       \_/  \__,_| _|    _| \__,_| _.__/  _| \___|
#
#

class DymvaVarFiller(TreeCloner):

    def __init__(self):
        pass


    def createDYMVA(self):
        self.getDYMVAV0j0 = ROOT.TMVA.Reader();
        self.getDYMVAV0j1 = ROOT.TMVA.Reader();
        self.getDYMVAV1j0 = ROOT.TMVA.Reader();
        self.getDYMVAV1j1 = ROOT.TMVA.Reader();

        self.getDYMVAV0j0.AddVariable("met",           (self.var1))
        self.getDYMVAV0j0.AddVariable("trackMet",      (self.var2))
        self.getDYMVAV0j0.AddVariable("jet1pt",        (self.var3))
        self.getDYMVAV0j0.AddVariable("metSig",        (self.var4))
        self.getDYMVAV0j0.AddVariable("dPhiDiLepJet1", (self.var5))
        self.getDYMVAV0j0.AddVariable("dPhiJet1MET",   (self.var6))
        self.getDYMVAV0j0.AddVariable("mt",            (self.var7))

        self.getDYMVAV0j1.AddVariable("met",           (self.var1))
        self.getDYMVAV0j1.AddVariable("trackMet",      (self.var2))
        self.getDYMVAV0j1.AddVariable("jet1pt",        (self.var3))
        self.getDYMVAV0j1.AddVariable("metSig",        (self.var4))
        self.getDYMVAV0j1.AddVariable("dPhiDiLepJet1", (self.var5))
        self.getDYMVAV0j1.AddVariable("dPhiJet1MET",   (self.var6))
        self.getDYMVAV0j1.AddVariable("mt",            (self.var7))

        self.getDYMVAV1j0.AddVariable("pmet",           (self.var1))
        self.getDYMVAV1j0.AddVariable("pTrackMet",      (self.var2))
        self.getDYMVAV1j0.AddVariable("nvtx",           (self.var3))
        self.getDYMVAV1j0.AddVariable("dilpt",          (self.var4))
        self.getDYMVAV1j0.AddVariable("jet1pt",         (self.var5))
        self.getDYMVAV1j0.AddVariable("metSig",         (self.var6))
        self.getDYMVAV1j0.AddVariable("dPhiDiLepJet1",  (self.var7))
        self.getDYMVAV1j0.AddVariable("dPhiDiLepMET",   (self.var8))
        self.getDYMVAV1j0.AddVariable("dPhiJet1MET",    (self.var9))
        self.getDYMVAV1j0.AddVariable("recoil",         (self.var10))
        self.getDYMVAV1j0.AddVariable("mt",             (self.var11))

        self.getDYMVAV1j1.AddVariable("pmet",           (self.var1))
        self.getDYMVAV1j1.AddVariable("pTrackMet",      (self.var2))
        self.getDYMVAV1j1.AddVariable("nvtx",           (self.var3))
        self.getDYMVAV1j1.AddVariable("dilpt",          (self.var4))
        self.getDYMVAV1j1.AddVariable("jet1pt",         (self.var5))
        self.getDYMVAV1j1.AddVariable("metSig",         (self.var6))
        self.getDYMVAV1j1.AddVariable("dPhiDiLepJet1",  (self.var7))
        self.getDYMVAV1j1.AddVariable("dPhiDiLepMET",   (self.var8))
        self.getDYMVAV1j1.AddVariable("dPhiJet1MET",    (self.var9))
        self.getDYMVAV1j1.AddVariable("recoil",         (self.var10))
        self.getDYMVAV1j1.AddVariable("mt",             (self.var11))


        #baseCMSSW = string(getenv("CMSSW_BASE"))
        #self.getDYMVAV0j0.BookMVA("BDTB",baseCMSSW+string("/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_0j_BDTB.weights.xml"))
        #self.getDYMVAV0j1.BookMVA("BDTB",baseCMSSW+string("/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_1j_BDTB.weights.xml"))
        #self.getDYMVAV1j0.BookMVA("BDTG",baseCMSSW+string("/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_BDTG_0j_MCtrain.weights.xml"))
        #self.getDYMVAV1j1.BookMVA("BDTG",baseCMSSW+string("/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_BDTG_1j_MCtrain.weights.xml"))

        #baseCMSSW = os.getenv('CMSSW_BASE')
        #self.getDYMVAV0j0.BookMVA("BDTB",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_0j_BDTB.weights.xml")
        #self.getDYMVAV0j1.BookMVA("BDTB",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_1j_BDTB.weights.xml")
        #self.getDYMVAV1j0.BookMVA("BDTG",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_BDTG_0j_MCtrain.weights.xml")
        #self.getDYMVAV1j1.BookMVA("BDTG",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_BDTG_1j_MCtrain.weights.xml")

        # new dymva trainined xml
        baseCMSSW = os.getenv('CMSSW_BASE')
        self.getDYMVAV0j0.BookMVA("BDTB",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_0j_BDTB.weights.xml")
        self.getDYMVAV0j1.BookMVA("BDTB",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_1j_BDTB.weights.xml")
        self.getDYMVAV1j0.BookMVA("BDTG",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_0j_metshift_BDTG.weights.xml")
        self.getDYMVAV1j1.BookMVA("BDTG",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_1j_metshift_BDTG.weights.xml")


    def deltaPhi(self,l1,l2):
       dphi = fabs(l1.DeltaPhi(l2))
       #    dphi = fabs(ROOT.Math.VectorUtil.DeltaPhi(l1.p4(),l2.p4()))
       return dphi


    def help(self):
        return '''Add dy mva variables'''


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

        self.getDYMVAV0j0 = None
        self.getDYMVAV0j1 = None
        self.getDYMVAV0j0 = None
        self.getDYMVAV1j1 = None
        self.var1 = numpy.ones(1, dtype=numpy.float32)
        self.var2 = numpy.ones(1, dtype=numpy.float32)
        self.var3 = numpy.ones(1, dtype=numpy.float32)
        self.var4 = numpy.ones(1, dtype=numpy.float32)
        self.var5 = numpy.ones(1, dtype=numpy.float32)
        self.var6 = numpy.ones(1, dtype=numpy.float32)
        self.var7 = numpy.ones(1, dtype=numpy.float32)
        self.var8 = numpy.ones(1, dtype=numpy.float32)
        self.var9 = numpy.ones(1, dtype=numpy.float32)
        self.var10 = numpy.ones(1, dtype=numpy.float32)
        self.var11 = numpy.ones(1, dtype=numpy.float32)
        self.var12 = numpy.ones(1, dtype=numpy.float32)
        self.var13 = numpy.ones(1, dtype=numpy.float32)
        self.var14 = numpy.ones(1, dtype=numpy.float32)
        self.var15 = numpy.ones(1, dtype=numpy.float32)
        self.var16 = numpy.ones(1, dtype=numpy.float32)
        self.var17 = numpy.ones(1, dtype=numpy.float32)
        self.var18 = numpy.ones(1, dtype=numpy.float32)
        self.var19 = numpy.ones(1, dtype=numpy.float32)
        self.var20 = numpy.ones(1, dtype=numpy.float32)
        self.var21 = numpy.ones(1, dtype=numpy.float32)
        self.var22 = numpy.ones(1, dtype=numpy.float32)

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ['dymva0new', 'dymva1new', 'dphilljet1', 'dphimetjet1', 'recoil']

        self.clone(output,newbranches)

        dymva0      = numpy.ones(1, dtype=numpy.float32)
        dymva1      = numpy.ones(1, dtype=numpy.float32)
        dphilljet1  = numpy.ones(1, dtype=numpy.float32)
        dphimetjet1 = numpy.ones(1, dtype=numpy.float32)
        recoil      = numpy.ones(1, dtype=numpy.float32)


        self.otree.Branch('dymva0new',  dymva0,  'dymva0new/F')
        self.otree.Branch('dymva1new',  dymva1,  'dymva1new/F')
        self.otree.Branch('dphilljet1',   dphilljet1,  'dphilljet1/F')
        self.otree.Branch('dphimetjet1',  dphimetjet1, 'dphimetjet1/F')
        self.otree.Branch('recoil',       recoil,      'recoil/F')


        self.createDYMVA()

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


            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(itree.pt1, itree.eta1, itree.phi1, 0)
            l2.SetPtEtaPhiM(itree.pt2, itree.eta2, itree.phi2, 0)

            met = ROOT.TLorentzVector()
            met.SetPxPyPzE(itree.pfmet * cos (itree.pfmetphi), itree.pfmet * sin (itree.pfmetphi), 0, itree.pfmet)

            #dphillmet[0] = self.deltaPhi(l1+l2,met)
            #dphilmet1[0] = self.deltaPhi(l1   ,met)
            #dphilmet2[0] = self.deltaPhi(   l2,met)
            #dphilmet [0] = min (dphilmet1[0], dphilmet2[0])



            jetpt1 = itree.jetpt1
            if itree.jetpt1 < 15 :
                jetpt1 = 15
                dphilljet1[0]  = -0.1;
                dphimetjet1[0] = -0.1;
            else :
                jet1 = ROOT.TLorentzVector()
                jet1.SetPtEtaPhiM(itree.jetpt1, itree.jeteta1, itree.jetphi1, 0)
                dphilljet1[0]  = self.deltaPhi(l1+l2,jet1)
                dphimetjet1[0] = self.deltaPhi(met,jet1)





            self.var1[0] =  itree.pfmet
            self.var2[0] =  itree.chmet
            self.var3[0] =  itree.jetpt1
            self.var4[0] =  itree.pfmetSignificance
            self.var5[0] =  dphilljet1[0]
            self.var6[0] =  dphimetjet1[0]
            self.var7[0] =  itree.mth


            if itree.njet == 0:
                  dymva0[0] = self.getDYMVAV0j0.EvaluateMVA("BDTB")
            elif itree.njet == 1:
                  dymva0[0] = self.getDYMVAV0j1.EvaluateMVA("BDTB")
            else :
                  dymva0[0] = -999

            px_rec = itree.pfmet * cos(itree.pfmetphi) + (l1+l2).Px()
            py_rec = itree.pfmet * sin(itree.pfmetphi) + (l1+l2).Py()

            recoil[0] = sqrt(px_rec*px_rec + py_rec*py_rec)

            self.var1[0]  =  itree.ppfmet
            self.var2[0]  =  itree.pchmet
            self.var3[0]  =  itree.nvtx
            self.var4[0]  =  itree.ptll
            self.var5[0]  =  itree.jetpt1
            self.var6[0]  =  itree.pfmetMEtSig
            self.var7[0]  =  dphilljet1[0]
            self.var8[0]  =  itree.dphillmet
            self.var9[0]  =  dphimetjet1[0]
            self.var10[0] =  recoil[0]
            self.var11[0] =  itree.mth


            if itree.njet == 0:
                  dymva1[0] = self.getDYMVAV1j0.EvaluateMVA("BDTG")
            elif itree.njet == 1:
                  dymva1[0] = self.getDYMVAV1j1.EvaluateMVA("BDTG")
            else :
                  dymva1[0] = -999

            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



