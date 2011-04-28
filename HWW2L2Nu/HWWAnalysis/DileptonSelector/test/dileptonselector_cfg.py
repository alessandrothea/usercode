import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as opts

options = opts.VarParsing('analysis')

options.register ('skipEvents',
        0, # default value
        opts.VarParsing.multiplicity.singleton, # singleton or list
        opts.VarParsing.varType.int,          # string, int, or float
        "Number of events to skip")

options.register ('debugLevel',
        0, # default value
        opts.VarParsing.multiplicity.singleton, # singleton or list
        opts.VarParsing.varType.int,          # string, int, or float
        "Level of debug verbosity")

options.outputFile = 'diSelection.root'
options.maxEvents  = -1 #all events

options.parseArguments()

process = cms.Process("DilepSelector")

process.load("FWCore.MessageService.MessageLogger_cfi")

# process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring( options.inputFiles ),
    skipEvents = cms.untracked.uint32( options.skipEvents ),
)

process.maxEvents = cms.untracked.PSet(
            input = cms.untracked.int32 (options.maxEvents),
            )

process.load('HWWAnalysis.DileptonSelector.dileptonselector_cfi')
process.DileptonSelector.debugLevel = cms.untracked.int32(options.debugLevel)

process.TFileService = cms.Service("TFileService", 
        fileName = cms.string(options.outputFile),
        closeFileFast = cms.untracked.bool(True)
        )

# initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)
# process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
# process.MessageLogger.cerr.threshold = 'INFO'
# process.MessageLogger.categories.append('pippo')
# process.MessageLogger.cerr.INFO = cms.untracked.PSet(
#             limit = cms.untracked.int32(-1)
#             )
process.p = cms.Path(process.DileptonSelector)
