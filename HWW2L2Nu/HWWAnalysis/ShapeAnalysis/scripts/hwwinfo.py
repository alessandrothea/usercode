import re

#  ___                         _              
# | _ \__ _ _ _ __ _ _ __  ___| |_ ___ _ _ ___
# |  _/ _` | '_/ _` | '  \/ -_)  _/ -_) '_(_-<
# |_| \__,_|_| \__,_|_|_|_\___|\__\___|_| /__/
#                                             
# channels = ['all', 'mm', 'ee', 'em', 'me', 'sf', 'of']
channels             = ['mm', 'ee', 'em', 'me']
flavors				 = dict( sf=['ee','mm'],of=['em','me'] )
# masses               = [ 110 , 115 , 120 , 130 , 140 , 150 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600]
masses               = [ 110 , 115 , 118 , 120 , 122 , 124 , 126 , 128 , 130 , 135 , 140 , 150 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600]
jets 				 = [0,1]


channelCuts = {}
channelCuts['all'] = '1'			 #'channel>-1'
channelCuts['mm']  = 'channel == 0' #'channel>-0.5 && channel<0.5'
channelCuts['ee']  = 'channel == 1' #'channel> 0.5 && channel<1.5'
channelCuts['em']  = 'channel == 2' #'channel> 1.5 && channel<2.5'
channelCuts['me']  = 'channel == 3' #'channel> 2.5 && channel<4.5'
channelCuts['sf']  = 'channel< 1.5'
channelCuts['of']  = 'channel>1.5' 

#  __  __               ___     _      
# |  \/  |__ _ ______  / __|  _| |_ ___
# | |\/| / _` (_-<_-< | (_| || |  _(_-<
# |_|  |_\__,_/__/__/  \___\_,_|\__/__/
#                                      

# old bdt cuts
# _cuts['mllmax_bdt']  = [ 50  , 60  , 70  , 80  , 90  , 100 , 100 , 100 , 110 , 120 , 130 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600  ]

# masses             = [ 110 , 115 , 118 , 120 , 122 , 124 , 126 , 128 , 130 , 135 , 140 , 150 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600]

_cuts = {}
_cuts['mllmax_bdt']  = [ 70  , 70  , 70  , 70  , 70  , 70  , 80  , 80  , 80  , 90  , 90  , 100 , 100 , 100 , 110 , 120 , 130 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600  ]
_cuts['pt1min']      = [ 20  , 20  , 20  , 20  , 21  , 22  , 23  , 24  , 25  , 25  , 25  , 27  , 30  , 34  , 36  , 38  , 40  , 55  , 70  , 80  , 90  , 110 , 120 , 130 , 140 ]
_cuts['pt2min']      = [ 10  , 10  , 10  , 10  , 10  , 10  , 10  , 10  , 10  , 12  , 15  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  ]
_cuts['mllmax']      = [ 40  , 40  , 40  , 40  , 41  , 42  , 43  , 44  , 45  , 45  , 45  , 50  , 50  , 50  , 60  , 80  , 90  , 150 , 200 , 250 , 300 , 350 , 400 , 450 , 500 ]
_cuts['dphimax']     = [ 115 , 115 , 115 , 115 , 110 , 105 , 100 , 95  , 90  , 90  , 90  , 90  , 60  , 60  , 70  , 90  , 100 , 140 , 175 , 175 , 175 , 175 , 175 , 175 , 175 ]

_cuts['dphimax']     = [ str(phi)+'*pi/180' for phi in _cuts['dphimax'] ]

_cuts['mt']          = [(80,110), (80,110), (80,115), (80,120), (80,121), (80,122), (80,123), (80,124), (80,125), (80,128), (80,130), (80,150), (90,160), (110,170), (120,180), (120,190), (120,200), (120,250), (120,300), (120,350), (120,400), (120,450), (120,500), (120,550), (120,600) ]

singleVarCuts = {}
for c,list in _cuts.iteritems():
    if len(list) != len(masses):
        raise RuntimeError('Wrong number of entries in {cut} ({list} vs. {masses})'.format( cut = c, list = len(list), masses = len(masses)) )
    singleVarCuts[c] = dict(zip(masses,list))
# cleanup
del _cuts


#  ___      _        _   _             
# / __| ___| |___ __| |_(_)___ _ _  ___
# \__ \/ -_) / -_) _|  _| / _ \ ' \(_-<
# |___/\___|_\___\__|\__|_\___/_||_/__/
#                                      

_cuts = {}
_cuts['base']       = 'trigger && nextra == 0 && mll > (12 + 8*sameflav) && (pt2 > 15 || !sameflav) && ptll > 45'
_cuts['antiZ']	    = 'pfmet > 20 && zveto && mpmet > (20+(17+nvtx/2.)*sameflav) && (dphiveto || ! sameflav)'
_cuts['antiB']	    = 'bveto_mu && bveto_ip && ( njet == 0 || (njet !=0 && nbjet==0 ) )'

# 
_cuts['WWsel']      = _cuts['base']  + ' && ' + _cuts['antiB'] + ' && ' + _cuts['antiZ']
_cuts['ctrZ']       = _cuts['base']  + ' && ' + _cuts['antiB'] + ' && pfmet > 20 && zveto && mpmet>20 && mpmet<37 && (dphiveto || ! sameflav)'
_cuts['ctrWW']      = _cuts['WWsel'] + ' && mll>100'
_cuts['ctrT']       = _cuts['base']  + ' && ' + _cuts['antiZ'] + ' && ' + '!( '+_cuts['antiB']+' )'
_cuts['massZ']      = _cuts['base']  + ' && sameflav && !zveto && mpmet>20 && mpmet<37'
_cuts['vetoZ']      = _cuts['base']  + ' && zveto && mpmet>20'


# selections = _tmpSel 
selections = _cuts 
del _cuts

def massSelections(mass):
    mthmin_bdt = 80.

    masscuts = dict([(cut,singleVarCuts[cut][mass]) for cut in singleVarCuts])
    hwwlvl = {}
    hwwlvl['mll']    = 'mll < {0}'.format(masscuts['mllmax'])
    hwwlvl['pt1']    = 'pt1 > {0:.1f}'.format(masscuts['pt1min'])
    hwwlvl['pt2']    = 'pt2 > {0:.1f}'.format(masscuts['pt2min'])
    hwwlvl['dphill'] = 'dphill < {0}'.format(masscuts['dphimax'])
    hwwlvl['mth']    = '(mth > {0:.1f} && mth < {1:.1f})'.format(masscuts['mt'][0], masscuts['mt'][1])

    sel = selections.copy()
    sel['BDT']     = 'mll < {0} && (mth > {1:.0f} && mth < {2:.0f})'.format(masscuts['mllmax_bdt'], mthmin_bdt, int(mass)) 

    sel['HWW-sel']  = sel['WWsel']+' && '+' && '.join([cut for cut in hwwlvl.itervalues()])
    sel['mll-sel']  = sel['WWsel']+' && '+' && '.join([cut for var,cut in hwwlvl.iteritems() if var != 'mll'])
    sel['mth-sel']  = sel['WWsel']+' && '+' && '.join([cut for var,cut in hwwlvl.iteritems() if var != 'mth'])
    sel['dphi-sel'] = sel['WWsel']+' && '+' && '.join([cut for var,cut in hwwlvl.iteritems() if var != 'dphill'])
    sel['gammaMRStar-sel']  = sel['WWsel']+' && '+' && '.join([cut for var,cut in hwwlvl.iteritems() if var != 'mll'])
    sel['bdtl-sel'] = sel['WWsel']+' && '+sel['BDT']
    sel['bdts-sel'] = sel['WWsel']+' && '+sel['BDT']

    sel['HWW-ctrZ']  = sel['ctrZ']+' && '+' && '.join([cut for cut in hwwlvl.itervalues()])
    sel['mll-ctrZ']  = sel['ctrZ']+' && '+' && '.join([cut for var,cut in hwwlvl.iteritems() if var != 'mll'])
    sel['mth-ctrZ']  = sel['ctrZ']+' && '+' && '.join([cut for var,cut in hwwlvl.iteritems() if var != 'mth'])
    sel['dphi-ctrZ'] = sel['ctrZ']+' && '+' && '.join([cut for var,cut in hwwlvl.iteritems() if var != 'dphill'])
    sel['gammaMRStar-ctrZ']  = sel['ctrZ']+' && '+' && '.join([cut for var,cut in hwwlvl.iteritems() if var != 'mll'])
    sel['bdtl-ctrZ'] = sel['ctrZ']+' && '+sel['BDT']
    sel['bdts-ctrZ'] = sel['ctrZ']+' && '+sel['BDT']

    # TODO gammastar test
    sel['gammaMRStar-sel']  = sel['bdts-sel']
    sel['gammaMRStar-ctrZ'] = sel['bdts-ctrZ']

    return sel



    
#  ___                  _        
# / __| __ _ _ __  _ __| |___ ___
# \__ \/ _` | '  \| '_ \ / -_|_-<
# |___/\__,_|_|_|_| .__/_\___/__/
#                 |_|            

backgrounds = {}
backgrounds['WW']               = ['latino_000_WWJets2LMad.root']
backgrounds['ggWW']             = ['latino_001_GluGluToWWTo4L.root']
backgrounds['Vg']               = ['latino_082_WgammaToElNuMad.root',
                                   'latino_083_WgammaToMuNuMad.root',
                                   'latino_084_WgammaToTauNuMad.root',
                                   'latino_085_WGstarToLNu2Mu.root',
                                   'latino_086_WGstarToLNu2E.root',
                                   ]
backgrounds['WJet']             = ['latino_WJets_Full2011.root']
backgrounds['WJetFakeRate']     = ['latino_WJets_Full2011_Mu30El15.root']
# backgrounds['WJet']      = ['latino_WJets_LP.root']
backgrounds['Top']              = ['latino_011_TtWFullDR.root',
                                   'latino_012_TbartWFullDR.root',
                                   'latino_013_TtFull.root',
                                   'latino_014_TbartFull.root',
                                   'latino_015_TsFull.root',
                                   'latino_016_TbarsFull.root',
                                   'latino_019_TTTo2L2Nu2B.root',
                                  ]
backgrounds['VV']               = ['latino_074_WZJetsMad.root',
                                   'latino_071_ZZFull.root',
                                  ]
backgrounds['DYTT']             = [ 'latino_032_DYtoTauTau.root',
                                   'latino_035_DY10toTauTau.root',
                                  ]
backgrounds['DYLL']             = ['latino_030_DYtoElEl.root',
                                   'latino_031_DYtoMuMu.root',
                                   'latino_033_DY10toElEl.root',
                                   'latino_034_DY10toMuMu.root',
                                  ]
backgrounds['DYLLtemplate']     = ['latino_030_DYtoElEl_pfmet20.root',
                                   'latino_031_DYtoMuMu_pfmet20.root',
                                   'latino_033_DY10toElEl_pfmet20.root',
                                   'latino_034_DY10toMuMu_pfmet20.root',
                                  ]
backgrounds['DYLLtemplatesyst'] = ['latino_030_DYtoElEl_pfmet20jet40.root',
                                   'latino_031_DYtoMuMu_pfmet20jet40.root',
                                   'latino_033_DY10toElEl_pfmet20jet40.root',
                                   'latino_034_DY10toMuMu_pfmet20jet40.root',
                                  ]
backgrounds['WWnlo']            = ['latino_002_WWto2L2NuMCatNLO.root']
backgrounds['WWnloUp']          = ['latino_003_WWto2L2NuMCatNLOUp.root']
backgrounds['WWnloDown']        = ['latino_004_WWto2L2NuMCatNLODown.root']

data = {}
data['Data2011A'] = [
    'latino_150_SingleElectron2011AMay10.root',
    'latino_151_SingleMuon2011AMay10.root',
    'latino_152_DoubleMuon2011AMay10.root',
    'latino_153_DoubleElectron2011AMay10.root',
    'latino_154_MuEG2011AMay10.root',

    'latino_100_SingleElectron2011Av4.root',
    'latino_101_SingleMuon2011Av4.root',
    'latino_102_DoubleElectron2011Av4.root',
    'latino_103_DoubleMuon2011Av4.root',
    'latino_104_MuEG2011Av4.root',

    'latino_160_SingleElectron2011AAug05.root',
    'latino_161_SingleMuon2011AAug05.root',
    'latino_162_DoubleElectron2011AAug05.root',
    'latino_163_DoubleMuon2011AAug05.root',
    'latino_164_MuEG2011AAug05.root',

    'latino_120_SingleElectron2011Av6.root',
    'latino_121_SingleMuon2011Av6.root',
    'latino_122_DoubleElectron2011Av6.root',
    'latino_123_DoubleMuon2011Av6.root',
    'latino_124_MuEG2011Av6.root',

]

data['Data2011B'] = [
    'latino_140_SingleElectron2011Bv1a.root',
    'latino_141_SingleMuon2011Bv1a.root',
    'latino_142_DoubleElectron2011Bv1a.root',
    'latino_143_DoubleMuon2011Bv1a.root',
    'latino_144_MuEG2011Bv1a.root',

]
data['Data2011'] =  data['Data2011A']+data['Data2011B']

def signalSamples(mass):
    signals = {}
    ggH = ['latino_1{mass}_ggToH{mass}toWWto2L2Nu.root',
           'latino_2{mass}_ggToH{mass}toWWtoLNuTauNu.root',
           'latino_3{mass}_ggToH{mass}toWWto2Tau2Nu.root',
          ]
    ggHnew = ['latino_9{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root']
    vbfH   = ['latino_4{mass}_vbfToH{mass}toWWto2L2Nu.root', 
              'latino_5{mass}_vbfToH{mass}toWWtoLNuTauNu.root',
              'latino_6{mass}_vbfToH{mass}toWWto2Tau2Nu.root', 
             ]
    vbfHnew = ['latino_8{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root']
    wzttH   = ['latino_7{mass}_wzttH{mass}ToWW.root']

    if int(mass)==122:
        signals['ggH']  = [f.format(mass = mass) for f in ggHnew]
        signals['wzttH'] = [f.format(mass = mass) for f in wzttH]
    elif int(mass)==118 or (int(mass)>120 and int(mass)<130) or int(mass)==135:
        signals['ggH']  = [f.format(mass = mass) for f in ggHnew]
        signals['vbfH'] = [f.format(mass = mass) for f in vbfHnew]
        signals['wzttH'] = [f.format(mass = mass) for f in wzttH]
    elif int(mass) > 115:
        signals['ggH']  = [f.format(mass = mass) for f in ggH]
        signals['vbfH'] = [f.format(mass = mass) for f in vbfH]
        signals['wzttH'] = [f.format(mass = mass) for f in wzttH]
    else:
        signals['ggH']  = ['latino_9{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root'.format(mass = mass)]
        signals['vbfH'] = ['latino_8{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root'.format(mass = mass)]

    return signals

    
def samples(mass, datatag='Data2011'):
    '''
    mass: mass for the higgs samples'
    datatag: tag for the dataset to be included
    '''
    samples = {}
    signals = signalSamples(mass)
    samples.update(signals)
    samples.update(backgrounds)
    if 'Data' in datatag:
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

    return samples


import os.path

def loadOptDefaults(parser,rc='shape.rc'):
    if not os.path.exists(rc):
        print rc,'not found'
        return

    f = open(rc)
    for line in f:
        if line[0] == '#':
            continue
        tokens = line.split(':')
        if len(tokens) < 2:
            continue
        opt_name = tokens[0]
        opt_longname = '--'+tokens[0]
        if parser.has_option(opt_longname):
            value = line[line.index(':')+1:-1]
            o = parser.get_option(opt_longname)
            o.default = value
            parser.defaults[opt_name] = value

            print ' - new default value:',opt_name,'=',value

            

def addOptions(parser):
    parser.add_option('-l', '--lumi', dest='lumi', type='float', help='Luminosity', default=None)
    parser.add_option('-v', '--var',  dest='var',  help='variable', default=None)
    parser.add_option('-m', '--mass', dest='mass', type='int', help='run on one mass point only ', default=0)
 
