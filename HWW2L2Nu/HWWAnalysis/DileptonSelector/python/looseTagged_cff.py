# import the cuts
from HWWAnalysis.DileptonSelector.electronCuts_cff import *
from HWWAnalysis.DileptonSelector.muonCuts_cff import *
import FWCore.ParameterSet.Config as cms

ELE_BASE = "( pt > 10 && abs(eta)<2.5 )"
MUON_BASE= "( pt > 10 && abs(eta)<2.4 )"

# make an electron producer with the ip cut
taggedElectrons = cms.EDProducer("PATElectronFlagger",
    src = cms.InputTag("boostedElectrons"),
    tags = cms.PSet(),
)
taggedMuons     = cms.EDProducer("PATMuonFlagger",
    src = cms.InputTag("boostedMuons"),
    tags = cms.PSet(),
)

hwwLooseTaggedElectrons = taggedElectrons.clone()
hwwLooseTaggedElectrons.tags.tight = cms.string(ELE_BASE + " && " + ELE_MERGE_ID2 + " && " + ELE_MERGE_ISO + " && " + ELE_MERGE_CONV + " && " + ELE_MERGE_IP)
hwwLooseTaggedMuons     = taggedMuons.clone()
hwwLooseTaggedMuons.tags.tight     = cms.string(MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_MERGE_ISO+"&&"+MUON_MERGE_IP)

hwwLooseDileptons = cms.EDProducer('DileptonProducer',
    electronSrc = cms.InputTag('hwwLooseTaggedElectrons'),
    muonSrc     = cms.InputTag('hwwLooseTaggedMuons'),
    cut         = cms.string('oppositeSign() && leading().pt() > 20.'),
)

# hwwLeptons = cms.Sequence((hwwLooseTaggedElectrons+hwwLooseTaggedMuons)*hwwLooseDileptons)

hwwLooseViews = cms.EDProducer('EventViewProducer',
    hltSummarySrc = cms.InputTag('hltSummary'),
    dileptonSrc   = cms.InputTag('hwwLooseDileptons'),
    jetSrc        = cms.InputTag('hwwCleanJets'), 
    softMuonSrc   = cms.InputTag('hwwMuons4Veto'),
    pfMetSrc      = cms.InputTag('pfMet'),
    tcMetSrc      = cms.InputTag('tcMet'),
    chargedMetSrc = cms.InputTag('trackMetProducer'),
    vertexSrc     = cms.InputTag('goodPrimaryVertices'),
    pfChCandSrc   = cms.InputTag('reducedPFCands'),
)


