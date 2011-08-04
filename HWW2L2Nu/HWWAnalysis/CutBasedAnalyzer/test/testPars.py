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

# get and parse the command line arguments
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
        filter     = cms.string('isTight1 == 1 && isTight2')
)

process.channels = cms.VPSet(
    cms.PSet(
        name = cms.string('mm'),
        selection = cms.string('channel == 0'),
    ),
    cms.PSet(
        name = cms.string('me'),
        selection = cms.string('channel == 3'),
    ),
    cms.PSet(
        name = cms.string('em'),
        selection = cms.string('channel == 2'),
    ),
    cms.PSet(
        name = cms.string('ee'),
        selection = cms.string('channel == 1'),
    ),

)

process.cuts = cms.VPSet(
    cut('trigger',    'trigger', ''),
    cut('minMet',     'min #slash{E}_{T}','met > 20'),
    cut('minMll',     'min M_{ll}','mll > 12.'),
    cut('Zveto',      'Zveto','sameflav == 0 || (TMath::Abs(mll - 91.18699) > 15.)'),
    cut('projMet',    'projMet','( sameflav == 1 && TMath::Min(pmet,pmet2) > 40. ) || ( sameflav == 0 && TMath::Min(pmet,pmet2) > 20. ) '),
    cut('jetVeto',    'Jet Veto','njet == 0'),
    cut('dphiJll',    'd#Phi_{jll}','sameflav == 0 || dphilljet*TMath::RadToDeg() < 165.'),
    cut('softMu',     'Soft mu','bveto_mu == 1'),
    cut('extraLep',   'Extra Lepton Veto','nextra == 0'),
    cut('antiB',      'Anti B','bveto_ip == 1'),
    cut('maxMll',     'max M_{ll}','mll < 50'),
    cut('pTLead',     'p_{T} lead','pt1 > 30'),
    cut('pTTrail',    'p_{T} trail','pt2 > 25'),
    cut('dPhi',       'd#Phi','dphill*'+radToDeg+' < 60'),
    cut('mT',         'm_{T}','mth > 90. && mth < 160.'),
    )



process.variables = cms.VPSet(
    variable('mll',     'm_{ll};GeV',               'mll',50,0.,200.),
    variable('met',     '#slash{E}_{T};GeV',        'met',50,0.,100.),
    variable('projMet', 'proj#slash{E}_{T};GeV',    'pmet',50,0.,100.),
    variable('nJets',   'N_{jets}',                 'njet',10,0.,10.),
    variable('dPhillj', '#Delta#Phi_{ll,j};deg',    'dphilljet*'+radToDeg,36,0.,180.),
    variable('dPhi',    '#Delta#phi',               'dphill*'+radToDeg,36,0.,180.),
    variable('ptLead',  'p_{T}^{lead}',             'pt1',50,0,200.),
    variable('ptTrail', 'p_{T}^{trail}',            'pt2',50,0,200.),

)

