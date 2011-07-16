#  _____    _                       
# |_   _|  (_)                      
#   | |_ __ _  __ _  __ _  ___ _ __ 
#   | | '__| |/ _` |/ _` |/ _ \ '__|
#   | | |  | | (_| | (_| |  __/ |   
#   \_/_|  |_|\__, |\__, |\___|_|   
#              __/ | __/ |          
#             |___/ |___/           
import FWCore.ParameterSet.Config as cms

hltSummary = cms.EDProducer('HltSummaryProducer',
    dataTrgSrc = cms.InputTag('TriggerResults','','HLT'),
    mcTrgSrc   = cms.InputTag('TriggerResults','','REDIGI311X'),

#     singleMuDataPaths = cms.vstring(
#         '1-163261:HLT_Mu15_v*',
#         '163262-164237:HLT_Mu24_v*',
#         '165085-999999:HLT_Mu30_v*',
#         '163262-999999:HLT_IsoMu17_v*'
#     ),
#     singleElDataPaths = cms.vstring(
#         '1-164237:HLT_Ele27_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_v*',
#         '165085-999999:HLT_Ele32_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_v*'
#     ),
#     doubleMuDataPaths = cms.vstring(
#         '1-164237:HLT_DoubleMu7_v*',
#         '165085-999999:HLT_Mu13_Mu8_v*'
#     ),
#     doubleElDataPaths = cms.vstring(
#         'HLT_Ele17_CaloIdL_CaloIsoVL_Ele8_CaloIdL_CaloIsoVL_v*',
#         #'HLT_Ele17_CaloIdT_TrkIdVL_CaloIsoVL_TrkIsoVL_Ele8_CaloIdT_TrkIdVL_CaloIsoVL_TrkIsoVL_v*'
#     ),
#     muEGDataPaths     = cms.vstring(
#         'HLT_Mu8_Ele17_CaloIdL_v*',
#         'HLT_Mu17_Ele8_CaloIdL_v*'
#     ),
    singleMuDataPaths = cms.vstring(
        "1-163261:HLT_Mu15_v*",
        "163262-164237:HLT_Mu24_v*",
        "165085-166967:HLT_Mu30_v*",
        "163262-166967:HLT_IsoMu17_v*"
        "167039-999999:HLT_IsoMu20_eta2p1_v*"
    ),
    doubleMuDataPaths = cms.vstring(
        "1-164237:HLT_DoubleMu7_v*",
        "165085-999999:HLT_Mu13_Mu8_v*"
    ),
    doubleElDataPaths = cms.vstring(
        "HLT_Ele17_CaloIdL_CaloIsoVL_Ele8_CaloIdL_CaloIsoVL_v*",
        #"HLT_Ele17_CaloIdT_TrkIdVL_CaloIsoVL_TrkIsoVL_Ele8_CaloIdT_TrkIdVL_CaloIsoVL_TrkIsoVL_v*"
    ),
    muEGDataPaths     = cms.vstring(
        "HLT_Mu8_Ele17_CaloIdL_v*",
        "HLT_Mu17_Ele8_CaloIdL_v*"
    ),
    singleElDataPaths = cms.vstring(
        "1-164237:HLT_Ele27_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_v*",
        "165085-166967:HLT_Ele32_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_v*",
        "166968-999999:HLT_Ele52_CaloIdVT_TrkIdT_v*"
    ),
                            
    singleMuMCPaths   = cms.vstring('*'),
    singleElMCPaths   = cms.vstring('*'),
    doubleMuMCPaths   = cms.vstring('*'),
    doubleElMCPaths   = cms.vstring('*'),
    muEGMCPaths       = cms.vstring('*'),
                                    
)

hltFilter = cms.EDFilter('HltDatasetFilter',
    hltSummarySrc = cms.InputTag('hltSummary'),
    mode = cms.string('mc'),
    mc       = cms.PSet(
        accept = cms.vstring('singleMuMCPaths','singleElMCPaths','doubleMuMCPaths','doubleElMCPaths','muEGMCPaths'),
        reject = cms.vstring(),
    ),
    data       = cms.PSet(
        accept = cms.vstring('singleMuDataPaths','doubleMuDataPaths','doubleElDataPaths','muEGDataPaths'),
        reject = cms.vstring(),
    ),
    singleMu = cms.PSet(
        accept = cms.vstring('singleMuDataPaths'),
        reject = cms.vstring('doubleMuDataPaths'),
    ),
    doubleMu = cms.PSet(
        accept = cms.vstring('doubleMuDataPaths'),
        reject = cms.vstring(),
    ),
    doubleEl = cms.PSet(
        accept = cms.vstring('doubleElDataPaths'),
        reject = cms.vstring(),
    ),
    muEG = cms.PSet(
        accept = cms.vstring('muEGDataPaths'),
        reject = cms.vstring('singleMuDataPaths'),
    )
)


