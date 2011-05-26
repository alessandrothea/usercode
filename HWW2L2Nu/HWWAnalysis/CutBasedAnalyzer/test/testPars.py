import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.VarParsing as VarParsing

import math

radToDeg = str(180./math.pi)

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.outputFile = 'simpleTest.root'
# options.inputFiles= 'file1.root', 'file2.root'
options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()


process = cms.PSet(
        inputFiles = cms.vstring(options.inputFiles),
        outputFile = cms.string(options.outputFile),
        reportEvery = cms.int32(1000),
)

process.channels = cms.VPSet(
    cms.PSet(
        name = cms.string('ll'),
        selection = cms.string('1 == 1 '),
    ),
    cms.PSet(
        name = cms.string('ee'),
        selection = cms.string('is(\'elel\')'),
    ),
    cms.PSet(
        name = cms.string('em'),
        selection = cms.string('is(\'elmu\')'),
    ),
    cms.PSet(
        name = cms.string('me'),
        selection = cms.string('is(\'muel\')'),
    ),
    cms.PSet(
        name = cms.string('mm'),
        selection = cms.string('is(\'mumu\')'),
    ),
)

process.cuts = cms.VPSet(
    cms.PSet(
        name = cms.string('skim'),
        cut = cms.string('1 == 1'),
    ),
    cms.PSet(
        name = cms.string('minMet'),
        cut = cms.string('met > 20'),
    ),
    cms.PSet(
        name = cms.string('minMll'),
        cut = cms.string('mll > 12.'),
    ),
    cms.PSet(
        name = cms.string('Zveto'),
        cut = cms.string('different() || (abs(mll - 91.18699) > 15.)'),
    ),
    cms.PSet(
        name = cms.string('projMet'),
        cut = cms.string('( same() &&  projMet > 35 ) || ( different() && projMet > 20 ) '),
    ),
    cms.PSet(
        name = cms.string('Jet Veto'),
        cut = cms.string('nJets == 0'),
    ),
#     cms.PSet(
#         name = cms.string('dPhi(ll,j)'),
#         cut = cms.string('different() || dPhillj*'+radToDeg+' < 165.'),
#     ),
    cms.PSet(
        name = cms.string('Soft mu'),
        cut = cms.string('nSoftMus == 0'),
    ),
    cms.PSet(
        name = cms.string('Top Veto'),
        cut = cms.string('nBJets == 0'),
    ),
    cms.PSet(
        name = cms.string('maxMll'),
        cut = cms.string('mll < 50'),
    ),
    cms.PSet(
        name = cms.string('pT lead'),
        cut = cms.string('pA.pt() > 30'),
    ),
    cms.PSet(
        name = cms.string('pT trail'),
        cut = cms.string('pB.pt() > 25'),
    ),
    cms.PSet(
        name = cms.string('dPhi'),
        cut = cms.string('dPhi*'+radToDeg+' < 60'),
    ),

)

def variable( name, formula,bins, min, max ):
    return cms.PSet(
        name     = cms.string(name),
        formula  = cms.string(formula),
        min      = cms.double(min),
        max      = cms.double(max),
        bins     = cms.int32(bins),
    )


process.variables = cms.VPSet(
    variable('mll','mll',200,0.,200.),
    variable('met','met',100,0.,100.),
    variable('projMet','projMet',100,0.,100.),
    variable('nJets','nJets',10,0.,10.),
    variable('dPhillj','dPhillj*'+radToDeg,180,0.,180.),
    variable('dPhi','dPhi*'+radToDeg,180,0.,180.),
    variable('ptLead','pA.pt()',200,0,200.),
    variable('ptTrail','pB.pt()',200,0,200.),
)

process.xxx = cms.PSet(
        a = cms.string('a'),
        b = cms.int32(10),
        c = cms.double(1E-3),
        )

