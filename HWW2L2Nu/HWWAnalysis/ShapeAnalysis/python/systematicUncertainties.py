import os, re
from math import *

def file2map(file):
    map = {}
    for line in open(file,"r"):
        fields = [x.strip() for x in line.split()]
        if len(fields) > 1 and re.match("\d+", fields[0]):
            map[float(fields[0])] = [float(y) for y in fields[1:] if re.match(r"-?\d+.*",y) ]
    return map

def juerg2map(file):
    map = {}
    for line in open(file,"r"):
        if line[0] == '#': continue
        fields = [x.strip() for x in line.split()]
        map[fields[0]] = [float(y) for y in fields[1:]]
    return map

SYST_PATH      = os.getenv('CMSSW_BASE')+'/src/HWWAnalysis/ShapeAnalysis/data/nuisances/'
YR_ggH         = file2map(SYST_PATH+'YR-ggH.txt')
YR_vbfH        = file2map(SYST_PATH+'YR-vbfH.txt')
YR_wzttH       = file2map(SYST_PATH+'YR-wzttH.txt')
YR_wH          = file2map(SYST_PATH+'YR-wH.txt')
YR_zH          = file2map(SYST_PATH+'YR-zH.txt')
YR_ttH         = file2map(SYST_PATH+'YR-ttH.txt')

ggH_pdfErrYR   = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_ggH.items()] )
ggH_scaErrYR   = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_ggH.items()] )
vbfH_pdfErrYR  = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_vbfH.items()] )
vbfH_scaErrYR  = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_vbfH.items()] )
wzttH_pdfErrYR = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_wzttH.items()] )
wzttH_scaErrYR = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_wzttH.items()] )

wH_pdfErrYR = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_wH.items()] )
wH_scaErrYR = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_wH.items()] )

zH_pdfErrYR = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_zH.items()] )
zH_scaErrYR = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_zH.items()] )

ttH_pdfErrYR = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_ttH.items()] )
ttH_scaErrYR = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_ttH.items()] )


for X in 450, 550:
    ggH_pdfErrYR[X]  = 0.5*(ggH_pdfErrYR[X-10] +ggH_pdfErrYR[X+10])
    ggH_scaErrYR[X]  = 0.5*(ggH_scaErrYR[X-10] +ggH_scaErrYR[X+10])
    vbfH_pdfErrYR[X] = 0.5*(vbfH_pdfErrYR[X-10]+vbfH_pdfErrYR[X+10])
    vbfH_scaErrYR[X] = 0.5*(vbfH_scaErrYR[X-10]+vbfH_scaErrYR[X+10])

ggH_jets = dict([(m, dict(zip(['f0','f1','f2','k1','k2'], vals))) for m,vals in file2map(SYST_PATH+"ggH_jetBins.txt").items()]) 

ggH_UEPS = dict([(m, dict(zip(['u0','u1','u2'], vals))) for m,vals in file2map(SYST_PATH+"ggH_UEPS.txt").items()])

ggH_intf = dict([(m, dict(zip(['intf'], vals))) for m,vals in file2map(SYST_PATH+"ggH_interference.txt").items()])

def getCommonSysts(mass,channel,jets,qqWWfromData,shape,options,suffix,isssactive):
    nuisances = {} 
    #MCPROC = ['ggH', 'vbfH', 'DTT', 'ggWW', 'VV', 'Vg' ]; 
    MCPROC = ['ggH', 'vbfH', 'wzttH', 'wH', 'zH', 'ttH', 'DYTT', 'VV', 'VgS', 'Vg', 'Other', 'ggH125', 'vbfH125', 'wzttH125'];
    if channel == 'elmu' or channel == 'muel': MCPROC+=['DYMM','DYEE']
    if channel == 'of': MCPROC += ['DYLL']
    if not qqWWfromData: MCPROC+=['WW','ggWW']
    # -- Luminosity ---------------------
    lumiunc = 1.044
    if '7TeV' in suffix: lumiunc = 1.022
    nuisances['lumi'+suffix] = [ ['lnN'], dict([(p,lumiunc) for p in MCPROC])]
    # -- PDF ---------------------
    #nuisances['pdf_gg']    = [ ['lnN'], { 'ggH':ggH_pdfErrYR[mass], 'ggWW':(1.00 if qqWWfromData else 1.04) }]
    nuisances['pdf_gg']    = [ ['lnN'], { 'ggH':ggH_pdfErrYR[mass], 'ggWW':1.04 }]
    nuisances['pdf_qqbar'] = [ ['lnN'], { 'wzttH':(1.0 if mass>300 else wzttH_pdfErrYR[mass]),  'wH':(1.0 if mass>300 else wH_pdfErrYR[mass]),  'zH':(1.0 if mass>300 else zH_pdfErrYR[mass]),  'ttH':(1.0 if mass>300 else ttH_pdfErrYR[mass]), 'vbfH':vbfH_pdfErrYR[mass], 'VV':1.04, 'WW':(1.0 if qqWWfromData else 1.04), 'wzttH125':(1.0 if mass>300 else wzttH_pdfErrYR[mass]) }]
    # -- Theory ---------------------
    if jets == 0:
        # appendix D of https://indico.cern.ch/getFile.py/access?contribId=0&resId=0&materialId=0&confId=135333
        k0 = pow(ggH_scaErrYR[mass],     1/ggH_jets[mass]['f0'])
        k1 = pow(ggH_jets[mass]['k1'], 1-1/ggH_jets[mass]['f0']) # -f1-f2=f0-1
        nuisances['QCDscale_ggH']    = [  ['lnN'], { 'ggH':k0, 'ggH125':k0 }]
        nuisances['QCDscale_ggH1in'] = [  ['lnN'], { 'ggH':k1, 'ggH125':k1 }]
        if not qqWWfromData:
            nuisances['QCDscale_WW']    = [ ['lnN'], {'WW': 1.042 }]
            nuisances['QCDscale_WW1in'] = [ ['lnN'], {'WW': 0.978 }]
    elif jets == 1:
        k1 = pow(ggH_jets[mass]['k1'], 1+ggH_jets[mass]['f2']/ggH_jets[mass]['f1'])
        k2 = pow(ggH_jets[mass]['k2'],  -ggH_jets[mass]['f2']/ggH_jets[mass]['f1'])
        nuisances['QCDscale_ggH1in'] = [  ['lnN'], { 'ggH':k1, 'ggH125':k1 }]
        nuisances['QCDscale_ggH2in'] = [  ['lnN'], { 'ggH':k2, 'ggH125':k2 }]
        if not qqWWfromData:
            nuisances['QCDscale_WW1in'] = [ ['lnN'], {'WW': 1.076 }]
            nuisances['QCDscale_WW2in'] = [ ['lnN'], {'WW': 0.914 }]
    elif jets == 2:
        if options.VH:
            nuisances['QCDscale_ggH2in_vh'] = [  ['lnN'], { 'ggH':1.30, 'ggH125':1.30 }]
            #nuisances['QCDscale_ggH2in_vh'] = [  ['lnN'], { 'ggH':1.70 }]
        else :
            nuisances['QCDscale_ggH2in'] = [  ['lnN'], { 'ggH':ggH_jets[mass]['k2'], 'ggH125':ggH_jets[mass]['k2'] }]
        if not qqWWfromData:
            nuisances['QCDscale_WW2in'] = [ ['lnN'], {'WW': 1.210 }] # reduce by 1/2 because not applicable to vbf
            if not options.VH:
               nuisances['QCDscale_WWvbf'] = [ ['lnN'], {'WW': 1.500 }]
    nuisances['QCDscale_ggWW'] = [ ['lnN'], {'ggWW': 1.30}]
    nuisances['QCDscale_qqH']    = [ ['lnN'], { 'vbfH':vbfH_scaErrYR[mass] }]
    if mass in wzttH_scaErrYR: nuisances['QCDscale_VH']  = [ ['lnN'], { 'wzttH':wzttH_scaErrYR[mass], 'wzttH125':wzttH_scaErrYR[mass] }]
    nuisances['QCDscale_VV']     = [ ['lnN'], { 'VV':1.03 }]
    nuisances['QCDscale_VgS']    = [ ['lnN'], {'VgS':1.30 }]

    if isssactive == True :
        # -- extrapolation from same sign (ss) to opposite sign (os) region ---- 10% ? -> to be checked on data: how much is the charge misidentification difference data/MC by CMS?
        # that it may be bin dependent, ... right? One nuisance for each jet bin
        if jets == 0 :
            nuisances['ssos_extrap_VgS_0jet']    = [ ['lnN'], {'VgS':1.10 }]
            nuisances['ssos_extrap_Vg_0jet']     = [ ['lnN'], {'Vg':1.10 }]

        if jets == 1 :
            nuisances['ssos_extrap_VgS_1jet']    = [ ['lnN'], {'VgS':1.10 }]
            nuisances['ssos_extrap_Vg_1jet']     = [ ['lnN'], {'Vg':1.10 }]

    # uncertainty on H125
    #nuisances['CMS_hww_SMH125']  = [ ['lnN'], {'ggH125':1.30, 'vbfH125':1.30, 'wzttH125':1.30} ]

    # -- Experimental ---------------------
    nuisances['QCDscale_ggH_ACCEPT'] = [ ['lnN'], {'ggH':1.02, 'ggH125':1.02}]
    nuisances['QCDscale_qqH_ACCEPT'] = [ ['lnN'], {'vbfH':1.02, 'vbfH125':1.02}]
    if   jets == 0: nuisances['UEPS'] = [ ['lnN'], {'ggH':ggH_UEPS[mass]['u0'], 'ggH125':ggH_UEPS[mass]['u0']}]
    elif jets == 1: nuisances['UEPS'] = [ ['lnN'], {'ggH':ggH_UEPS[mass]['u1'], 'ggH125':ggH_UEPS[mass]['u1']}]
    elif jets == 2: nuisances['UEPS'] = [ ['lnN'], {'ggH':ggH_UEPS[mass]['u2'], 'ggH125':ggH_UEPS[mass]['u2']}]
    if ((not qqWWfromData) and (jets != 2)): nuisances['QCDscale_WW_EXTRAP'] = [ ['lnN'], {'WW':1.06}]
    # --- new ---
    # not needed with line-shape reweighting
    #nuisances['theoryUncXS_HighMH'] = [ ['lnN'], { 'ggH':1+1.5*pow(float(mass)/1000,3), 'vbfH':1+1.5*pow(float(mass)/1000,3), 'wzttH':1+1.5*pow(float(mass)/1000,3) } ]
    # -- Interference term ----------------
    if mass>=400:
        nuisances['interf_ggH'] = [ ['lnN'], {'ggH':ggH_intf[mass]['intf']}]
    else :
        nuisances['interf_ggH'] = [ ['lnN'], {'ggH':1.00}]
              
    #if options.WJsub:
    #    nuisances['CMS_FakeRate_e'] = [ ['lnN'], { 'WJet': 1.0+options.WJsub } ]
    #    nuisances['CMS_FakeRate_m'] = [ ['lnN'], { 'WJet': 1.0+options.WJsub } ]
    #elif options.WJadd:
    #    nuisances['CMS_FakeRate_e'] = [ ['lnN'], { 'WJet': 1.0+options.WJadd } ]
    #    nuisances['CMS_FakeRate_m'] = [ ['lnN'], { 'WJet': 1.0+options.WJadd } ]
    addFakeRateSyst(nuisances, mass, channel, jets, shape, suffix)

    if 'e' in channel:     nuisances['CMS'+suffix+'_eff_l'] = [ ['lnN'], dict([(p,pow(1.02,channel.count('e'))) for p in MCPROC])]
    #elif channel == 'all': nuisances['CMS_eff_l'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    #elif channel == 'sf':  nuisances['CMS_eff_l'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    #elif channel == 'of':  nuisances['CMS_eff_l'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    else :
        nuisances['CMS'+suffix+'_eff_e'] = [ ['lnN'], dict([(p,1.04) for p in MCPROC])]
        nuisances['CMS'+suffix+'_eff_m'] = [ ['lnN'], dict([(p,1.03) for p in MCPROC])]
    # just put a common one now
    if   channel == 'mumu': nuisances['CMS_p_scale_m'] = [ ['lnN'], dict([(p,1.015) for p in MCPROC if p != 'DTT'] )]
    elif channel == 'elmu': nuisances['CMS_p_scale_m'] = [ ['lnN'], dict([(p,1.015) for p in MCPROC if p != 'DTT'] )]
    elif channel == 'muel': nuisances['CMS_p_scale_e'] = [ ['lnN'], dict([(p,1.020) for p in MCPROC if p != 'DTT'] )]
    elif channel == 'elel': nuisances['CMS_p_scale_e'] = [ ['lnN'], dict([(p,1.020) for p in MCPROC if p != 'DTT'] )]
    elif channel in ['all', 'sf', 'of']: 
       nuisances['CMS'+suffix+'_p_scale_e'] = [ ['lnN'], dict([(p,1.020) for p in MCPROC if p != 'DTT'] )]
       nuisances['CMS'+suffix+'_p_scale_m'] = [ ['lnN'], dict([(p,1.015) for p in MCPROC if p != 'DTT'] )]
    nuisances['CMS'+suffix+'_met'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    nuisances['CMS'+suffix+'_p_scale_j'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    if channel == 'of':
       nuisances['CMS'+suffix+'_norm_DYof'] = [ ['lnN'], { 'DYLL':2.0 } ]
    nuisances['CMS'+suffix+'_norm_DYTT'] = [ ['lnN'], { 'DYTT':1.3 } ]
    nuisances['CMS'+suffix+'_norm_Vg']   = [ ['lnN'], { 'Vg':1.3 } ]

    return nuisances

def addFakeBackgroundSysts(nuisances, mass,channel,jets,errWW=0.2,errggWW=0.2,errDY=1.0,errTop0j=1.0,errTop1j=0.3,errWJ=0.5):
    if errWW:  nuisances['CMS_norm_WW'           ] = [ ['lnN'], { 'WW':(1+errWW)} ] 
    if errggWW:  nuisances['CMS_norm_ggWW'           ] = [ ['lnN'], { 'ggWW':(1+errggWW)} ] 
    if errTop0j and jets == 0: nuisances['CMS_norm_Top0j'] = [ ['lnN'], { 'Top':(1+errTop0j)}] 
    if errTop1j and jets == 1: nuisances['CMS_norm_Top1j'] = [ ['lnN'], { 'Top':(1+errTop1j)}] 
    if errWJ: nuisances['CMS_fake_%s'%channel[2]] = [ ['lnN'], { 'WJet':(1+errWJ) } ] 
    if errDY and channel in ['mumu', 'elel']:
        proc = "DY{0}{0}".format(channel[0].upper())
        nuisances['CMS_norm_DY_%s' % channel[0]]  = [ ['lnN'], { proc:(1+errDY) } ]

def addFakeRateSyst(nuisances, mass, channel, jets, shape, suffix=''):
    # some hard-coded numbers for now
    # define later in separate text + make it mH dependent for cut-based
    # do an asymmetric error, if possible...
    fake_m_up = 1.0
    fake_m_dn = 1.0
    fake_e_up = 1.0
    fake_e_dn = 1.0
    
    if (shape):
        if mass <= 300: 
            if jets == 0:
                fake_m_up = 0.75
                fake_m_dn = 1.18
                fake_e_up = 0.86
                fake_e_dn = 1.07
            elif jets == 1:
                fake_m_up = 0.78
                fake_m_dn = 1.13
                fake_e_up = 0.84
                fake_e_dn = 1.04
        else:
            if jets == 0:
                fake_m_up = 0.81
                fake_m_dn = 1.12
                fake_e_up = 0.73
                fake_e_dn = 1.02
            elif jets == 1:
                fake_m_up = 0.83
                fake_m_dn = 1.10
                fake_e_up = 0.76
                fake_e_dn = 1.03
    else:
        if jets == 0:
            fake_m_up = 0.69
            fake_m_dn = 1.23
            fake_e_up = 0.93
            fake_e_dn = 1.10
        elif jets == 1:
            fake_m_up = 0.71
            fake_m_dn = 1.18
            fake_e_up = 0.91
            fake_e_dn = 1.06

    nuisances['CMS'+suffix+'_hww_FakeRate']   = [ ['lnN'], { 'WJet': 1.20 } ] # from closure test
    nuisances['CMS_hww_FakeRate_m'] = [ ['lnN'], { 'WJet': (fake_m_up,fake_m_dn) } ] # from jet ET variation
    nuisances['CMS_hww_FakeRate_e'] = [ ['lnN'], { 'WJet': (fake_e_up,fake_e_dn) } ] # from jet ET variation


def floatNorm(process):
    nuisances = {}
    if process in 'WW':
        nuisances['CMS_norm_'+process] = [ ['lnU'], { 'WW':2.00, 'ggWW':2.00 } ]
    else :
        nuisances['CMS_norm_'+process] = [ ['lnU'], { process:2.00 } ]
    return nuisances
