import re

#  ___                  _        
# / __| __ _ _ __  _ __| |___ ___
# \__ \/ _` | '  \| '_ \ / -_|_-<
# |___/\__,_|_|_|_| .__/_\___/__/
#                 |_|            
backgrounds = {}
backgrounds['WW']               = ['nominals/latino_000_WWJets2LMad.root']
backgrounds['ggWW']             = ['nominals/latino_001_GluGluToWWTo4L.root']
backgrounds['Vg']               = ['nominals/latino_082_WGstarToElNuMad_filtered.root',
                                   'nominals/latino_083_WGstarToMuNuMad_filtered.root',
                                   'nominals/latino_084_WGstarToTauNuMad_filtered.root',
                                   'nominals/latino_085_WgammaToLNuG.root',
                                  ]
backgrounds['WJet']             = ['wjets/latino_10X_LooseLoose.root',
                                   'wjets/latino_20X_LooseLoose.root',
                                   'wjets/latino_22X_LooseLoose.root',
                                   'wjets/latino_23X_LooseLoose.root',
                                   'wjets/latino_24X_LooseLoose.root'
                                  ]
backgrounds['WJetFakeRate']     = ['wjets/latino_10X_LooseLoose.root',
                                   'wjets/latino_20X_LooseLoose.root',
                                   'wjets/latino_22X_LooseLoose.root',
                                   'wjets/latino_23X_LooseLoose.root',
                                   'wjets/latino_24X_LooseLoose.root'
                                  ]
backgrounds['Top']              = ['nominals/latino_019_TTTo2L2Nu2B.root',
                                   'nominals/latino_011_TtWFullDR.root',
                                   'nominals/latino_012_TbartWFullDR.root',
                                  ]
# backgrounds['TopTT']            = ['nominals/latino_019_TTTo2L2Nu2B.root']
# backgrounds['TopTW']            = ['nominals/latino_011_TtWFullDR.root',
#                                    'nominals/latino_012_TbartWFullDR.root',
#                                   ]
backgrounds['VV']               = ['nominals/latino_074_WZJetsMad.root',
                                   'nominals/latino_075_ZZJetsMad.root',
                                   'nominals/latino_078_WZTo2L2QMad.root',
                                   'nominals/latino_079_ZZTo2L2QMad.root',
                                  ]
backgrounds['DYTT']             = ['nominals/latino_222_EMBtt.root',
                                   'nominals/latino_037_DY50toLLMad.root',
                                  ]
backgrounds['DYLL']             = ['nominals/latino_036_DY10toLLMad.root',
                                   'nominals/latino_037_DY50toLLMad.root',
                                  ]
backgrounds['DYLLtemplate']     = ['dyTemplate/latino_036_DY10toLLMad.root',
                                   'dyTemplate/latino_037_DY50toLLMad.root',
                                  ]
backgrounds['DYLLtemplatesyst'] = ['dyTemplate-syst/latino_036_DY10toLLMad.root',
                                   'dyTemplate-syst/latino_037_DY50toLLMad.root',
                                  ]
# backgrounds['DYLLtemplatedd']   = ['dyTemplate-dd/latino_036_DY10toLLMad.root',
#                                    'dyTemplate-dd/latino_037_DY50toLLMad.root',
#                                    ]
backgrounds['WWnlo']            = ['nominals/latino_002_WWto2L2NuMCatNLO.root']
backgrounds['WWnloUp']          = ['nominals/latino_004_WWto2L2NuMCatNLOUp.root']
backgrounds['WWnloDown']        = ['nominals/latino_003_WWto2L2NuMCatNLODown.root']

data = {}
data['Data2011A'] = [
    'data/latino_150_SingleElectron2011AMay10.root',
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
]

data['Data2011B'] = [
    'data/latino_140_SingleElectron2011Bv1a.root',
    'data/latino_141_SingleMuon2011Bv1a.root',
    'data/latino_142_DoubleElectron2011Bv1a.root',
    'data/latino_143_DoubleMuon2011Bv1a.root',
    'data/latino_144_MuEG2011Bv1a.root',

]
data['Data2011'] =  data['Data2011A']+data['Data2011B']

data['Data2012A']=[
    'data/latino_100_SingleElectron2012A.root',
    'data/latino_101_SingleMuon2012A.root',
    'data/latino_102_DoubleElectron2012A.root',
    'data/latino_103_DoubleMuon2012A.root',
    'data/latino_104_MuEG2012A.root',
]

data['Data2012B']=[
    'data/latino_200_SingleElectron2012B.root',
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
]

data['Data2012'] = data['Data2012A']+data['Data2012B']

def signalSamples(mass):
    signals = {}
    ggH = ['nominals/latino_1{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root',
#            'latino_1{mass}_ggToH{mass}toWWto2L2Nu.root',
#            'latino_2{mass}_ggToH{mass}toWWtoLNuTauNu.root',
#            'latino_3{mass}_ggToH{mass}toWWto2Tau2Nu.root',
          ]
#     ggHnew = ['latino_9{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root']
    vbfH   = ['nominals/latino_2{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root',
#               'latino_4{mass}_vbfToH{mass}toWWto2L2Nu.root', 
#               'latino_5{mass}_vbfToH{mass}toWWtoLNuTauNu.root',
#               'latino_6{mass}_vbfToH{mass}toWWto2Tau2Nu.root', 
             ]
#     vbfHnew = ['latino_8{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root']
    wzttH   = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root']

#     if int(mass)==122:
#         signals['ggH']  = [f.format(mass = mass) for f in ggHnew]
#         signals['wzttH'] = [f.format(mass = mass) for f in wzttH]
#     elif int(mass)==118 or (int(mass)>120 and int(mass)<130) or int(mass)==135:
#         signals['ggH']  = [f.format(mass = mass) for f in ggHnew]
#         signals['vbfH'] = [f.format(mass = mass) for f in vbfHnew]
#         signals['wzttH'] = [f.format(mass = mass) for f in wzttH]
#     elif int(mass) > 115:
#         signals['ggH']  = [f.format(mass = mass) for f in ggH]
#         signals['vbfH'] = [f.format(mass = mass) for f in vbfH]
#         signals['wzttH'] = [f.format(mass = mass) for f in wzttH]
#     else:
#         signals['ggH']  = ['latino_9{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root'.format(mass = mass)]
#         signals['vbfH'] = ['latino_8{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root'.format(mass = mass)]

    if mass <= 300:
        signals['ggH']   = [f.format(mass = mass) for f in ggH]
        signals['vbfH']  = [f.format(mass = mass) for f in vbfH]
        signals['wzttH'] = [f.format(mass = mass) for f in wzttH]
    else:
        signals['ggH']   = [f.format(mass = mass) for f in ggH]
        signals['vbfH']  = [f.format(mass = mass) for f in vbfH]
    return signals

    
def samples(mass, datatag='Data2012', filter='all'):
    '''
    mass: mass for the higgs samples'
    datatag: tag for the dataset to be included
    '''
    samples = {}
    signals = signalSamples(mass)
    samples.update(signals)
    samples.update(backgrounds)
    if datatag == 'NoData':
        pass
    elif 'Data' in datatag:
        samples['Data'] = data[datatag]
    elif 'SI' in datatag:
        # add the signal samples of the given mass
        m = re.match('SI(\d+)',datatag)
        if not m:
            raise ValueError('Signal injection must have the format SImmm where mmm is the mass')
        simass = int(m.group(1))
        siSamples = signalSamples(simass)
        # add the signal samples to the list with a _SI tag
        for s,f in siSamples.iteritems():
            samples[s+'-SI']=f
    else:
        raise ValueError('Data tag '+datatag+' not supported')

    return samples

