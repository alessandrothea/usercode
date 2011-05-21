import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.VarParsing as VarParsing

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.outputFile = '/uscms/home/cplager/nobackup/outputFiles/try_3.root'
# options.inputFiles= 'file1.root', 'file2.root'
options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()


process = cms.PSet(
        inputFiles=cms.vstring(options.inputFiles)
)

process.xxx = cms.PSet(
        a = cms.string('a'),
        b = cms.int32(10),
        c = cms.double(1E-3),
        )
