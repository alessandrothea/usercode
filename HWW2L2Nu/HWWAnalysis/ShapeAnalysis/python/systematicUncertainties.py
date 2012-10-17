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

ggH_pdfErrYR   = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_ggH.items()] )
ggH_scaErrYR   = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_ggH.items()] )
vbfH_pdfErrYR  = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_vbfH.items()] )
vbfH_scaErrYR  = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_vbfH.items()] )
wzttH_pdfErrYR = dict([(m, sqrt((1+0.01*pdf_hi)/(1+0.01*pdf_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_wzttH.items()] )
wzttH_scaErrYR = dict([(m, sqrt((1+0.01*sca_hi)/(1+0.01*sca_lo))) for m,(xs,xs_hi,xs_lo,sca_hi,sca_lo,pdf_hi,pdf_lo) in YR_wzttH.items()] )

for X in 450, 550:
    ggH_pdfErrYR[X]  = 0.5*(ggH_pdfErrYR[X-10] +ggH_pdfErrYR[X+10])
    ggH_scaErrYR[X]  = 0.5*(ggH_scaErrYR[X-10] +ggH_scaErrYR[X+10])
    vbfH_pdfErrYR[X] = 0.5*(vbfH_pdfErrYR[X-10]+vbfH_pdfErrYR[X+10])
    vbfH_scaErrYR[X] = 0.5*(vbfH_scaErrYR[X-10]+vbfH_scaErrYR[X+10])

ggH_jets = dict([(m, dict(zip(['f0','f1','f2','k1','k2'], vals))) for m,vals in file2map(SYST_PATH+"ggH_jetBins.txt").items()]) 


def getCommonSysts(mass,channel,jets,qqWWfromData,options):
    nuisances = {} 
    #MCPROC = ['ggH', 'vbfH', 'DTT', 'ggWW', 'VV', 'Vg' ]; 
    MCPROC = ['ggH', 'vbfH', 'wzttH', 'DYTT', 'VV', 'Vg' ]; 
    if channel == 'elmu' or channel == 'muel': MCPROC+=['DYMM','DYEE']
    if channel == 'of': MCPROC += ['DYLL']
    if not qqWWfromData: MCPROC+=['WW','ggWW']
    # -- Luminosity ---------------------
    nuisances['lumi'] = [ ['lnN'], dict([(p,1.044) for p in MCPROC])]
    # -- PDF ---------------------
    #nuisances['pdf_gg']    = [ ['lnN'], { 'ggH':ggH_pdfErrYR[mass], 'ggWW':(1.00 if qqWWfromData else 1.04) }]
    nuisances['pdf_gg']    = [ ['lnN'], { 'ggH':ggH_pdfErrYR[mass], 'ggWW':1.04 }]
    nuisances['pdf_qqbar'] = [ ['lnN'], { 'wzttH':vbfH_pdfErrYR[mass], 'vbfH':vbfH_pdfErrYR[mass], 'VV':1.04, 'WW':(1.0 if qqWWfromData else 1.04) }]
    # -- Theory ---------------------
    if jets == 0:
        # appendix D of https://indico.cern.ch/getFile.py/access?contribId=0&resId=0&materialId=0&confId=135333
        k0 = pow(ggH_scaErrYR[mass],     1/ggH_jets[mass]['f0'])
        k1 = pow(ggH_jets[mass]['k1'], 1-1/ggH_jets[mass]['f0']) # -f1-f2=f0-1
        nuisances['QCDscale_ggH']    = [  ['lnN'], { 'ggH':k0 }]
        nuisances['QCDscale_ggH1in'] = [  ['lnN'], { 'ggH':k1 }]
        if not qqWWfromData:
            nuisances['QCDscale_WW']    = [ ['lnN'], {'WW': 1.042 }]
            nuisances['QCDscale_WW1in'] = [ ['lnN'], {'WW': 0.978 }]
    elif jets == 1:
        k1 = pow(ggH_jets[mass]['k1'], 1+ggH_jets[mass]['f2']/ggH_jets[mass]['f1'])
        k2 = pow(ggH_jets[mass]['k2'],  -ggH_jets[mass]['f2']/ggH_jets[mass]['f1'])
        nuisances['QCDscale_ggH1in'] = [  ['lnN'], { 'ggH':k1 }]
        nuisances['QCDscale_ggH2in'] = [  ['lnN'], { 'ggH':k2 }]
        if not qqWWfromData:
            nuisances['QCDscale_WW1in'] = [ ['lnN'], {'WW': 1.076 }]
            nuisances['QCDscale_WW2in'] = [ ['lnN'], {'WW': 0.914 }]
    elif jets == 2:
        nuisances['QCDscale_ggH2in'] = [  ['lnN'], { 'ggH':ggH_jets[mass]['k2'] }]
        if not qqWWfromData:
            nuisances['QCDscale_WW2in'] = [ ['lnN'], {'WW': 1.210 }] # reduce by 1/2 because not applicable to vbf
            nuisances['QCDscale_WWvbf'] = [ ['lnN'], {'WW': 1.500 }]
    nuisances['QCDscale_ggWW'] = [ ['lnN'], {'ggWW': 1.30}]
    nuisances['QCDscale_qqH']    = [ ['lnN'], { 'vbfH':vbfH_scaErrYR[mass] }]
    if mass in wzttH_scaErrYR: nuisances['QCDscale_VH']  = [ ['lnN'], { 'wzttH':wzttH_scaErrYR[mass] }]
    nuisances['QCDscale_VV']     = [ ['lnN'], { 'VV':1.03 }]
    nuisances['QCDscale_Vg'] = [ ['lnN'], {'Vg':1.30}]

    # -- Experimental ---------------------
    nuisances['QCDscale_ggH_ACCEPT'] = [ ['lnN'], {'ggH':1.02}]
    nuisances['QCDscale_qqH_ACCEPT'] = [ ['lnN'], {'vbfH':1.02}]
    if   jets == 0: nuisances['UEPS'] = [ ['lnN'], {'ggH':0.943}]
    elif jets == 1: nuisances['UEPS'] = [ ['lnN'], {'ggH':1.084}]
    elif jets == 2: nuisances['UEPS'] = [ ['lnN'], {'ggH':1.138}]
    if ((not qqWWfromData) and (jets != 2)): nuisances['QCDscale_WW_EXTRAP'] = [ ['lnN'], {'WW':1.06}]
    # --- new ---
    # not needed with line-shape reweighting
    #nuisances['theoryUncXS_HighMH'] = [ ['lnN'], { 'ggH':1+1.5*pow(float(mass)/1000,3), 'vbfH':1+1.5*pow(float(mass)/1000,3), 'wzttH':1+1.5*pow(float(mass)/1000,3) } ]
    if options.WJsub:
        nuisances['FakeRate'] = [ ['lnN'], { 'WJet': 1.0+options.WJsub } ] 
    elif options.WJadd:
        nuisances['FakeRate'] = [ ['lnN'], { 'WJet': 1.0+options.WJadd } ] 
    if 'e' in channel:     nuisances['CMS_eff_l'] = [ ['lnN'], dict([(p,pow(1.02,channel.count('e'))) for p in MCPROC])]
    #elif channel == 'all': nuisances['CMS_eff_l'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    #elif channel == 'sf':  nuisances['CMS_eff_l'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    #elif channel == 'of':  nuisances['CMS_eff_l'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    else :
        nuisances['CMS_eff_e'] = [ ['lnN'], dict([(p,1.04) for p in MCPROC])]
        nuisances['CMS_eff_m'] = [ ['lnN'], dict([(p,1.03) for p in MCPROC])]  
    # just put a common one now
    if   channel == 'mumu': nuisances['CMS_p_scale_m'] = [ ['lnN'], dict([(p,1.015) for p in MCPROC if p != 'DTT'] )]
    elif channel == 'elmu': nuisances['CMS_p_scale_m'] = [ ['lnN'], dict([(p,1.015) for p in MCPROC if p != 'DTT'] )]
    elif channel == 'muel': nuisances['CMS_p_scale_e'] = [ ['lnN'], dict([(p,1.020) for p in MCPROC if p != 'DTT'] )]
    elif channel == 'elel': nuisances['CMS_p_scale_e'] = [ ['lnN'], dict([(p,1.020) for p in MCPROC if p != 'DTT'] )]
    elif channel in ['all', 'sf', 'of']: 
        nuisances['CMS_p_scale_e'] = [ ['lnN'], dict([(p,1.020) for p in MCPROC if p != 'DTT'] )]
        nuisances['CMS_p_scale_m'] = [ ['lnN'], dict([(p,1.015) for p in MCPROC if p != 'DTT'] )]
    nuisances['CMS_met'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    nuisances['CMS_p_scale_j'] = [ ['lnN'], dict([(p,1.02) for p in MCPROC])]
    if channel == 'of':
       nuisances['CMS_norm_DYof'] = [ ['lnN'], { 'DYLL':2.0 } ]
    nuisances['CMS_norm_DYTT'] = [ ['lnN'], { 'DYTT':1.3 } ]

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

