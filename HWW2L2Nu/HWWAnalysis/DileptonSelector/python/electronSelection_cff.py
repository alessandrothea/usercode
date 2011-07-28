import FWCore.ParameterSet.Config as cms
from HWWAnalysis.DileptonSelector.electronCuts_cff import *

selectedRefPatElectrons = cms.EDFilter("PATElectronRefSelector",
   src = cms.InputTag("boostedElectrons"),
   filter = cms.bool(False),
   cut = cms.string(""),
)

selectedPatElectrons = cms.EDFilter("PATElectronSelector",
   src = cms.InputTag("boostedElectrons"),
   filter = cms.bool(False),
   cut = cms.string(""),
)

ELE_BASE = "( pt > 10 && abs(eta)<2.5 )"
hwwEleMatch = selectedRefPatElectrons.clone( cut = ELE_BASE )



# LHL
hwwEleIDLHL      = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_95_2011 )
hwwEleISOLHL     = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_95_2011 + " && " + ELE_ISO_LH_95_2011 ) 
hwwEleCONVLHL    = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_95_2011 + " && " + ELE_ISO_LH_95_2011  + " && " + ELE_NOCONV ) 
hwwEleIPLHL      = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_95_2011 + " && " + ELE_ISO_LH_95_2011  + " && " + ELE_NOCONV + " && " + ELE_IP ) 

# LHT
hwwEleIDLHT      = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_90_2011 ) 
hwwEleISOLHT     = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_90_2011 + " && " + ELE_ISO_LH_90_2011 ) 
hwwEleCONVLHT    = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_90_2011 + " && " + ELE_ISO_LH_90_2011 + " && " + ELE_NOCONV ) 
hwwEleIPLHT      = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_90_2011 + " && " + ELE_ISO_LH_90_2011 + " && " + ELE_NOCONV + " && " + ELE_IP ) 

hwwEleISOPFLHT   = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_90_2011 + " && " + ELE_ISOPF_LH_90_2011 ) 
hwwEleCONVPFLHT  = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_90_2011 + " && " + ELE_ISOPF_LH_90_2011 + " && " + ELE_NOCONV ) 
hwwEleIPPFLHT    = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_LH_90_2011 + " && " + ELE_ISOPF_LH_90_2011 + " && " + ELE_NOCONV + " && " + ELE_IP )

# CBL
hwwEleIDCBL      = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_CB_95_2011 ) 
hwwEleISOCBL     = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_CB_95_2011 + " && " + ELE_ISO_CB_95_2011 ) 
hwwEleCONVCBL    = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_CB_95_2011 + " && " + ELE_ISO_CB_95_2011 + " && " + ELE_NOCONV ) 
hwwEleIPCBL      = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_ID_CB_95_2011 + " && " + ELE_ISO_CB_95_2011 + " && " + ELE_NOCONV + " && " + ELE_IP )

# CBT
hwwEleIDCBT      = selectedRefPatElectrons.clone( cut = ELE_BASE+ " && " + ELE_ID_CB_90_2011 ) 
hwwEleISOCBT     = selectedRefPatElectrons.clone( cut = ELE_BASE+ " && " + ELE_ID_CB_90_2011 + " && " + ELE_ISO_CB_90_2011 ) 
hwwEleCONVCBT    = selectedRefPatElectrons.clone( cut = ELE_BASE+ " && " + ELE_ID_CB_90_2011 + " && " + ELE_ISO_CB_90_2011 + " && " + ELE_NOCONV ) 
hwwEleIPCBT      = selectedRefPatElectrons.clone( cut = ELE_BASE+ " && " + ELE_ID_CB_90_2011 + " && " + ELE_ISO_CB_90_2011 + " && " + ELE_NOCONV + " && " + ELE_IP )

# Merge
hwwEleIDMerge    = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_MERGE_ID ) 
hwwEleISOMerge   = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_MERGE_ID + " && " + ELE_MERGE_ISO ) 
hwwEleCONVMerge  = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_MERGE_ID + " && " + ELE_MERGE_ISO + " && " + ELE_MERGE_CONV ) 
hwwEleIPMerge    = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_MERGE_ID + " && " + ELE_MERGE_ISO + " && " + ELE_MERGE_CONV + " && " + ELE_MERGE_IP )

# Merge2
hwwEleIDMerge2   = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_MERGE_ID2 ) 
hwwEleISOMerge2  = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_MERGE_ID2 + " && " + ELE_MERGE_ISO ) 
hwwEleCONVMerge2 = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_MERGE_ID2 + " && " + ELE_MERGE_ISO + " && " + ELE_MERGE_CONV ) 
hwwEleIPMerge2   = selectedRefPatElectrons.clone( cut = ELE_BASE + " && " + ELE_MERGE_ID2 + " && " + ELE_MERGE_ISO + " && " + ELE_MERGE_CONV + " && " + ELE_MERGE_IP ) 

# object copy for final storage
hwwSelectedElectrons = selectedPatElectrons.clone( cut = hwwEleIPMerge.cut )

selectHwwElectrons = cms.Sequence(  
    hwwEleMatch *

    hwwEleIDMerge *
    hwwEleISOMerge *
    hwwEleCONVMerge *
    hwwEleIPMerge *
    hwwEleIDMerge2 *
    hwwEleISOMerge2 *
    hwwEleCONVMerge2 *
    hwwEleIPMerge2 
)
