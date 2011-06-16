import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.VarParsing as VarParsing

import math

radToDeg = str(180./math.pi)

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

options.register ( 'monitor',
                  False,
                  VarParsing.VarParsing.multiplicity.singleton,
                  VarParsing.VarParsing.varType.bool,
                  "monitor informations for every selected event")


# setup any defaults you want
options.outputFile = 'simpleTest.root'
# options.inputFiles= 'file1.root', 'file2.root'
options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()


process = cms.PSet(
        inputFiles = cms.vstring(options.inputFiles),
        outputFile = cms.string(options.outputFile),
        maxEvents  = cms.int64(options.maxEvents),
        monitor    = cms.bool(options.monitor),
        copyObjects = cms.vstring(['entries']),
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

def variable( name, title, formula,bins, min, max ):
    return cms.PSet(
        name     = cms.string(name),
        title    = cms.string(title),
        formula  = cms.string(formula),
        min      = cms.double(min),
        max      = cms.double(max),
        bins     = cms.int32(bins),
    )


process.variables = cms.VPSet(
    variable('mll',     'm_{ll};GeV',               'mll',50,0.,200.),
    variable('met',     '#slash{E}_{T};GeV',        'met',50,0.,100.),
    variable('projMet', 'proj#slash{E}_{T};GeV',    'projMet',50,0.,100.),
    variable('nJets',   'N_{jets}',                 'nJets',10,0.,10.),
    variable('dPhillj', '#Delta#Phi_{ll,j};deg',    'dPhillj*'+radToDeg,36,0.,180.),
    variable('dPhi',    '#Delta#phi',               'dPhi*'+radToDeg,36,0.,180.),
    variable('ptLead',  'p_{T}^{lead}',             'pA.pt()',50,0,200.),
    variable('ptTrail', 'p_{T}^{trail}',            'pB.pt()',50,0,200.),
)

process.monitored = cms.vstring([]) 

process.xxx = cms.PSet(
        a = cms.string('a'),
        b = cms.int32(10),
        c = cms.double(1E-3),
        )

