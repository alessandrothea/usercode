import hwwtools
import re

backgrounds = {
    'WW'                     : ['nominals/latino_000_WWJets2LMad.root'],
    'ggWW'                   : ['nominals/latino_001_GluGluToWWTo4L.root'],
    'Vg'                     : ['nominals/latino_082_WGstarToElNuMad.root',
                                'nominals/latino_083_WGstarToMuNuMad.root',
                                'nominals/latino_084_WGstarToTauNuMad.root',
                                'nominals/latino_085_WgammaToLNuG.root',
                                'nominals/latino_086_ZgammaToLLuG.root',
                               ],
    'WJet'                   : ['wjets/latino_RunA_892pbinv_LooseLoose.root',
                                'wjets/latino_RunB_4404pbinv_LooseLoose.root',
                                'wjets/latino_RunC_6807pbinv_LooseLoose.root',
                               ],
    'WJetFakeRate'           : ['wjets/latino_RunA_892pbinv_LooseLoose.root',
                                'wjets/latino_RunB_4404pbinv_LooseLoose.root',
                                'wjets/latino_RunC_6807pbinv_LooseLoose.root',
                               ],
    'Top'                    : ['nominals/latino_019_TTTo2L2Nu2B.root',
                                'nominals/latino_011_TtWFullDR.root',
                                'nominals/latino_012_TbartWFullDR.root',
                               ],
    'VV'                     : ['nominals/latino_074_WZJetsMad.root',
                                'nominals/latino_075_ZZJetsMad.root',
                                'nominals/latino_078_WZTo2L2QMad.root',
                                'nominals/latino_079_ZZTo2L2QMad.root',
                               ],
    'DYTT'                   : ['nominals/latino_RunABC_DYtt_8fb.root'], # for ee/mm channels DYTT is included in DD
    'DYLL'                   : ['nominals/latino_036_DY10toLLMad.root',
                                'nominals/latino_037_DY50toLLMad.root',
                               ],
    'DYee'                   : ['nominals/latino_000_WWJets2LMad.root',   # dummy, just to have the histogram in cut based
                               ],
    'DYmm'                   : ['nominals/latino_000_WWJets2LMad.root',   # dummy, just to have the histogram in cut based
                               ],
    'DYLL-template-0j1j'     : ['dyTemplate/latino_036_DY10toLLMad.root',
                                'dyTemplate/latino_037_DY50toLLMad.root',
                               ],
    'DYLL-templatesyst-0j1j' : ['dyTemplate/latino_036_DY10toLLMad.root',
                                'dyTemplate/latino_037_DY50toLLMad.root',
                               ],
    'WWnlo'                  : ['nominals/latino_002_WWto2L2NuMCatNLO.root'],
    'WWnloUp'                : ['nominals/latino_004_WWto2L2NuMCatNLOUp.root'],
    'WWnloDown'              : ['nominals/latino_003_WWto2L2NuMCatNLODown.root'],
    'TopTW'                  : ['nominals/latino_019_TTTo2L2Nu2B.root',
                                'tW/latino_011_TtWFullDR.root',
                                'tW/latino_012_TbartWFullDR.root',
                                ],
    'TopCtrl'                : ['nominals/latino_019_TTTo2L2Nu2B.root',
                                'nominals/latino_011_TtWFullDR.root',
                                'nominals/latino_012_TbartWFullDR.root',
                                ],
    'DYLL-template-dd'       : ['dyTemplate-dd/latino_036_DY10toLLMad.root',
                                'dyTemplate-dd/latino_037_DY50toLLMad.root',
                               ],
    'DYLL-template-vbf'      : ['dyTemplate/latino_036_DY10toLLMad.root',
                                'dyTemplate/latino_037_DY50toLLMad.root',
                               ],
}

data = {
    'Data2011A' : ['data/latino_150_SingleElectron2011AMay10.root',
                   'data/latino_151_SingleMuon2011AMay10.root',
                   'data/latino_152_DoubleMuon2011AMay10.root',
                   'data/latino_153_DoubleElectron2011AMay10.root',
                   'data/latino_154_MuEG2011AMay10.root',

                   'data/latino_100_SingleElectron2011Av4.root',
                   'data/latino_101_SingleMuon2011Av4.root',
                   'data/latino_102_DoubleElectron2011Av4.root',
                   'data/latino_103_DoubleMuon2011Av4.root',
                   'data/latino_104_MuEG2011Av4.root',

                   'data/latino_160_SingleElectron2011AAug05.root',
                   'data/latino_161_SingleMuon2011AAug05.root',
                   'data/latino_162_DoubleElectron2011AAug05.root',
                   'data/latino_163_DoubleMuon2011AAug05.root',
                   'data/latino_164_MuEG2011AAug05.root',

                   'data/latino_120_SingleElectron2011Av6.root',
                   'data/latino_121_SingleMuon2011Av6.root',
                   'data/latino_122_DoubleElectron2011Av6.root',
                   'data/latino_123_DoubleMuon2011Av6.root',
                   'data/latino_124_MuEG2011Av6.root',
                  ],

    'Data2011B'  :['data/latino_140_SingleElectron2011Bv1a.root',
                   'data/latino_141_SingleMuon2011Bv1a.root',
                   'data/latino_142_DoubleElectron2011Bv1a.root',
                   'data/latino_143_DoubleMuon2011Bv1a.root',
                   'data/latino_144_MuEG2011Bv1a.root',
                  ],

    'Data2012A' : ['data/latino_RunA_892pbinv.root'],

    'Data2012B' : ['data/latino_RunB_4404pbinv.root'],

    'Data2012C' : ['data/latino_RunC_6807pbinv.root'],
}

data['Data2011'] = data['Data2011A']+data['Data2011B']

data['Data2012'] = data['Data2012A']+data['Data2012B']+data['Data2012C']

#--------------
# signal samples labels and generation

signals = ['ggH','vbfH','wzttH','jhu','jhu_ALT']

def signalSamples(sigtag,mass=125):

    signals = {}

    if sigtag == 'SM':
        ggH   = ['nominals/latino_1{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root',
                ]
        vbfH  = ['nominals/latino_2{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root',
                ]
        wzttH = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root']


        if mass <= 300:
            signals['ggH']   = [f.format(mass = mass) for f in ggH]
            signals['vbfH']  = [f.format(mass = mass) for f in vbfH]
            signals['wzttH'] = [f.format(mass = mass) for f in wzttH]
        else:
            signals['ggH']   = [f.format(mass = mass) for f in ggH]
            signals['vbfH']  = [f.format(mass = mass) for f in vbfH]
    elif sigtag == 'JHU' and mass==125:
        signals['jhu']     = ['nominals/latino_1125_ggToH125toWWTo2LAndTau2Nu.root']
        signals['jhu_ALT'] = ['nominals/latino_1125_ggToH125toWWTo2LAndTau2Nu.root']
    else:
        raise ValueError('Signal tag %s not found for mass %d' % (sigtag,mass) )
    return signals

#--------------
# mcsets,
# list of samples and compact dictionary
#
mcsets = {
    '0j1j-JHU' : [
        #signals
        'jhu','jhu_ALT',
        # bkgs
        'WW','ggWW','Vg','WJet','WJetFakeRate','Top','VV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown','TopTW','TopCtrl',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    '0j1j' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW','ggWW','Vg','WJet','WJetFakeRate','Top','VV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown','TopTW','TopCtrl',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    'cutbased' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW', 'Vg','WJet','Top','VV','DYTT',
        # replce ggWW and DYLL
        ('ggWW',    'WW'),
        ('DYLL',    'WW'),
    ],
    'vbf_sf' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        #'WW','ggWW','Vg','WJet','Top','VV','DYTT','DYLL',
        'WW','ggWW','Vg','WJet','Top','VV','DYTT','DYee','DYmm'
    ],
   'vbf_of' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW','ggWW','Vg','WJet','Top','VV','DYTT',
    ],
}

#--------------
def samples(mass, datatag='Data2012', sigtag='SM', mctag='all'):
    '''
    mass: mass for the higgs samples'
    datatag: tag for the dataset to be included
    mctag: tag for the set of mc to be included
    '''

    signals = signalSamples(sigtag,mass)

    mcsamples = {}
    mcsamples.update(signals)
    mcsamples.update(backgrounds)

    if isinstance(mctag,list):
        mclabels = mctag
    else:
        if mctag not in mcsets:
            raise ValueError('MCtag '+mctag+' not supported')
        mclabels = mcsets[mctag]

    selectedMc = hwwtools.filterSamples( mcsamples, mclabels )

    # add data
    selectedData = {}
    if datatag == 'NoData':
        pass
    elif 'Data' in datatag:
        selectedData['Data'] = data[datatag]
    elif 'SI' in datatag:
        # add the signal samples of the given mass
        m = re.match('SI(\d+)',datatag)
        if not m:
            raise ValueError('Signal injection must have the format SImmm where mmm is the mass')
        simass = int(m.group(1))
        siSamples = signalSamples(sigtag, simass)
        # add the signal samples to the list with a _SI tag
        for s,f in siSamples.iteritems():
            selectedData[s+'-SI']=f
    else:
        raise ValueError('Data tag '+datatag+' not supported')

    samples = {}
    samples.update(selectedMc)
    samples.update(selectedData)

    return samples



