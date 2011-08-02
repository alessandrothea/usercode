# import the cuts
from HWWAnalysis.DileptonSelector.electronCuts_cff import *
from HWWAnalysis.DileptonSelector.muonCuts_cff import *
from HWWAnalysis.DileptonSelector.muonSelection_cff import hwwMuons4Veto


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

hwwLooseTaggedElectrons             = taggedElectrons.clone()
hwwLooseTaggedElectrons.tags.tight  = cms.string(ELE_BASE + " && " + ELE_MERGE_ID + " && " + ELE_MERGE_ISO + " && " + ELE_MERGE_CONV + " && " + ELE_MERGE_IP)
hwwLooseTaggedElectrons.tags.base   = cms.string(ELE_BASE )
hwwLooseTaggedElectrons.tags.id     = cms.string(ELE_MERGE_ID )
hwwLooseTaggedElectrons.tags.iso    = cms.string(ELE_MERGE_ISO )
hwwLooseTaggedElectrons.tags.noconv = cms.string(ELE_MERGE_CONV )
hwwLooseTaggedElectrons.tags.ip     = cms.string(ELE_MERGE_IP )

hwwLooseTaggedMuons               = taggedMuons.clone()
hwwLooseTaggedMuons.tags.tight    = cms.string(MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_MERGE_ISO+"&&"+MUON_MERGE_IP)
hwwLooseTaggedMuons.tags.fiducial = cms.string(MUON_BASE)
hwwLooseTaggedMuons.tags.id       = cms.string(MUON_ID_CUT)
hwwLooseTaggedMuons.tags.iso      = cms.string(MUON_MERGE_ISO)
hwwLooseTaggedMuons.tags.noconv   = cms.string('') # always 1, just electron compatibility
hwwLooseTaggedMuons.tags.ip       = cms.string(MUON_MERGE_IP)

# hwwLeptons = cms.Sequence((hwwLooseTaggedElectrons+hwwLooseTaggedMuons)*hwwLooseDileptons)

# hwwLooseDileptons       = dileptonProducer.clone( extraCut = cms.string('userInt("tight") == 1') )



