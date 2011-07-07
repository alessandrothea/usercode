import FWCore.ParameterSet.Config as cms
# from PhysicsTools.PatAlgos.patSequences_cff import *
from HWWAnalysis.DileptonSelector.muonCuts_cff import *

selectedRefPatJets = cms.EDFilter('PATJetRefSelector',
   src = cms.InputTag('slimPatJetsTriggerMatch'),
   filter = cms.bool(False),
   cut = cms.string("")
)

JET_LOOSE_ID = '''neutralEmEnergyFraction() < 0.99 
        && neutralHadronEnergyFraction() < 0.99
        && (neutralMultiplicity() + chargedMultiplicity()) > 0
        && ( abs(eta()) > 2.4 
            || (
                chargedEmEnergyFraction() < 0.99
                && chargedHadronEnergyFraction() > 0. 
                && chargedMultiplicity() > 0
                )
            )'''

hwwJetLooseId = selectedRefPatJets.clone( cut = JET_LOOSE_ID )

hwwJetSequence = cms.Sequence( 
    hwwJetLooseId
)
