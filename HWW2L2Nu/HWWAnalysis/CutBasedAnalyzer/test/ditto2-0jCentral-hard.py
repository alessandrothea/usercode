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
        name = cms.string('eta barrel'),
        cut = cms.string('abs(pA.eta()) <  1.5 && abs(pB.eta()) < 1.5'),
    ),
    cms.PSet(
        name = cms.string('minMet'),
        cut = cms.string('met > 30'),
    ),
    cms.PSet(
        name = cms.string('mllRange'),
        cut = cms.string('mll > 12. && mll < 60.'),
    ),
    cms.PSet(
        name = cms.string('Central Jet Veto'),
        cut = cms.string('nCentralJets == 0'),
    ),
    cms.PSet(
        name = cms.string('pT trail'),
        cut = cms.string('pB.pt() > 30'),
    ),

    cms.PSet(
        name = cms.string('dPhi'),
        cut = cms.string('dPhi*'+radToDeg+' < 45.'),
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
    variable('mll',             'm_{ll};GeV',                       'mll',50,0.,200.),
    variable('met',             '#slash{E}_{T};GeV',                'met',50,0.,100.),
    variable('projMet',         'proj#slash{E}_{T};GeV',            'projMet',50,0.,100.),
    variable('nJets',           'N_{jets}',                         'nJets',10,0.,10.),
    variable('nCentralJets',    'N_{jets}^{central}',               'nCentralJets',10,0.,10.),
    variable('nCentralJets40',  'N_{jets}^{central}, p_{T}>40',     'nCentralJets40',10,0.,10.),
    variable('nBJets',          'N_{Bjets}',                        'nBJets',10,0.,10.),
    variable('nSoftMus',        'N_{soft#mu}',                      'nSoftMus',10,0.,10.),
    variable('dPhi',            '#Delta#phi;deg',                   'dPhi*'+radToDeg,36,0.,180.),
    variable('ptLead',          'p_{T}^{lead};GeV',                 'pA.pt()',50,0,200.),
    variable('ptTrail',         'p_{T}^{trail},GeV',                'pB.pt()',50,0,200.),
)

process.monitored = cms.vstring(['type','dPhi','mll','met','pA.pt()','pB.pt()','pA.eta()','pB.eta()']) 

