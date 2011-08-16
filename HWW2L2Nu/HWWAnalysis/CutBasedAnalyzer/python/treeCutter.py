import FWCore.ParameterSet.Config as cms

import HWWAnalysis.Misc.VarParsing as VarParsing

import math


def cut(name, label, cut):
    return cms.PSet(
        name = cms.string(name),
        label = cms.string(label),
        cut = cms.string(cut)
        )

def variable( name, title, formula,bins, min, max ):
    return cms.PSet(
        name     = cms.string(name),
        title    = cms.string(title),
        formula  = cms.string(formula),
        min      = cms.double(min),
        max      = cms.double(max),
        bins     = cms.int32(bins),
    )

def invertCut( cuts, old, new = None ):
    for c in cuts:
        if c.name.value() != old:
            continue

        if not new:
            new = '!'+old

        c.name.setValue(new)
        c.label.setValue(new)
        c.cut.setValue( '!('+c.cut.value()+')')
        break

def removeCut( cuts, name ):
    for c in cuts:
        if c.name.value() != name:
            continue
        cuts.remove(c)
        break

def findCut( cuts, name ):
    for c in cuts:
        if c.name.value() == name:
            return c

    return None
radToDeg = str(180./math.pi)

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

options.register ( 'monitor',
                  False,
                  VarParsing.VarParsing.multiplicity.singleton,
                  VarParsing.VarParsing.varType.bool,
                  "monitor informations for every selected event")
options.register ( 'applyWeights',
                  True,
                  VarParsing.VarParsing.multiplicity.singleton,
                  VarParsing.VarParsing.varType.bool,
                  "Apply event weights")


# setup any defaults you want
options.outputFile = 'simpleTest.root'
# options.inputFiles= 'file1.root', 'file2.root'
options.maxEvents = -1 # -1 means all events

options.parseArguments()

process = cms.PSet(
        treeName   = cms.string('stage3flat/probe_tree'),
        inputFiles = cms.vstring(options.inputFiles),
        outputFile = cms.string(options.outputFile),
        maxEvents  = cms.int64(options.maxEvents),
        monitor    = cms.bool(options.monitor),
        copyObjects = cms.vstring([]),
        applyWeights = cms.bool(options.applyWeights),
        weight     = cms.string("puW*kfW"),
        monitored  = cms.vstring(['channel']),
)
