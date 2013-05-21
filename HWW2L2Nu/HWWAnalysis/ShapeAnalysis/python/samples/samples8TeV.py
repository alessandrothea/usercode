import hwwtools
import re


backgrounds = {
    'VVV'                     : ['nominals/latino_092_WWWJets.root',
                                 'nominals/latino_091_WWZJets.root',
                                ],
    'WW'                      : ['nominals/latino_000_WWJets2LMad.root'],
    'ggWW'                    : ['nominals/latino_001_GluGluToWWTo4L.root'],
    'VgS'                     : ['nominals/latino_082_WGstarToElNuMad.root',
                                 'nominals/latino_083_WGstarToMuNuMad.root',
                                 'nominals/latino_084_WGstarToTauNuMad.root',
                                ],
    'VgS-template'            : ['vgTemplate/latino_082_WGstarToElNuMad.root',
                                 'vgTemplate/latino_083_WGstarToMuNuMad.root',
                                 'vgTemplate/latino_084_WGstarToTauNuMad.root',
                                ],
    'Vg'                      : ['nominals/latino_085_WgammaToLNuG.root',
                                 'nominals/latino_086_ZgammaToLLuG.root',
                                ],
    'Vg-template'             : ['vgTemplate/latino_085_WgammaToLNuG.root',
                                 'vgTemplate/latino_086_ZgammaToLLuG.root',
                                ],
    'WJet'                    : ['wjets/latino_RunA_892pbinv_LooseLoose.root',
                                 'wjets/latino_RunB_4404pbinv_LooseLoose.root',
                                 'wjets/latino_RunC_7032pbinv_LooseLoose.root',
                                 'wjets/latino_RunD_7274pbinv_LooseLoose.root',
                                ],
    'WJetFakeRate-nominal'    : ['wjets/latino_RunA_892pbinv_LooseLoose.root',
                                 'wjets/latino_RunB_4404pbinv_LooseLoose.root',
                                 'wjets/latino_RunC_7032pbinv_LooseLoose.root',
                                 'wjets/latino_RunD_7274pbinv_LooseLoose.root',
                                ],
    'WJet-template-2j'        : ['wjetsTemplate/latino_RunA_892pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunB_4404pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunC_7032pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunD_7274pbinv_LooseLoose.root',
                                ],
    'WJetFakeRate-template-2j': ['wjetsTemplate/latino_RunA_892pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunB_4404pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunC_7032pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunD_7274pbinv_LooseLoose.root',
                                ],
   'WJetFakeRate-vh-template-nominal' :['wjetsTemplate/latino_RunA_892pbinv_LooseLoose.root',
                                        'wjetsTemplate/latino_RunB_4404pbinv_LooseLoose.root',
                                        'wjetsTemplate/latino_RunC_7032pbinv_LooseLoose.root',
                                        'wjetsTemplate/latino_RunD_7274pbinv_LooseLoose.root',
                                       ],
    'Top'                     : ['nominals/latino_019_TTTo2L2Nu2B.root',
                                 'nominals/latino_011_TtWFullDR.root',
                                 'nominals/latino_012_TbartWFullDR.root',
                                ],
    'VV'                      : ['nominals/latino_074_WZJetsMad.root',
                                 'nominals/latino_075_ZZJetsMad.root',
                                 'nominals/latino_078_WZTo2L2QMad.root',
                                 'nominals/latino_079_ZZTo2L2QMad.root',
                                ],
    'DYTT'                    : ['nominals/latino_DYtt_19.5fb.root'], # for ee/mm channels DYTT is included in DD
    'DYLL'                    : ['nominals/latino_036_DY10toLLMad.root',
                                 'nominals/latino_037_DY50toLLMad.root',
                                ],
    'DYmm'                    : ['nominals/latino_036_DY10toLLMad.root',
                                 'nominals/latino_037_DY50toLLMad.root',
                                ],
    'DYee'                    : ['nominals/latino_036_DY10toLLMad.root',
                                 'nominals/latino_037_DY50toLLMad.root',
                                ],
    'DYLL-template-0j1j'      : ['dyTemplate/latino_036_DY10toLLMad.root',
                                 'dyTemplate/latino_037_DY50toLLMad.root',
                                ],
    'DYLL-templatesyst-0j1j'  : ['dyTemplate/latino_036_DY10toLLMad.root',
                                 'dyTemplate/latino_037_DY50toLLMad.root',
                                ],
    'WWewk'                   : ['nominals/latino_052_WW2JetsPhantom.root'],
    'WWpow'                   : ['nominals/latino_006_WWJets2LPowheg.root'],
    'WWnloNorm'               : ['nominals/latino_002_WWto2L2NuMCatNLO.root'],
    'WWnlo'                   : ['nominals/latino_002_WWto2L2NuMCatNLO.root'],
    'WWnloUp'                 : ['nominals/latino_004_WWto2L2NuMCatNLOUp.root'],
    'WWnloDown'               : ['nominals/latino_003_WWto2L2NuMCatNLODown.root'],
    'Top-template'            : ['topTemplate/latino_000_WWJets2LMad.root',
                                 'topTemplate/latino_001_GluGluToWWTo4L.root',
                                 'topTemplate/latino_036_DY10toLLMad.root',
                                 'topTemplate/latino_037_DY50toLLMad.root',
                                 'topTemplate/latino_074_WZJetsMad.root',
                                 'topTemplate/latino_075_ZZJetsMad.root',
                                 'topTemplate/latino_078_WZTo2L2QMad.root',
                                 'topTemplate/latino_079_ZZTo2L2QMad.root',
                                 'topTemplate/latino_082_WGstarToElNuMad.root',
                                 'topTemplate/latino_083_WGstarToMuNuMad.root',
                                 'topTemplate/latino_084_WGstarToTauNuMad.root',
                                 'topTemplate/latino_085_WgammaToLNuG.root',
                                 'topTemplate/latino_086_ZgammaToLLuG.root',
                                 'topTemplate/latino_RunA_892pbinv_LooseLoose.root',
                                 'topTemplate/latino_RunB_4404pbinv_LooseLoose.root',
                                 'topTemplate/latino_RunC_7032pbinv_LooseLoose.root',
                                 'topTemplate/latino_RunD_7274pbinv_LooseLoose.root',
                                ],
    'DYLL-template-dd'        : ['dyTemplate-dd/latino_036_DY10toLLMad.root',
                                 'dyTemplate-dd/latino_037_DY50toLLMad.root',
                                ],
    'DYLL-template-vbf'       : ['dyTemplate/latino_036_DY10toLLMad.root',
                                 'dyTemplate/latino_037_DY50toLLMad.root',
                                ],
}

backgrounds['Other'] = backgrounds['WW']+backgrounds['ggWW']+backgrounds['Top']+backgrounds['VV']+backgrounds['DYTT']+backgrounds['DYLL']

data = {

    'Data2012A' : ['data/latino_RunA_892pbinv.root'],

    'Data2012B' : ['data/latino_RunB_4404pbinv.root'],

    'Data2012C' : ['data/latino_RunC_7032pbinv.root'],

    'Data2012D' : ['data/latino_RunD_7274pbinv.root'],
}


data['Data2012'] = data['Data2012A']+data['Data2012B']+data['Data2012C']+data['Data2012D']

#--------------
# signal samples labels and generation

def signalSamples(sigtag,mass=125,suffix=''):

    signals = {}

    # some preliminary definitions
    std_ggH      = ['nominals/latino_1125_ggToH125toWWTo2LAndTau2Nu.root']
    std_qqH      = ['nominals/latino_2125_vbfToH125toWWTo2LAndTau2Nu.root']
    std_wzttH    = ['nominals/latino_3125_wzttH125ToWW.root']

    jhu_ggSM     = ['nominals/latino_8001_SMH125ToWW2L2Nu.root',
                    'nominals/latino_8004_SMH125ToWW2Tau2Nu.root',
                    'nominals/latino_8007_SMH125ToWWLTau2Nu.root' 
                   ]

    jhu_ggHiggs0M= ['nominals/latino_8002_Higgs0M125ToWW2L2Nu.root',
                    'nominals/latino_8005_Higgs0M125ToWW2Tau2Nu.root',
                    'nominals/latino_8008_Higgs0M125ToWWLTau2Nu.root'
                   ]

    jhu_ggGrav2PM= ['nominals/latino_8003_Graviton2PM.root',
                    'nominals/latino_8006_Graviton2PMToWW2Tau2nu.root',
                    'nominals/latino_8009_Graviton2PMToWWLTau2nu.root'
                   ]

    jhu_qqGrav2PM= ['nominals/latino_8010_Graviton2PMqqbarToWW2L2nu.root',
                    'nominals/latino_8011_Graviton2PMqqbarToWW2Tau2nu.root',
                    'nominals/latino_8012_Graviton2PMqqbarToWWLTau2nu.root'
                   ]

    if sigtag == 'SM':
        ggH   = ['nominals/latino_1{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root',
                ]
        qqH   = ['nominals/latino_2{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root',
                ]
        wzttH = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root']
        WH    = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root']
        ZH    = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root']
        ttH   = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root']



        if mass <= 300:
            signals['ggH'+suffix]   = [f.format(mass = mass) for f in ggH]
            signals['qqH'+suffix]   = [f.format(mass = mass) for f in qqH]
            signals['wzttH'+suffix] = [f.format(mass = mass) for f in wzttH]
            signals['WH'+suffix]    = [f.format(mass = mass) for f in WH]
            signals['ZH'+suffix]    = [f.format(mass = mass) for f in ZH]
            signals['ttH'+suffix]   = [f.format(mass = mass) for f in ttH]
        else:
            signals['ggH'+suffix]   = [f.format(mass = mass) for f in ggH]
            signals['qqH'+suffix]   = [f.format(mass = mass) for f in qqH]


# and the JHU case:

    elif sigtag == 'Grav2PM' and mass==125:

        signals['ggH']     = std_ggH
        signals['qqH']     = std_qqH
        signals['wzttH']   = std_wzttH
               
        signals['ggH_ALT'] = jhu_ggGrav2PM
        signals['qqH_ALT'] = jhu_qqGrav2PM
        signals['jhu_NORM']= std_ggH

    elif sigtag == 'Higgs0M' and mass==125:

        signals['ggH']     = std_ggH
        signals['qqH']     = std_qqH
        signals['wzttH']   = std_wzttH
               
        signals['ggH_ALT'] = jhu_ggHiggs0M
        signals['jhu_NORM']= std_ggH


# some old stuff (kept for reference & commented out)
#    elif sigtag == 'JHUSMONLY' and mass==125:
#
#        signals['jhu']     = jhu_ggSM 
#        signals['jhu_NORM']= std_ggH
#
#
#    elif sigtag == 'JHU0MONLY' and mass==125:
#
#        signals['jhu']     = jhu_ggHiggs0M 
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHU2MONLY' and mass==125:
#
#        signals['jhu']     = jhu_ggGrav2PM
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHUSMvs0M' and mass==125:
#        signals['jhu']     = jhu_ggSM 
#        signals['jhu_ALT'] = jhu_ggHiggs0M
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHUSMvs2M' and mass==125:
#        signals['jhu']     = jhu_ggSM
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        signals['jhu_NORM']= std_ggH
#        signals['jhu_NLO'] = std_ggH
#
#    elif sigtag == 'JHUSMvs2MnoNLO' and mass==125:
#        signals['jhu']     = jhu_ggSM
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'PWGSMvs2M' and mass==125:
#
#        signals['jhu']      = std_ggH
#        signals['jhu_ALT']  = jhu_ggGrav2PM
#        signals['jhu_NORM'] = std_ggH
#        signals['jhu_NLO']  = std_ggH 
#
#    elif sigtag == 'PWGSMvs2MnoNLO' and mass==125:
#        signals['jhu']     = std_ggH
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHUSMvs2MplOthers' and mass==125:
#
#        signals['jhu']       = jhu_ggSM
#        signals['vbfH']      = std_vbf
#        signals['wzttH']     = std_wzttH
#
#        signals['jhu_ALT']   = jhu_ggGrav2PM
#        signals['vbfH_ALT']  = std_vbf
#        signals['wzttH_ALT'] = std_wzttH
#        signals['jhu_NORM']  = std_ggH
#
#
#    elif sigtag == 'PWGSMqqHwzttHvs2MnoNLO' and mass==125:
#
#        signals['jhu']     = std_ggH
#        signals['vbfH']    = std_vbf
#        signals['wzttH']   = std_wzttH
#               
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        #signals['vbfH_ALT'] = std_vbf
#        #signals['wzttH_ALT']= std_wzttH
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'PWGSMqqHwzttHvs2MnoNLOnormALL' and mass==125:
#
#        signals['jhu']     = std_ggH
#        signals['vbfH']    = std_vbf
#        signals['wzttH']   = std_wzttH
#
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        #signals['vbfH_ALT'] = std_vbf
#        #signals['wzttH_ALT']= std_wzttH
#        signals['jhu_NORM']= std_ggH+std_vbf+std_wzttH
#
#    elif sigtag == 'PWGSMqqHwzttHvs2MnoNLOnoNorm' and mass==125:
#
#
#        signals['jhu']       = std_ggH
#        signals['vbfH']      = std_vbf
#        signals['wzttH']     = std_wzttH
#
#        signals['jhu_ALT']   = jhu_ggGrav2PM
#        #signals['vbfH_ALT'] = std_vbf
#        #signals['wzttH_ALT']= std_wzttH
#        #signals['jhu_NORM'] = std_ggH+std_vbf+std_wzttH
#
#    elif sigtag == 'PWGSMqqHwzttHvs0MnoNLO' and mass==125:
#
#        signals['jhu']     = std_ggH
#        signals['vbfH']    = std_vbf
#        signals['wzttH']   = std_wzttH
#
#        signals['jhu_ALT'] = jhu_ggHiggs0M
#
#        #signals['vbfH_ALT'] = std_vbf
#        #signals['wzttH_ALT']= std_wzttH
#        signals['jhu_NORM']= std_ggH

    else:
        raise ValueError('Signal tag %s not found for mass %d' % (sigtag,mass) )
    return signals

