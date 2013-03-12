#!/usr/bin/env python

## Example:
## ./scaleAndSmearTree.py -i H140_ll.root -o blu/bla/bli.root -t latino -a leptonEfficiency -d down


## FIXME:
## 1) make an n events argument... it's hardcoded at the moment...
## 2) lepton efficiency are at the moment moved up / down for electrons and muosn simultaneously


import optparse
import os
import ROOT
import numpy
import math
# from ROOT import *
 
from math import sqrt, cos

## MET resolution sigma for gaussian smearing (fraction of x- and y- component)
## mean is x- and y- component
metSigma = 0.1
## electron resolution sigma (not used yet)
electronSigmaEB = 0.02
electronSigmaEE = 0.04
## muon scale uncertainty
muonUncertainty = 0.01
## electron scale uncertainty
electronUncertaintyEB = 0.02
electronUncertaintyEE = 0.04

## charge mismeasurement
# in MC mischarge   = 4.45 / 10^4
# in DATA mischarge = 5.55 / 10^4
# absolute difference is 1.1 / 10^4
#

sigmaChargeElectron = (0.000240123, 7.55615e-05, 0.000144796, 2.52092e-05, 0.00120842, 0.00236264)
sigmaChargeMuon     = 0.0002



## pu uncertainty
puUp   = "puDATAup.root"
puDown = "puDATAdown.root"
puMC   = "puMC.root"
weightNamePU = "puW"



#verbose = False
mZ = 91.1876
to = ' -> '

def openTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f

def getHist(file, hist):
    h = file.Get(hist)
    if not h.__nonzero__():
        raise NameError('Histogram '+hist+' doesn\'t exist in '+str(file))
    return h

def invariantMass(l1,l2):
    mll = (l1+l2).M()
    return mll

def dileptonPt(l1, l2):
    ptll = (l1+l2).Pt()
    return ptll

def deltaPhi(l1,l2):
    radToDeg = 180./math.pi
##     dphi = abs(l1.DeltaPhi(l2))*radToDeg
    dphi = abs(l1.DeltaPhi(l2))
    return dphi

def transverseMass(p,m):
    mt = sqrt( 2* p.Pt() * m.Pt() * (1 - cos(p.DeltaPhi(m))))
    return mt

def correctMet(met, j1_hold, j2_hold, j1, j2):
    met = met + j1_hold - j1 + j2_hold - j2
    return met

def smearMET(met,sigma):
    metpx = met.Px()
    metpy = met.Py()
    ## throw the dices
    newpx = ROOT.gRandom.Gaus(metpx, sigma*metpx)
    newpy = ROOT.gRandom.Gaus(metpy, sigma*metpy)
    ## and replace the vector
    met.SetPxPyPzE(newpx, newpy,0,0)
    return met

def smearPt(pt, sigma):
    pt = ROOT.gRandom.Gaus(pt, sigma*pt)
    return pt

def smearCharge(sigma):
    change = ROOT.gRandom.Uniform(0, 1)
    if change < sigma :
       return -1
    else :
       return 1

def calculateGammaMRStar(ja, jb):
##def gammaMRstar(ja, jb):
    A = ja.P()
    B = jb.P()
    az = ja.Pz()
    bz = jb.Pz()
    jaT = ROOT.TVector3()
    jbT = ROOT.TVector3()
    jaT.SetXYZ(ja.Px(),ja.Py(),0.0)
    jbT.SetXYZ(jb.Px(),jb.Py(),0.0)
    ATBT = (jaT+jbT).Mag2()

    temp = sqrt((A+B)*(A+B)-(az+bz)*(az+bz)-(jbT.Dot(jbT)-jaT.Dot(jaT))*(jbT.Dot(jbT)-jaT.Dot(jaT))/(jaT+jbT).Mag2())
    mybeta = (jbT.Dot(jbT)-jaT.Dot(jaT))/sqrt(ATBT*((A+B)*(A+B)-(az+bz)*(az+bz)))
    mygamma = 1./sqrt(1.-mybeta*mybeta)
    ## gamma times MRstar
    temp *= mygamma
    return temp

def checkZveto(mll, channel):
    zveto = 0
    if abs(mll - mZ) > 15 or channel > 1:
        zveto = 1
    return zveto


# pass eta and pt from a jet plus the list containing the uncertaibties
# from Emanueles file to extract the uncertainty as function of pt and eta
def getJEUFactor(pt, eta, jeuList):
    scale = -1
    ## if there is no jet there is also no uncertainty defined...
    if pt < 0:
        scale = 0
        return scale
    ## loop over the table and find the matching uncertainty!
    for s in jeuList:
        if eta > float(s[0]) and eta <= float(s[1]):
            for p in xrange(len(s)):
                if p%3 != 0:
                    continue
                ## uncertainties have some minimum pt, set to the  lowest defined value if pt is too small...
                if pt <  float(s[3]): # 3 = minimum pt in table
                    scale = float(s[4]) # 4 = corresponding smallest uncertainty
##                     print ' ----------------------------------'
                    print 'Jet has too low pt: '+str(pt)
##                     print 'Setting uncertainty to minimum pt uncertainty: '+str(scale)
##                     print 'pseudorapidity: '+str(eta)
                    break
                if pt > float(s[p]):
                    scale = float(s[p+1])
                else:
                    break
    ##scale = 0.
    return scale



###############################################################################################
##                 _                        _                                 
##                | |                      | |                                
##  ___  ___  __ _| | ___    __ _ _ __   __| |  ___ _ __ ___   ___  __ _ _ __ 
## / __|/ __|/ _` | |/ _ \  / _` | '_ \ / _` | / __| '_ ` _ \ / _ \/ _` | '__|
## \__ \ (__| (_| | |  __/ | (_| | | | | (_| | \__ \ | | | | |  __/ (_| | |   
## |___/\___|\__,_|_|\___|  \__,_|_| |_|\__,_| |___/_| |_| |_|\___|\__,_|_|   
##                                                                           
##                                                                           
class scaleAndSmear:
    def __init__(self):
        self.inputFileName = ''
        self.outputFileName = ''
        self.path = ''
        self.inFile = None
        self.outFile = None
        self.treeDir = ''
        self.ttree = None
        self.oldttree = None
        self.nentries = 0
        self.systArgument = ''
        self.direction = ''

        
    def __del__(self):
        if self.outFile:
            self.outFile.Write()
            self.outFile.Close()



    def openOriginalTFile(self):
        filename = self.inputFileName
        print 'opening file: '+filename
        self.inFile = ROOT.TFile.Open(filename)

    def openOutputTFile(self):
        filename = self.outputFileName
        dir = os.path.dirname(filename)
        if not os.path.exists(dir):
            print 'directory does not exist yet...'
            print 'creating output directory: '+dir
            os.system('mkdir -p '+dir)
        print 'creating output file: '+filename
        self.outFile = ROOT.TFile.Open(filename,'recreate')

###############################################################################################
##  _____ _                    _____             
## /  __ \ |                  |_   _|            
## | /  \/ | ___  _ __   ___    | |_ __ ___  ___ 
## | |   | |/ _ \| '_ \ / _ \   | | '__/ _ \/ _ \
## | \__/\ | (_) | | | |  __/   | | | |  __/  __/
##  \____/_|\___/|_| |_|\___|   \_/_|  \___|\___|
##                                              
    def cloneTree(self):
        ## clone the tree
        self.inFile.ls()
        oldTree = self.inFile.Get(self.treeDir)
        ## do not clone the branches which we want to drop for systematics ntuples
        ## i.e. set status to 0
        oldTree.SetBranchStatus('bdt1'           ,0)
        oldTree.SetBranchStatus('bdt2'           ,0)
        oldTree.SetBranchStatus('cjeteta1'       ,0)
        oldTree.SetBranchStatus('cjeteta2'       ,0)
        oldTree.SetBranchStatus('cjetid1'        ,0)
        oldTree.SetBranchStatus('cjetid2'        ,0)
        oldTree.SetBranchStatus('cjetmva1'       ,0)
        oldTree.SetBranchStatus('cjetmva2'       ,0)
        oldTree.SetBranchStatus('cjetphi1'       ,0)
        oldTree.SetBranchStatus('cjetphi2'       ,0)
        oldTree.SetBranchStatus('cjetpt1'        ,0)
        oldTree.SetBranchStatus('cjetpt2'        ,0)
        oldTree.SetBranchStatus('effAW'          ,0)
        oldTree.SetBranchStatus('effBW'          ,0)
        oldTree.SetBranchStatus('fakeAW'         ,0)
        oldTree.SetBranchStatus('fakeBW'         ,0)
        oldTree.SetBranchStatus('imet'           ,0)
        oldTree.SetBranchStatus('iso1'           ,0)
        oldTree.SetBranchStatus('iso2'           ,0)
        oldTree.SetBranchStatus('jetbjpb1'       ,0)
        oldTree.SetBranchStatus('jetbjpb2'       ,0)
        oldTree.SetBranchStatus('jetbjpb3'       ,0)
        oldTree.SetBranchStatus('jetid1'         ,0)
        oldTree.SetBranchStatus('jetid2'         ,0)
        oldTree.SetBranchStatus('jetid3'         ,0)
        oldTree.SetBranchStatus('jetid4'         ,0)
        oldTree.SetBranchStatus('jetmva1'        ,0)
        oldTree.SetBranchStatus('jetmva2'        ,0)
        oldTree.SetBranchStatus('jetmva3'        ,0)
        oldTree.SetBranchStatus('jetmva4'        ,0)
        oldTree.SetBranchStatus('jettche1'       ,0)
        oldTree.SetBranchStatus('jettche2'       ,0)
        oldTree.SetBranchStatus('jettche3'       ,0)
        oldTree.SetBranchStatus('jettchp1'       ,0)
        oldTree.SetBranchStatus('jettchp2'       ,0)
        oldTree.SetBranchStatus('jettchp3'       ,0)
        oldTree.SetBranchStatus('lh1'            ,0)
        oldTree.SetBranchStatus('lh2'            ,0)
        oldTree.SetBranchStatus('nbrem1'         ,0)
        oldTree.SetBranchStatus('nbrem2'         ,0)
        oldTree.SetBranchStatus('sceta1'         ,0)
        oldTree.SetBranchStatus('sceta2'         ,0)
        oldTree.SetBranchStatus('triggAW'        ,0)
        oldTree.SetBranchStatus('triggBW'        ,0)
        oldTree.SetBranchStatus('bveto_munj'     ,0)
        oldTree.SetBranchStatus('bveto_munj05'   ,0)
        oldTree.SetBranchStatus('bveto_munj30'   ,0)
        oldTree.SetBranchStatus('bveto_munj3005' ,0)
        oldTree.SetBranchStatus('bveto_nj'       ,0)
        oldTree.SetBranchStatus('bveto_nj05'     ,0)
        oldTree.SetBranchStatus('bveto_nj30'     ,0)
        oldTree.SetBranchStatus('bveto_nj3005'   ,0)
        oldTree.SetBranchStatus('puWsmurf'       ,0)
        oldTree.SetBranchStatus('puWABtrue'      ,0)
        oldTree.SetBranchStatus('puWCtrue'       ,0)
        oldTree.SetBranchStatus('puWABCtrue'     ,0)
        oldTree.SetBranchStatus('puW120AB'       ,0)
        oldTree.SetBranchStatus('puW600AB'       ,0)
        oldTree.SetBranchStatus('puW120C'        ,0)
        oldTree.SetBranchStatus('puW600C'        ,0)
        oldTree.SetBranchStatus('puW120ABC'      ,0)
        oldTree.SetBranchStatus('puW600ABC'      ,0)

        ## do not clone the branches which should be scaled
        ## i.e. set status to 0
        if self.systArgument == 'muonScale':
            oldTree.SetBranchStatus('pt1'       ,0)
            oldTree.SetBranchStatus('pt2'       ,0)
            oldTree.SetBranchStatus('mll'       ,0)
            oldTree.SetBranchStatus('ptll'      ,0)
##             oldTree.SetBranchStatus('dphill'    ,0)
##             oldTree.SetBranchStatus('dphilljet' ,0)
            oldTree.SetBranchStatus('dphillmet' ,0)
            oldTree.SetBranchStatus('dphilmet' ,0)
            oldTree.SetBranchStatus('dphilmet1' ,0)
            oldTree.SetBranchStatus('dphilmet2' ,0)
            oldTree.SetBranchStatus('mth'       ,0)
            oldTree.SetBranchStatus('mtw1'      ,0)
            oldTree.SetBranchStatus('mtw2'      ,0)
            oldTree.SetBranchStatus('pfmet'     ,0)
            oldTree.SetBranchStatus('pfmetphi'  ,0)
            oldTree.SetBranchStatus('chmet'     ,0)
            oldTree.SetBranchStatus('chmetphi'  ,0)
            ## oldTree.SetBranchStatus('tcmet'     ,0)
            ## oldTree.SetBranchStatus('tcmetphi'  ,0)
            oldTree.SetBranchStatus('ppfmet'    ,0)
            oldTree.SetBranchStatus('pchmet'    ,0)
            ## oldTree.SetBranchStatus('ptcmet'    ,0)
            oldTree.SetBranchStatus('mpmet'     ,0)
            oldTree.SetBranchStatus('gammaMRStar',0)
            oldTree.SetBranchStatus('zveto',0)

        if self.systArgument == 'electronScale':
            oldTree.SetBranchStatus('pt1'       ,0)
            oldTree.SetBranchStatus('pt2'       ,0)
            oldTree.SetBranchStatus('mll'       ,0)
            oldTree.SetBranchStatus('ptll'      ,0)
##             oldTree.SetBranchStatus('dphill'    ,0)
##             oldTree.SetBranchStatus('dphilljet' ,0)
            oldTree.SetBranchStatus('dphillmet' ,0)
            oldTree.SetBranchStatus('dphilmet' ,0)
            oldTree.SetBranchStatus('dphilmet1' ,0)
            oldTree.SetBranchStatus('dphilmet2' ,0)
            oldTree.SetBranchStatus('mth'       ,0)
            oldTree.SetBranchStatus('mtw1'      ,0)
            oldTree.SetBranchStatus('mtw2'      ,0)
            oldTree.SetBranchStatus('pfmet'     ,0)
            oldTree.SetBranchStatus('pfmetphi'  ,0)
            oldTree.SetBranchStatus('chmet'     ,0)
            oldTree.SetBranchStatus('chmetphi'  ,0)
            ## oldTree.SetBranchStatus('tcmet'     ,0)
            ## oldTree.SetBranchStatus('tcmetphi'  ,0)
            oldTree.SetBranchStatus('ppfmet'    ,0)
            oldTree.SetBranchStatus('pchmet'    ,0)
            ## oldTree.SetBranchStatus('ptcmet'    ,0)
            oldTree.SetBranchStatus('mpmet'     ,0)
            oldTree.SetBranchStatus('gammaMRStar',0)
            oldTree.SetBranchStatus('zveto',0)
            
        if self.systArgument == 'leptonEfficiency':
            oldTree.SetBranchStatus('effW'      ,0)
            oldTree.SetBranchStatus('effAW'     ,0)
            oldTree.SetBranchStatus('effBW'     ,0)            

        if self.systArgument == 'jetEnergyScale':
            oldTree.SetBranchStatus('jetpt1'    ,0)
            oldTree.SetBranchStatus('jetpt2'    ,0)
            oldTree.SetBranchStatus('njet'      ,0)
            oldTree.SetBranchStatus('pfmet'     ,0)
            oldTree.SetBranchStatus('pfmetphi'  ,0)
            oldTree.SetBranchStatus('chmet'     ,0)
            oldTree.SetBranchStatus('chmetphi'  ,0)
            ## oldTree.SetBranchStatus('tcmet'     ,0)
            ## oldTree.SetBranchStatus('tcmetphi'  ,0)
            oldTree.SetBranchStatus('mth'       ,0)
            oldTree.SetBranchStatus('mtw1'      ,0)
            oldTree.SetBranchStatus('mtw2'      ,0)
##             oldTree.SetBranchStatus('dphill'    ,0)
##             oldTree.SetBranchStatus('dphilljet' ,0)
            oldTree.SetBranchStatus('dphilljetjet' ,0)
            oldTree.SetBranchStatus('dphillmet' ,0)
            oldTree.SetBranchStatus('dphilmet' ,0)
            oldTree.SetBranchStatus('dphilmet1' ,0)
            oldTree.SetBranchStatus('dphilmet2' ,0)
            oldTree.SetBranchStatus('mjj'       ,0)
            oldTree.SetBranchStatus('ppfmet'    ,0)
            oldTree.SetBranchStatus('pchmet'    ,0)
            ## oldTree.SetBranchStatus('ptcmet'    ,0)
            ## oldTree.SetBranchStatus('mpmet'     ,0)
            #oldTree.SetBranchStatus('hardbdisctche' ,0)
            #oldTree.SetBranchStatus('softbdisctche' ,0)
            oldTree.SetBranchStatus('jetpt3'    ,0)
            oldTree.SetBranchStatus('jetpt4'    ,0)
            oldTree.SetBranchStatus('cjetpt1'    ,0)
            oldTree.SetBranchStatus('cjetpt2'    ,0)
            oldTree.SetBranchStatus('njetvbf'    ,0)
            
        if self.systArgument == 'metResolution':
            oldTree.SetBranchStatus('pfmet'     ,0)
            oldTree.SetBranchStatus('pfmetphi'  ,0)
            oldTree.SetBranchStatus('chmet'     ,0)
            oldTree.SetBranchStatus('chmetphi'  ,0)
            ## oldTree.SetBranchStatus('tcmet'     ,0)
            ## oldTree.SetBranchStatus('tcmetphi'  ,0)
            oldTree.SetBranchStatus('mth'       ,0)
            oldTree.SetBranchStatus('mtw1'      ,0)
            oldTree.SetBranchStatus('mtw2'      ,0)
            oldTree.SetBranchStatus('dphillmet' ,0)
            oldTree.SetBranchStatus('dphilmet' ,0)
            oldTree.SetBranchStatus('dphilmet1' ,0)
            oldTree.SetBranchStatus('dphilmet2' ,0)
            oldTree.SetBranchStatus('ppfmet'    ,0)
            oldTree.SetBranchStatus('pchmet'    ,0)
            ## oldTree.SetBranchStatus('ptcmet'    ,0)
            oldTree.SetBranchStatus('mpmet'     ,0)            

        if self.systArgument == 'electronResolution':
            oldTree.SetBranchStatus('pt1'       ,0)
            oldTree.SetBranchStatus('pt2'       ,0)
            oldTree.SetBranchStatus('mll'       ,0)
            oldTree.SetBranchStatus('ptll'      ,0)
##             oldTree.SetBranchStatus('dphill'    ,0)
##             oldTree.SetBranchStatus('dphilljet' ,0)
            oldTree.SetBranchStatus('dphillmet' ,0)
            oldTree.SetBranchStatus('dphilmet' ,0)
            oldTree.SetBranchStatus('dphilmet1' ,0)
            oldTree.SetBranchStatus('dphilmet2' ,0)
            oldTree.SetBranchStatus('mth'       ,0)
            oldTree.SetBranchStatus('mtw1'      ,0)
            oldTree.SetBranchStatus('mtw2'      ,0)
            oldTree.SetBranchStatus('pfmet'     ,0)
            oldTree.SetBranchStatus('pfmetphi'  ,0)
            oldTree.SetBranchStatus('chmet'     ,0)
            oldTree.SetBranchStatus('chmetphi'  ,0)
            ## oldTree.SetBranchStatus('tcmet'     ,0)
            ## oldTree.SetBranchStatus('tcmetphi'  ,0)
            oldTree.SetBranchStatus('ppfmet'    ,0)
            oldTree.SetBranchStatus('pchmet'    ,0)
            ## oldTree.SetBranchStatus('ptcmet'    ,0)
            oldTree.SetBranchStatus('mpmet'     ,0)
            oldTree.SetBranchStatus('gammaMRStar',0)
            oldTree.SetBranchStatus('zveto',0)

        if self.systArgument == 'dyTemplate':
            oldTree.SetBranchStatus('pfmet'     ,0)
            oldTree.SetBranchStatus('chmet'     ,0)
            ## oldTree.SetBranchStatus('tcmet'     ,0)
            oldTree.SetBranchStatus('ppfmet'    ,0)
            oldTree.SetBranchStatus('pchmet'    ,0)
            ## oldTree.SetBranchStatus('ptcmet'    ,0)
            oldTree.SetBranchStatus('mth'       ,0)
            oldTree.SetBranchStatus('mtw1'      ,0)
            oldTree.SetBranchStatus('mtw2'      ,0)
            oldTree.SetBranchStatus('mpmet'     ,0)            
            oldTree.SetBranchStatus('njet'      ,0)
            oldTree.SetBranchStatus('dymva0'    ,0)
            oldTree.SetBranchStatus('dymva1'    ,0)

        if self.systArgument == 'puscale':
            oldTree.SetBranchStatus('puW'       ,0)

        if self.systArgument == 'chargeResolution':
            oldTree.SetBranchStatus('ch1'       ,0)
            oldTree.SetBranchStatus('ch2'       ,0)

        newTree = oldTree.CloneTree(0)
        nentries = oldTree.GetEntriesFast()
        print 'Tree with '+str(nentries)+' entries cloned...'
        self.nentries = nentries
        
        self.ttree = newTree
        ## BUT keep all branches "active" in the old tree
        oldTree.SetBranchStatus('*'  ,1)

        self.oldttree = oldTree
        for branch in self.ttree.GetListOfBranches():
            print branch


###############################################################################################
##     
##     
##        _ \   |   |                         _)         |   _)               
##       |   |  |   |     \ \   /  _` |   __|  |   _` |  __|  |   _ \   __ \  
##       ___/   |   |      \ \ /  (   |  |     |  (   |  |    |  (   |  |   | 
##      _|     \___/        \_/  \__,_| _|    _| \__,_| \__| _| \___/  _|  _| 
##                                                                            
##     

    def puVariation(self):
        from ROOT import std
 
        ## define a new branch
        print 'PU scaling'
        puW = numpy.ones(1, dtype=numpy.float32)
        self.ttree.Branch(weightNamePU,puW,weightNamePU+"/F")


        inDATAFileUp   = openTFile(puUp)
        inDATAFileDown = openTFile(puDown)
        inMCFile       = openTFile(puMC)


        puScaleDATAhistoUp   = getHist(inDATAFileUp,"pileup")
        puScaleDATAhistoDown = getHist(inDATAFileDown,"pileup")
        puScaleMChisto       = getHist(inMCFile,"pileup")


        dataUp_nBin = puScaleDATAhistoUp.GetNbinsX()
        dataUp_minValue = puScaleDATAhistoUp.GetXaxis().GetXmin()
        dataUp_maxValue = puScaleDATAhistoUp.GetXaxis().GetXmax()
        dataUp_dValue = (dataUp_maxValue - dataUp_minValue) / dataUp_nBin

        dataDown_nBin = puScaleDATAhistoDown.GetNbinsX()
        dataDown_minValue = puScaleDATAhistoDown.GetXaxis().GetXmin()
        dataDown_maxValue = puScaleDATAhistoDown.GetXaxis().GetXmax()
        dataDown_dValue = (dataDown_maxValue - dataDown_minValue) / dataDown_nBin

        mc_nBin = puScaleMChisto.GetNbinsX()
        mc_minValue = puScaleMChisto.GetXaxis().GetXmin()
        mc_maxValue = puScaleMChisto.GetXaxis().GetXmax()
        mc_dValue = (mc_maxValue - mc_minValue) / mc_nBin
  
        ratioUp = mc_dValue/dataUp_dValue
        nBinUp = dataUp_nBin
        minValueUp = dataUp_minValue
        maxValueUp = dataUp_maxValue
        dValueUp = dataUp_dValue

        ratioDown = mc_dValue/dataDown_dValue
        nBinDown = dataDown_nBin
        minValueDown = dataDown_minValue
        maxValueDown = dataDown_maxValue
        dValueDown = dataDown_dValue
      
        if (mc_dValue/dataUp_dValue - (int) (mc_dValue/dataUp_dValue)) != 0 :
          print " ERROR:: incompatible intervals!  Up"
          exit(0);
        
        if (mc_dValue/dataDown_dValue - (int) (mc_dValue/dataDown_dValue)) != 0 :
          print " ERROR:: incompatible intervals!  Down"
          exit(0);
 
        puScaleDATAUp   = std.vector(float)()
        puScaleDATADown = std.vector(float)()
        puScaleMCtemp   = std.vector(float)()
        puScaleMC       = std.vector(float)()

        ################
        nBin = nBinUp
        # remove last bin -> peak in DATA distribution
        nBin = nBin-1
        ################   

        for iBin in range(0, nBin):
            puScaleDATAUp.push_back(puScaleDATAhistoUp.GetBinContent(iBin+1))
            puScaleDATADown.push_back(puScaleDATAhistoDown.GetBinContent(iBin+1))
            mcbin = int(floor(iBin / ratioUp))
            puScaleMCtemp.push_back(puScaleMChisto.GetBinContent(mcbin+1))

 
        integralDATA = 0.
        integralMC   = 0.
 
        for iBin in range(0, nBin):
            integralDATA += puScaleDATAUp.at(iBin)
            integralMC   += puScaleMCtemp.at(iBin)

        print " integralDATA = " + "%.3f" %integralDATA
        print " integralMC   = " + "%.3f" %integralMC
 
        for iBin in range(0, nBin):
            puScaleMC.push_back( puScaleMCtemp.at(iBin) * integralDATA / integralMC) 


 
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i = 0
        for ientry in range(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 50000
            if i > 0 and i%step == 0.:
                print str(i)+' events processed.'

            puW[0] = 1.
            
            
            if self.direction == 'up':
                ibin = int(self.oldttree.trpu / dValueUp)
                if ibin < puScaleDATAUp.size() :
                   if puScaleMC.at(ibin) != 0 :
                      puW[0] = 1. * puScaleDATAUp.at(ibin) / puScaleMC.at(ibin)
                   else :
                      puW[0] = 1.
                else :
                   ibin = puScaleDATAUp.size()-1
                   if puScaleMC.at(ibin) != 0 :
                      puW[0] = 1. * puScaleDATAUp.at(ibin) / puScaleMC.at(ibin)
                   else :
                      puW[0] = 1.


            if self.direction == 'down':
                ibin = int(self.oldttree.trpu / dValueDown)
                if ibin < puScaleDATADown.size() :
                   if puScaleMC.at(ibin) != 0 :
                      puW[0] = 1. * puScaleDATADown.at(ibin) / puScaleMC.at(ibin)
                   else :
                      puW[0] = 1.
                else :
                   ibin = puScaleDATADown.size()-1
                   if puScaleMC.at(ibin) != 0 :
                      puW[0] = 1. * puScaleDATADown.at(ibin) / puScaleMC.at(ibin)
                   else :
                      puW[0] = 1.

            if self.verbose is True:
                print '-----------------------------------'
                print 'puW: '+str(puW[0])


            # fill old and new values
            self.ttree.Fill()







###############################################################################################
## ___  ___                    _____            _      
## |  \/  |                   /  ___|          | |     
## | .  . |_   _  ___  _ __   \ `--.  ___  __ _| | ___ 
## | |\/| | | | |/ _ \| '_ \   `--. \/ __|/ _` | |/ _ \
## | |  | | |_| | (_) | | | | /\__/ / (__| (_| | |  __/
## \_|  |_/\__,_|\___/|_| |_| \____/ \___|\__,_|_|\___|
##                                                    
    def muonScale(self):
##        uncertainty = 0.02
        uncertainty = muonUncertainty
        if self.direction == 'up':
            direction = +1.0
        if self.direction == 'down':
            direction = -1.0
        scale = uncertainty * direction

        ## define a new branch
        pt1 = numpy.zeros(1, dtype=numpy.float32)
        pt2 = numpy.zeros(1, dtype=numpy.float32)
        mll = numpy.zeros(1, dtype=numpy.float32)
        ptll = numpy.zeros(1, dtype=numpy.float32)
##         dphill = numpy.zeros(1, dtype=numpy.float32)
##         dphilljet = numpy.zeros(1, dtype=numpy.float32)
        dphillmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet1 = numpy.zeros(1, dtype=numpy.float32)
        dphilmet2 = numpy.zeros(1, dtype=numpy.float32)
        mth = numpy.zeros(1, dtype=numpy.float32)
        mtw1 = numpy.zeros(1, dtype=numpy.float32)
        mtw2 = numpy.zeros(1, dtype=numpy.float32)
        pfmet = numpy.zeros(1, dtype=numpy.float32)
        pfmetphi = numpy.zeros(1, dtype=numpy.float32)
        chmet = numpy.zeros(1, dtype=numpy.float32)
        chmetphi = numpy.zeros(1, dtype=numpy.float32)
        ## tcmet = numpy.zeros(1, dtype=numpy.float32)
        ## tcmetphi = numpy.zeros(1, dtype=numpy.float32)
        ppfmet = numpy.zeros(1, dtype=numpy.float32)
        pchmet = numpy.zeros(1, dtype=numpy.float32)
        ## ptcmet = numpy.zeros(1, dtype=numpy.float32)
        mpmet = numpy.zeros(1, dtype=numpy.float32)
        gammaMRStar = numpy.zeros(1, dtype=numpy.float32)
        zveto = numpy.zeros(1, dtype=int)
                
        self.ttree.Branch('pt1',pt1,'pt1/F')
        self.ttree.Branch('pt2',pt2,'pt2/F')
        self.ttree.Branch('mll',mll,'mll/F')
        self.ttree.Branch('ptll',ptll,'ptll/F')
##         self.ttree.Branch('dphill',dphill,'dphill/F')
##         self.ttree.Branch('dphilljet',dphilljet,'dphilljet/F')
        self.ttree.Branch('dphillmet',dphillmet,'dphillmet/F')
        self.ttree.Branch('dphilmet',dphilmet,'dphilmet/F')
        self.ttree.Branch('dphilmet1',dphilmet1,'dphilmet1/F')
        self.ttree.Branch('dphilmet2',dphilmet2,'dphilmet2/F')
        self.ttree.Branch('mth',mth,'mth/F')
        self.ttree.Branch('mtw1',mtw1,'mtw1/F')
        self.ttree.Branch('mtw2',mtw2,'mtw2/F')
        self.ttree.Branch('pfmet',pfmet,'pfmet/F')
        self.ttree.Branch('pfmetphi',pfmetphi,'pfmetphi/F')
        self.ttree.Branch('chmet',chmet,'chmet/F')
        self.ttree.Branch('chmetphi',chmetphi,'chmetphi/F')
        ## self.ttree.Branch('tcmet',tcmet,'tcmet/F')
        ## self.ttree.Branch('tcmetphi',tcmetphi,'tcmetphi/F')
        self.ttree.Branch('ppfmet',ppfmet,'ppfmet/F')
        self.ttree.Branch('pchmet',pchmet,'pchmet/F')
        ## self.ttree.Branch('ptcmet',ptcmet,'ptcmet/F')
        self.ttree.Branch('mpmet',mpmet,'mpmet/F')
        self.ttree.Branch('gammaMRStar',gammaMRStar,'gammaMRStar/F')
        self.ttree.Branch('zveto',zveto,'zveto/I')

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            # get the "old" lepton pt
            pt1_hold  = self.oldttree.pt1
            eta1_hold = self.oldttree.eta1
            phi1_hold = self.oldttree.phi1
            pt2_hold  = self.oldttree.pt2
            eta2_hold = self.oldttree.eta2
            phi2_hold = self.oldttree.phi2

            ## scale the lepton pt
            ## muon-muon channel
            if self.oldttree.channel == 0:
                pt1[0] = pt1_hold + pt1_hold * scale
                pt2[0] = pt2_hold + pt2_hold * scale
            ## electron-electron channel    
            ## dont scale at all
            if self.oldttree.channel == 1:
                pt1[0] = pt1_hold  ## do not scale electrons here
                pt2[0] = pt2_hold  ## independent of "up" or "down"
            ## electron-muon channel
            if self.oldttree.channel == 2:
                pt1[0] = pt1_hold
                pt2[0] = pt2_hold + pt2_hold * scale
            ## muon-electron channel    
            if self.oldttree.channel == 3:
                pt1[0] = pt1_hold + pt1_hold * scale
                pt2[0] = pt2_hold 

##             print '---------------------'
##             print str(self.oldttree.channel)+': '+str(pt1_hold)+' -> '+str(pt1[0])
##             print str(self.oldttree.channel)+': '+str(pt2_hold)+' -> '+str(pt2[0])


## FIXME: after the scaling one has to recalculate some variables
##        like invariant mass etc...
##        does delta phi, eta change? guess not...
            l1_hold = ROOT.TLorentzVector()
            l2_hold = ROOT.TLorentzVector()
            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1_hold.SetPtEtaPhiM(pt1_hold, eta1_hold, phi1_hold, 0)
            l2_hold.SetPtEtaPhiM(pt2_hold, eta2_hold, phi2_hold, 0)
            l1.SetPtEtaPhiM(pt1[0], eta1_hold, phi1_hold, 0)
            l2.SetPtEtaPhiM(pt2[0], eta2_hold, phi2_hold, 0)


            ## correct MET
            ## PFMET:
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)           
            ## FIXME: cross-check this!!
            ## add "old leptons" and subtract the "new" ones:
            met = correctMet(met, l1_hold, l2_hold, l1, l2)

            ## substitute the values
            pfmet[0] = met.Pt()
            pfmetphi[0] = met.Phi()
            ## other METs:
            ## - chmet
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)      
            chmet4 = correctMet(chmet4, l1_hold, l2_hold, l1, l2)
            chmet[0] = chmet4.Pt()
            chmetphi[0] = chmet4.Phi()
            ## ## - tcmet
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)      
            ## tcmet4 = correctMet(tcmet4, l1_hold, l2_hold, l1, l2)
            ## tcmet[0] = tcmet4.Pt()
            ## tcmetphi[0] = tcmet4.Phi()

            ## correct projected MET
            ratio = pfmet[0] / self.oldttree.pfmet
            ppfmet[0] = self.oldttree.ppfmet * ratio
            chratio = chmet[0] / self.oldttree.chmet
            pchmet[0] = self.oldttree.pchmet * chratio
            ## tcratio = tcmet[0] / self.oldttree.tcmet
            ## ptcmet[0] = self.oldttree.ptcmet * tcratio
            mpmet[0] = min( ppfmet[0], pchmet[0] )

            mll[0]  = invariantMass(l1, l2)
            ptll[0] = dileptonPt(l1, l2)
##             dphill[0] =  deltaPhi(l1,l2)

##             j1 = ROOT.TLorentzVector()
##             j1.SetPtEtaPhiM(self.oldttree.jetpt1, self.oldttree.jeteta1, self.oldttree.jetphi1, 0)
##             dphilljet[0] =  deltaPhi(l1+l2,j1)

            dphillmet[0] =  deltaPhi(l1+l2,met)
            dphilmet1[0] =  deltaPhi(l1,met)
            dphilmet2[0] =  deltaPhi(l2,met)
            dphilmet[0] =  min(dphilmet1[0], dphilmet2[0])
            
            mth[0] = transverseMass((l1+l2),met)
            mtw1[0] = transverseMass((l1),met)
            mtw2[0] = transverseMass((l2),met)

            gammaMRStar[0] = calculateGammaMRStar(l1,l2)


            zveto[0] = checkZveto(mll[0], self.oldttree.channel)

            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'scale: '+str(scale)
                print 'channel: '+str(self.oldttree.channel)
                print 'pt1: '+str(pt1_hold)+' -> '+ str(pt1[0])
                print 'pt1: '+str(pt2_hold)+' -> '+ str(pt2[0])
                print 'pfmet: '    +str(self.oldttree.pfmet)    +to+str(pfmet[0])
                print 'pfmetphi: ' +str(self.oldttree.pfmetphi) +to+str(pfmetphi[0])
                print 'chmet: '    +str(self.oldttree.chmet)    +to+str(chmet[0])
                print 'chmetphi: ' +str(self.oldttree.chmetphi) +to+str(chmetphi[0])
                ## print 'tcmet: '    +str(self.oldttree.tcmet)    +to+str(tcmet[0])
                ## print 'tcmetphi: ' +str(self.oldttree.tcmetphi) +to+str(tcmetphi[0])
                print 'mll: '    + str(self.oldttree.mll)    +to+ str(mll[0])
                print 'ptll: '   + str(self.oldttree.ptll)   +to+ str(ptll[0])
##                 print 'dphill: ' + str(self.oldttree.dphill) +to+ str(dphill[0])
                print 'dphillmet: ' + str(self.oldttree.dphillmet) +to+ str(dphillmet[0])
                print 'dphilmet: ' + str(self.oldttree.dphilmet) +to+ str(dphilmet[0])
##                 print 'dphilljet: ' + str(self.oldttree.dphilljet) +to+ str(dphilljet[0])
                print 'dphilmet1: ' + str(self.oldttree.dphilmet1) +to+ str(dphilmet1[0])
                print 'dphilmet2: ' + str(self.oldttree.dphilmet2) +to+ str(dphilmet2[0])
                print 'mth: ' + str(self.oldttree.mth) +to+ str(mth[0])
                print 'mtw1: ' + str(self.oldttree.mtw1) +to+ str(mtw1[0])
                print 'mtw2: ' + str(self.oldttree.mtw2) +to+ str(mtw2[0])
                print 'ppfmet: '    +str(self.oldttree.ppfmet)    +to+str(ppfmet[0])
                print 'pchmet: '    +str(self.oldttree.pchmet)    +to+str(pchmet[0])
                ## print 'ptcmet: '    +str(self.oldttree.ptcmet)    +to+str(ptcmet[0])
                print 'mpmet: '    +str(self.oldttree.mpmet)    +to+str(mpmet[0])
                print 'gammaMRStar: '    +str(self.oldttree.gammaMRStar)    +to+str(gammaMRStar[0])
                print 'zveto: '    +str(self.oldttree.zveto)    +to+str(zveto[0])

            
            # fill old and new values
            self.ttree.Fill()


###############################################################################################
##  _____ _           _                     _____            _      
## |  ___| |         | |                   /  ___|          | |     
## | |__ | | ___  ___| |_ _ __ ___  _ __   \ `--.  ___  __ _| | ___ 
## |  __|| |/ _ \/ __| __| '__/ _ \| '_ \   `--. \/ __|/ _` | |/ _ \
## | |___| |  __/ (__| |_| | | (_) | | | | /\__/ / (__| (_| | |  __/
## \____/|_|\___|\___|\__|_|  \___/|_| |_| \____/ \___|\__,_|_|\___|
##                                                                 

    def electronScale(self):
        uncertaintyEB = electronUncertaintyEB
        uncertaintyEE = electronUncertaintyEE
        if self.direction == 'up':
            direction = +1.0
        if self.direction == 'down':
            direction = -1.0
        scaleEB = uncertaintyEB * direction
        scaleEE = uncertaintyEE * direction
                
        ## define a new branch
        pt1 = numpy.zeros(1, dtype=numpy.float32)
        pt2 = numpy.zeros(1, dtype=numpy.float32)
        mll = numpy.zeros(1, dtype=numpy.float32)
        ptll = numpy.zeros(1, dtype=numpy.float32)
##         dphill = numpy.zeros(1, dtype=numpy.float32)
##         dphilljet = numpy.zeros(1, dtype=numpy.float32)
        dphillmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet1 = numpy.zeros(1, dtype=numpy.float32)
        dphilmet2 = numpy.zeros(1, dtype=numpy.float32)
        mth = numpy.zeros(1, dtype=numpy.float32)
        mtw1 = numpy.zeros(1, dtype=numpy.float32)
        mtw2 = numpy.zeros(1, dtype=numpy.float32)
        pfmet = numpy.zeros(1, dtype=numpy.float32)
        pfmetphi = numpy.zeros(1, dtype=numpy.float32)
        chmet = numpy.zeros(1, dtype=numpy.float32)
        chmetphi = numpy.zeros(1, dtype=numpy.float32)
        ## tcmet = numpy.zeros(1, dtype=numpy.float32)
        ## tcmetphi = numpy.zeros(1, dtype=numpy.float32)
        ppfmet = numpy.zeros(1, dtype=numpy.float32)
        pchmet = numpy.zeros(1, dtype=numpy.float32)
        ## ptcmet = numpy.zeros(1, dtype=numpy.float32)
        mpmet = numpy.zeros(1, dtype=numpy.float32)
        gammaMRStar = numpy.zeros(1, dtype=numpy.float32)
        zveto = numpy.zeros(1, dtype=int)        
        self.ttree.Branch('pt1',pt1,'pt1/F')
        self.ttree.Branch('pt2',pt2,'pt2/F')
        self.ttree.Branch('mll',mll,'mll/F')
        self.ttree.Branch('ptll',ptll,'ptll/F')
##         self.ttree.Branch('dphill',dphill,'dphill/F')
##         self.ttree.Branch('dphilljet',dphilljet,'dphilljet/F')
        self.ttree.Branch('dphillmet',dphillmet,'dphillmet/F')
        self.ttree.Branch('dphilmet',dphilmet,'dphilmet/F')
        self.ttree.Branch('dphilmet1',dphilmet1,'dphilmet1/F')
        self.ttree.Branch('dphilmet2',dphilmet2,'dphilmet2/F')
        self.ttree.Branch('mth',mth,'mth/F')
        self.ttree.Branch('mtw1',mtw1,'mtw1/F')
        self.ttree.Branch('mtw2',mtw2,'mtw2/F')
        self.ttree.Branch('pfmet',pfmet,'pfmet/F')
        self.ttree.Branch('pfmetphi',pfmetphi,'pfmetphi/F')
        self.ttree.Branch('chmet',chmet,'chmet/F')
        self.ttree.Branch('chmetphi',chmetphi,'chmetphi/F')
        ## self.ttree.Branch('tcmet',tcmet,'tcmet/F')
        ## self.ttree.Branch('tcmetphi',tcmetphi,'tcmetphi/F')
        self.ttree.Branch('ppfmet',ppfmet,'ppfmet/F')
        self.ttree.Branch('pchmet',pchmet,'pchmet/F')
        ## self.ttree.Branch('ptcmet',ptcmet,'ptcmet/F')
        self.ttree.Branch('mpmet',mpmet,'mpmet/F')
        self.ttree.Branch('gammaMRStar',gammaMRStar,'gammaMRStar/F')
        self.ttree.Branch('zveto',zveto,'zveto/I')
 
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            # get the "old" lepton pt
            pt1_hold  = self.oldttree.pt1
            eta1_hold = self.oldttree.eta1
            phi1_hold = self.oldttree.phi1
            pt2_hold  = self.oldttree.pt2
            eta2_hold = self.oldttree.eta2
            phi2_hold = self.oldttree.phi2

            ## scale the lepton pt
            ## muon-muon channel
            ## dont scale at all
            if self.oldttree.channel == 0:
                pt1[0] = pt1_hold           ## do not scale electrons here  
                pt2[0] = pt2_hold           ## independent of "up" or "down"
            ## electron-electron channel    
            if self.oldttree.channel == 1:
                if abs(self.oldttree.eta1) < 1.5:
                    pt1[0] = pt1_hold + pt1_hold * scaleEB
                if abs(self.oldttree.eta1) >= 1.5:
                    pt1[0] = pt1_hold + pt1_hold * scaleEE

                if abs(self.oldttree.eta2) < 1.5:
                    pt2[0] = pt2_hold + pt2_hold * scaleEB
                if abs(self.oldttree.eta2) >= 1.5:
                    pt2[0] = pt2_hold + pt2_hold * scaleEE
            ## electron-muon channel
            if self.oldttree.channel == 2:
                if abs(self.oldttree.eta1) < 1.5:
                    pt1[0] = pt1_hold + pt1_hold * scaleEB
                if abs(self.oldttree.eta1) >= 1.5:
                    pt1[0] = pt1_hold + pt1_hold * scaleEE
                pt2[0] = pt2_hold
            ## muon-electron channel    
            if self.oldttree.channel == 3:
                pt1[0] = pt1_hold
                if abs(self.oldttree.eta2) < 1.5:
                    pt2[0] = pt2_hold + pt2_hold * scaleEB
                if abs(self.oldttree.eta2) >= 1.5:
                    pt2[0] = pt2_hold + pt2_hold * scaleEE


                

            
## FIXME: after the scaling one has to recalculate some variables
##        like invariant mass etc...
##        does delta phi, eta change? guess not...

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1_hold = ROOT.TLorentzVector()
            l2_hold = ROOT.TLorentzVector()
            l1_hold.SetPtEtaPhiM(pt1_hold, eta1_hold, phi1_hold, 0)
            l2_hold.SetPtEtaPhiM(pt2_hold, eta2_hold, phi2_hold, 0)
            l1.SetPtEtaPhiM(pt1[0], eta1_hold, phi1_hold, 0)
            l2.SetPtEtaPhiM(pt2[0], eta2_hold, phi2_hold, 0)

            ## correct MET
            ## PFMET:
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)           
            ## FIXME: cross-check this!!
            ## add "old leptons" and subtract the "new" ones:
            met = correctMet(met, l1_hold, l2_hold, l1, l2)

            ## substitute the values
            pfmet[0] = met.Pt()
            pfmetphi[0] = met.Phi()
            ## other METs:
            ## - chmet
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)      
            chmet4 = correctMet(chmet4, l1_hold, l2_hold, l1, l2)
            chmet[0] = chmet4.Pt()
            chmetphi[0] = chmet4.Phi()
            ## ## - tcmet
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)      
            ## tcmet4 = correctMet(tcmet4, l1_hold, l2_hold, l1, l2)
            ## tcmet[0] = tcmet4.Pt()
            ## tcmetphi[0] = tcmet4.Phi()

            ## correct projected MET
            ratio = pfmet[0] / self.oldttree.pfmet
            ppfmet[0] = self.oldttree.ppfmet * ratio
            chratio = chmet[0] / self.oldttree.chmet
            pchmet[0] = self.oldttree.pchmet * chratio
            ## tcratio = tcmet[0] / self.oldttree.tcmet
            ## ptcmet[0] = self.oldttree.ptcmet * tcratio
            mpmet[0] = min( ppfmet[0], pchmet[0] )

            ## additional variables
            mll[0]  = invariantMass(l1, l2)
            ptll[0] = dileptonPt(l1, l2)

##             dphill[0] =  deltaPhi(l1,l2)
            dphillmet[0] =  deltaPhi(l1+l2,met)
            dphilmet1[0] =  deltaPhi(l1,met)
            dphilmet2[0] =  deltaPhi(l2,met)
            dphilmet[0]  =  min(dphilmet1[0], dphilmet2[0])

            j1 = ROOT.TLorentzVector()
            j1.SetPtEtaPhiM(self.oldttree.jetpt1, self.oldttree.jeteta1, self.oldttree.jetphi1, 0)
##             dphilljet[0] =  deltaPhi(l1+l2,j1)

            mth[0] = transverseMass((l1+l2),met)
            mtw1[0] = transverseMass((l1),met)
            mtw2[0] = transverseMass((l2),met)

            gammaMRStar[0] = calculateGammaMRStar(l1,l2)

            zveto[0] = checkZveto(mll[0], self.oldttree.channel)

            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'scale EB: '+str(scaleEB)
                print 'scale EE: '+str(scaleEE)
                print 'channel: '+str(self.oldttree.channel)
                print 'pt1: '+str(pt1_hold)+' -> '+ str(pt1[0])
                print 'pt1: '+str(pt2_hold)+' -> '+ str(pt2[0])
                print 'pfmet: '    +str(self.oldttree.pfmet)    +to+str(pfmet[0])
                print 'pfmetphi: ' +str(self.oldttree.pfmetphi) +to+str(pfmetphi[0])
                print 'chmet: '    +str(self.oldttree.chmet)    +to+str(chmet[0])
                print 'chmetphi: ' +str(self.oldttree.chmetphi) +to+str(chmetphi[0])
                ## print 'tcmet: '    +str(self.oldttree.tcmet)    +to+str(tcmet[0])
                ## print 'tcmetphi: ' +str(self.oldttree.tcmetphi) +to+str(tcmetphi[0])
                print 'mll: '    + str(self.oldttree.mll)    +to+ str(mll[0])
                print 'ptll: '   + str(self.oldttree.ptll)   +to+ str(ptll[0])
##                 print 'dphill: ' + str(self.oldttree.dphill) +to+ str(dphill[0])
                print 'dphillmet: ' + str(self.oldttree.dphillmet) +to+ str(dphillmet[0])
                print 'dphilmet: ' + str(self.oldttree.dphilmet) +to+ str(dphilmet[0])
##                 print 'dphilljet: ' + str(self.oldttree.dphilljet) +to+ str(dphilljet[0])
                print 'dphilmet1: ' + str(self.oldttree.dphilmet1) +to+ str(dphilmet1[0])
                print 'dphilmet2: ' + str(self.oldttree.dphilmet2) +to+ str(dphilmet2[0])
                print 'mth: ' + str(self.oldttree.mth) +to+ str(mth[0])
                print 'mtw1: ' + str(self.oldttree.mtw1) +to+ str(mtw1[0])
                print 'mtw2: ' + str(self.oldttree.mtw2) +to+ str(mtw2[0])
                print 'ppfmet: '    +str(self.oldttree.ppfmet)    +to+str(ppfmet[0])
                print 'pchmet: '    +str(self.oldttree.pchmet)    +to+str(pchmet[0])
                ## print 'ptcmet: '    +str(self.oldttree.ptcmet)    +to+str(ptcmet[0])
                print 'mpmet: '    +str(self.oldttree.mpmet)    +to+str(mpmet[0])
                print 'gammaMRStar: '    +str(self.oldttree.gammaMRStar)    +to+str(gammaMRStar[0])
                print 'zveto: '    +str(self.oldttree.zveto)    +to+str(zveto[0])

                            

            
            # fill old and new values
            self.ttree.Fill()

        


###############################################################################################
##    ___      _     _____                              _____            _      
##   |_  |    | |   |  ___|                            /  ___|          | |     
##     | | ___| |_  | |__  _ __   ___ _ __ __ _ _   _  \ `--.  ___  __ _| | ___ 
##     | |/ _ \ __| |  __|| '_ \ / _ \ '__/ _` | | | |  `--. \/ __|/ _` | |/ _ \
## /\__/ /  __/ |_  | |___| | | |  __/ | | (_| | |_| | /\__/ / (__| (_| | |  __/
## \____/ \___|\__| \____/|_| |_|\___|_|  \__, |\__, | \____/ \___|\__,_|_|\___|
##                                         __/ | __/ |                          
##                                        |___/ |___/                           
##
    def jetEnergyScale(self):
        jetthreshold = 30.
        if self.direction == 'up':
            direction = +1.0
        if self.direction == 'down':
            direction = -1.0

        ## read the JES corrections
        jeu = []
        base_path = os.path.join(os.getenv('CMSSW_BASE'),'src/HWWAnalysis/ShapeAnalysis/data/')
        file = open(base_path+'START38_V13_AK5PF_Uncertainty.txt')

        for line in file:
            if (line[0] == '#' or line[0] == '{'):
                continue
            s = line.split(None)
            #print s[0],s[1],s[2],s[3]
            #print s
            jeu.append(s)

        ## define a new branch
        jetpt1 = numpy.zeros(1, dtype=numpy.float32)
        jetpt2 = numpy.zeros(1, dtype=numpy.float32)
        njet = numpy.zeros(1, dtype=numpy.float32)
        pfmet = numpy.zeros(1, dtype=numpy.float32)
        pfmetphi = numpy.zeros(1, dtype=numpy.float32)
        chmet = numpy.zeros(1, dtype=numpy.float32)
        chmetphi = numpy.zeros(1, dtype=numpy.float32)
        ## tcmet = numpy.zeros(1, dtype=numpy.float32)
        ## tcmetphi = numpy.zeros(1, dtype=numpy.float32)
        mth = numpy.zeros(1, dtype=numpy.float32)
        mtw1 = numpy.zeros(1, dtype=numpy.float32)
        mtw2 = numpy.zeros(1, dtype=numpy.float32)
##         dphill = numpy.zeros(1, dtype=numpy.float32)
##         dphilljet = numpy.zeros(1, dtype=numpy.float32)
        dphilljetjet = numpy.zeros(1, dtype=numpy.float32)
        dphillmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet1 = numpy.zeros(1, dtype=numpy.float32)
        dphilmet2 = numpy.zeros(1, dtype=numpy.float32)
        mjj = numpy.zeros(1, dtype=numpy.float32)
        ppfmet = numpy.zeros(1, dtype=numpy.float32)
        pchmet = numpy.zeros(1, dtype=numpy.float32)
        ## ptcmet = numpy.zeros(1, dtype=numpy.float32)
        mpmet = numpy.zeros(1, dtype=numpy.float32)
        #hardbdisctche = numpy.zeros(1, dtype=numpy.float32)
        #softbdisctche = numpy.zeros(1, dtype=numpy.float32)
        jetpt3 = numpy.zeros(1, dtype=numpy.float32)
        jetpt4 = numpy.zeros(1, dtype=numpy.float32)
        cjetpt1 = numpy.zeros(1, dtype=numpy.float32)
        cjetpt2 = numpy.zeros(1, dtype=numpy.float32)
        njetvbf = numpy.zeros(1, dtype=numpy.float32)

        self.ttree.Branch('jetpt1',jetpt1,'jetpt1/F')
        self.ttree.Branch('jetpt2',jetpt2,'jetpt2/F')
        self.ttree.Branch('njet',njet,'njet/F')
        self.ttree.Branch('pfmet',pfmet,'pfmet/F')
        self.ttree.Branch('pfmetphi',pfmetphi,'pfmetphi/F')
        self.ttree.Branch('chmet',chmet,'chmet/F')
        self.ttree.Branch('chmetphi',chmetphi,'chmetphi/F')
        ## self.ttree.Branch('tcmet',tcmet,'tcmet/F')
        ## self.ttree.Branch('tcmetphi',tcmetphi,'tcmetphi/F')
        self.ttree.Branch('mth',mth,'mth/F')
        self.ttree.Branch('mtw1',mtw1,'mtw1/F')
        self.ttree.Branch('mtw2',mtw2,'mtw2/F')
##         self.ttree.Branch('dphill',dphill,'dphill/F')
##         self.ttree.Branch('dphilljet',dphilljet,'dphilljet/F')
        self.ttree.Branch('dphilljetjet',dphilljetjet,'dphilljetjet/F')
        self.ttree.Branch('dphillmet',dphillmet,'dphillmet/F')
        self.ttree.Branch('dphilmet',dphilmet,'dphilmet/F')
        self.ttree.Branch('dphilmet1',dphilmet1,'dphilmet1/F')
        self.ttree.Branch('dphilmet2',dphilmet2,'dphilmet2/F')
        self.ttree.Branch('mjj',mjj,'mjj/F')
        self.ttree.Branch('ppfmet',ppfmet,'ppfmet/F')
        self.ttree.Branch('pchmet',pchmet,'pchmet/F')
        ## self.ttree.Branch('ptcmet',ptcmet,'ptcmet/F')     
        self.ttree.Branch('mpmet',mpmet,'mpmet/F')
        #self.ttree.Branch('hardbdisctche',hardbdisctche,'hardbdisctche/F')
        #self.ttree.Branch('softbdisctche',softbdisctche,'softbdisctche/F')
        self.ttree.Branch('jetpt3',jetpt3,'jetpt3/F')
        self.ttree.Branch('jetpt4',jetpt4,'jetpt4/F')
        self.ttree.Branch('cjetpt1',cjetpt1,'cjetpt1/F')
        self.ttree.Branch('cjetpt2',cjetpt2,'cjetpt2/F')
        self.ttree.Branch('njetvbf',njetvbf,'njetvbf/F')

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
## FIXME: load tree envirenement like Chiara does?
##             j = loadTree(i)
##             if j < 0:
##                 break
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## calculate the scaled pt
            scale1 = -1. ## a dummy value...
            scale2 = -1.
            scale3 = -1.
            scale4 = -1.

            ## get pt and eta of the jets
            pt1  = self.oldttree.jetpt1
            eta1 = self.oldttree.jeteta1
            phi1 = self.oldttree.jetphi1
            pt2  = self.oldttree.jetpt2
            eta2 = self.oldttree.jeteta2
            phi2 = self.oldttree.jetphi2
            pt3  = self.oldttree.jetpt3
            eta3 = self.oldttree.jeteta3
            phi3 = self.oldttree.jetphi3
            pt4  = self.oldttree.jetpt4
            eta4 = self.oldttree.jeteta4
            phi4 = self.oldttree.jetphi4

            cpt1  = self.oldttree.cjetpt1
            ceta1 = self.oldttree.cjeteta1
            cphi1 = self.oldttree.cjetphi1
            cpt2  = self.oldttree.cjetpt2
            ceta2 = self.oldttree.cjeteta2
            cphi2 = self.oldttree.cjetphi2

 

            ## get the scale factor - i.e. this is the relative uncertainty!
            scale1 = getJEUFactor(pt1, eta1, jeu) * direction
            scale2 = getJEUFactor(pt2, eta2, jeu) * direction
            scale3 = getJEUFactor(pt3, eta3, jeu) * direction
            scale4 = getJEUFactor(pt4, eta4, jeu) * direction
            cscale1 = getJEUFactor(cpt1, ceta1, jeu) * direction
            cscale2 = getJEUFactor(cpt2, ceta2, jeu) * direction


            # get the "old" jet pt
            jetpt1_hold = self.oldttree.jetpt1
            jetpt2_hold = self.oldttree.jetpt2
            jetpt3_hold = self.oldttree.jetpt3
            jetpt4_hold = self.oldttree.jetpt4
            cjetpt1_hold = self.oldttree.cjetpt1
            cjetpt2_hold = self.oldttree.cjetpt2

            ## do not scale "no jet"
            if jetpt1_hold < 0:
                scale1 = 0
            if jetpt2_hold < 0: 
                scale2 = 0
            if cjetpt1_hold < 0:
                cscale1 = 0
            if cjetpt2_hold < 0: 
                cscale2 = 0

            # scale the jet pt
            jetpt1[0] = jetpt1_hold + jetpt1_hold * scale1
            jetpt2[0] = jetpt2_hold + jetpt2_hold * scale2
            jetpt3[0] = jetpt3_hold + jetpt3_hold * scale3
            jetpt4[0] = jetpt4_hold + jetpt4_hold * scale4
            cjetpt1[0] = cjetpt1_hold + cjetpt1_hold * scale1
            cjetpt2[0] = cjetpt2_hold + cjetpt2_hold * scale2

##             print '---------------------'
##             print str(jetpt1_hold)+' -> '+str( jetpt1[0])
##             print str(jetpt2_hold)+' -> '+str( jetpt2[0])
            
            # calculate the number of jets
            # we only have bin migration, so check if a jet "walks" over the threshold
            # we can not gain a potential third jet!!
            # remind the vbf analysis people of that
##             n = self.oldttree.njet
##             if jetpt1_hold < jetthreshold and jetpt1[0] > jetthreshold:
##                 n+=1
##             if jetpt2_hold < jetthreshold and jetpt2[0] > jetthreshold:
##                 n+=1
##             if jetpt1_hold > jetthreshold and jetpt1[0] < jetthreshold:
##                 n-=1
##             if jetpt2_hold > jetthreshold and jetpt2[0] < jetthreshold:
##                 n-=1
##             njet[0] = n

            nJetOverThreshold = 0
            if jetpt1[0] > jetthreshold :
                nJetOverThreshold+=1
            if jetpt2[0] > jetthreshold :
                nJetOverThreshold+=1
            if jetpt3[0] > jetthreshold :
                nJetOverThreshold+=1
            if jetpt4[0] > jetthreshold :
                nJetOverThreshold+=1
            njet[0] = nJetOverThreshold

            # calculate the number of jets between tag jets (NB: no jet order inversion is considered!)
            newnjetvbf = 0
            if cjetpt1[0] > jetthreshold :
                newnjetvbf+=1
            if cjetpt2[0] > jetthreshold :
                newnjetvbf+=1
            njetvbf[0] = newnjetvbf


            ## set hardbdisc and soft...
            #if njet[0] == 2:
            #    hardbdisctche[0] = max(self.oldttree.jettche1, self.oldttree.jettche2)
            #if njet[0] == 1:
            #    hardbdiscrche[0] = self.oldttree.jettche1
            #    softbdisctche[0] = max(self.oldttree.jettche2, self.oldttree.softbdisc)
            #if njet[0] == 0:
            #    hardbdisctche[0] = -9999.9
            #    softbdisctche[0] = max(max(self.oldttree.jettche1, self.oldttree.jettche2),self.oldttree.softbdisc)
                
            
            ## correct MET
            ## get "old" and "new" jets as TLorentzVectors
            j1_hold = ROOT.TLorentzVector()
            j1_hold.SetPtEtaPhiM(0, 0, 0, 0) ## make sure that no jet is no jet
            j2_hold = ROOT.TLorentzVector()
            j2_hold.SetPtEtaPhiM(0, 0, 0, 0)
            j1 = ROOT.TLorentzVector()
            j1.SetPtEtaPhiM(0, 0, 0, 0)
            j2 = ROOT.TLorentzVector()
            j2.SetPtEtaPhiM(0, 0, 0, 0)

            j3_hold = ROOT.TLorentzVector()
            j3_hold.SetPtEtaPhiM(0, 0, 0, 0) ## make sure that no jet is no jet
            j4_hold = ROOT.TLorentzVector()
            j4_hold.SetPtEtaPhiM(0, 0, 0, 0)
            j3 = ROOT.TLorentzVector()
            j3.SetPtEtaPhiM(0, 0, 0, 0)
            j4 = ROOT.TLorentzVector()
            j4.SetPtEtaPhiM(0, 0, 0, 0)

            if jetpt1_hold > 0:
                j1_hold.SetPtEtaPhiM(jetpt1_hold, eta1, phi1, 0)
            if jetpt2_hold > 0:
                j2_hold.SetPtEtaPhiM(jetpt2_hold, eta2, phi2, 0)
            if jetpt1[0] > 0:
                j1.SetPtEtaPhiM(jetpt1[0], eta1, phi1, 0)
            if jetpt2[0] > 0:
                j2.SetPtEtaPhiM(jetpt2[0], eta2, phi2, 0)
            
            if jetpt3_hold > 0:
                j3_hold.SetPtEtaPhiM(jetpt3_hold, eta3, phi3, 0)
            if jetpt4_hold > 0:
                j4_hold.SetPtEtaPhiM(jetpt4_hold, eta4, phi4, 0)
            if jetpt3[0] > 0:
                j3.SetPtEtaPhiM(jetpt3[0], eta3, phi3, 0)
            if jetpt4[0] > 0:
                j4.SetPtEtaPhiM(jetpt4[0], eta4, phi4, 0)

            ## PFMET:
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)           
            ## FIXME: cross-check this!!
            ## add "old jets" and subtract the "new" ones:
            #met = met + j1_hold - j1 + j2_hold - j2
            met = correctMet(met, j1_hold, j2_hold, j1, j2)
            met = correctMet(met, j3_hold, j4_hold, j3, j4)
            
            ## substitute the values
            pfmet[0] = met.Pt()
            pfmetphi[0] = met.Phi()


            ## changing MET means also changing transverse masses...
            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
            l2.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)
            ## recalculate mth
            mth[0] = transverseMass((l1+l2),met)
            mtw1[0] = transverseMass((l1),met)
            mtw2[0] = transverseMass((l2),met)

##             dphill[0] =  deltaPhi(l1,l2)
            dphillmet[0] =  deltaPhi(l1+l2,met)
            dphilmet1[0] =  deltaPhi(l1,met)
            dphilmet2[0] =  deltaPhi(l2,met)
            dphilmet[0]  = min(dphilmet1[0], dphilmet2[0])  
##             dphilljet[0] =  deltaPhi(l1+l2,j1)
            dphilljetjet[0] =  deltaPhi(l1+l2,j1+j2)
            mjj[0] = invariantMass(j1,j2)
##             mjj[0] = (j1+j2).M()

            ## other METs:
            ## - chmet
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)      
            chmet4 = correctMet(chmet4, j1_hold, j2_hold, j1, j2)
            chmet4 = correctMet(chmet4, j3_hold, j4_hold, j3, j4)            
            chmet[0] = chmet4.Pt()
            chmetphi[0] = chmet4.Phi()
            ## ## - tcmet
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)      
            ## tcmet4 = correctMet(tcmet4, j1_hold, j2_hold, j1, j2)
            ## tcmet4 = correctMet(tcmet4, j3_hold, j4_hold, j3, j4)
            ## tcmet[0] = tcmet4.Pt()
            ## tcmetphi[0] = tcmet4.Phi()

            ## correct projected MET
            ratio = pfmet[0] / self.oldttree.pfmet
            ppfmet[0] = self.oldttree.ppfmet * ratio
            chratio = chmet[0] / self.oldttree.chmet
            pchmet[0] = self.oldttree.pchmet * chratio
            ## tcratio = tcmet[0] / self.oldttree.tcmet
            ## ptcmet[0] = self.oldttree.ptcmet * tcratio
            mpmet[0] = min( ppfmet[0], pchmet[0] )


            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'scale1: '+str(scale1)
                print 'scale2: '+str(scale2)
                print 'channel: '+str(self.oldttree.channel)
                print 'jetpt1: '+str(self.oldttree.jetpt1)+' -> '+ str(jetpt1[0])
                print 'jetpt2: '+str(self.oldttree.jetpt2)+' -> '+ str(jetpt2[0])
                print 'jetpt3: '+str(self.oldttree.jetpt3)+' -> '+ str(jetpt3[0])
                print 'jetpt4: '+str(self.oldttree.jetpt4)+' -> '+ str(jetpt4[0])
                print 'cjetpt1: '+str(self.oldttree.cjetpt1)+' -> '+ str(cjetpt1[0])
                print 'cjetpt2: '+str(self.oldttree.cjetpt2)+' -> '+ str(cjetpt2[0])
                print 'njet: '  +str(self.oldttree.njet)        +to+str(njet[0])
                print 'njetvbf: '  +str(self.oldttree.njetvbf)        +to+str(njetvbf[0])
                print 'pfmet: '    +str(self.oldttree.pfmet)    +to+str(pfmet[0])
                print 'pfmetphi: ' +str(self.oldttree.pfmetphi) +to+str(pfmetphi[0])
                print 'chmet: '    +str(self.oldttree.chmet)    +to+str(chmet[0])
                print 'chmetphi: ' +str(self.oldttree.chmetphi) +to+str(chmetphi[0])
                ## print 'tcmet: '    +str(self.oldttree.tcmet)    +to+str(tcmet[0])
                ## print 'tcmetphi: ' +str(self.oldttree.tcmetphi) +to+str(tcmetphi[0])
##                 print 'dphill: ' + str(self.oldttree.dphill) +to+ str(dphill[0])
                print 'dphillmet: ' + str(self.oldttree.dphillmet) +to+ str(dphillmet[0])
                print 'dphilmet: ' + str(self.oldttree.dphilmet) +to+ str(dphilmet[0])
##                 print 'dphilljet: ' + str(self.oldttree.dphilljet) +to+ str(dphilljet[0])
                print 'dphilljetjet: ' + str(self.oldttree.dphilljetjet) +to+ str(dphilljetjet[0])
                print 'dphilmet1: ' + str(self.oldttree.dphilmet1) +to+ str(dphilmet1[0])
                print 'dphilmet2: ' + str(self.oldttree.dphilmet2) +to+ str(dphilmet2[0])
                print 'mth: ' + str(self.oldttree.mth) +to+ str(mth[0])
                print 'mtw1: ' + str(self.oldttree.mtw1) +to+ str(mtw1[0])
                print 'mtw2: ' + str(self.oldttree.mtw2) +to+ str(mtw2[0])
                print 'mjj: ' + str(self.oldttree.mjj) +to+ str(mjj[0])
                print 'ppfmet: '    +str(self.oldttree.ppfmet)    +to+str(ppfmet[0])
                print 'pchmet: '    +str(self.oldttree.pchmet)    +to+str(pchmet[0])
                ## print 'ptcmet: '    +str(self.oldttree.ptcmet)    +to+str(ptcmet[0])            
                print 'mpmet: '    +str(self.oldttree.mpmet)    +to+str(mpmet[0])
                #print 'hardbdisctche: '    +str(self.oldttree.hardbdisctche)    +to+str(hardbdisctche[0])
                #print 'softbdisctche: '    +str(self.oldttree.softbdisctche)    +to+str(softbdisctche[0])


            # fill old and new values            
            self.ttree.Fill()



###############################################################################################
##  
## ___  ___ _____ _____  ______                _       _   _             
## |  \/  ||  ___|_   _| | ___ \              | |     | | (_)            
## | .  . || |__   | |   | |_/ /___  ___  ___ | |_   _| |_ _  ___  _ __  
## | |\/| ||  __|  | |   |    // _ \/ __|/ _ \| | | | | __| |/ _ \| '_ \ 
## | |  | || |___  | |   | |\ \  __/\__ \ (_) | | |_| | |_| | (_) | | | |
## \_|  |_/\____/  \_/   \_| \_\___||___/\___/|_|\__,_|\__|_|\___/|_| |_|
##    
##


    def metResolution(self):

        sigma = metSigma
        
        pfmet = numpy.zeros(1, dtype=numpy.float32)
        pfmetphi = numpy.zeros(1, dtype=numpy.float32)
        chmet = numpy.zeros(1, dtype=numpy.float32)
        chmetphi = numpy.zeros(1, dtype=numpy.float32)
        ## tcmet = numpy.zeros(1, dtype=numpy.float32)
        ## tcmetphi = numpy.zeros(1, dtype=numpy.float32)
        dphillmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet1 = numpy.zeros(1, dtype=numpy.float32)
        dphilmet2 = numpy.zeros(1, dtype=numpy.float32)
        mth = numpy.zeros(1, dtype=numpy.float32)
        mtw1 = numpy.zeros(1, dtype=numpy.float32)
        mtw2 = numpy.zeros(1, dtype=numpy.float32)
        ppfmet = numpy.zeros(1, dtype=numpy.float32)
        pchmet = numpy.zeros(1, dtype=numpy.float32)
        ## ptcmet = numpy.zeros(1, dtype=numpy.float32)
        mpmet = numpy.zeros(1, dtype=numpy.float32)
        self.ttree.Branch('pfmet',pfmet,'pfmet/F')
        self.ttree.Branch('pfmetphi',pfmetphi,'pfmetphi/F')
        self.ttree.Branch('chmet',chmet,'chmet/F')
        self.ttree.Branch('chmetphi',chmetphi,'chmetphi/F')
        ## self.ttree.Branch('tcmet',tcmet,'tcmet/F')
        ## self.ttree.Branch('tcmetphi',tcmetphi,'tcmetphi/F')
        self.ttree.Branch('dphillmet',dphillmet,'dphillmet/F')
        self.ttree.Branch('dphilmet',dphilmet,'dphilmet/F')
        self.ttree.Branch('dphilmet1',dphilmet1,'dphilmet1/F')
        self.ttree.Branch('dphilmet2',dphilmet2,'dphilmet2/F')
        self.ttree.Branch('mth',mth,'mth/F')
        self.ttree.Branch('mtw1',mtw1,'mtw1/F')
        self.ttree.Branch('mtw2',mtw2,'mtw2/F')
        self.ttree.Branch('ppfmet',ppfmet,'ppfmet/F')
        self.ttree.Branch('pchmet',pchmet,'pchmet/F')
        ## self.ttree.Branch('ptcmet',ptcmet,'ptcmet/F')     
        self.ttree.Branch('mpmet',mpmet,'mpmet/F')     

        #nentries = self.ttree.GetEntriesFast()
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)
            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'
                

            ## get the "old" met vector and smear px and py
            ## PFMET:
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)         
            met = smearMET(met, sigma)
            ## CHMET:
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)         
            chmet4 = smearMET(chmet4, sigma)
            ## ## TCMET:
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)         
            ## tcmet4 = smearMET(tcmet4, sigma)


            ## get the variables
            pfmet[0] = met.Pt()
            pfmetphi[0] = met.Phi()
            chmet[0] = chmet4.Pt()
            chmetphi[0] = chmet4.Phi()
            ## tcmet[0] = tcmet4.Pt()
            ## tcmetphi[0] = tcmet4.Phi()

            ## correct projected MET
            ratio = pfmet[0] / self.oldttree.pfmet
            ppfmet[0] = self.oldttree.ppfmet * ratio
            chratio = chmet[0] / self.oldttree.chmet
            pchmet[0] = self.oldttree.pchmet * chratio
            ## tcratio = tcmet[0] / self.oldttree.tcmet
            ## ptcmet[0] = self.oldttree.ptcmet * tcratio
            mpmet[0] = min( ppfmet[0], pchmet[0] )


            ## changing MET means also changing transverse masses...
            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
            l2.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)
            ## recalculate mth
            mth[0] = transverseMass((l1+l2),met)
            mtw1[0] = transverseMass((l1),met)
            mtw2[0] = transverseMass((l2),met)
            dphillmet[0] =  deltaPhi(l1+l2,met)
            dphilmet1[0] =  deltaPhi(l1,met)
            dphilmet2[0] =  deltaPhi(l2,met)           
            dphilmet[0]  =  min(dphilmet1[0], dphilmet2[0])

            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '    +str(i)
                print 'sigma: '    +str(sigma)
                print 'channel: '  +str(self.oldttree.channel)
                print 'pfmet: '    +str(self.oldttree.pfmet) +to+ str(pfmet[0])
                print 'pfmetphi: ' +str(self.oldttree.pfmetphi) +to+ str(pfmetphi[0])
                print 'chmet: '    +str(self.oldttree.chmet) +to+ str(chmet[0])
                print 'chmetphi: ' +str(self.oldttree.chmetphi) +to+ str(chmetphi[0])
                ## print 'tcmet: '    +str(self.oldttree.tcmet) +to+ str(tcmet[0])
                ## print 'tcmetphi: ' +str(self.oldttree.tcmetphi) +to+ str(tcmetphi[0])
                print 'mth: ' + str(self.oldttree.mth) +to+ str(mth[0])
                print 'mtw1: ' + str(self.oldttree.mtw1) +to+ str(mtw1[0])
                print 'mtw2: ' + str(self.oldttree.mtw2) +to+ str(mtw2[0])
                print 'dphillmet: ' + str(self.oldttree.dphillmet) +to+ str(dphillmet[0])
                print 'dphilmet: ' + str(self.oldttree.dphilmet) +to+ str(dphilmet[0])
                print 'dphilmet1: ' + str(self.oldttree.dphilmet1) +to+ str(dphilmet1[0])
                print 'dphilmet2: ' + str(self.oldttree.dphilmet2) +to+ str(dphilmet2[0])
                print 'ppfmet: '    +str(self.oldttree.ppfmet)    +to+str(ppfmet[0])
                print 'pchmet: '    +str(self.oldttree.pchmet)    +to+str(pchmet[0])
                ## print 'ptcmet: '    +str(self.oldttree.ptcmet)    +to+str(ptcmet[0])            
                print 'mpmet: '    +str(self.oldttree.mpmet)    +to+str(mpmet[0])


            # fill old and new values            
            self.ttree.Fill()


###############################################################################################
##      _     _____                    _       _       
##     | |   |_   _|                  | |     | |      
##   __| |_   _| | ___ _ __ ___  _ __ | | __ _| |_ ___ 
##  / _` | | | | |/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \
## | (_| | |_| | |  __/ | | | | | |_) | | (_| | ||  __/
##  \__,_|\__, \_/\___|_| |_| |_| .__/|_|\__,_|\__\___|
##         __/ |                | |                    
##        |___/                 |_|                    


    def dyTemplate(self):


        
        pfmet = numpy.zeros(1, dtype=numpy.float32)
        chmet = numpy.zeros(1, dtype=numpy.float32)
        mth = numpy.zeros(1, dtype=numpy.float32)
        mtw1 = numpy.zeros(1, dtype=numpy.float32)
        mtw2 = numpy.zeros(1, dtype=numpy.float32)
        ppfmet = numpy.zeros(1, dtype=numpy.float32)
        pchmet = numpy.zeros(1, dtype=numpy.float32)
        mpmet = numpy.zeros(1, dtype=numpy.float32)
        njet = numpy.zeros(1, dtype=numpy.float32)
        dymva0 = numpy.zeros(1, dtype=numpy.float32)
        dymva1 = numpy.zeros(1, dtype=numpy.float32)
        dyW = numpy.zeros(1, dtype=numpy.float32)
        dyWUp = numpy.zeros(1, dtype=numpy.float32)
        self.ttree.Branch('pfmet',pfmet,'pfmet/F')
        self.ttree.Branch('chmet',chmet,'chmet/F')
        self.ttree.Branch('mth',mth,'mth/F')
        self.ttree.Branch('mtw1',mtw1,'mtw1/F')
        self.ttree.Branch('mtw2',mtw2,'mtw2/F')
        self.ttree.Branch('ppfmet',ppfmet,'ppfmet/F')
        self.ttree.Branch('pchmet',pchmet,'pchmet/F')
        self.ttree.Branch('mpmet',mpmet,'mpmet/F')
        self.ttree.Branch('njet',njet,'njet/F')
        self.ttree.Branch('dymva0',dymva0,'dymva0/F')
        self.ttree.Branch('dymva1',dymva1,'dymva1/F')
        self.ttree.Branch('dyW',dyW,'dyW/F')
        self.ttree.Branch('dyWUp',dyWUp,'dyWUp/F')

        #nentries = self.ttree.GetEntriesFast()
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)
            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            dyW[0]=1.
            dyWUp[0]=1.

            if self.oldttree.channel < 1.5:

                # reweighting as a function of ptll
                # preliminary (almost random) implementation for test
                ptll_temp = self.oldttree.ptll
                dyWUp[0] = 1.
                dyW[0]   = 1.1*ptll_temp*(1./400.)
            
                # get the "old" met
                pfmet_hold  = self.oldttree.pfmet
                chmet_hold  = self.oldttree.chmet
                ## tcmet_hold  = self.oldttree.tcmet

                pfmet[0] = pfmet_hold + 25 
                chmet[0] = chmet_hold + 25
                ## tcmet[0] = tcmet_hold + 25
                
                ## fix met related variables
                # get the "old" met
                ppfmet_hold  = self.oldttree.ppfmet
                pchmet_hold  = self.oldttree.pchmet
                ## ptcmet_hold  = self.oldttree.ptcmet
                ppfmet[0] = ppfmet_hold * (pfmet[0] / pfmet_hold)
                pchmet[0] = pchmet_hold * (chmet[0] / chmet_hold)
                ## ptcmet[0] = ptcmet_hold * (tcmet[0] / tcmet_hold)

                #mpmet[0] = min( ppfmet[0], pchmet[0] )
                mpmet_hold  = self.oldttree.mpmet
                mpmet[0] = mpmet_hold + 25;

                met = ROOT.TLorentzVector()
                met.SetPtEtaPhiM(pfmet[0], 0, self.oldttree.pfmetphi, 0)         
                chmet4 = ROOT.TLorentzVector()
                chmet4.SetPtEtaPhiM(chmet[0], 0, self.oldttree.chmetphi, 0)         
                ## tcmet4 = ROOT.TLorentzVector()
                ## tcmet4.SetPtEtaPhiM(tcmet[0], 0, self.oldttree.tcmetphi, 0)         
                
                ## changing MET means also changing transverse masses...
                l1 = ROOT.TLorentzVector()
                l2 = ROOT.TLorentzVector()
                l1.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
                l2.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)
                ## recalculate mth
                mth[0]  = transverseMass((l1+l2),met)
                mtw1[0] = transverseMass((l1),met)
                mtw2[0] = transverseMass((l2),met)
                ## assign binary to dymva based on mpmet
                dymva0[0] = mpmet[0]>20;
                dymva1[0] = mpmet[0]>20;

                ## migrate events in jet bins, only for the systematics
                if self.direction == 'syst':
                    jetpt1 = self.oldttree.jetpt1
                    jetpt2 = self.oldttree.jetpt2
                    jetpt3 = self.oldttree.jetpt3
                    jetpt4 = self.oldttree.jetpt4
                    ptjets = [jetpt1,jetpt2,jetpt3,jetpt4]
                    nj = 0
                    for pt in ptjets:
                        if pt > 35:
                            nj=nj+1

                    if nj <= 4:
                        njet[0] = nj
                    else:
                        njet[0] = self.oldttree.njet
                elif self.direction == 'temp':
                    njet[0] = self.oldttree.njet
            else:
                pfmet[0]  = self.oldttree.pfmet
                chmet[0]  = self.oldttree.chmet
                mth[0]    = self.oldttree.mth
                mtw1[0]   = self.oldttree.mtw1
                mtw2[0]   = self.oldttree.mtw2
                ppfmet[0] = self.oldttree.ppfmet
                pchmet[0] = self.oldttree.pchmet
                mpmet[0]  = self.oldttree.mpmet
                njet[0]   = self.oldttree.njet
                dymva0[0] = self.oldttree.dymva0
                dymva1[0] = self.oldttree.dymva1
                

            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '    +str(i)
                print 'channel: '  +str(self.oldttree.channel)
                print 'pfmet: '    +str(self.oldttree.pfmet) +to+ str(pfmet[0])
                print 'chmet: '    +str(self.oldttree.chmet) +to+ str(chmet[0])
                ## print 'tcmet: '    +str(self.oldttree.tcmet) +to+ str(tcmet[0])
                print 'mth: ' + str(self.oldttree.mth) +to+ str(mth[0])
                print 'mtw1: ' + str(self.oldttree.mtw1) +to+ str(mtw1[0])
                print 'mtw2: ' + str(self.oldttree.mtw2) +to+ str(mtw2[0])
                print 'ppfmet: '    +str(self.oldttree.ppfmet)    +to+str(ppfmet[0])
                print 'pchmet: '    +str(self.oldttree.pchmet)    +to+str(pchmet[0])
                ## print 'ptcmet: '    +str(self.oldttree.ptcmet)    +to+str(ptcmet[0])            
                print 'mpmet: '     +str(self.oldttree.mpmet)     +to+str(mpmet[0])
                print 'jetpt1: '    +str(self.oldttree.jetpt1)    +to+str(self.oldttree.jetpt1)
                print 'jetpt2: '    +str(self.oldttree.jetpt2)    +to+str(self.oldttree.jetpt2)
                print 'jetpt3: '    +str(self.oldttree.jetpt3)    +to+str(self.oldttree.jetpt3)
                print 'jetpt4: '    +str(self.oldttree.jetpt4)    +to+str(self.oldttree.jetpt4)
                print 'njet: '      +str(self.oldttree.njet)      +to+str(njet[0])
                print 'dymva0: '    +str(self.oldttree.dymva0)    +to+str(dymva0[0])
                print 'dymva1: '    +str(self.oldttree.dymva1)    +to+str(dymva1[0])


            # fill old and new values            
            self.ttree.Fill()







###############################################################################################
##
##   \  | _)         ___|  |                                                           |         |   _)
##  |\/ |  |   __|  |      __ \    _` |   __|  _` |   _ \       __|  _ \   __|   _ \   |  |   |  __|  |   _ \   __ \
##  |   |  | \__ \  |      | | |  (   |  |    (   |   __/      |     __/ \__ \  (   |  |  |   |  |    |  (   |  |   |
## _|  _| _| ____/ \____| _| |_| \__,_| _|   \__, | \___|     _|   \___| ____/ \___/  _| \__,_| \__| _| \___/  _|  _|
##                                           |___/
##
###############################################################################################

    def chargeResolution(self):

        ## define a new branch
        ch1 = numpy.zeros(1, dtype=numpy.float32)
        ch2 = numpy.zeros(1, dtype=numpy.float32)
        self.ttree.Branch('ch1',ch1,'ch1/F')
        self.ttree.Branch('ch2',ch2,'ch2/F')

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## muon-muon channel
            if self.oldttree.channel == 0:
               ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeMuon)
               ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeMuon)

            ## electron-muon electron
            if self.oldttree.channel == 1:
               if ( self.oldttree.pt1 < 30) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[0])
               if ( self.oldttree.pt1 >= 30 and self.oldttree.pt1 < 50) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[1])
               if ( self.oldttree.pt1 >= 50) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[2])
               if ( self.oldttree.pt1 < 30) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[3])
               if ( self.oldttree.pt1 >= 30 and self.oldttree.pt1 < 50) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[4])
               if ( self.oldttree.pt1 >= 50) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[5])

               if ( self.oldttree.pt2 < 30) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[0])
               if ( self.oldttree.pt2 >= 30 and self.oldttree.pt2 < 50) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[1])
               if ( self.oldttree.pt2 >= 50) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[2])
               if ( self.oldttree.pt2 < 30) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[3])
               if ( self.oldttree.pt2 >= 30 and self.oldttree.pt2 < 50) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[4])
               if ( self.oldttree.pt2 >= 50) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[5])

            ## electron-muon channel
            if self.oldttree.channel == 2:
               if ( self.oldttree.pt1 < 30) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[0])
               if ( self.oldttree.pt1 >= 30 and self.oldttree.pt1 < 50) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[1])
               if ( self.oldttree.pt1 >= 50) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[2])
               if ( self.oldttree.pt1 < 30) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[3])
               if ( self.oldttree.pt1 >= 30 and self.oldttree.pt1 < 50) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[4])
               if ( self.oldttree.pt1 >= 50) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[5])
               ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeMuon)

            ## muon-electron channel
            if self.oldttree.channel == 3:
               ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeMuon)
               if ( self.oldttree.pt2 < 30) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[0])
               if ( self.oldttree.pt2 >= 30 and self.oldttree.pt2 < 50) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[1])
               if ( self.oldttree.pt2 >= 50) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[2])
               if ( self.oldttree.pt2 < 30) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[3])
               if ( self.oldttree.pt2 >= 30 and self.oldttree.pt2 < 50) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[4])
               if ( self.oldttree.pt2 >= 50) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[5])


            # fill old and new values
            self.ttree.Fill()




###############################################################################################
##  _____ _           _                    ______                _       _   _             
## |  ___| |         | |                   | ___ \              | |     | | (_)            
## | |__ | | ___  ___| |_ _ __ ___  _ __   | |_/ /___  ___  ___ | |_   _| |_ _  ___  _ __  
## |  __|| |/ _ \/ __| __| '__/ _ \| '_ \  |    // _ \/ __|/ _ \| | | | | __| |/ _ \| '_ \ 
## | |___| |  __/ (__| |_| | | (_) | | | | | |\ \  __/\__ \ (_) | | |_| | |_| | (_) | | | |
## \____/|_|\___|\___|\__|_|  \___/|_| |_| \_| \_\___||___/\___/|_|\__,_|\__|_|\___/|_| |_|
##                                                                                       
##                                      

    def electronResolution(self):
        
        sigmaEB = electronSigmaEB
        sigmaEE = electronSigmaEE

        ## define a new branch
        pt1 = numpy.zeros(1, dtype=numpy.float32)
        pt2 = numpy.zeros(1, dtype=numpy.float32)
        mll = numpy.zeros(1, dtype=numpy.float32)
        ptll = numpy.zeros(1, dtype=numpy.float32)
##         dphill = numpy.zeros(1, dtype=numpy.float32)
##         dphilljet = numpy.zeros(1, dtype=numpy.float32)
        dphillmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet = numpy.zeros(1, dtype=numpy.float32)
        dphilmet1 = numpy.zeros(1, dtype=numpy.float32)
        dphilmet2 = numpy.zeros(1, dtype=numpy.float32)
        mth = numpy.zeros(1, dtype=numpy.float32)
        mtw1 = numpy.zeros(1, dtype=numpy.float32)
        mtw2 = numpy.zeros(1, dtype=numpy.float32)
        pfmet = numpy.zeros(1, dtype=numpy.float32)
        pfmetphi = numpy.zeros(1, dtype=numpy.float32)
        chmet = numpy.zeros(1, dtype=numpy.float32)
        chmetphi = numpy.zeros(1, dtype=numpy.float32)
        ## tcmet = numpy.zeros(1, dtype=numpy.float32)
        ## tcmetphi = numpy.zeros(1, dtype=numpy.float32)
        ppfmet = numpy.zeros(1, dtype=numpy.float32)
        pchmet = numpy.zeros(1, dtype=numpy.float32)
        ## ptcmet = numpy.zeros(1, dtype=numpy.float32)
        mpmet = numpy.zeros(1, dtype=numpy.float32)
        gammaMRStar = numpy.zeros(1, dtype=numpy.float32)
        zveto = numpy.zeros(1, dtype=int)        
        self.ttree.Branch('pt1',pt1,'pt1/F')
        self.ttree.Branch('pt2',pt2,'pt2/F')
        self.ttree.Branch('mll',mll,'mll/F')
        self.ttree.Branch('ptll',ptll,'ptll/F')
##         self.ttree.Branch('dphill',dphill,'dphill/F')
##         self.ttree.Branch('dphilljet',dphilljet,'dphilljet/F')
        self.ttree.Branch('dphillmet',dphillmet,'dphillmet/F')
        self.ttree.Branch('dphilmet',dphilmet,'dphilmet/F')
        self.ttree.Branch('dphilmet1',dphilmet1,'dphilmet1/F')
        self.ttree.Branch('dphilmet2',dphilmet2,'dphilmet2/F')
        self.ttree.Branch('mth',mth,'mth/F')
        self.ttree.Branch('mtw1',mtw1,'mtw1/F')
        self.ttree.Branch('mtw2',mtw2,'mtw2/F')
        self.ttree.Branch('pfmet',pfmet,'pfmet/F')
        self.ttree.Branch('pfmetphi',pfmetphi,'pfmetphi/F')
        self.ttree.Branch('chmet',chmet,'chmet/F')
        self.ttree.Branch('chmetphi',chmetphi,'chmetphi/F')
        ## self.ttree.Branch('tcmet',tcmet,'tcmet/F')
        ## self.ttree.Branch('tcmetphi',tcmetphi,'tcmetphi/F')
        self.ttree.Branch('ppfmet',ppfmet,'ppfmet/F')
        self.ttree.Branch('pchmet',pchmet,'pchmet/F')
        ## self.ttree.Branch('ptcmet',ptcmet,'ptcmet/F')
        self.ttree.Branch('mpmet',mpmet,'mpmet/F')
        self.ttree.Branch('gammaMRStar',gammaMRStar,'gammaMRStar/F')
        self.ttree.Branch('zveto',zveto,'zveto/I')

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'



            ## scale the lepton pt
            ## muon-muon channel
            ## dont scale at all
            if self.oldttree.channel == 0:
                pt1[0] = self.oldttree.pt1                  ## do not scale electrons here  
                pt2[0] = self.oldttree.pt2                  ## independent of "up" or "down"
            ## electron-electron channel    
            if self.oldttree.channel == 1:
                if abs(self.oldttree.eta1) < 1.5:
                    pt1[0] = smearPt(self.oldttree.pt1,sigmaEB)
                if abs(self.oldttree.eta1) > 1.5:
                    pt1[0] = smearPt(self.oldttree.pt1,sigmaEE)
                if abs(self.oldttree.eta2) < 1.5:
                    pt2[0] = smearPt(self.oldttree.pt2,sigmaEB)
                if abs(self.oldttree.eta2) > 1.5:
                    pt2[0] = smearPt(self.oldttree.pt2,sigmaEE)
            ## electron-muon channel
            if self.oldttree.channel == 2:
                if abs(self.oldttree.eta1) < 1.5:
                    pt1[0] = smearPt(self.oldttree.pt1,sigmaEB)
                if abs(self.oldttree.eta1) > 1.5:
                    pt1[0] = smearPt(self.oldttree.pt1,sigmaEE)
                pt2[0] = self.oldttree.pt2
            ## muon-electron channel    
            if self.oldttree.channel == 3:
                pt1[0] = self.oldttree.pt1
                if abs(self.oldttree.eta2) < 1.5:
                    pt2[0] = smearPt(self.oldttree.pt2,sigmaEB)
                if abs(self.oldttree.eta2) > 1.5:
                    pt2[0] = smearPt(self.oldttree.pt2,sigmaEE)

        
## FIXME: after the scaling one has to recalculate some variables
##        like invariant mass etc...
##        does delta phi, eta change? guess not...

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1_hold = ROOT.TLorentzVector()
            l2_hold = ROOT.TLorentzVector()
            l1_hold.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
            l2_hold.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)
            l1.SetPtEtaPhiM(pt1[0], self.oldttree.eta1, self.oldttree.phi1, 0)
            l2.SetPtEtaPhiM(pt2[0], self.oldttree.eta2, self.oldttree.phi2, 0)

            ## correct MET
            ## PFMET:
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)           
            ## FIXME: cross-check this!!
            ## add "old leptons" and subtract the "new" ones:
            met = correctMet(met, l1_hold, l2_hold, l1, l2)

            ## substitute the values
            pfmet[0] = met.Pt()
            pfmetphi[0] = met.Phi()
            ## other METs:
            ## - chmet
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)      
            chmet4 = correctMet(chmet4, l1_hold, l2_hold, l1, l2)
            chmet[0] = chmet4.Pt()
            chmetphi[0] = chmet4.Phi()
            ## ## - tcmet
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)      
            ## tcmet4 = correctMet(tcmet4, l1_hold, l2_hold, l1, l2)
            ## tcmet[0] = tcmet4.Pt()
            ## tcmetphi[0] = tcmet4.Phi()

            ## correct projected MET
            ratio = pfmet[0] / self.oldttree.pfmet
            ppfmet[0] = self.oldttree.ppfmet * ratio
            chratio = chmet[0] / self.oldttree.chmet
            pchmet[0] = self.oldttree.pchmet * chratio
            ## tcratio = tcmet[0] / self.oldttree.tcmet
            ## ptcmet[0] = self.oldttree.ptcmet * tcratio
            mpmet[0] = min( ppfmet[0], pchmet[0] )

            ## additional variables
            mll[0]  = invariantMass(l1, l2)
            ptll[0] = dileptonPt(l1, l2)

##             dphill[0] =  deltaPhi(l1,l2)
            dphillmet[0] =  deltaPhi(l1+l2,met)
            dphilmet1[0] =  deltaPhi(l1,met)
            dphilmet2[0] =  deltaPhi(l2,met)
            dphilmet[0]  =  min(dphilmet1[0], dphilmet2[0])

            j1 = ROOT.TLorentzVector()
            j1.SetPtEtaPhiM(self.oldttree.jetpt1, self.oldttree.jeteta1, self.oldttree.jetphi1, 0)
##             dphilljet[0] =  deltaPhi(l1+l2,j1)

            mth[0] = transverseMass((l1+l2),met)
            mtw1[0] = transverseMass((l1),met)
            mtw2[0] = transverseMass((l2),met)
            gammaMRStar[0] = calculateGammaMRStar(l1,l2)

            zveto[0] = checkZveto(mll[0], self.oldttree.channel)


            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'sigma: '+str(sigma)
                print 'channel: '+str(self.oldttree.channel)
                print 'pt1: '+str(self.oldttree.pt1)+' -> '+ str(pt1[0])
                print 'pt1: '+str(self.oldttree.pt2)+' -> '+ str(pt2[0])
                print 'pfmet: '    +str(self.oldttree.pfmet)    +to+str(pfmet[0])
                print 'pfmetphi: ' +str(self.oldttree.pfmetphi) +to+str(pfmetphi[0])
                print 'chmet: '    +str(self.oldttree.chmet)    +to+str(chmet[0])
                print 'chmetphi: ' +str(self.oldttree.chmetphi) +to+str(chmetphi[0])
                ## print 'tcmet: '    +str(self.oldttree.tcmet)    +to+str(tcmet[0])
                ## print 'tcmetphi: ' +str(self.oldttree.tcmetphi) +to+str(tcmetphi[0])
                print 'mll: '    + str(self.oldttree.mll)    +to+ str(mll[0])
                print 'ptll: '   + str(self.oldttree.ptll)   +to+ str(ptll[0])
##                 print 'dphill: ' + str(self.oldttree.dphill) +to+ str(dphill[0])
                print 'dphillmet: ' + str(self.oldttree.dphillmet) +to+ str(dphillmet[0])
                print 'dphilmet: ' + str(self.oldttree.dphilmet) +to+ str(dphilmet[0])
##                 print 'dphilljet: ' + str(self.oldttree.dphilljet) +to+ str(dphilljet[0])
                print 'dphilmet1: ' + str(self.oldttree.dphilmet1) +to+ str(dphilmet1[0])
                print 'dphilmet2: ' + str(self.oldttree.dphilmet2) +to+ str(dphilmet2[0])
                print 'mth: ' + str(self.oldttree.mth) +to+ str(mth[0])
                print 'mtw1: ' + str(self.oldttree.mtw1) +to+ str(mtw1[0])
                print 'mtw2: ' + str(self.oldttree.mtw2) +to+ str(mtw2[0])
                print 'ppfmet: '    +str(self.oldttree.ppfmet)    +to+str(ppfmet[0])
                print 'pchmet: '    +str(self.oldttree.pchmet)    +to+str(pchmet[0])
                ## print 'ptcmet: '    +str(self.oldttree.ptcmet)    +to+str(ptcmet[0])
                print 'mpmet: '    +str(self.oldttree.mpmet)    +to+str(mpmet[0])
                print 'gammaMRStar: '    +str(self.oldttree.gammaMRStar)    +to+str(gammaMRStar[0])
                print 'zveto: '    +str(self.oldttree.zveto)    +to+str(zveto[0])

                            

            
            # fill old and new values
            self.ttree.Fill()
                

###############################################################################################
##  _                 _                 _____  __  __ _      _                 _          
## | |               | |               |  ___|/ _|/ _(_)    (_)               (_)         
## | |      ___ _ __ | |_  ___  _ __   | |__ | |_| |_ _  ___ _  ___ _ __   ___ _  ___ ___ 
## | |     / _ \ '_ \| __|/ _ \| '_ \  |  __||  _|  _| |/ __| |/ _ \ '_ \ / __| |/ _ | __|
## | |____|  __/ |_) | |_| (_) | | | | | |___| | | | | | (__| |  __/ | | | (__| |  __|__ \
## \_____/ \___| .__/ \__|\___/|_| |_| \____/|_| |_| |_|\___|_|\___|_| |_|\___|_|\___|___/
##             | |                                                                        
##             |_|                                                                        
##
    def leptonEfficiency(self):
        print 'lepton efficiency'

        effW = numpy.zeros(1, dtype=numpy.float32)
        effAW = numpy.zeros(1, dtype=numpy.float32)
        effBW = numpy.zeros(1, dtype=numpy.float32)
        self.ttree.Branch('effW',effW,'effW/F')
        self.ttree.Branch('effAW',effAW,'effAW/F')
        self.ttree.Branch('effBW',effBW,'effBW/F')

## this are the 1stNov efficiency weights:
        base_path = os.path.join(os.getenv('CMSSW_BASE'),'src/HWWAnalysis/ShapeAnalysis/data/')
##         base_path = '/shome/jueugste/HWWSystematics/leptonEfficiencies/'
##         mA_path = base_path+'OutputScaleFactorMap_Run2011AData_vs_42XMC.root'
##         mB_path = base_path+'OutputScaleFactorMap_Run2011BData_vs_42XMC.root'
##         eA_path = base_path+'OutputScaleFactorMap_DATA_Run2011A_MC_42X_BDTID.root'
##         eB_path = base_path+'OutputScaleFactorMap_DATA_Run2011B_MC_42X_BDTID.root'
        mA_path = base_path+'m_OutputScaleFactorMap_MC42X_2011AReweighted.root'
        mB_path = base_path+'m_OutputScaleFactorMap_MC42X_2011BReweighted.root'
        eA_path = base_path+'e_OutputScaleFactorMap_MC42X_2011AReweighted.root'
        eB_path = base_path+'e_OutputScaleFactorMap_MC42X_2011BReweighted.root'
        lumiA = 2.118
        #lumiB = 1.841
        lumiB = 2.511

        
##         # open the root files containing the weights and errors...
##         base_path = '/shome/jueugste/HWWSystematics/leptonEfficiencies/'
## ##         m_path = base_path+'Muons_vpvPlusExpo_OutputScaleFactorMap.root'
##         m_path = base_path+'OutputScaleFactorMap_MuonEfficiencies_DataRun2011A_vs_MC42X.root'
## ##        m_path = base_path+'AbsEta-Pt_Histrogram_2011AData_MuonPRcenario2_MAP.root'
## ##         e_path = base_path+'Electrons_vpvPlusExpo_OutputScaleFactorMap.root'
##         e_path = base_path+'electronEff_CutID_SFmap_Run2011A.root'
## ##        e_path = base_path+'OutputScaleFactorMap_Scenario4_BDTElectrons_Run2011A_MC42X.root'


        fA_muon = openTFile(mA_path)
        fB_muon = openTFile(mB_path)
        fA_ele  = openTFile(eA_path)
        fB_ele  = openTFile(eB_path)
##         f_muon = openTFile(m_path)
##         f_ele  = openTFile(e_path)
        hA_muon = getHist(fA_muon,'hScaleFactorMap')
        hB_muon = getHist(fB_muon,'hScaleFactorMap')
        hA_ele  = getHist(fA_ele,'hScaleFactorMap')
        hB_ele  = getHist(fB_ele,'hScaleFactorMap')
##         h_muon = getHist(f_muon,'hScaleFactorMap')
##         h_ele  = getHist(f_ele,'pt_abseta_PLOT')

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i = 0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0.:
                print str(i)+' events processed.'

            # get the bin coordinates
            cpt1 = 1
            cpt2 = 1
            ceta1 = 1
            ceta2 = 1
            lpt1 = self.oldttree.pt1
            lpt2 = self.oldttree.pt2
            leta1 = self.oldttree.eta1
            leta2 = self.oldttree.eta2
            if lpt1 < 15:
                cpt1 = 1
            if lpt1 >= 15 and lpt1 < 20:
                cpt1 = 2
            if lpt1 >= 20 and lpt1 < 50:
                cpt1 = 3
            if lpt1 >= 50:
                cpt1 = 4
            if lpt2 < 15:
                cpt2 = 1
            if lpt2 >= 15 and lpt2 < 20:
                cpt2 = 2
            if lpt2 >= 20 and lpt2 < 50:
                cpt2 = 3
            if lpt2 >= 50:
                cpt2 = 4
            if abs(leta1) > 1.48:
                ceta1 = 2
            if abs(leta2) > 1.48:
                ceta2 = 2

            ## muon-muon channel
            if self.oldttree.channel == 0:
                valA1 = hA_muon.GetBinContent(cpt1,ceta1)
                valA2 = hA_muon.GetBinContent(cpt2,ceta2)
                errA1 = hA_muon.GetBinError(cpt1,ceta1)
                errA2 = hA_muon.GetBinError(cpt2,ceta2)

                valB1 = hB_muon.GetBinContent(cpt1,ceta1)
                valB2 = hB_muon.GetBinContent(cpt2,ceta2)
                errB1 = hB_muon.GetBinError(cpt1,ceta1)
                errB2 = hB_muon.GetBinError(cpt2,ceta2)
##                 val1 = h_muon.GetBinContent(cpt1,ceta1)
##                 val2 = h_muon.GetBinContent(cpt2,ceta2)
##                 err1 = h_muon.GetBinError(cpt1,ceta1)
##                 err2 = h_muon.GetBinError(cpt2,ceta2)

            ## electron-electron channel    
            if self.oldttree.channel == 1:
                if lpt1 < 15:
                    cpt1 = 1
                if lpt1 >= 15 and lpt1 < 20:
                    cpt1 = 2
                if lpt1 >= 20 and lpt1 < 25:
                    cpt1 = 3
                if lpt1 >= 25 and lpt1 < 50:
                    cpt1 = 4
                if lpt1 >= 50:
                    cpt1 = 5
                if lpt2 < 15:
                    cpt2 = 1
                if lpt2 >= 15 and lpt2 < 20:
                    cpt2 = 2
                if lpt2 >= 20 and lpt2 < 25:
                    cpt2 = 3
                if lpt2 >= 25 and lpt2 < 50:
                    cpt2 = 4
                if lpt2 >= 50:
                    cpt2 = 5
                if abs(leta1) <= 1.4442:
                    ceta1 = 1
                if abs(leta1) > 1.4442 and abs(leta1) <1.556:
                    ceta1 = 2
                if abs(leta1) >= 1.556:
                    ceta1 = 3
                if abs(leta2) <= 1.4442:
                    ceta2 = 1
                if abs(leta2) > 1.4442 and abs(leta2) <1.556:
                    ceta2 = 2
                if abs(leta2) >= 1.556:
                    ceta2 = 3
                
                valA1 = hA_ele.GetBinContent(cpt1,ceta1)
                valA2 = hA_ele.GetBinContent(cpt2,ceta2)
                errA1 = hA_ele.GetBinError(cpt1,ceta1)
                errA2 = hA_ele.GetBinError(cpt2,ceta2)

                valB1 = hB_ele.GetBinContent(cpt1,ceta1)
                valB2 = hB_ele.GetBinContent(cpt2,ceta2)
                errB1 = hB_ele.GetBinError(cpt1,ceta1)
                errB2 = hB_ele.GetBinError(cpt2,ceta2)

##                 val1 = h_ele.GetBinContent(cpt1,ceta1)
##                 val2 = h_ele.GetBinContent(cpt2,ceta2)
##                 err1 = h_ele.GetBinError(cpt1,ceta1)
##                 err2 = h_ele.GetBinError(cpt2,ceta2)

            ## electron-muon channel
            if self.oldttree.channel == 2:
                if lpt1 < 15:
                    cpt1 = 1
                if lpt1 >= 15 and lpt1 < 20:
                    cpt1 = 2
                if lpt1 >= 20 and lpt1 < 25:
                    cpt1 = 3
                if lpt1 >= 25 and lpt1 < 50:
                    cpt1 = 4
                if lpt1 >= 50:
                    cpt1 = 5
                if abs(leta1) <= 1.4442:
                    ceta1 = 1
                if abs(leta1) > 1.4442 and abs(leta1) <1.556:
                    ceta1 = 2
                if abs(leta1) >= 1.556:
                    ceta1 = 3

                valA1 = hA_ele.GetBinContent(cpt1,ceta1)
                valA2 = hA_muon.GetBinContent(cpt2,ceta2)
                errA1 = hA_ele.GetBinError(cpt1,ceta1)
                errA2 = hA_muon.GetBinError(cpt2,ceta2)

                valB1 = hB_ele.GetBinContent(cpt1,ceta1)
                valB2 = hB_muon.GetBinContent(cpt2,ceta2)
                errB1 = hB_ele.GetBinError(cpt1,ceta1)
                errB2 = hB_muon.GetBinError(cpt2,ceta2)

##                 val1 = h_ele.GetBinContent(cpt1,ceta1)
##                 val2 = h_muon.GetBinContent(cpt2,ceta2)
##                 err1 = h_ele.GetBinError(cpt1,ceta1)
##                 err2 = h_muon.GetBinError(cpt2,ceta2)

            ## muon-electron channel    
            if self.oldttree.channel == 3:
                if lpt2 < 15:
                    cpt2 = 1
                if lpt2 >= 15 and lpt2 < 20:
                    cpt2 = 2
                if lpt2 >= 20 and lpt2 < 25:
                    cpt2 = 3
                if lpt2 >= 25 and lpt2 < 50:
                    cpt2 = 4
                if lpt2 >= 50:
                    cpt2 = 5
                if abs(leta2) <= 1.4442:
                    ceta2 = 1
                if abs(leta2) > 1.4442 and abs(leta2) <1.556:
                    ceta2 = 2
                if abs(leta2) >= 1.556:
                    ceta2 = 3
                    
                valA1 = hA_muon.GetBinContent(cpt1,ceta1)
                valA2 = hA_ele.GetBinContent(cpt2,ceta2)
                errA1 = hA_muon.GetBinError(cpt1,ceta1)
                errA2 = hA_ele.GetBinError(cpt2,ceta2)

                valB1 = hB_muon.GetBinContent(cpt1,ceta1)
                valB2 = hB_ele.GetBinContent(cpt2,ceta2)
                errB1 = hB_muon.GetBinError(cpt1,ceta1)
                errB2 = hB_ele.GetBinError(cpt2,ceta2)

                ## constrain the error from wild values...
                if errA1 > 0.03:
                    errA1 = 0.03
                if errA2 > 0.03:
                    errA2 = 0.03
                if errB1 > 0.03:
                    errB1 = 0.03
                if errB2 > 0.03:
                    errB2 = 0.03
                ## ... and set the lower limit to 1%
                if errA1 < 0.01:
                    errA1 = 0.01
                if errA2 < 0.01:
                    errA2 = 0.01
                if errB1 < 0.01:
                    errB1 = 0.01
                if errB2 < 0.01:
                    errB2 = 0.01
                    
##                 val1 = h_muon.GetBinContent(cpt1,ceta1)
##                 val2 = h_ele.GetBinContent(cpt2,ceta2)
##                 err1 = h_muon.GetBinError(cpt1,ceta1)
##                 err2 = h_ele.GetBinError(cpt2,ceta2)

            ## add the statistical error
            ##effW_sup = (val1+err2)*(val2+err2)
            ##effW_sdown = (val1-err2)*(val2-err2)
            effAW_sup = (valA1+errA1)*(valA2+errA2)
            effAW_sdown = (valA1-errA1)*(valA2-errA2)

            effBW_sup = (valB1+errB1)*(valB2+errB2)
            effBW_sdown = (valB1-errB1)*(valB2-errB2)

            effW_sup   = (effAW_sup*lumiA + effBW_sup*lumiB) / (lumiA + lumiB)
            effW_sdown = (effAW_sdown*lumiA + effBW_sdown*lumiB) / (lumiA + lumiB) 

##             ## just replace the "old" value with the one from the root files
##             ##effW_sup   = val1*val2
##             ##effW_sdown = val1*val2
##             effAW_sup   = valA1*valA2
##             effAW_sdown = valA1*valA2
##             effBW_sup   = valB1*valB2
##             effBW_sdown = valB1*valB2

##             effW_sup   = (effAW_sup*lumiA + effBW_sup*lumiB) / (lumiA + lumiB)
##             effW_sdown = (effAW_sdown*lumiA + effBW_sdown*lumiB) / (lumiA + lumiB) 


##Some printouts to check that I am doing the right thing...        
#             print '------------------------'
#             print self.oldttree.channel
#             print lpt1, leta1, valA1, valB1,'\n' 
#             print lpt2, leta2, valA2, valB2,'\n' 
#             print 'err1: ', errA1, errB1
#             print 'err2: ', errA2, errB2


##             #print 'up  : '+str(effW_sup)
##             print 'val : '+str(val1*val2)
##             #print 'down: '+str(effW_sdown)
##             print 'effW: '+str(self.oldttree.effW)
            
            if self.direction == 'up':
                effAW[0] = effAW_sup
                effBW[0] = effBW_sup
                effW[0] = effW_sup
            if self.direction == 'down':
                effAW[0] = effAW_sdown
                effBW[0] = effBW_sdown
                effW[0] = effW_sdown

#             print effAW_sup, effAW_sdown
#             print effBW_sup, effBW_sdown

#             print effW[4], effAW[0], effBW[0]

##            print self.direction+' : '+str(effW[0])
            # fill old and new values
            self.ttree.Fill()

    def addOptions(self,parser):
        parser.add_option('-i', '--inputFileName',      dest='inputFileName',   help='Name of the input *.root file.',)
        parser.add_option('-o', '--outputFileName',     dest='outputFileName',  help='Name of the output *.root file.',)
        parser.add_option('-a', '--systematicArgument', dest='systArgument',    help='Argument to specify systematic (possible arguments are: "muonScale","electronScale","leptonEfficiency","jetEnergyScale","metResolution","electronResolution","dyTemplate","puVariation","chargeResolution",)',)
        parser.add_option('-v', '--variation',          dest='variation',       help='Direction of the scale variation ("up"/"down") or type of DY template ("temp"/"syst"), works only in combination with "-a dyTemplate". In the case of "metResolution" and "electronResolution" and "chargeResolution" this is ommitted.',)
        parser.add_option('-t', '--treeDir',            dest='treeDir',         help='TDirectry structure to the tree to scale and smear.',)
        #    parser.add_option('-n', '--nEvents',           dest='nEvents',         help='Number of events to run over',)
        parser.add_option('-d', '--debug',              dest='debug',           help='Switch to debug mode',default=False, action='store_true')



###############################################################################################
##                  _       
##                 (_)      
##  _ __ ___   __ _ _ _ __  
## | '_ ` _ \ / _` | | '_ \ 
## | | | | | | (_| | | | | |
## |_| |_| |_|\__,_|_|_| |_|
##                         
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    
    parser.set_defaults(overwrite=False)
    
    parser.add_option('-i', '--inputFileName',      dest='inputFileName',   help='Name of the input *.root file.',)
    parser.add_option('-o', '--outputFileName',     dest='outputFileName',  help='Name of the output *.root file.',)
    parser.add_option('-a', '--systematicArgument', dest='systArgument',    help='Argument to specify systematic (possible arguments are: "muonScale","electronScale","leptonEfficiency","jetEnergyScale","metResolution","electronResolution","dyTemplate","puVariation","chargeResolution",)',)
    parser.add_option('-v', '--variation',          dest='variation',       help='Direction of the scale variation ("up"/"down") or type of DY template ("temp"/"syst"), works only in combination with "-a dyTemplate". In the case of "metResolution" and "electronResolution" and "chargeResolution" this is ommitted.',)
    parser.add_option('-t', '--treeDir',            dest='treeDir',         help='TDirectry structure to the tree to scale and smear.',default="latino")
#    parser.add_option('-n', '--nEvents',           dest='nEvents',         help='Number of events to run over',)
    parser.add_option('-d', '--debug',              dest='debug',           help='Switch to debug mode',default=False, action='store_true')


    (opt, args) = parser.parse_args()

    if opt.inputFileName is None:
        parser.error('No input file defined')
    if opt.outputFileName is None:
        parser.error('No output file defined')
    if opt.systArgument is None:
        parser.error('No systematic argument given')
    possibleSystArguments = ['muonScale','electronScale','leptonEfficiency','jetEnergyScale','metResolution','electronResolution','dyTemplate','puVariation','chargeResolution']
    if opt.systArgument not in possibleSystArguments:
        parser.error('Wrong systematic argument')        
    possibleDirections = ['up','down','temp','syst']
    needdir = ["muonScale","electronScale","leptonEfficiency","jetEnergyScale","dyTemplate","puVariation"]
    if opt.systArgument in needdir and opt.variation not in possibleDirections:
        parser.error('No direction of the systematic variation given')
    if opt.treeDir is None:
        parser.error('No path to the tree specyfied')
    if opt.systArgument == 'dyTemplate' and opt.variation not in ['temp','syst']:
        parser.error('template and syst only allowed for dyTemplate')
    if opt.systArgument == 'dyTemplate' and opt.variation in ['up','down']:
        parser.error('"up" or "down" not allowed for "dyTemplate"')

#    verbose = opt.debug

##     sys.argv.append('-b')
##     ROOT.gROOT.SetBatch()

    s = scaleAndSmear()
    s.inputFileName = opt.inputFileName
    s.outputFileName = opt.outputFileName
    s.treeDir = opt.treeDir
    s.systArgument = opt.systArgument
    s.direction = opt.variation
    s.verbose = opt.debug
    
    print s.systArgument

    s.openOriginalTFile()
    s.openOutputTFile()
    s.cloneTree()
    
    if s.systArgument == 'muonScale':
        s.muonScale()
    if s.systArgument == 'electronScale':
        s.electronScale()
    if s.systArgument == 'leptonEfficiency':
        s.leptonEfficiency()
    if s.systArgument == 'jetEnergyScale':
        s.jetEnergyScale()
    if s.systArgument == 'metResolution':
        s.metResolution()
    if s.systArgument == 'electronResolution':
        s.electronResolution()
    if s.systArgument == 'dyTemplate':
        s.dyTemplate()
    if s.systArgument == 'puVariation':
        s.puVariation()
    if s.systArgument == 'chargeResolution':
        s.chargeResolution()
    
    print 'Job finished...'


if __name__ == '__main__':
    main()
