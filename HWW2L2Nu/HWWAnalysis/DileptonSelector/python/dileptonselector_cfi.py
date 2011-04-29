import FWCore.ParameterSet.Config as cms
from HWWAnalysis.DileptonSelector.electronIdWp_cfi import *
from HWWAnalysis.DileptonSelector.pileupSpring2011_cfi import *


DileptonSelector = cms.EDAnalyzer('DileptonSelector',
        debugLevel = cms.untracked.int32(0),
        elWorkingPointsFile = cms.untracked.string('data/elWorkingPoints.txt'),
        pileupFactors = cms.vdouble(puFactors[:]),
        elWorkingPoints = elWpTable,
        hltPaths = cms.PSet(
            el = cms.vstring( 
                'HLT_Ele10_LW_L1R',
                'HLT_Ele15_SW_L1R',
                'HLT_Ele15_SW_CaloEleId_L1R',
                'HLT_Ele17_SW_CaloEleId_L1R',
                'HLT_Ele17_SW_TightEleId_L1R',
                'HLT_Ele17_SW_TighterEleIdIsol_L1R_v2',
                'HLT_Ele17_SW_TighterEleIdIsol_L1R_v3', 
                ),
            mu = cms.vstring( 'HLT_Mu9','HLT_Mu15_v1',),
            ),
        vrtxCuts = cms.PSet(
            nDof = cms.double(4.),
            rho  = cms.double(2.),
            z    = cms.double(24.),
            ),
        lepCuts = cms.PSet(
            leadingPt = cms.double(20),
            trailingPt = cms.double(10),
            d0PrimaryVertex = cms.double(0.02),
            dZPrimaryVertex = cms.double(1.),
            ),
        elCuts = cms.PSet(
            tightWorkingPoint = cms.int32(80),
            looseWorkingPoint = cms.int32(80),
            ),
        muCuts = cms.PSet(
            nMuHits         = cms.int32(0),
            nMuMatches      = cms.int32(1),
            nTrackerHits    = cms.int32(10),
            nPixelHits      = cms.int32(0),
            nChi2           = cms.double(10),
            relPtResolution = cms.double(0.1),
            combIso         = cms.double(0.15),
            ),
        muSoftCuts = cms.PSet(
            Pt     = cms.double(3.),
            HighPt = cms.double(20.),
            NotIso = cms.double(0.1),
            ),
        jetCuts = cms.PSet(
            Dr       = cms.double(0.3),
            Pt       = cms.double(25.),
            Eta      = cms.double(5.),
            BtagProb = cms.double(2.1),
            ),
)
