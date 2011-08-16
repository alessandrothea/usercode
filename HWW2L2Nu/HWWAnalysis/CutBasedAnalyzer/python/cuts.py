import FWCore.ParameterSet.Config as cms

from HWWAnalysis.CutBasedAnalyzer.treeCutter import cut, variable, radToDeg

channels = cms.VPSet(
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

cuts0j = cms.VPSet(
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

cutsWW0j = cms.VPSet(
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
)

variables = cms.VPSet(
    variable('mll',     'm_{ll};GeV',               'mll',50,0.,200.),
    variable('met',     '#slash{E}_{T};GeV',        'met',50,0.,100.),
    variable('projMet', 'proj#slash{E}_{T};GeV',    'pmet',50,0.,100.),
    variable('nJets',   'N_{jets}',                 'njet',10,0.,10.),
    variable('dPhillj', '#Delta#Phi_{ll,j};deg',    'dphilljet*'+radToDeg,36,0.,180.),
    variable('dPhi',    '#Delta#phi',               'dphill*'+radToDeg,36,0.,180.),
    variable('ptLead',  'p_{T}^{lead}',             'pt1',50,0,200.),
    variable('ptTrail', 'p_{T}^{trail}',            'pt2',50,0,200.),

)

