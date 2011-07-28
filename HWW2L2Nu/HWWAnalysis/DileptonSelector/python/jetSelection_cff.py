import FWCore.ParameterSet.Config as cms

selectedRefPatJets = cms.EDFilter("PATJetRefSelector",
   src = cms.InputTag("slimPatJetsTriggerMatch"),
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


# Clean the Jets from the seleted leptons
hwwCleanJets = cms.EDProducer('PATJetCleaner',
    src = cms.InputTag('hwwJetLooseId'),
    preselection = cms.string(''), 
    checkOverlaps = cms.PSet(
      muons = cms.PSet(
          src = cms.InputTag('hwwMuons'),
          algorithm = cms.string('byDeltaR'),
          preselection = cms.string(''),
          deltaR = cms.double(0.3),
          checkRecoComponents = cms.bool(False),
          pairCut = cms.string(''),
          requireNoOverlaps = cms.bool(True),
      ),
      electrons = cms.PSet(
          src = cms.InputTag('hwwElectrons'),
          algorithm = cms.string('byDeltaR'),
          preselection = cms.string(''),
          deltaR = cms.double(0.3),
          checkRecoComponents = cms.bool(False),
          pairCut = cms.string(''),
          requireNoOverlaps = cms.bool(True),
      )
    ),
    finalCut = cms.string('')
)


selectCleanHwwJets = cms.Sequence( 
    hwwJetLooseId*hwwCleanJets
)
