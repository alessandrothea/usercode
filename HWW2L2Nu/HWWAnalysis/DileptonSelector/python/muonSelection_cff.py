import FWCore.ParameterSet.Config as cms
from HWWAnalysis.DileptonSelector.muonCuts_cff import *

selectedRefPatMuons = cms.EDFilter("PATMuonRefSelector",
   src = cms.InputTag("boostedMuons"),
   filter = cms.bool(False),
   cut = cms.string("")
)

selectedPatMuons = cms.EDFilter("PATMuonSelector",
   src = cms.InputTag("boostedMuons"),
   filter = cms.bool(False),
   cut = cms.string("")
)

MUON_BASE=("pt > 10 && abs(eta)<2.4")

hwwMuMatch = selectedRefPatMuons.clone()
hwwMuMatch.cut = (MUON_BASE)


hwwMuonsID           = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT )
hwwMuonsMergeID      = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT )
hwwMuonsISO          = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_ISO_CUT )
hwwMuonsISOT         = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_ISO_CUT_TIGHT )
hwwMuonsMergeISO     = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_MERGE_ISO )
hwwMuonsISOPF        = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_ISOPF_CUT )
hwwMuonsIP           = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_IP_CUT )
hwwMuonsMergeCONV    = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_MERGE_ISO )
hwwMuonsMergeIP      = selectedRefPatMuons.clone( cut = MUON_BASE +"&&"+ MUON_ID_CUT +"&&"+ MUON_MERGE_ISO+"&&"+MUON_MERGE_IP )
hwwMuons4Veto        = selectedRefPatMuons.clone( cut = "pt > 3 && " + MUON_ID_CUT_4VETO )

# object copy for final storage
# dont' add them to the sequence by default
hwwSelectedMuons     = selectedPatMuons.clone( cut = hwwMuonsMergeIP.cut )

hwwMuonSequence = cms.Sequence( 
    hwwMuMatch * 
    hwwMuonsID * 
    hwwMuonsISO * 
    hwwMuonsIP * 
    hwwMuonsMergeID * 
    hwwMuonsMergeISO * 
    hwwMuonsMergeCONV * 
    hwwMuonsMergeIP * 
    hwwMuons4Veto
)
