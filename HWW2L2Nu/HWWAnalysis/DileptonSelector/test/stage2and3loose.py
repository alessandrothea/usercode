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

options.register ( 'saveStage2',
                  False,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.bool,
                  'Save step 2 files')




#-------------------------------------------------------------------------------
# defaults
options.outputFile = 'stage3loose.root'
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

# process.load('HWWAnalysis.DileptonSelector.electronSelection_cff')
# process.load('HWWAnalysis.DileptonSelector.muonSelection_cff')
process.load('HWWAnalysis.DileptonSelector.jetSelection_cff')
process.load('HWWAnalysis.DileptonSelector.dileptons_cff')
process.load('HWWAnalysis.DileptonSelector.looseTagged_cff')

#--------------------------------------------------------------------
#  _____             _            _   _                    
# /  __ \           | |          | | | |                   
# | /  \/ ___   ___ | | _____  __| | | |     ___ _ __  ___ 
# | |    / _ \ / _ \| |/ / _ \/ _` | | |    / _ \ '_ \/ __|
# | \__/\ (_) | (_) |   <  __/ (_| | | |___|  __/ |_) \__ \
#  \____/\___/ \___/|_|\_\___|\__,_| \_____/\___| .__/|___/
#                                               | |        
#                                               |_|        

from HWWAnalysis.DileptonSelector.eventViewProducer_cfi import makeEventViews

process.hwwElectrons = process.hwwLooseTaggedElectrons.clone()
process.hwwMuons     = process.hwwLooseTaggedMuons.clone()

# set the input lepton collections
process.hwwCleanJets.checkOverlaps.muons.src     = cms.InputTag('hwwMuons')
process.hwwCleanJets.checkOverlaps.electrons.src = cms.InputTag('hwwElectrons')

# remove the tight leptons from the jets
process.hwwCleanJets.checkOverlaps.muons.preselection = cms.string('userInt("tight") == 1')
process.hwwCleanJets.checkOverlaps.electrons.preselection = cms.string('userInt("tight") == 1')

# additional cut on the extra leptons, tight only
process.hwwDilep     = process.dileptonProducer.clone(
    electronSrc = cms.InputTag('hwwElectrons'),
    muonSrc     = cms.InputTag('hwwMuons'),
    extraCut    = cms.string('userInt("tight") == 1')
)
# tweak the cut to have tight tight pairs
# process.hwwDilep.cut = cms.string( process.hwwDilep.cut.value() + ' && leading.userInt("tight") == 1 && trailing.userInt("tight") == 1' )
# tweak the cut to have tight tight || tight loose pairs
# process.hwwDilep.cut = cms.string( process.hwwDilep.cut.value() + ' && leading.userInt("tight") == 1 || trailing.userInt("tight") == 1' )
# tweak the cut to have tight loose pairs
# process.hwwDilep.cut = cms.string( process.hwwDilep.cut.value() + ' && leading.userInt("tight") == 1')

process.hwwOneOrMoreDilep = process.dilepFilter.clone(
    src = cms.InputTag( 'hwwDilep' ),
)

process.hwwLeptons = cms.Sequence(
    (process.hwwElectrons+process.hwwMuons)
    *process.hwwDilep
    *process.hwwOneOrMoreDilep
)

# switch on the additional overlap check as the two dileptons are not necessarily tight
process.hwwViews = makeEventViews.clone(
    dileptonSrc   = cms.InputTag('hwwDilep'),
    ljOverlapByDr = cms.double(0.3),
)

process.pLep *= ( process.hwwLeptons 
                 * process.selectCleanHwwJets
                 * process.hwwMuons4Veto
                 * process.hwwViews )

#--------------------------------------------------------------------
# ______     _   _      ______ _ _ _            
# | ___ \   | | | |     |  ___(_) | |           
# | |_/ /_ _| |_| |__   | |_   _| | |_ ___ _ __ 
# |  __/ _` | __| '_ \  |  _| | | | __/ _ \ '__|
# | | | (_| | |_| | | | | |   | | | ||  __/ |   
# \_|  \__,_|\__|_| |_| \_|   |_|_|\__\___|_|   
                                              
# if defined in the command line apply the filterin
if options.dataPath:
    process.hltFilter.mode = cms.string(options.dataPath)
    process.pLep *= process.hltFilter

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

addWeights( process, pileUpLabel, higgsMass=options.higgsPtWeights )
process.puWeights.src = cms.InputTag("hwwViews")
process.ptWeights.src = cms.InputTag("hwwViews")

process.pLep *= process.weightSequence

#--------------------------------------------------------------------
# ______      _ _          ______ _       
# | ___ \    | | |         | ___ (_)      
# | |_/ /___ | | | ___ _ __| |_/ /_ _ __  
# |    // _ \| | |/ _ \ '__|  __/| | '_ \ 
# | |\ \ (_) | | |  __/ |  | |   | | | | |
# \_| \_\___/|_|_|\___|_|  \_|   |_|_| |_|

process.load("HWWAnalysis.DileptonSelector.roller_cff")

process.stage3flat = process.rollerPin.clone(
    src = cms.InputTag("hwwViews"),
)

from HWWAnalysis.DileptonSelector.roller_cff import addLeptonQuality
addLeptonQuality( process.stage3flat )
process.stage3flat.flags.isTight1  = cms.string('dilep[0].userInt("tight")   = 1')
process.stage3flat.flags.isTight2  = cms.string('dilep[1].userInt("tight")   = 1')
process.stage3flat.flags.isBase1   = cms.string('dilep[0].userInt("base")    = 1')
process.stage3flat.flags.isBase2   = cms.string('dilep[1].userInt("base")    = 1')
process.stage3flat.flags.isIso1    = cms.string('dilep[0].userInt("iso")     = 1')
process.stage3flat.flags.isIso2    = cms.string('dilep[1].userInt("iso")     = 1')
process.stage3flat.flags.isId1     = cms.string('dilep[0].userInt("id")      = 1')
process.stage3flat.flags.isId2     = cms.string('dilep[1].userInt("id")      = 1')
process.stage3flat.flags.isNoConv1 = cms.string('dilep[0].userInt("noconv")  = 1')
process.stage3flat.flags.isNoConv2 = cms.string('dilep[1].userInt("noconv")  = 1')
process.stage3flat.flags.isIp1     = cms.string('dilep[0].userInt("ip")      = 1')
process.stage3flat.flags.isIp2     = cms.string('dilep[1].userInt("ip")      = 1')

#--------------------------------------------------------------------
process.testStuff = cms.EDAnalyzer('TestStuffAnalyzer',
    viewSrc     = cms.InputTag('hwwViews'),
    electronSrc = cms.InputTag('hwwEleIPMerge'),
    muonSrc     = cms.InputTag('hwwMuonsMergeIP'),
    jetSrc      = cms.InputTag('hwwJetLooseId'),
    cleanJetSrc = cms.InputTag('hwwCleanJets'),
)

# process.pLep *= process.testStuff
process.pLep *= process.stage3flat



#  _____       _               _   
# |  _  |     | |             | |  
# | | | |_   _| |_ _ __  _   _| |_ 
# | | | | | | | __| '_ \| | | | __|
# \ \_/ / |_| | |_| |_) | |_| | |_ 
#  \___/ \__,_|\__| .__/ \__,_|\__|
#                 | |              
#                 |_|              

if options.saveStage2:
    process.out = cms.OutputModule("PoolOutputModule",
       fileName = cms.untracked.string('stage2.root'),
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
