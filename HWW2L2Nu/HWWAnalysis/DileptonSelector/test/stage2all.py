import FWCore.ParameterSet.Config as cms
# import FWCore.ParameterSet.VarParsing as opts
import HWWAnalysis.Misc.VarParsing as opts

# from HWWAnalysis.DileptonSelector.pileupSpring2011_cfi import puWeights
# from HWWAnalysis.DileptonSelector.higgsPtWeights_cfi import *
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

options.register ( 'saveStep2',
                  False,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.bool,
                  'Save step 2 files')




#-------------------------------------------------------------------------------
# defaults
options.outputFile = 'stage2.root'
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

pileUpLabel = 'certifiedLatinos.42X_Jun24' if not options.flatPuWeights else 'Flat'

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

process.pLep = cms.Path()

#--------------------------------------------------------------------
#  _    _      _       _     _       
# | |  | |    (_)     | |   | |      
# | |  | | ___ _  __ _| |__ | |_ ___ 
# | |/\| |/ _ \ |/ _` | '_ \| __/ __|
# \  /\  /  __/ | (_| | | | | |_\__ \
#  \/  \/ \___|_|\__, |_| |_|\__|___/
#                 __/ |              
#                |___/               

from HWWAnalysis.DileptonSelector.weights_cff import addWeights

addWeights( process, pileUpLabel, higgsMass=options.higgsPtWeights, summary = True )

# process.pLep *= process.weightSequence
process.pLep *= (process.puWeights*ptWeights)

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

process.pLep *= process.hltSummary

#--------------------------------------------------------------------
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

process.pLep += (process.selectHwwElectrons
                    + process.selectHwwMuons)


#---------------------------------------------------------
# ______ _ _            _                  
# |  _  (_) |          | |                 
# | | | |_| | ___ _ __ | |_ ___  _ __  ___ 
# | | | | | |/ _ \ '_ \| __/ _ \| '_ \/ __|
# | |/ /| | |  __/ |_) | || (_) | | | \__ \
# |___/ |_|_|\___| .__/ \__\___/|_| |_|___/
#                | |                       
#                |_|                       

process.load('HWWAnalysis.DileptonSelector.dileptons_cff')

process.pLep *= process.makeDileptons


#--------------------------------------------------------------------
# ______     _   _      ______ _ _ _            
# | ___ \   | | | |     |  ___(_) | |           
# | |_/ /_ _| |_| |__   | |_   _| | |_ ___ _ __ 
# |  __/ _` | __| '_ \  |  _| | | | __/ _ \ '__|
# | | | (_| | |_| | | | | |   | | | ||  __/ |   
# \_|  \__,_|\__|_| |_| \_|   |_|_|\__\___|_|   
                                              
process.dilepMonHLT   = process.dilepMonitor.clone( src = cms.InputTag('hwwDilepIP' ) )

# if defined in the command line apply the filterin
if options.dataPath:
    process.hltFilter.mode = cms.string(options.dataPath)
    process.pLep *= process.hltFilter

process.pLep *= process.dilepMonHLT

#--------------------------------------------------------------------
# __   ___      _     _                    __           
# \ \ / (_)    | |   | |                  / _|          
#  \ V / _  ___| | __| |___   ___  ___   | |_ __ _ _ __ 
#   \ / | |/ _ \ |/ _` / __| / __|/ _ \  |  _/ _` | '__|
#   | | | |  __/ | (_| \__ \ \__ \ (_) | | || (_| | |   
#   \_/ |_|\___|_|\__,_|___/ |___/\___/  |_| \__,_|_|   

process.pYield = cms.Path(process.yieldAnalyzer)


#--------------------------------------------------------------------
#  _____             _            _   _                    
# /  __ \           | |          | | | |                   
# | /  \/ ___   ___ | | _____  __| | | |     ___ _ __  ___ 
# | |    / _ \ / _ \| |/ / _ \/ _` | | |    / _ \ '_ \/ __|
# | \__/\ (_) | (_) |   <  __/ (_| | | |___|  __/ |_) \__ \
#  \____/\___/ \___/|_|\_\___|\__,_| \_____/\___| .__/|___/
#                                               | |        
#                                               |_|        

process.hwwElectrons = process.hwwSelectedElectrons.clone()
process.hwwMuons     = process.hwwSelectedMuons.clone()

# set the input lepton collections
process.hwwCleanJets.checkOverlaps.muons.src     = cms.InputTag('hwwMuons')
process.hwwCleanJets.checkOverlaps.electrons.src = cms.InputTag('hwwElectrons')

process.hwwDilep     = process.dileptonProducer.clone(
    electronSrc = cms.InputTag( 'hwwElectrons' ),
    muonSrc     = cms.InputTag( 'hwwMuons' )
)

process.hwwLeptons = cms.Sequence((process.hwwElectrons+process.hwwMuons)*process.hwwDilep)

process.pLep *= process.hwwLeptons*process.selectCleanHwwJets

process.hwwViews = cms.EDProducer('EventViewProducer',
    hltSummarySrc = cms.InputTag('hltSummary'),
    dileptonSrc   = cms.InputTag('hwwDilep'),
    jetSrc        = cms.InputTag('hwwCleanJets'), 
    softMuonSrc   = cms.InputTag('hwwMuons4Veto'),
    pfMetSrc      = cms.InputTag('pfMet'),
    tcMetSrc      = cms.InputTag('tcMet'),
    chargedMetSrc = cms.InputTag('trackMetProducer'),
    vertexSrc     = cms.InputTag('goodPrimaryVertices'),
    pfChCandSrc   = cms.InputTag('reducedPFCands'),
)

process.pLep *= process.hwwViews

#--------------------------------------------------------------------
#  _   _ _____           _      
# | \ | |_   _|         | |     
# |  \| | | |_   _ _ __ | | ___ 
# | . ` | | | | | | '_ \| |/ _ \
# | |\  | | | |_| | |_) | |  __/
# \_| \_/ \_/\__,_| .__/|_|\___|
#                 | |           
#                 |_|          

process.ntupleproducer = cms.EDAnalyzer('HWWNtupleTreeProducer',
    treeName      = cms.string('hwwStep3'),
    weightSrc     = cms.InputTag('eventWeights'),
    viewSrc       = cms.InputTag('hwwViews'),
)

#--------------------------------------------------------------------
# ______      _ _          ______ _       
# | ___ \    | | |         | ___ (_)      
# | |_/ /___ | | | ___ _ __| |_/ /_ _ __  
# |    // _ \| | |/ _ \ '__|  __/| | '_ \ 
# | |\ \ (_) | | |  __/ |  | |   | | | | |
# \_| \_\___/|_|_|\___|_|  \_|   |_|_| |_|

process.load("HWWAnalysis.DileptonSelector.roller_cff")

process.eventWeights.src = cms.InputTag("hwwViews") )
process.stage3flat = process.rollerPin.clone(
    src = cms.InputTag("hwwViews"),
)

#--------------------------------------------------------------------
process.testStuff = cms.EDAnalyzer('TestStuffAnalyzer',
    viewSrc     = cms.InputTag('hwwViews'),
    electronSrc = cms.InputTag('hwwEleIPMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeIP'),
    jetSrc      = cms.InputTag('hwwJetLooseId'),
    cleanJetSrc = cms.InputTag('hwwCleanJets'),
)

# process.pLep *= process.testStuff
process.pLep *= process.eventWeights
process.pLep *= process.ntupleproducer
process.pLep *= process.stage3flat)



#  _____       _               _   
# |  _  |     | |             | |  
# | | | |_   _| |_ _ __  _   _| |_ 
# | | | | | | | __| '_ \| | | | __|
# \ \_/ / |_| | |_| |_) | |_| | |_ 
#  \___/ \__,_|\__| .__/ \__,_|\__|
#                 | |              
#                 |_|              

if options.saveStep2:
    process.out = cms.OutputModule("PoolOutputModule",
       fileName = cms.untracked.string('test.root'),
       # save only events passing the full path
       SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('pLep') ),
       # unpack the list of commands 'patEventContent'
       outputCommands = cms.untracked.vstring(
           'drop *',
           'keep *_hwwElectrons_*_*',
           'keep *_hwwMuons_*_*',
           'keep *_hwwCleanJets_*_*',
           'keep *_hwwDilep_*_*',
           'keep *_hwwViews_*_*',
           'keep GenEventInfoProduct_generator__*',
           'keep edmTriggerResults_*_*_*',
           'keep *_goodPrimaryVertices_*_Yield',
           'keep *_pfMet_*_*',
           'keep *_tcMet_*_*',
           'keep *_onlyHiggsGen_*_*',
           'keep *_goodPrimaryVertices_*_*',
           'drop edmTriggerResults_*_*_Yield',
           'drop edmTriggerResults_*_*_Step2',
       ),
       dropMetaData = cms.untracked.string('ALL'),
    )

    process.outpath = cms.EndPath(process.out)

# process.schedule = cms.Schedule( process.pLep, process.pYield, process.outpath )

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
# process.MessageLogger.categories.append('')
# process.MessageLogger.cerr.INFO = cms.untracked.PSet(
#             limit = cms.untracked.int32(-1)
#             )
