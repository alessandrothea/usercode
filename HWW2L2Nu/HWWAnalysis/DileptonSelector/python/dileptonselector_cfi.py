import FWCore.ParameterSet.Config as cms
from HWWAnalysis.DileptonSelector.electronIdWp_cfi import *
from HWWAnalysis.DileptonSelector.pileupSpring2011_cfi import *


DileptonSelector = cms.EDAnalyzer('DileptonSelector',
        debugLevel  = cms.untracked.int32(0),

        pileupSrc   = cms.InputTag(''),
        electronSrc = cms.InputTag(''),
        muonSrc     = cms.InputTag(''),
        jetSrc      = cms.InputTag(''),

        pileupFactors = cms.vdouble(puWeights[:]),
        elCutBasedId = elVBTF2011,
        elLikelihood = elLH2011,
        hltMode = cms.string('all'),
        vrtxCuts = cms.PSet(
            nDof = cms.double(4.),
            rho  = cms.double(2.),
            z    = cms.double(24.),
            ),
        lepCuts = cms.PSet(
            extraPt = cms.double(10.),
            ),
        elCuts = cms.PSet(
            leadingPt = cms.double(20.),
            trailingPt = cms.double(15.),
            tightWorkingPoint = cms.int32(90),
            looseWorkingPoint = cms.int32(90),
            ip3D              = cms.double(0.03),
            ),
        muCuts = cms.PSet(
            leadingPt = cms.double(20.),
            trailingPt = cms.double(10.),
            nChi2           = cms.double(10),
            nMuHits         = cms.int32(0),
            nMuMatches      = cms.int32(1),

            nTrackerHits    = cms.int32(10),
            nPixelHits      = cms.int32(0),
            relPtResolution = cms.double(0.1),

            combIso         = cms.double(0.15),

            ip2D            = cms.double(0.01),
            dZPrimaryVertex = cms.double(0.05),
            ),
        muSoftCuts = cms.PSet(
            Pt     = cms.double(3.),
            HighPt = cms.double(20.),
            NotIso = cms.double(0.1),
            ),
        jetCuts = cms.PSet(
            Dr       = cms.double(0.3),
            Pt       = cms.double(30.),
            Eta      = cms.double(5.),
            BtagProb = cms.double(2.1),

            neutralEmFrac  = cms.double(0.99),
            neutralHadFrac = cms.double(0.99),
            multiplicity   = cms.int32(0),
            chargedEmFrac  = cms.double(0.99),
            chargedHadFrac = cms.double(0.),
            chargedMulti   = cms.int32(0)
            ),
)
