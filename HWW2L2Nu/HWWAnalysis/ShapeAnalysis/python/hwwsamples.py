import re

backgrounds = {
    'WW'                     : ['nominals/latino_000_WWJets2LMad.root'],
    'ggWW'                   : ['nominals/latino_001_GluGluToWWTo4L.root'],
    'Vg'                     : ['nominals/latino_082_WGstarToElNuMad_filtered.root',
                                'nominals/latino_083_WGstarToMuNuMad_filtered.root',
                                'nominals/latino_084_WGstarToTauNuMad_filtered.root',
                                'nominals/latino_085_WgammaToLNuG.root',
                               ],
    'WJet'                   : ['wjets/latino_10X_LooseLoose.root',
                                'wjets/latino_20X_LooseLoose.root',
                                'wjets/latino_22X_LooseLoose.root',
                                'wjets/latino_23X_LooseLoose.root',
                                'wjets/latino_24X_LooseLoose.root'
                               ],
    'WJetFakeRate'           : ['wjets/latino_10X_LooseLoose.root',
                                'wjets/latino_20X_LooseLoose.root',
                                'wjets/latino_22X_LooseLoose.root',
                                'wjets/latino_23X_LooseLoose.root',
                                'wjets/latino_24X_LooseLoose.root'
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
    'DYTT'                   : ['nominals/latino_222_EMBtt.root',
                                'nominals/latino_037_DY50toLLMad.root',
                               ],
    'DYLL'                   : ['nominals/latino_036_DY10toLLMad.root',
                                'nominals/latino_037_DY50toLLMad.root',
                               ],
    'DYLL-template-0j1j'     : ['dyTemplate/latino_036_DY10toLLMad.root',
                                'dyTemplate/latino_037_DY50toLLMad.root',
                               ],
    'DYLL-templatesyst-0j1j' : ['dyTemplate-syst/latino_036_DY10toLLMad.root',
                                'dyTemplate-syst/latino_037_DY50toLLMad.root',
                               ],
    'WWnlo'                  : ['nominals/latino_002_WWto2L2NuMCatNLO.root'],
    'WWnloUp'                : ['nominals/latino_004_WWto2L2NuMCatNLOUp.root'],
    'WWnloDown'              : ['nominals/latino_003_WWto2L2NuMCatNLODown.root'],
    'DYLL-template-dd'       : ['dyTemplate-dd/latino_036_DY10toLLMad.root',
                                'dyTemplate-dd/latino_037_DY50toLLMad.root',
                               ],

    'TopTT'                  : ['nominals/latino_019_TTTo2L2Nu2B.root'],
    'TopTW'                  : ['nominals/latino_011_TtWFullDR.root',
                                'nominals/latino_012_TbartWFullDR.root',
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

    'Data2012A' : ['data/latino_100_SingleElectron2012A.root',
                   'data/latino_101_SingleMuon2012A.root',
                   'data/latino_102_DoubleElectron2012A.root',
                   'data/latino_103_DoubleMuon2012A.root',
                   'data/latino_104_MuEG2012A.root',
                  ],

    'Data2012B' : ['data/latino_200_SingleElectron2012B.root',
                   'data/latino_201_SingleMuon2012B.root',
                   'data/latino_202_DoubleElectron2012B.root',
                   'data/latino_203_DoubleMuon2012B.root',
                   'data/latino_204_MuEG2012B.root',

                   'data/latino_220_SingleElectron2012B.root',
                   'data/latino_221_SingleMuon2012B.root',
                   'data/latino_222_DoubleElectron2012B.root',
                   'data/latino_223_DoubleMuon2012B.root',
                   'data/latino_224_MuEG2012B.root',

                   'data/latino_230_SingleElectron2012B.root',
                   'data/latino_231_SingleMuon2012B.root',
                   'data/latino_232_DoubleElectron2012B.root',
                   'data/latino_233_DoubleMuon2012B.root',
                   'data/latino_234_MuEG2012B.root',

                   'data/latino_240_SingleElectron2012B.root',
                   'data/latino_241_SingleMuon2012B.root',
                   'data/latino_242_DoubleElectron2012B.root',
                   'data/latino_243_DoubleMuon2012B.root',
                   'data/latino_244_MuEG2012B.root',

                   'data/latino_240_SingleElectron2012B_extra.root',
                   'data/latino_241_SingleMuon2012B_extra.root',
                   'data/latino_242_DoubleElectron2012B_extra.root',
                   'data/latino_243_DoubleMuon2012B_extra.root',
                   'data/latino_244_MuEG2012B_extra.root',    
                  ],
}

data['Data2011'] = data['Data2011A']+data['Data2011B']

data['Data2012'] = data['Data2012A']+data['Data2012B']

#--------------
def signalSamples(mass):
    signals = {}
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
    return signals

#
# mcsets,
# list of samples and compact dictionary
#
mcsets = {
    '0j1j' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW','ggWW','Vg','WJet','WJetFakeRate','Top','VV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j')
    ],
    'vbf' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW','ggWW','Vg','WJet','Top','VV','DYTT','DYLL',
        #'WWnlo','WWnloUp','WWnloDown',
        # vbf mapping
        # ('WJet-template','WJet-template-vbf'),
#         ('DYLL-template','DYLL-template-vbf'),
    ],
}

#--------------
def _mcFilterAndRename( samples, voc ):
    
    filtered = {}

    # convert the vocabulary, which is a mixture of strings and 2d tuples, into a dictionary
    fullvoc = dict([ e if isinstance(e,tuple) else (e,e) for e in voc])
    for proc,label in fullvoc.iteritems():
#         print proc,label

        if label not in samples: continue

        filtered[proc] = samples[label]

    return filtered

#--------------
def samples(mass, datatag='Data2012', mctag='all'):
    '''
    mass: mass for the higgs samples'
    datatag: tag for the dataset to be included
    mctag: tag for the set of mc to be included
    '''

    signals = signalSamples(mass)

    mcsamples = {}
    mcsamples.update(signals)
    mcsamples.update(backgrounds)

    #--
    # check mc
    if mctag not in mcsets:
        raise ValueError('Data tag '+mctag+' not supported')

    selectedMc = _mcFilterAndRename( mcsamples, mcsets[mctag] )

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
        siSamples = signalSamples(simass)
        # add the signal samples to the list with a _SI tag
        for s,f in siSamples.iteritems():
            selectedData[s+'-SI']=f
    else:
        raise ValueError('Data tag '+datatag+' not supported')

    samples = {}
    samples.update(selectedMc)
    samples.update(selectedData)
#     for i,j in  samples.iteritems():
#         print i,j
#     import sys
#     sys.exit(0)
    return samples



