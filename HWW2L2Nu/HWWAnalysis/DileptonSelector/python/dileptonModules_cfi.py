import FWCore.ParameterSet.Config as cms

# producer template
dileptonProducer = cms.EDProducer('DileptonProducer',
    electronSrc = cms.InputTag(''),
    muonSrc     = cms.InputTag(''),
    cut         = cms.string('oppositeSign() && leading().pt() > 20.'),
)

# filter template
dilepFilter = cms.EDFilter('DileptonCounter',
    src = cms.InputTag(''),
    min = cms.int32(1),
)

# monitor template
dilepMonitor = cms.EDProducer('DileptonMonitor',
    src     = cms.InputTag(''),
    categories = cms.PSet(
        ll = cms.string(''),
        ee = cms.string('isElEl()'),
        em = cms.string('isElMu()'),
        me = cms.string('isMuEl()'),
        mm = cms.string('isMuMu()'),
    ),
)

