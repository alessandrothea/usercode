import FWCore.ParameterSet.Config as cms

rollerPin = cms.EDFilter('ProbeTreeProducer',
    src = cms.InputTag('DUMMY'),
    maxProbes = cms.uint32(1),
    variables = cms.PSet(
        channel = cms.string('channel'),
    ),
    flags = cms.PSet(
    ),
    addRunLumiInfo = cms.bool(True)
)


def addVarFlags(roller, vars = {}, flags = {} ): 
    for (key,val) in vars.iteritems():
        setattr(roller.variables, key, val)
    for (key,val) in flags.iteritems():
        setattr(roller.flags, key, val)

def addTrgBits( roller ):
    flags = dict(
        singleMuBit = cms.string('bit("singleMuDataPaths")'),               
        doubleMuBit = cms.string('bit("doubleMuDataPaths")'),             
        singleElBit = cms.string('bit("singleElDataPaths")'),
        doubleElBit = cms.string('bit("doubleElDataPaths")'),               
        muEGBit     = cms.string('bit("muEGDataPaths")'),               
    )
    addVarFlags( roller, flags=flags )


def addLatinos( roller ):
    vars = dict(
        # latino's
        baseW   = cms.string('1.'),         # 1000/(#inputEvents)*crossSection(in pb)
        puW     = cms.InputTag('puWeights'),         # PU reweighting
        kfW     = cms.InputTag('ptWeights'),         # kf reweight (like higgs pt kf)
        effW    = cms.string('1.'),         # efficiency reweight --> 1 for the moment
        triggW  = cms.string('1.'),         # trigger reweight    --> 1 for the moment

        dphilmet1 = cms.string('dPhilMet(0,"kPfMET")'), # wrt to the leading pt lepton
        dphilmet2 = cms.string('dPhilMet(1,"kPfMET")'), # wrt to the second-leading pt lepton
        pt1       = cms.string('dilep[0].p4.pt'),
        pt2       = cms.string('dilep[1].p4.pt'),
        eta1      = cms.string('dilep[0].p4.eta'),
        eta2      = cms.string('dilep[1].p4.eta'),
        phi1      = cms.string('dilep[0].p4.phi'),
        phi2      = cms.string('dilep[1].p4.phi'),
        ch1       = cms.string('dilep[0].charge'),
        ch2       = cms.string('dilep[1].charge'),
        iso1      = cms.string('? dilep.isEl(0) ? dilep[0].userFloat("eleSmurfPF")/dilep[0].pt : dilep[0].userFloat("muSmurfPF")/ dilep[0].pt '),
        iso2      = cms.string('? dilep.isEl(1) ? dilep[1].userFloat("eleSmurfPF")/dilep[1].pt : dilep[1].userFloat("muSmurfPF")/ dilep[1].pt '),

        jetpt1    = cms.string('? nJets > 0 ? jet(0).p4.pt : -9999 '), # leading jet pt
        jetpt2    = cms.string('? nJets > 1 ? jet(1).p4.pt : -9999 '), # second-leading jet pt

        dphill    = cms.string('dilep.dPhi'),                                         # 
        mll       = cms.string('dilep.mll'),
        ptll      = cms.string('dilep.p4ll.pt'),
        drll      = cms.string('dilep.dR'),
        dphilljet = cms.string('dPhiJll(15.,5.)'),                                    # wrt to leading jet
        dphillmet = cms.string('dPhiMet("kPfMET")'),                                  # min(dphilmet1,dphilmet2)     (optional)

        nextra    = cms.string('dilep.nExtra()'),
        njet      = cms.string('nJets(30.,5.)'),                                      # 30./5.
        met       = cms.string('met("kPfMET")'),                                      # pfMET
        met2      = cms.string('met("kChargedMETSmurf")'),                            # tkMET
        met3      = cms.string('1.'),                                                 # reduced-MET
        pmet      = cms.string('projMet("kPfMET")'),                                  # projected pfMET (default MET)
        pmet2     = cms.string('projMet("kChargedMETSmurf")'),                        # projected tkMET (2nd kind of MET)
        mpmet     = cms.string('min(projMet("kPfMET"),projMet("kChargedMETSmurf"))'), # min(pmet,pmet2)     (optional)

        mth       = cms.string('mtll("kPfMET")'),                                     # transverse mass from both leptons
        nvtx      = cms.string('nVrtx'),                                              # number of vertices
        mtw1      = cms.string('mtl(0,"kPfMET")'),                                    # transverse mass from lepton1
        mtw2      = cms.string('mtl(1,"kPfMET")'),                                    # transverse mass from lepton2
        ellh      = cms.string('dilep.worstEGammaLikelihood()'),                      # likelihood of the electron (or worst likelihood  if 2 electrons in the elel event)
        razor     = cms.string('dilep.gammaMRstar()'),                                # gammaMRStar variable
        hardbdisc = cms.string('1.'),                                                 # worst b-discriminator value for the jets above the pt cut (optional)
        softbdisc = cms.string('1.'),                                                 # worst b-discriminator value for the jets with pt in [15,30]   (optional)
    )

    flags = dict(
        sameflav  = cms.string('dilep.isElEl || dilep.isMuMu'),
        zveto     = cms.string('abs(dilep.mll-91.1876)>15 || dilep.isElEl || dilep.isMuMu'), # 
        bveto_ip  = cms.string('nBJetsAbove("trackCountingHighEffBJetTags",2.1,0.)== 0'), #
        bveto_mu  = cms.string('nSoftMuons() == 0'), #
        bveto     = cms.string('nBJetsAbove("trackCountingHighEffBJetTags",2.1,0.)== 0 && nSoftMuons() == 0'), #     bveto_ip && bveto_mu (optional)
    )

    addVarFlags(roller, vars, flags )

#------------------------------------------------------------------------------
def addLeptonQuality(roller ):

    lepVars = dict(
        lepDzPV                     = '{0}.userFloat("dzPV")',
        lepD0PV                     = '{0}.userFloat("d0PV")',
    )

    elVars = dict(
        elSigmaIetaIeta             = '{0}.sigmaIetaIeta()',
        elDeltaEtaSuperClusterAtVtx = '{0}.deltaEtaSuperClusterTrackAtVtx()',
        elDeltaPhiSuperClusterAtVtx = '{0}.deltaPhiSuperClusterTrackAtVtx()',
        elCaloEnergy                = '{0}.caloEnergy()',
        elHcalOverEcal              = '{0}.hcalOverEcal()',
        elNumberOfMissingInnerHits  = '{0}.gsfTrack.trackerExpectedHitsInner().numberOfHits()',
        elConvPartnerTrkDCot        = '{0}.userFloat("convValueMapProd:dcot")',
        elConvPartnerTrkDist        = '{0}.userFloat("convValueMapProd:dist")',
        elDr03EcalRecHitSumEt       = '{0}.dr03EcalRecHitSumEt()',
        elDr03HcalTowerSumEt        = '{0}.dr03HcalTowerSumEt()',
        elDr03TkSumPt               = '{0}.dr03TkSumPt()',
        elDR03HcalFull              = '{0}.userFloat("hcalFull")',
        elPAtVtx                    = '{0}.trackMomentumAtVtx().R()',
    )

    muVars = dict(
        muNMatches                  = '{0}.numberOfMatches',
        muNChi2                     = '(? {0}.isGlobalMuon ? {0}.globalTrack.normalizedChi2 : -9999.)',
        muNMuHits                   = '(? {0}.isGlobalMuon ? {0}.globalTrack.hitPattern.numberOfValidMuonHits : 0.)',
        muNPxHits                   = '{0}.innerTrack.hitPattern.numberOfValidPixelHits',
        muNTkHits                   = '{0}.innerTrack.found',
        muIso03EmEt                 = '{0}.isolationR03.emEt',
        muIso03HadEt                = '{0}.isolationR03.hadEt',
        muIso03SumPt                = '{0}.isolationR03.sumPt',
    ) 

    vars = {}
    for i in [0,1]:
        for (name,raw) in lepVars.iteritems():
            formula = raw.format('dilep['+str(i)+']')
            vars[name+str(i+1)] = cms.string(formula)

    for i in [0,1]:
        for (name,raw) in elVars.iteritems():
            formula = ('? abs({0}.pdgId) == 11 ? '+raw+' : -9999').format('dilep['+str(i)+']')
            vars[name+str(i+1)] = cms.string(formula)

    for i in [0,1]:
        for (name,raw) in muVars.iteritems():
            formula = ('? abs({0}.pdgId) == 13 ? '+raw+' : -9999').format('dilep['+str(i)+']')
            vars[name+str(i+1)] = cms.string(formula)

#     for (v,f) in vars.iteritems():
#         print v,':',f

    addVarFlags(roller, vars = vars)


def addOldVars(roller):
    vars= dict(

        channel = cms.string('channel'),
        
        mll  = cms.string('dilep.mll()'),
        ptll = cms.string('dilep.p4ll.pt()'),
        pt1  = cms.string('dilep[0].p4.pt()'),
        pt2  = cms.string('dilep[1].p4.pt()'),
        met  = cms.string('met("kPfMET")'),
#         peaking  = cms.string('peaking'),
#         trigmatch = cms.string('triggerMatchingCut('DATASET')'),
#         trigguil  = cms.string('guillelmoTrigger('DATASET')'),
#         trigbits  = cms.string('triggerBitsCut('DATASET')'),
        nextra  = cms.string('dilep.nExtra()'),
        pmet = cms.string('projMet("kPfMET")'),
        pchmet = cms.string('projChargedMetSmurf()'), 
        pmmet = cms.string('min(projPfMet,projChargedMetSmurf)'), ##note: min of proj and proj of min are not the same
        dphill = cms.string('dilep.dPhi()'),
        drll   = cms.string('dilep.dR()'),
        dphilljet  = cms.string('dPhiJll(15.,5.)'),
        dphillcjet  = cms.string('dPhiJll(15.,2.5)'),
        dphilmet = cms.string('dPhiMet("kPfMET")'),
        mtw1 = cms.string('mtl(0,"kPfMET")'),
        mtw2 = cms.string('mtl(1,"kPfMET")'),
        mth  = cms.string('mtll("kPfMET")'),
        gammaMRStar = cms.string('dilep.gammaMRstar()'),
        njet  = cms.string('nJets(30.,5.0)'),
        ncjet = cms.string('nJets(30.,2.5)'),
        nbjet = cms.string('nBJetsAbove("trackCountingHighEffBJetTags",2.1,30.)'),
#         leadjetpt = cms.string('leadingJetPt(0,5.0)'),
#         leadjeteta = cms.string('leadingJetEta(0,5.0)'),
#         iso1 = cms.string('allIsoByPt(0)/ptByPt(0)'),
#         iso2 = cms.string('allIsoByPt(1)/ptByPt(1)'),
#         eta1 = cms.string('etaByPt(0)'),
#         eta2 = cms.string('etaByPt(1)'),
#         softbdisc = cms.string('highestSoftBDisc(30.0)'),
#         hardbdisc = cms.string('highestHardBDisc(30.0)'),
#         worstJetLepPt = cms.string('max(matchedJetPt(0, 0.5)/pt(0), matchedJetPt(1, 0.5)/pt(1))'),
#         dataset = cms.string('REPLACE_ME'),
        weight     = cms.InputTag('weightsMap')
#         puWeight   = cms.InputTag('puWeight'),
#         ptWeight   = cms.InputTag('ptWeight'),
#         lumiWeight = cms.string('REPLACE_ME'),
#         fourWeight = cms.string('REPLACE_ME'),
    ),
    flags = dict(
        sameflav   = cms.string('dilep.isElEl || dilep.isMuMu'),
        zveto      = cms.string('abs(dilep.mll-91.1876)>15 || dilep.isElEl || dilep.isMuMu'),
        bveto_ip   = cms.string('nBJetsAbove("trackCountingHighEffBJetTags",2.1,0.)== 0'),
        bveto_mu   = cms.string('nSoftMuons() == 0'),
#         bveto      = cms.string('bTaggedJetsUnder(30,2.1) == 0 && nSoftMuons() == 0'),
#         bveto_nj   = cms.string('bTaggedJetsUnder(30,2.1) == 0 && nSoftMu(3,1) == 0'),
#         dphiveto   = cms.string('passesDPhillJet'),
    )
    addVarFlags(roller, vars, flags )
    
addTrgBits( rollerPin ) 
addLatinos( rollerPin ) 
addLeptonQuality( rollerPin )
