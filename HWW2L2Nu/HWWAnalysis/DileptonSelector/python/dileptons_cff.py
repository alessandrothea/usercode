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
#--------------------------------------------------------------------
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

# producers implementation
hwwDilepMatch = dileptonProducer.clone(
    electronSrc = cms.InputTag('hwwEleMatch'),
    muonSrc     = cms.InputTag('hwwMuMatch'),
)
hwwDilepID    = dileptonProducer.clone(
    electronSrc = cms.InputTag('hwwEleIDMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeID'),
)
hwwDilepISO   = dileptonProducer.clone(
    electronSrc = cms.InputTag('hwwEleISOMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeISO'),
)
hwwDilepCONV  = dileptonProducer.clone(
    electronSrc = cms.InputTag('hwwEleCONVMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeCONV'),
)
hwwDilepIP    = dileptonProducer.clone(
    electronSrc = cms.InputTag('hwwEleIPMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeIP'),
)

# filters implementation
dilepFilterMatch = dilepFilter.clone( src = cms.InputTag('hwwDilepMatch') )
dilepFilterID    = dilepFilter.clone( src = cms.InputTag('hwwDilepID') )
dilepFilterISO   = dilepFilter.clone( src = cms.InputTag('hwwDilepISO') )
dilepFilterCONV  = dilepFilter.clone( src = cms.InputTag('hwwDilepCONV') )
dilepFilterIP    = dilepFilter.clone( src = cms.InputTag('hwwDilepIP') )

dilepMonMatch = dilepMonitor.clone( src = cms.InputTag('hwwDilepMatch' ) )
dilepMonID    = dilepMonitor.clone( src = cms.InputTag('hwwDilepID' ) )
dilepMonISO   = dilepMonitor.clone( src = cms.InputTag('hwwDilepISO' ) )
dilepMonCONV  = dilepMonitor.clone( src = cms.InputTag('hwwDilepCONV' ) )
dilepMonIP    = dilepMonitor.clone( src = cms.InputTag('hwwDilepIP' ) )


makeDileptons = cms.Sequence(
    (
        hwwDilepMatch
        + hwwDilepID
        + hwwDilepISO
        + hwwDilepCONV
        + hwwDilepIP
    )
    * dilepFilterMatch
    * dilepMonMatch
    * dilepFilterID
    * dilepMonID
    * dilepFilterISO
    * dilepMonISO
    * dilepFilterCONV
    * dilepMonCONV
    * dilepFilterIP
    * dilepMonIP
)



yieldAnalyzer = cms.EDAnalyzer('LeptonYieldAnalyzer',
    weightSrc = cms.InputTag('eventWeights'),
    categories = cms.vstring('ll','ee','em','me','mm'),
    bins = cms.VPSet(
        cms.PSet( name = cms.string('fiducial'),    src = cms.InputTag('dilepMonMatch') ),
        cms.PSet( name = cms.string('id'),          src = cms.InputTag('dilepMonID') ),
        cms.PSet( name = cms.string('iso'),         src = cms.InputTag('dilepMonISO') ),
        cms.PSet( name = cms.string('conv'),        src = cms.InputTag('dilepMonCONV') ),
        cms.PSet( name = cms.string('ip'),          src = cms.InputTag('dilepMonIP') ),
        cms.PSet( name = cms.string('trgbits'),     src = cms.InputTag('dilepMonHLT') ),
    )
)



