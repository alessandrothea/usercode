import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.VarParsing as VarParsing

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

radToDeg = str(180./math.pi)

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

options.register ( 'monitor',
                  False,
                  VarParsing.VarParsing.multiplicity.singleton,
                  VarParsing.VarParsing.varType.bool,
                  "monitor informations for every selected event")
options.register ( 'useWeights',
                  True,
                  VarParsing.VarParsing.multiplicity.singleton,
                  VarParsing.VarParsing.varType.bool,
                  "Apply event weights")


# setup any defaults you want
options.outputFile = 'simpleTest.root'
# options.inputFiles= 'file1.root', 'file2.root'
options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()


process = cms.PSet(
        treeName   = cms.string('ntupleproducer/hwwStep3'),
        inputFiles = cms.vstring(options.inputFiles),
        outputFile = cms.string(options.outputFile),
        maxEvents  = cms.int64(options.maxEvents),
        monitor    = cms.bool(options.monitor),
#         copyObjects = cms.vstring(['entries']),
        copyObjects = cms.vstring([]),
        useWeights = cms.bool(options.useWeights),
)

process.channels = cms.VPSet(
#     cms.PSet(
#         name = cms.string('ll'),
#         selection = cms.string('1 == 1 '),
#     ),
    cms.PSet(
        name = cms.string('mm'),
        selection = cms.string('is(\'mumu\')'),
    ),
    cms.PSet(
        name = cms.string('me'),
        selection = cms.string('is(\'muel\')'),
    ),
    cms.PSet(
        name = cms.string('em'),
        selection = cms.string('is(\'elmu\')'),
    ),
    cms.PSet(
        name = cms.string('ee'),
        selection = cms.string('is(\'elel\')'),
    ),

)

process.monitored = cms.vstring(['mll','nJets','dPhillj0jet','nBJets']) 

process.cuts = cms.VPSet(
    cut('skim',       'skim',               ''),
    cut('minMet',     'min #slash{E}_{T}','met > 20'),
    cut('minMll',     'min M_{ll}',         'mll > 12.'),
    cut('Zveto',      'Zveto',              'different() || (abs(mll - 91.18699) > 15.)'),
    cut('projMet',    'projMet',            '( same() && min(projPfMet,projChargedMetSmurf) > 40. ) || ( different() && min(projPfMet,projChargedMetSmurf) > 20. ) '),
    cut('jetVeto',    'Jet Veto',           'nJets == 1'),
    cut('dPhiJll',    'DY jet veto',        '( same() && dPhillj0jet*'+radToDeg+'< 165.) || different()'),
    cut('softMu',     'Soft mu',            'nSoftMus == 0'),
    cut('extraLep',   'Extra Lepton Veto',  'nExtra == 0'),
    cut('antiB',      'Anti B',             'nBJets == 0'),
    cut('maxMll',     'max M_{ll}',         'mll < 50'),
    cut('pTLead',     'p_{T} lead',         'pA.pt() > 30'),
    cut('pTTrail',    'p_{T} trail',        'pB.pt() > 25'),
    cut('dPhi',       'd#Phi',              'dPhi*'+radToDeg+' < 60.'),
    cut('mT',         'm_{T}',              'mtll > 90. && mtll < 160.'),
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

