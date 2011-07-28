import FWCore.ParameterSet.Config as cms

makeEventViews = cms.EDProducer('EventViewProducer',
    hltSummarySrc = cms.InputTag('hltSummary'),
    dileptonSrc   = cms.InputTag('hwwDileptons'),
    jetSrc        = cms.InputTag('hwwCleanJets'), 
    softMuonSrc   = cms.InputTag('hwwMuons4Veto'),
    pfMetSrc      = cms.InputTag('pfMet'),
    tcMetSrc      = cms.InputTag('tcMet'),
    chargedMetSrc = cms.InputTag('trackMetProducer'),
    vertexSrc     = cms.InputTag('goodPrimaryVertices'),
    pfChCandSrc   = cms.InputTag('reducedPFCands'),
)

