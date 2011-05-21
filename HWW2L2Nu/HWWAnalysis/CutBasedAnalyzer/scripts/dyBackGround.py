#!/usr/bin/env python

import optparse
import sys
import ROOT
import array
import os.path
from HWWAnalysis.Misc.ROOTAndUtils import TH1AddDirSentry

z0mass=9.11869999999999976e+01

# one needs:
# dy10-20 [ee,mm]
# dy20 [ee,mm]
# scale factors for all the 4 samples

def getTree( file, tree ):
    t = file.Get(tree)
    if not t.__nonzero__():
        raise NameError('Tree '+tree+' doesn\'t exist in '+file)
    return t

class Sample:
    def __init__(self):
        self.path  = None
        self.file  = None
        self.tree  = None
        self.scale = 1.



class DYEstimator:

    def __init__(self,  out):
        self.dyee10 = Sample()
        self.dyee   = Sample()
        self.dymm10 = Sample()
        self.dymm   = Sample()
        self.data   = Sample()

        self.outFile = None
        self.outPath = out

        self.eeRoutin = []
        self.mmRoutin = []
        self.eeMetEff = 0
        self.mmMetEff = 0

    def __del__(self):
        if self.outFile:
            self.outFile.Write()
            self.outFile.Close()
    
    def openTFile(self, path, option=''):
        f =  ROOT.TFile.Open(path,option)
        if not f.__nonzero__() or not f.IsOpen():
            raise NameError('File '+path+' not open')
        return f

    def connect(self):
        # open dyee
        self.dyee10.file = self.openTFile( self.dyee10.path )
        self.dyee10.tree = getTree( self.dyee10.file, 'hwwAnalysis' )
        self.dyee.file   = self.openTFile( self.dyee.path )
        self.dyee.tree   = getTree( self.dyee.file, 'hwwAnalysis' )
        self.dymm10.file = self.openTFile( self.dymm10.path )
        self.dymm10.tree = getTree( self.dymm10.file, 'hwwAnalysis' )
        self.dymm.file   = self.openTFile( self.dymm.path )
        self.dymm.tree   = getTree( self.dymm.file, 'hwwAnalysis' )

        # data
        self.data.file    = self.openTFile( self.data.path )
        self.data.tree   = getTree( self.data.file, 'hwwAnalysis' )

        #open output

        self.outFile = self.openTFile(self.outPath,'recreate')

    def calculateInOut(self, channel):
        if not hasattr(self, channel):
            raise NameError('Channel '+channel+' not known')

        dy = getattr(self,channel)

        n = ROOT.HWWNtuple()
        dy.tree.SetBranchAddress('nt',ROOT.AddressOf(n))

        metRange = [ m+2.5 for m in xrange(0,46,5) ]
        jetRange = range(3)
        
        pool = [[None]*len(metRange)]*len(jetRange)
        for jet in range(len(jetRange)):
            for met in range(len(metRange)):
                tag = 'n_met%.1f_jet%self' % (metRange[met], jetRange[jet])
                dyIn = ROOT.TH1D('dyIn'+tag,'dyIn'+tag,1000,0,1000)
                dyOut = ROOT.TH1D('dyOut'+tag,'dyOut'+tag,1000,0,1000)
                pool[jet][met] = ( dyIn, dyOut )


        print channel+'- histogram pool initialized'

        for i in xrange(dy.tree.GetEntries()):
            dy.tree.GetEntry(i)
            
        print 'Done'

    def computeRoutRin(self, channel, nJets):

        if channel == 'ee':
            dy10 = self.dyee10
            dy = self.dyee
            color = ROOT.kBlue
        elif channel == 'mm':
            dy10 = self.dymm10
            dy = self.dymm
            color = ROOT.kRed
        else:
            raise NameError('Channel '+channel+' not known')

        self.outFile.mkdir('ratio%s_%djets' % (channel,nJets) ).cd()


        zwidth = 15 #GeV
        weight = ROOT.TCut('nt.weight')
#         ptCut = ROOT.TCut('nt.pB.Pt() > 10')
#         ptCut = ROOT.TCut('1')
        cutJets = ROOT.TCut('nt.nPfJets == %d' % nJets)
        wwCuts = ROOT.TCut('nt.mll > 12 && nt.nSoftMus==0 && nt.nBJets == 0')

        cutZpeak = ROOT.TCut('TMath::Abs(nt.mll-%f) < 15' % z0mass) 
        cutAntiZpeak = ROOT.TCut('TMath::Abs(nt.mll-%f) >= 15' % z0mass)

        cutsDYin  = weight*cutJets*wwCuts*cutZpeak
        cutsDYout = weight*cutJets*wwCuts*cutAntiZpeak

        mets = [0]
#         mets.extend([ x+2.5 for x in xrange( 0,46,5)])

        x, ex = array.array('d'), array.array('d')
        y, ey = array.array('d'), array.array('d')

        for met in mets:
            metCut = ROOT.TCut('(nt.minProjMet > %f)' % met)

            nameDYin10  = 'dyIn10_pjMet%d_nJ%d' % (met,nJets)
            nameDYout10 = 'dyOut10_pjMet%d_nJ%d'%  (met,nJets)
            nameDYin    = 'dyIn_pjMet%d_nJ%d' %  (met,nJets)
            nameDYout   = 'dyOut_pjMet%d_nJ%d'%  (met,nJets)


            histDYin10  = ROOT.TH1F( nameDYin10,nameDYin10,1000,0,1000)
            histDYout10 = ROOT.TH1F( nameDYout10,nameDYout10,1000,0,1000)
            histDYin    = ROOT.TH1F( nameDYin,nameDYin,1000,0,1000)
            histDYout   = ROOT.TH1F( nameDYout,nameDYout,1000,0,1000)

            histDYin10.Sumw2()
            histDYout10.Sumw2()
            histDYin.Sumw2()
            histDYout.Sumw2()

            dy10.tree.Project(nameDYin10,'nt.mll',(metCut*cutsDYin).GetTitle())
            dy10.tree.Project(nameDYout10,'nt.mll',(metCut*cutsDYout).GetTitle())
#             dy10.tree.Project(nameDYin,'nt.mll',(metCut*cutsDYin).GetTitle())
#             dy10.tree.Project(nameDYout,'nt.mll',(metCut*cutsDYout).GetTitle())
            dy.tree.Project(nameDYin,'nt.mll',(metCut*cutsDYin).GetTitle())
            dy.tree.Project(nameDYout,'nt.mll',(metCut*cutsDYout).GetTitle())

            histDYin10.Scale(dy10.scale)
            histDYout10.Scale(dy10.scale)
            histDYin.Scale(dy.scale)
            histDYout.Scale(dy.scale)

            dyIn    = histDYin.GetSumOfWeights()+histDYin10.GetSumOfWeights()
            dyOut   = histDYout.GetSumOfWeights()+histDYout10.GetSumOfWeights()
            ROutIn = dyOut/dyIn if dyIn != 0 else 0
            eDYin2  = histDYin.GetSumw2().GetSum()
            eDYout2 = histDYout.GetSumw2().GetSum()

            eROutIn = ROOT.TMath.Sqrt( ROutIn**2 * ( eDYin2/dyIn**2 + eDYout2/dyOut**2) ) if ROutIn != 0 else 0
            print channel,met,'dyIn',dyIn,'dyOut',dyOut,' : ', ROutIn,'+-',eROutIn

            if ROutIn != 0:
                x.append(met)
                ex.append(0)
                y.append(ROutIn)
                ey.append(eROutIn)

            histDYin10.Write()
            histDYout10.Write()
            histDYin.Write()
            histDYout.Write()

        g = ROOT.TGraphErrors(len(x), x,y,ex,ey)
        
        g.SetName('ROutIn')
        g.SetTitle('R_{Out/In} '+channel)
        g.SetMarkerStyle(20)
        g.GetXaxis().SetTitle('proj#slash E_{T}')
        g.GetYaxis().SetTitle('R_{out/in}')
        g.SetMarkerColor(color)
        g.Write()
        
        return (g,y[0],ey[0])

    def computeAllJetBins( self):
        c = ROOT.TCanvas('cROutIn_all','cROutIn_all')
        c.Divide(2,2)
        hline = '-'*80
        # 0 jets-----------------------------------------------
        print hline
        gee0,R_ee0,eR_ee0 = self.computeRoutRin('ee',0)
        print hline
        gmm0,R_mm0,eR_mm0 = self.computeRoutRin('mm',0)

        self.eeRoutin.append( (R_ee0,eR_ee0) ) 
        self.mmRoutin.append( (R_mm0,eR_mm0) ) 

        self.outFile.cd()
        m0 = ROOT.TMultiGraph()
        m0.SetName('ROutIn_0jets')
        m0.Add(gee0,'p')
        m0.Add(gmm0,'p')
        m0.SetTitle('0 jets')
        # draw
        p = c.cd(1)
        m0.Draw('ap')
        m0.GetXaxis().SetTitle('min(projPF #slashE_{T},projCh #slashE_{T},)')
        p.BuildLegend()

        m0.Write()

        # 1 jets----------------------------------------------
        print hline
        gee1,R_ee1,eR_ee1 = self.computeRoutRin('ee',1)
        print hline
        gmm1,R_mm1,eR_mm1  = self.computeRoutRin('mm',1)
        self.eeRoutin.append( (R_ee1,eR_ee1) ) 
        self.mmRoutin.append( (R_mm1,eR_mm1) ) 

        self.outFile.cd()
        m1 = ROOT.TMultiGraph()
        m1.SetName('ROutIn_1jets')
        m1.Add(gee1,'p')
        m1.Add(gmm1,'p')
        m1.SetTitle('1 jets')
        # draw
        p = c.cd(2)
        m1.Draw('ap')
        m1.GetXaxis().SetTitle('min(projPF #slashE_{T},projCh #slashE_{T},)')
        p.BuildLegend()
        m1.Write()

        # 1 jets-----------------------------------------------
        print hline
        gee2,R_ee2,eR_ee2 = self.computeRoutRin('ee',2)
        print hline
        gmm2,R_mm2,eR_mm2 = self.computeRoutRin('mm',2)
        self.eeRoutin.append( (R_ee2,eR_ee2) ) 
        self.mmRoutin.append( (R_mm2,eR_mm2) ) 

        self.outFile.cd()
        m2 = ROOT.TMultiGraph()
        m2.SetName('ROutIn_2jets')
        m2.Add(gee2,'p')
        m2.Add(gmm2,'p')
        m2.SetTitle('2 jets')
        # draw
        p = c.cd(3)
        m2.Draw('ap')
        m2.GetXaxis().SetTitle('min(projPF #slashE_{T},projCh #slashE_{T},)')
        p.BuildLegend()

        m2.Write()

        c.Print(os.path.splitext(opt.outPath)[0]+'.pdf')
        c.Write()

    def countPairs(self):
        weight  = ROOT.TCut('nt.weight')
        cutJets = ROOT.TCut('nt.nPfJets == 0')
        minMet  = ROOT.TCut('nt.met > 20')
        wwCuts  = ROOT.TCut('nt.mll > 12 && nt.nSoftMus==0 && nt.nBJets == 0')

        cutZpeak = ROOT.TCut('TMath::Abs(nt.mll-%f) < 15' % z0mass) 
        cutsDYin  = weight*cutJets*wwCuts*cutZpeak*minMet

        cutElEl         = ROOT.TCut('nt.type == 0 && nt.projMet > 35')
        cutElMu         = ROOT.TCut('(nt.type == 1 || nt.type == 10) && nt.projMet > 20')
        cutMuMu         = ROOT.TCut('nt.type == 11 && nt.projMet > 35')
        cutElElLoose    = ROOT.TCut('nt.type == 0')
        cutMuMuLoose    = ROOT.TCut('nt.type == 11')

        nameElElLoose = 'CountDYinElElLoose'
        nameMuMuLoose = 'CountDYinMuMuLoose'
        nameElEl      = 'CountDYinElEl'
        nameElMu      = 'CountDYinElMu'
        nameMuMu      = 'CountDYinMuMu'

        self.outFile.mkdir('counts').cd()
        histElElLoose = ROOT.TH1F( nameElElLoose,nameElElLoose,1000,0,1000) 
        histMuMuLoose = ROOT.TH1F( nameMuMuLoose,nameMuMuLoose,1000,0,1000) 
        histElEl      = ROOT.TH1F( nameElEl,nameElEl,1000,0,1000) 
        histElMu      = ROOT.TH1F( nameElMu,nameElMu,1000,0,1000) 
        histMuMu      = ROOT.TH1F( nameMuMu,nameMuMu,1000,0,1000) 

        histElElLoose.Sumw2()
        histMuMuLoose.Sumw2()
        histElEl.Sumw2()
        histElMu.Sumw2()
        histMuMu.Sumw2()

        self.data.tree.Project(nameElElLoose,'nt.mll',(cutElElLoose*cutsDYin).GetTitle())
        self.data.tree.Project(nameMuMuLoose,'nt.mll',(cutMuMuLoose*cutsDYin).GetTitle())
        self.data.tree.Project(nameElEl,'nt.mll',(cutElEl*cutsDYin).GetTitle())
        self.data.tree.Project(nameElMu,'nt.mll',(cutElMu*cutsDYin).GetTitle())
        self.data.tree.Project(nameMuMu,'nt.mll',(cutMuMu*cutsDYin).GetTitle())

        histElElLoose.Write()
        histMuMuLoose.Write()
        histElEl.Write()
        histElMu.Write()
        histMuMu.Write()


        nee_loose = histElElLoose.GetSumOfWeights()
        nmm_loose = histMuMuLoose.GetSumOfWeights()
        nee = histElEl.GetSumOfWeights()
        nem = histElMu.GetSumOfWeights()
        nmm = histMuMu.GetSumOfWeights()
        print 'NeeLoose =',nee_loose
        print 'NmmLoose =',nmm_loose
        print 'Nee      =',nee
        print 'Nem+Nme  =',nem
        print 'Nmm      =',nmm

        k_em = 0.5*ROOT.TMath.Sqrt(float(nee_loose)/float(nmm_loose))
        k_me = 0.5*ROOT.TMath.Sqrt(float(nmm_loose)/float(nee_loose))
        ek_me = ROOT.TMath.Sqrt(1./4.*( 1/(4*nee_loose)+(4*nmm_loose/nee_loose**2) ) ) 
        ek_em = ROOT.TMath.Sqrt(1./4.*( 1/(4*nmm_loose)+(4*nee_loose/nmm_loose**2) ) ) 

        print 'k_em =',k_em,'+-',ek_em
        print 'k_me =',k_me,'+-',ek_me

        nee_obs = ( nee - k_em*nem)*self.eeRoutin[0][0]
        nmm_obs = ( nmm - k_me*nem)*self.mmRoutin[0][0]
        print 'Nee_obs',nee_obs
        print 'Nmm_obs',nmm_obs

    def getMetEfficiency(self, channel ):
        if channel == 'ee':
            dy10 = self.dyee10
            dy = self.dyee
            color = ROOT.kBlue
        elif channel == 'mm':
            dy10 = self.dymm10
            dy = self.dymm
            color = ROOT.kRed
        else:
            raise NameError('Channel '+channel+' not known')

        nameDYout       = 'dyEffOut'
        nameDYoutMet    = 'dyEffOutMet'

        histDYout   = ROOT.TH1F( nameDYout,nameDYout,1000,0,1000)
        histDYoutMet= ROOT.TH1F( nameDYoutMet,nameDYout,1000,0,1000)

        histDYout.Sumw2()
        histDYoutMet.Sumw2()

        weight   = ROOT.TCut('nt.weight')
        jetVetoCut  = ROOT.TCut('nt.nPfJets == 0')
        wwCuts   = ROOT.TCut('nt.mll > 12 && nt.nSoftMus==0 && nt.nBJets == 0')
        metCut   = ROOT.TCut('nt.met > 20 && nt.projMet > 35')
        zVetoCut = ROOT.TCut('TMath::Abs(nt.mll-%f) < 15' % z0mass)

        cutsDYout = weight*jetVetoCut*wwCuts*zVetoCut;

        dy10.tree.Project(nameDYout,'nt.mll',cutsDYout.GetTitle())
        dy.tree.Project(nameDYout,'nt.mll',cutsDYout.GetTitle())

        dy10.tree.Project(nameDYoutMet,'nt.mll',(metCut*cutsDYout).GetTitle())
        dy.tree.Project(nameDYoutMet,'nt.mll',(metCut*cutsDYout).GetTitle())

        dyAfterMet =  histDYoutMet.GetSumOfWeights()
        dyBeforeMet = histDYout.GetSumOfWeights()
        print 'met/noMet = ',dyAfterMet,dyBeforeMet
        return dyAfterMet/dyBeforeMet

    def computeMetEff( self ):
        print '-- ee met efficiency',
        self.eeMetEff = self.getMetEfficiency('ee')
        print self.eeMetEff
        print '-- mm met efficiency',
        self.mmMetEff = self.getMetEfficiency('mm')
        print self.mmMetEff

if __name__ == '__main__':
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    # drell yan ntuple file
    # data ntuple file

#     parser.add_option('--data', dest='dataPath', help='Data Ntuple File', )
#     parser.add_option('--dyee', dest='dyeePath', help='Drell-Yan to ElEl Ntuple File', )
#     parser.add_option('--dymm', dest='dymmPath', help='Drell-Yan to MuMu Ntuple File', )
    parser.add_option('--out', dest='outPath', help='Output Root File ')

    (opt, args) = parser.parse_args()

    if not opt.outPath:
        parser.error('Outout file not defined')
    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()
    ROOT.gSystem.Load('libFWCoreFWLite')
    ROOT.AutoLibraryLoader.enable()

#     if not opt.dyeePath or not opt.dymmPath:
#         parser.error('DY samples not defined')

    d = DYEstimator( opt.outPath )
    # hard code, though world
    d.dyee10.path = '~/higgsWW/Spring11/ntuples/h160/hww_DY10toElElZ2.root'
    d.dyee.path   = '~/higgsWW/Spring11/ntuples/h160/hww_DYtoElEl.root'
    d.dymm10.path = '~/higgsWW/Spring11/ntuples/h160/hww_DY10toMuMuZ2.root'
    d.dymm.path   = '~/higgsWW/Spring11/ntuples/h160/hww_DYtoMuMu.root'

    # data
    d.data.path   = '~/higgsWW/Spring11/ntuples/h160/hww_Data2011.root'

    # scale factors
    d.dyee10.scale = 1.7884117951 
    d.dyee.scale   = 0.8362295184
    d.dymm10.scale = 1.6246522295 
    d.dymm.scale   = 0.8396525673

 

    d.connect()

#     d.computeMetEff()
#     sys.exit(0)

    d.computeAllJetBins()
#     print d.eeRoutin
#     print d.mmRoutin

    d.countPairs()
