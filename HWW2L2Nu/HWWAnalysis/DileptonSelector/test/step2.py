import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as opts

from HWWAnalysis.DileptonSelector.pileupSpring2011_cfi import puWeights
from HWWAnalysis.DileptonSelector.higgsPtWeights_cfi import *
#
import PhysicsTools.PythonAnalysis.LumiList as LumiList
#
options = opts.VarParsing('analysis')

options.register ( 'summary',
                  False,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.bool,
                  'Print run summary')

options.register ('eventsToProcess',
				  '',
				  opts.VarParsing.multiplicity.list,
				  opts.VarParsing.varType.string,
				  'Events to process')

options.register ('skipEvents',
                  0, # default value
                  opts.VarParsing.multiplicity.singleton, # singleton or list
                  opts.VarParsing.varType.int,          # string, int, or float
                  'Number of events to skip')

options.register ( 'dataPath',
                  None,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.string,
                  'Data type to be processed, default: no filtering. available: mc, data, doubleEl, doubleMu, singleMu, muEG')

options.register ('debugLevel',
                  0, # default value
                  opts.VarParsing.multiplicity.singleton, # singleton or list
                  opts.VarParsing.varType.int,          # string, int, or float
                  'Level of debug verbosity')

options.register ( 'useLumi',
                  None,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.string,
                  'LumiSections to run on -json format - local runs only, don\'t use for crab')

options.register ( 'flatPuWeights',
                  False,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.bool,
                  'Set to true to force all the weights to 1')

options.register ( 'higgsPtWeights',
                  None,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.string,
                  'if not none apply the pt weights for the corresponding higgs mass')


#-------------------------------------------------------------------------------
# defaults
options.outputFile = 'diSelection.root'
options.maxEvents  = -1 #all events
#-------------------------------------------------------------------------------

options.parseArguments()

process = cms.Process('Step2')

#-------------------------------------------------------------------------------
# ______        __               _  _        
# |  _  \      / _|             | || |       
# | | | | ___ | |_  __ _  _   _ | || |_  ___ 
# | | | |/ _ \|  _|/ _` || | | || || __|/ __|
# | |/ /|  __/| | | (_| || |_| || || |_ \__ \
# |___/  \___||_|  \__,_| \__,_||_| \__||___/

pileupTag = 'certifiedLatinos.42X_Jun24'

#-------------------------------------------------------------------------------
#  _____                  _   
# |_   _|                | |  
#   | | _ __  _ __  _   _| |_ 
#   | || '_ \| '_ \| | | | __|
#  _| || | | | |_) | |_| | |_ 
#  \___/_| |_| .__/ \__,_|\__|
#            | |              
#            |_|              

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring( options.inputFiles ),
    skipEvents = cms.untracked.uint32( options.skipEvents ),
)

if options.eventsToProcess:
    process.source.eventsToProcess = cms.untracked.VEventRange (options.eventsToProcess)
    print  process.source.eventsToProcess

#-------------------------------------------------------------------------------
#  _                     ____  ___          _    
# | |                   (_)  \/  |         | |   
# | |    _   _ _ __ ___  _| .  . | __ _ ___| | __
# | |   | | | | '_ ` _ \| | |\/| |/ _` / __| |/ /
# | |___| |_| | | | | | | | |  | | (_| \__ \   < 
# \_____/\__,_|_| |_| |_|_\_|  |_/\__,_|___/_|\_\
#                                                

if options.useLumi:
    lumis = LumiList.LumiList(filename = options.useLumi ).getCMSSWString().split(',')
#     print lumis
    process.source.lumisToProcess = cms.untracked(cms.VLuminosityBlockRange())
#     print process.source.lumisToProcess
    process.source.lumisToProcess.extend(lumis)
    print process.source.lumisToProcess
#-------------------------------------------------------------------------------


process.maxEvents = cms.untracked.PSet(
            input = cms.untracked.int32 (options.maxEvents),
            )


process.selectionPath = cms.Path()

#-------------------------------------------------------------------------------
#  _   _                    _   ________         _                 
# | | | |                  | | / /|  ___|       | |                
# | |_| |_      ____      _| |/ / | |_ __ _  ___| |_ ___  _ __ ___ 
# |  _  \ \ /\ / /\ \ /\ / /    \ |  _/ _` |/ __| __/ _ \| '__/ __|
# | | | |\ V  V /  \ V  V /| |\  \| || (_| | (__| || (_) | |  \__ \
# \_| |_/ \_/\_/    \_/\_/ \_| \_/\_| \__,_|\___|\__\___/|_|  |___/


if options.higgsPtWeights: 
    scaleFile = higgsPtKFactorFile( options.higgsPtWeights )
    process.higgsPtWeights = cms.EDProducer('HWWKFactorProducer',
        genParticlesTag = cms.InputTag('prunedGen'),
        inputFilename = cms.untracked.string( scaleFile ),
        ProcessID = cms.untracked.int32(10010),
        Debug =cms.untracked.bool(False)
    )
    print 'Rescaling pt for higgs mass '+options.higgsPtWeights+' using '+ scaleFile
    process.selectionPath += process.higgsPtWeights


#  _    _      _       _     _       
# | |  | |    (_)     | |   | |      
# | |  | | ___ _  __ _| |__ | |_ ___ 
# | |/\| |/ _ \ |/ _` | '_ \| __/ __|
# \  /\  /  __/ | (_| | | | | |_\__ \
#  \/  \/ \___|_|\__, |_| |_|\__|___/
#                 __/ |              
#                |___/               


process.eventWeights = cms.EDProducer('WeightsCollector',
    puInfoSrc = cms.InputTag('addPileupInfo'),
    pileupWeights = cms.vdouble(puWeights['certifiedLatinos_May11']),
)

if options.flatPuWeights:
    print ' - Weights: Forcing all the PU eventWeights to 1.'
    process.eventWeights.pileupWeights = cms.vdouble(puWeights['Flat'])

if options.higgsPtWeights:
    print ' - Weights: Adding the pt eventWeights for mass '+options.higgsPtWeights
    process.eventWeights.ptWeightSrc = cms.InputTag('higgsPtWeights')

process.selectionPath += process.eventWeights

#  _                _              _____      _           _   _             
# | |              | |            /  ___|    | |         | | (_)            
# | |     ___ _ __ | |_ ___  _ __ \ `--.  ___| | ___  ___| |_ _  ___  _ __  
# | |    / _ \ '_ \| __/ _ \| '_ \ `--. \/ _ \ |/ _ \/ __| __| |/ _ \| '_ \ 
# | |___|  __/ |_) | || (_) | | | /\__/ /  __/ |  __/ (__| |_| | (_) | | | |
# \_____/\___| .__/ \__\___/|_| |_\____/ \___|_|\___|\___|\__|_|\___/|_| |_|
#            | |                                                            
#            |_|                                                            

process.load('HWWAnalysis.DileptonSelector.electronSelection_cff')
process.load('HWWAnalysis.DileptonSelector.muonSelection_cff')
process.load('HWWAnalysis.DileptonSelector.jetSelection_cff')

process.selectionPath += (process.hwwElectronSequence
                    + process.hwwMuonSequence
                    + process.hwwJetSequence)

#    ___      _     _____ _                  _             
#   |_  |    | |   /  __ \ |                (_)            
#     | | ___| |_  | /  \/ | ___  __ _ _ __  _ _ __   __ _ 
#     | |/ _ \ __| | |   | |/ _ \/ _` | '_ \| | '_ \ / _` |
# /\__/ /  __/ |_  | \__/\ |  __/ (_| | | | | | | | | (_| |
# \____/ \___|\__|  \____/_|\___|\__,_|_| |_|_|_| |_|\__, |
#                                                     __/ |
#                                                    |___/ 

# Clean the Jets from the seleted leptons
process.hwwCleanJets = cms.EDProducer('PATJetCleaner',
#     src = cms.InputTag('slimPatJetsTriggerMatch'),
    src = cms.InputTag('hwwJetLooseId'),
    preselection = cms.string(''), 
    checkOverlaps = cms.PSet(
      muons = cms.PSet(
          src = cms.InputTag('hwwMuonsMergeIP'),
          algorithm = cms.string('byDeltaR'),
          preselection = cms.string(''),
          deltaR = cms.double(0.3),
          checkRecoComponents = cms.bool(False),
          pairCut = cms.string(''),
          requireNoOverlaps = cms.bool(True),
      ),
      electrons = cms.PSet(
          src = cms.InputTag('hwwEleIPMerge'),
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


process.selectionPath *= process.hwwCleanJets

#---------------------------------------------------------
#  _____    _                       
# |_   _|  (_)                      
#   | |_ __ _  __ _  __ _  ___ _ __ 
#   | | '__| |/ _` |/ _` |/ _ \ '__|
#   | | |  | | (_| | (_| |  __/ |   
#   \_/_|  |_|\__, |\__, |\___|_|   
#              __/ | __/ |          
#             |___/ |___/  

process.load('HWWAnalysis.DileptonSelector.hltFilter_cff')

process.selectionPath *= process.hltSummary

#---------------------------------------------------------
# ______ _ _            _                  
# |  _  (_) |          | |                 
# | | | |_| | ___ _ __ | |_ ___  _ __  ___ 
# | | | | | |/ _ \ '_ \| __/ _ \| '_ \/ __|
# | |/ /| | |  __/ |_) | || (_) | | | \__ \
# |___/ |_|_|\___| .__/ \__\___/|_| |_|___/
#                | |                       
#                |_|                       

process.oppPairsMatch = cms.EDProducer('DileptonProducer',
    electronSrc = cms.InputTag('hwwEleMatch'),
    muonSrc     = cms.InputTag('hwwMuMatch'),
#     cut         = cms.string('oppositeSign() && isMuEl() && leading().pt() > 20. '),
    cut         = cms.string('oppositeSign() && leading().pt() > 20. '),
)

process.oppPairsID = process.oppPairsMatch.clone(
    electronSrc = cms.InputTag('hwwEleIDMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeID'),
)
process.oppPairsISO = process.oppPairsMatch.clone(
    electronSrc = cms.InputTag('hwwEleISOMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeISO'),
)
process.oppPairsCONV = process.oppPairsMatch.clone(
    electronSrc = cms.InputTag('hwwEleCONVMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeCONV'),
)
process.oppPairsIP = process.oppPairsMatch.clone(
    electronSrc = cms.InputTag('hwwEleIPMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeIP'),
)
#--------------------------------------------------------------------
process.oppPairMatchFilter  = cms.EDFilter('DileptonCounter',
    src = cms.InputTag('oppPairsMatch'),
    min = cms.int32(1),
)

process.oppPairFilterID   = process.oppPairMatchFilter.clone( src = cms.InputTag('oppPairsID') )
process.oppPairFilterISO  = process.oppPairMatchFilter.clone( src = cms.InputTag('oppPairsISO') )
process.oppPairFilterCONV = process.oppPairMatchFilter.clone( src = cms.InputTag('oppPairsCONV') )
process.oppPairFilterIP   = process.oppPairMatchFilter.clone( src = cms.InputTag('oppPairsIP') )

#--------------------------------------------------------------------
process.pairMonitor = cms.EDProducer('DileptonMonitor',
    src     = cms.InputTag(''),
    categories = cms.PSet(
        ll = cms.string(''),
        ee = cms.string('isElEl()'),
        em = cms.string('isElMu()'),
        me = cms.string('isMuEl()'),
        mm = cms.string('isMuMu()'),
    ),
)

process.monPairMatch = process.pairMonitor.clone( src = cms.InputTag('oppPairsMatch' ) )
process.monPairID    = process.pairMonitor.clone( src = cms.InputTag('oppPairsID' ) )
process.monPairISO   = process.pairMonitor.clone( src = cms.InputTag('oppPairsISO' ) )
process.monPairCONV  = process.pairMonitor.clone( src = cms.InputTag('oppPairsCONV' ) )
process.monPairIP    = process.pairMonitor.clone( src = cms.InputTag('oppPairsIP' ) )

#--------------------------------------------------------------------

process.pairSequence = cms.Sequence(
      ( process.oppPairsMatch
    + process.oppPairsID
    + process.oppPairsISO
    + process.oppPairsCONV
    + process.oppPairsIP)

    * process.oppPairMatchFilter
    * process.monPairMatch
    * process.oppPairFilterID
    * process.monPairID
    * process.oppPairFilterISO
    * process.monPairISO
    * process.oppPairFilterCONV
    * process.monPairCONV
    * process.oppPairFilterIP
    * process.monPairIP
)

process.selectionPath *= process.pairSequence

# ______     _   _      ______ _ _ _            
# | ___ \   | | | |     |  ___(_) | |           
# | |_/ /_ _| |_| |__   | |_   _| | |_ ___ _ __ 
# |  __/ _` | __| '_ \  |  _| | | | __/ _ \ '__|
# | | | (_| | |_| | | | | |   | | | ||  __/ |   
# \_|  \__,_|\__|_| |_| \_|   |_|_|\__\___|_|   
                                              
# if defined in the command line apply the filterin
if options.dataPath:
    process.hltFilter.mode = cms.string(options.dataPath)
    process.selectionPath *= process.hltFilter



#--------------------------------------------------------------------
#  _____            ______              _                     
# |_   _|           | ___ \            | |                    
#   | |_ __ ___  ___| |_/ / __ ___   __| |_   _  ___ ___ _ __ 
#   | | '__/ _ \/ _ \  __/ '__/ _ \ / _` | | | |/ __/ _ \ '__|
#   | | | |  __/  __/ |  | | | (_) | (_| | |_| | (_|  __/ |   
#   \_/_|  \___|\___\_|  |_|  \___/ \__,_|\__,_|\___\___|_|   
#                                                             

process.treeproducer = cms.EDAnalyzer('HWWTreeProducer',

    treeName      = cms.string('hwwStep2'),
    weightSrc     = cms.InputTag('eventWeights'),
    puInfoSrc     = cms.InputTag('addPileupInfo'),
    hltSummarySrc = cms.InputTag('hltSummary'),

    electronSrc   = cms.InputTag('hwwEleIPMerge'),
    muonSrc       = cms.InputTag('hwwMuonsMergeIP'),
    jetSrc        = cms.InputTag('hwwCleanJets'), 
    softMuonSrc   = cms.InputTag('hwwMuons4Veto'),

    pfMetSrc      = cms.InputTag('pfMet'),
    tcMetSrc      = cms.InputTag('tcMet'),
    chargedMetSrc = cms.InputTag('trackMetProducer'),
    vertexSrc     = cms.InputTag('goodPrimaryVertices'),
    chCandSrc     = cms.InputTag('reducedPFCands'),
    sptSrc        = cms.InputTag('vertexMapProd','sumPt'),
    spt2Src       = cms.InputTag('vertexMapProd','sumPt2'),

#     pileupWeights = cms.vdouble(puWeights['certifiedLatinos_May11']),
    jetCut        = cms.string('pt > 15.'),
    jetBTaggers   = cms.vstring('combinedSecondaryVertexBJetTags',
                               'combinedSecondaryVertexMVABJetTags',
                               'simpleSecondaryVertexHighEffBJetTags',
                               'simpleSecondaryVertexHighPurBJetTags',
                               'jetBProbabilityBJetTags',
                               'jetProbabilityBJetTags',
                               'trackCountingHighEffBJetTags',
                               'trackCountingHighPurBJetTags'
                               ),
    hltPaths      = cms.vstring('singleMuDataPaths',
                                'doubleMuDataPaths',
                                'doubleElDataPaths',
                                'muEGDataPaths',
                                'singleMuMCPaths',
                                'singleElMCPaths',
                                'doubleMuMCPaths',
                                'doubleElMCPaths',
                                'muEGMCPaths',
                               ),

    
)
# if options.flatPuWeights:
#     print ' - Forcing all the PU weights to 1.'
#     process.treeproducer.pileupWeights = cms.vdouble(puWeights['Flat'])

# if options.higgsPtWeights:
#     print ' - Adding the pt weights for mass '+options.higgsPtWeights
#     process.treeproducer.ptWeightSrc = cms.InputTag('higgsPtWeights')


#--------------------------------------------------------------------
process.testStuff = cms.EDAnalyzer('TestStuffAnalyzer',
    electronSrc = cms.InputTag('hwwEleIPMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeIP'),
    jetSrc      = cms.InputTag('hwwJetLooseId'),
    cleanJetSrc = cms.InputTag('hwwCleanJets'),
)

process.selectionPath *= cms.Sequence(
    process.treeproducer
)

#--------------------------------------------------------------------
# __   ___      _     _                    __           
# \ \ / (_)    | |   | |                  / _|          
#  \ V / _  ___| | __| |___   ___  ___   | |_ __ _ _ __ 
#   \ / | |/ _ \ |/ _` / __| / __|/ _ \  |  _/ _` | '__|
#   | | | |  __/ | (_| \__ \ \__ \ (_) | | || (_| | |   
#   \_/ |_|\___|_|\__,_|___/ |___/\___/  |_| \__,_|_|   
                                                      
process.yieldAnalyzer = cms.EDAnalyzer('LeptonYieldAnalyzer',
    weightSrc = cms.InputTag('eventWeights'),
    categories = cms.vstring('ll','ee','em','me','mm'),
    bins = cms.VPSet(
        cms.PSet( name = cms.string('fiducial'),    src = cms.InputTag('monPairMatch') ),
        cms.PSet( name = cms.string('id'),          src = cms.InputTag('monPairID') ),
        cms.PSet( name = cms.string('iso'),         src = cms.InputTag('monPairISO') ),
        cms.PSet( name = cms.string('conv'),        src = cms.InputTag('monPairCONV') ),
        cms.PSet( name = cms.string('ip'),          src = cms.InputTag('monPairIP') ),
    )
)

process.yieldSummary = cms.Path(process.yieldAnalyzer)

process.schedule = cms.Schedule( process.selectionPath, process.yieldSummary );

# apply json mask if defined
#     process.DileptonSelector.ptWeightSrc = cms.InputTag('higgsPt')
#     process.p = cms.Path(process.higgsPt * process.LepMatchMaker)
# else:
#     process.p = cms.Path(process.allLeptons*process.lepPairs*process.LepMatchMaker)

#-------------------------------------------------------------------------------
#  _____                 _               
# /  ___|               (_)              
# \ `--.  ___ _ ____   ___  ___ ___  ___ 
#  `--. \/ _ \ '__\ \ / / |/ __/ _ \/ __|
# /\__/ /  __/ |   \ V /| | (_|  __/\__ \
# \____/ \___|_|    \_/ |_|\___\___||___/
#                                        


process.TFileService = cms.Service('TFileService', 
        fileName = cms.string(options.outputFile),
        closeFileFast = cms.untracked.bool(True)
        )

process.load('FWCore.MessageService.MessageLogger_cfi')

# initialize MessageLogger and output report
process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.destinations = ['cerr']
# process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1)
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)

process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(options.summary) )
# process.MessageLogger.cerr.threshold = 'INFO'
# process.MessageLogger.categories.append('pippo')
# process.MessageLogger.cerr.INFO = cms.untracked.PSet(
#             limit = cms.untracked.int32(-1)
#             )