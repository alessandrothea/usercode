import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.VarParsing as VarParsing

options = VarParsing.VarParsing ('analysis')


# setup any defaults you want
options.outputFile = 'testAnalysis.root'
options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()

process = cms.PSet(
    folder = cms.string('treeproducer'),
    treeName = cms.string('hwwStep2'),

    inputFiles = cms.vstring(options.inputFiles),
    outputFile = cms.string(options.outputFile),
    maxEvents  = cms.int64(options.maxEvents),
 
    firstEvent = cms.int64(0),

    copyHistograms = cms.vstring('llCounters','eeCounters','emCounters','meCounters','mmCounters'),
    # preselection cuts
    analysisTreeName = cms.string('hwwStep3'),
    higgsMass       = cms.int32(160),
    cutFile         = cms.string('test/HmassCuts.cfg'),
    jetPtMin        = cms.double(30.),
    bDiscriminator  = cms.string('trackCountingHighEffBJetTags'),
    bThreshold      = cms.double(2.1),
    minMet          = cms.double(20.),
    minMll          = cms.double(12.),
    zVetoWidth      = cms.double(15.),

    minProjMetLL    = cms.double(35.),
    minProjMetEM    = cms.double(20.),
)


