import re
import HWWAnalysis.Misc.odict as odict

#  ___                         _              
# | _ \__ _ _ _ __ _ _ __  ___| |_ ___ _ _ ___
# |  _/ _` | '_/ _` | '  \/ -_)  _/ -_) '_(_-<
# |_| \__,_|_| \__,_|_|_|_\___|\__\___|_| /__/
#                                             
# flavors             = ['mm', 'ee', 'em', 'me']
# flavors				 = dict( sf=['ee','mm'],of=['em','me'] )
# masses               = [ 110 , 115 , 118 , 120 , 122 , 124 , 126 , 128 , 130 , 135 , 140 , 150 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600]
# jets 				 = [0,1]

class wwcutsB:
    wwcommon = odict.OrderedDict([
        ('trigger',                'trigger==1.'),
        ('min #slash{E}_{T}',      'pfmet>20.'),
        ('m_{ll}',                 'mll>12'),                       # ema7
        ('Z_{veto}',               '(zveto==1||!sameflav)'),
        ('min proj #slash{E}_{T}', 'mpmet>20.'),                    # ema9
        ('Soft #mu veto',          'bveto_mu==1'),
        ('Extra Lepton',           'nextra==0'),
        ('B veto',                 '(bveto_ip==1 && (nbjettche==0 || njet>3)  )'),
        ('p_{T}^{ll}',             'ptll>45.'),                     # ema 14
        ('Extra Jet',              'njet<4'),
    ])

    wwmin = odict.OrderedDict([
        ('trigger',                'trigger==1.'),
        ('min #slash{E}_{T}',      'pfmet>20.'),
        ('m_{ll}',                 'mll>12'),                       # ema7
        ('min proj #slash{E}_{T}', 'mpmet>20.'),                    # ema9
        ('Soft #mu veto',          'bveto_mu==1'),
        ('Extra Lepton',           'nextra==0'),
        ('Extra Jet',              'njet<4'),
    ])

    #dy cuts
    dphilljj   = '(njet==0 || njet==1 || (dphilljetjet<pi/180.*165. || !sameflav )  )'

    # met cuts 
    met  = '( !sameflav || ( (njet!=0 || dymva1>0.88) && (njet!=1 || dymva1>0.84) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) )'

    wwcommon.update([
        ('d#Phi_{lljj}', dphilljj),
        ('dymva',        met),
    ])
    
    wwmin.update([
        ('d#Phi_{lljj}', dphilljj),
    ])
        
    zerojet = 'njet == 0'
    onejet  = 'njet == 1'
    vbf     = '(njet >= 2 && njet <= 3 && (jetpt3 <= 30 || !(jetpt3 > 30 && (  (jeteta1-jeteta3 > 0 && jeteta2-jeteta3 < 0) || (jeteta2-jeteta3 > 0 && jeteta1-jeteta3 < 0))))) '


class wwcuts:
    wwcommon = [
        'trigger==1.',
        'pfmet>20.',
        'mll>12',                       # ema7
        '(zveto==1||!sameflav)',
        'mpmet>20.',                    # ema9
        'bveto_mu==1',
        'nextra==0',
        '(bveto_ip==1 && (nbjettche==0 || njet>3)  )',
        'ptll>45.',                     # ema 14
    ]

    # minimum for skimming
    wwmin = [
        'trigger==1',
        'pfmet>20',
        'mll>12',
        'mpmet>20',
        'bveto_mu==1',
        'nextra==0',
        'njet<4',
    ]
    
    #dy cuts
    dphilljj   = '(njet==0 || njet==1 || (dphilljetjet<pi/180.*165. || !sameflav )  )'

    # met cuts
    met  = '( !sameflav || ( (njet!=0 || dymva1>0.88) && (njet!=1 || dymva1>0.84) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) )'

    wwcommon = wwcommon+[dphilljj, met]
    wwmin    = wwmin   +[dphilljj]
    
    zerojet = 'njet == 0'
    onejet  = 'njet == 1'
    vbf     = '(njet >= 2 && njet <= 3 && (jetpt3 <= 30 || !(jetpt3 > 30 && (  (jeteta1-jeteta3 > 0 && jeteta2-jeteta3 < 0) || (jeteta2-jeteta3 > 0 && jeteta1-jeteta3 < 0))))) '

# da rifare
class vbfcuts:
    _massindep = [
        'abs(eta1 - (jeteta1+jeteta2)/2)/detajj < 0.5',
        'abs(eta2 - (jeteta1+jeteta2)/2)/detajj < 0.5',
    ]

    _cut   = [
        'detajj>3.5',
        'mjj>500',
    ]
    _shape = [
        'detajj>3.',
        'mjj>200',
    ]

#     vbflocut   = wwcuts.wwlo+_massindep+_cut
#     vbfhicut   = wwcuts.wwhi+_massindep+_cut
    vbfcut     = wwcuts.wwcommon+_massindep+_cut
    #vbfshape   = wwcuts.wwcommon+_massindep+_shape
    #vbfloshape = wwcuts.wwlo+_massindep+_shape
    #vbfhishape = wwcuts.wwhi+_massindep+_shape

    vbfshape = ['trigger==1. && pfmet>20. && mll>12 && zveto==1 && mpmet>20. && (njet==0 || njet==1 || (dphilljetjet<pi/180.*165. || !sameflav )  ) && bveto_mu==1 && nextra==0 && (bveto_ip==1 &&  (nbjettche==0 || njet>3))  && ptll>45. &&   ( !sameflav || ( (njet!=0 || dymva1>0.88) && (njet!=1 || dymva1>0.84) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) ) && (njet>=2 && njet<=3 && (jetpt3<=30 || !(jetpt3 > 30 && (  (jeteta1-jeteta3 > 0 && jeteta2-jeteta3 < 0) || (jeteta2-jeteta3 > 0 && jeteta1-jeteta3 < 0)))))   && abs(eta1 - (jeteta1+jeteta2)/2)/detajj < 0.5 && abs(eta2 - (jeteta1+jeteta2)/2)/detajj < 0.5      && detajj>3.5     && mjj>500']

    specificvbfloshape = ['pt1>20   &&      pt2>0   &&      mth>30  &&  mth<280      &&    mll<200 ']
    specificvbfhishape = ['pt1>50   &&      pt2>0   &&      mth>30  &&  mth<680      &&    mll<600 ']

    vbfloshape = vbfshape + specificvbfloshape
    vbfhishape = vbfshape + specificvbfhishape




masses = [110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 170, 180, 190, 200, 250, 300, 350, 400, 450, 500, 550, 600]

class Category:
    def __init__(self,name,cut,nick):
        self.name = name
        self.cut  = cut
        self.nick = nick

categories = {}
categories['0j'] = Category('0j',wwcuts.zerojet,'0jet')
categories['1j'] = Category('1j',wwcuts.onejet, '1jet')
categories['2j'] = Category('2j',wwcuts.vbf,    'vbf')

flavorCuts = {}
flavorCuts['all'] = '1'			       #'channel>-1'
flavorCuts['mm']  = 'channel == 0'     #'channel>-0.5 && channel<0.5'
flavorCuts['ee']  = 'channel == 1'     #'channel> 0.5 && channel<1.5'
flavorCuts['em']  = 'channel == 2'     #'channel> 1.5 && channel<2.5'
flavorCuts['me']  = 'channel == 3'     #'channel> 2.5 && channel<4.5'
flavorCuts['sf']  = 'channel < 1.5'
flavorCuts['of']  = 'channel > 1.5' 

flavors = {}
flavors['sf']=['mm','ee']
flavors['of']=['em','me']
flavors['ll']=['mm','ee','em','me']

channels = {}
channels['0j']    = ('0j','ll')#,['mm','ee','em','me'])
channels['1j']    = ('1j','ll')#,['mm','ee','em','me'])
channels['of_0j'] = ('0j','of')#,['em','me'])
channels['of_1j'] = ('1j','of')#,['em','me'])
channels['sf_0j'] = ('0j','sf')#,['mm','ee'])
channels['sf_1j'] = ('1j','sf')#,['mm','ee'])

channels['2j']    = ('2j','ll')#,['mm','ee','em','me'])
channels['of_2j'] = ('2j','of')#,['em','me'])
channels['sf_2j'] = ('2j','sf')#,['mm','ee'])

#  __  __               ___     _      
# |  \/  |__ _ ______  / __|  _| |_ ___
# | |\/| / _` (_-<_-< | (_| || |  _(_-<
# |_|  |_\__,_/__/__/  \___\_,_|\__/__/
#
# smurfs index              1     1     3     6     8     9    10    10    11    11    12    13    14    15    16   20     21    22    23    24    25    26    27
# masses              = [ 110 , 115 , 120 , 125 , 130 , 135 , 140 , 145 , 150 , 155 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600]
cutmap = {}                                                                     
cutmap['mllmax_bdt']  = [ 70  , 70  , 70  , 80  , 80  , 90  , 90  , 100 , 100 , 100 , 100 , 100 , 110 , 120 , 130 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600 ]
cutmap['pt1min']      = [ 20  , 20  , 20  , 23  , 25  , 25  , 25  , 25  , 27  , 27  , 30  , 34  , 36  , 38  , 40  , 55  , 70  , 80  , 90  , 110 , 120 , 130 , 140 ]
cutmap['pt2min']      = [ 10  , 10  , 10  , 10  , 10  , 12  , 15  , 15  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  ]
cutmap['mllmax']      = [ 40  , 40  , 40  , 43  , 45  , 45  , 45  , 45  , 50  , 50  , 50  , 50  , 60  , 80  , 90  , 150 , 200 , 250 , 300 , 350 , 400 , 450 , 500 ]
cutmap['dphimax']     = [ 115 , 115 , 115 , 100 , 90  , 90  , 90  , 90  , 90  , 90  , 60  , 60  , 70  , 90  , 100 , 140 , 175 , 175 , 175 , 175 , 175 , 175 , 175 ]

cutmap['mtmin']       = [ 80  , 80  , 80  , 80  , 80  , 80  , 80  , 80  , 80  , 80  , 90  , 110 , 120 , 120 , 120 , 120 , 120 , 120 , 120 , 120 , 120 , 120 , 120 ]
cutmap['mtmax']       = [ 110 , 110 , 120 , 123 , 125 , 128 , 130 , 140 , 150 , 155 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600 ]

# automatic conversion to radiants
cutmap['dphimax']     = [ str(phi)+'*pi/180' for phi in cutmap['dphimax'] ]

massDependantCutsbyVar = {}
for c,list in cutmap.iteritems():
    if len(list) != len(masses):
        raise RuntimeError('Wrong number of entries in {cut} ({list} vs. {masses})'.format( cut = c, list = len(list), masses = len(masses)) )
    massDependantCutsbyVar[c] = dict(zip(masses,list))
# cleanup
del cutmap
del c
del list
del phi



#  ___      _        _   _             
# / __| ___| |___ __| |_(_)___ _ _  ___
# \__ \/ -_) / -_) _|  _| / _ \ ' \(_-<
# |___/\___|_\___\__|\__|_\___/_||_/__/
#                                      

def massSelections(mass):

    mthmin_bdt = 80.
    mthmin_vbf = 30.
    masscuts = dict([(cut,massDependantCutsbyVar[cut][mass]) for cut in massDependantCutsbyVar])

    sel = {}
    sel['ww-min']       = ' && '.join(wwcuts.wwmin)
    sel['ww-common']    = ' && '.join(wwcuts.wwcommon)

    sel['vbf-shape-2d-himass']    = ' && '.join(vbfcuts.vbfhishape)
    sel['vbf-shape-2d-lomass']    = ' && '.join(vbfcuts.vbfloshape)
    sel['vbf-shape-2d']           = sel['vbf-shape-2d-lomass'] if mass <= 250 else sel['vbf-shape-2d-himass'] 
    
    sel['shape-lomass'] = 'mth>80 && mth<280 && mll<200'
    sel['shape-himass'] = 'mth>80 && mth<380 && mll<450 && pt1>50'
    
    sel['vbf-shape']    = ' && '.join(vbfcuts.vbfshape)
    sel['vbf-level']    = ' && '.join(vbfcuts.vbfcut)

    sel['ww-level']     = sel['ww-common']
    sel['bdt-specific'] = 'mll < {0} && (mth > {1:.0f} && mth < {2:.0f})'.format(masscuts['mllmax_bdt'], mthmin_bdt, int(mass))

    hwwlvl = {}
    hwwlvl['mll']    = 'mll < {0}'.format(masscuts['mllmax'])
    hwwlvl['pt1']    = 'pt1 > {0:.1f}'.format(masscuts['pt1min'])
    hwwlvl['pt2']    = 'pt2 > {0:.1f}'.format(masscuts['pt2min'])
    hwwlvl['dphill'] = 'dphill < {0}'.format(masscuts['dphimax'])
    hwwlvl['mth']    = '(mth > {0:.1f} && mth < {1:.1f})'.format(masscuts['mtmin'], masscuts['mtmax'])

    sel['ww-selection']           = sel['ww-level']
    sel['wwtight-selection']      = sel['ww-level']+' && mth > 80'
    sel['wwloose-selection']      = sel['ww-level'].replace('ptll>45','ptll>20')+' && mth > 80'
    sel['hww-selection']          = ' && '.join([sel['ww-level']]+[cut for cut     in hwwlvl.itervalues()])
    sel['mll-selection']          = ' && '.join([sel['ww-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'mll'])
    sel['mth-selection']          = ' && '.join([sel['ww-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'mth'])
    sel['dphi-selection']         = ' && '.join([sel['ww-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'dphill'])
    sel['gammaMRStar-selection']  = ' && '.join([sel['ww-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'mll'])
    sel['bdt-selection']          = sel['ww-level']+' && '+sel['bdt-specific']
    sel['bdtl-selection']         = sel['bdt-selection']
    sel['vbf-shape-2d-selection']         = sel['vbf-shape-2d']

    #sel['vbf-selection']          = sel['vbf-shape']+' && (mth > 50 && mth < {0:.0f})'.format(int(mass))
    #sel['vbf-selection']          = sel['vbf-shape']+' && (mth > 50 && mth < {0:.0f}) && mll > {0:.0f}    {0:.0f} {1:.0f} '.format(int(mass), float(12452))
    sel['vbf-selection']          = ' && '.join([sel['vbf-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'mth'])
    sel['vbf-selection']          = sel['vbf-selection'] + ' && (mth > {0:.1f} && mth < {1:.1f})'.format(mthmin_vbf, int(mass))
    sel['shape-selection']        = sel['ww-level']+' && '+sel['shape-lomass'] if mass <=250 else sel['ww-level']+' && '+sel['shape-himass']
 
    #sel['vbf-selection']          = sel['vbf-shape']+' && (mth > 50 && mth < {0:.0f})'.format(int(mass))

    # TODO gammastar test
#     sel['gammaMRStar-selection']  = sel['bdt-selection']

    return sel

