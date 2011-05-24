import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as opts

from HWWAnalysis.DileptonSelector.pileupSpring2011_cfi import *
from HWWAnalysis.DileptonSelector.higgsPtWeights_cfi import *
#
import PhysicsTools.PythonAnalysis.LumiList as LumiList
#
options = opts.VarParsing('analysis')

options.register ('eventsToProcess',
				  '',
				  opts.VarParsing.multiplicity.list,
				  opts.VarParsing.varType.string,
				  "Events to process")

options.register ('skipEvents',
                  0, # default value
                  opts.VarParsing.multiplicity.singleton, # singleton or list
                  opts.VarParsing.varType.int,          # string, int, or float
                  "Number of events to skip")

options.register ( 'dataType',
                  'mc',
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.string,
                  "Data type to be processed, default mc")

options.register ('debugLevel',
                  0, # default value
                  opts.VarParsing.multiplicity.singleton, # singleton or list
                  opts.VarParsing.varType.int,          # string, int, or float
                  "Level of debug verbosity")

options.register ( 'useLumi',
                  None,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.string,
                  "LumiSections to run on -json format - local runs only, don't use for crab")

options.register ( 'flatWeights',
                  False,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.bool,
                  "Set to true to force all the weights to 1")

options.register ( 'higgsPtWeights',
                  'none',
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.string,
                  "if not none apply the pt weights for the corresponding higgs mass")


#-------------------------------------------------------------------------------
# defaults
options.outputFile = 'diSelection.root'
options.maxEvents  = -1 #all events
#-------------------------------------------------------------------------------

options.parseArguments()

process = cms.Process("DilepSelector")

#-------------------------------------------------------------------------------
# pool source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring( options.inputFiles ),
    skipEvents = cms.untracked.uint32( options.skipEvents ),
)

if options.eventsToProcess:
    process.source.eventsToProcess = cms.untracked.VEventRange (options.eventsToProcess)
    print  process.source.eventsToProcess

#-------------------------------------------------------------------------------
# apply json mask if defined
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
# ______ _ _            _                _____      _      _             
# |  _  (_) |          | |              /  ___|    | |    | |            
# | | | |_| | ___ _ __ | |_ ___  _ __   \ `--.  ___| | ___| |_ ___  _ __ 
# | | | | | |/ _ \ '_ \| __/ _ \| '_ \   `--. \/ _ \ |/ __| __/ _ \| '__|
# | |/ /| | |  __/ |_) | || (_) | | | | /\__/ /  __/ | (__| || (_) | |   
# |___/ |_|_|\___| .__/ \__\___/|_| |_| \____/ \___|_|\___|\__\___/|_|   
#                | |                                                     
#                |_|                                                     

process.load('HWWAnalysis.DileptonSelector.dileptonselector_cfi')
process.DileptonSelector.debugLevel = cms.untracked.int32(options.debugLevel)
process.DileptonSelector.dataType = cms.string(options.dataType)
if options.flatWeights:
    print ' - Forcing all the weights to 1.'
    process.DileptonSelector.pileupFactors = cms.vdouble(puFlatWeights[:])

#  _   _                    _   ________         _                 
# | | | |                  | | / /|  ___|       | |                
# | |_| |_      ____      _| |/ / | |_ __ _  ___| |_ ___  _ __ ___ 
# |  _  \ \ /\ / /\ \ /\ / /    \ |  _/ _` |/ __| __/ _ \| '__/ __|
# | | | |\ V  V /  \ V  V /| |\  \| || (_| | (__| || (_) | |  \__ \
# \_| |_/ \_/\_/    \_/\_/ \_| \_/\_| \__,_|\___|\__\___/|_|  |___/

#-------------------------------------------------------------------------------

if options.higgsPtWeights != 'none':
    scaleFile = higgsPtFactorFile( options.higgsPtWeights )
    process.higgsPt = cms.EDProducer('HWWKFactorProducer',
        genParticlesTag = cms.InputTag('prunedGen'),
        inputFilename = cms.untracked.string( scaleFile ),
        ProcessID = cms.untracked.int32(10010),
        Debug =cms.untracked.bool(False)
    )
    print 'Rescaling pt for higgs mass '+options.higgsPtWeights+' using '+ scaleFile
    process.DileptonSelector.ptWeightSrc = cms.InputTag('higgsPt')
    process.p = cms.Path(process.higgsPt * process.DileptonSelector)
else:
    process.p = cms.Path(process.DileptonSelector)

#-------------------------------------------------------------------------------

process.TFileService = cms.Service("TFileService", 
        fileName = cms.string(options.outputFile),
        closeFileFast = cms.untracked.bool(True)
        )

process.load("FWCore.MessageService.MessageLogger_cfi")

# initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.destinations = ['cerr']
# process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1)
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)

# process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
# process.MessageLogger.cerr.threshold = 'INFO'
# process.MessageLogger.categories.append('pippo')
# process.MessageLogger.cerr.INFO = cms.untracked.PSet(
#             limit = cms.untracked.int32(-1)
#             )
