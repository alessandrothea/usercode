import re

#  ___                         _              
# | _ \__ _ _ _ __ _ _ __  ___| |_ ___ _ _ ___
# |  _/ _` | '_/ _` | '  \/ -_)  _/ -_) '_(_-<
# |_| \__,_|_| \__,_|_|_|_\___|\__\___|_| /__/
#                                             
# flavors             = ['mm', 'ee', 'em', 'me']
# flavors				 = dict( sf=['ee','mm'],of=['em','me'] )
# masses               = [ 110 , 115 , 118 , 120 , 122 , 124 , 126 , 128 , 130 , 135 , 140 , 150 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600]
# jets 				 = [0,1]

#lowmass
# 'trigger==1.'
# 'pfmet>20.'
# 'mll>12'
# 'zveto==1'
# 'mpmet>20.'
# '(njet==0 || njet==1 || (dphilljetjet<pi/180.*165. || !sameflav )  )'
# 'bveto_mu==1'
# 'nextra==0'
# '(bveto_ip==1 &&  (nbjettche==0 || njet>3))'
# 'ptll>45.'
# '( !sameflav || ( (njet!=0 || dymva1>0.60) && (njet!=1 || dymva1>0.30) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) )' 

# highmass
# 'trigger==1.'
# 'pfmet>20.'
# 'mll>12'
# 'zveto==1'
# 'mpmet>20.'
# '((njet<=1 && dphiveto) || (njet>1 && dphilljetjet<pi/180.*165.) || !sameflav )'
# 'bveto_mu==1'
# 'nextra==0'
# ' (bveto_ip==1 &&  (nbjettche==0 || njet>3))'
# 'ptll>45.'
# '( !sameflav || ( (njet>1 || mpmet>45) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) ) '

class wwcuts:
    wwcommon = [
        'trigger==1.',
        'pfmet>20.',
        'mll>12',                       # ema7
        '(zveto==1||!sameflav)',
        'mpmet>20.',                    # ema9
#         '((njet<=1 && dphiveto) || (njet>1 && dphilljetjet<pi/180.*165.) || !sameflav )', #ema 10
        'bveto_mu==1',
        'nextra==0',
        '(bveto_ip==1 && (nbjettche==0 || njet>3)  )',
        'ptll>45.',                     # ema 14
    ]

    dylo   = '(njet==0 || njet==1 || (dphilljetjet<pi/180.*165. || !sameflav )  )'
    dyhi   = '((njet<=1 && dphiveto) || (njet>1 && dphilljetjet<pi/180.*165.) || !sameflav )'

    # met cuts lo: <=140 GeV, hi > 140 GeV
    metlo  = '( !sameflav || ( (njet!=0 || dymva1>0.60) && (njet!=1 || dymva1>0.30) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) )'
    methi  = ''+'( !sameflav || ( (njet!=0 || mpmet>45.0) && (njet!=1 || mpmet>45.0) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) )'

    wwlo    = wwcommon+[dylo,metlo]
    wwhi    = wwcommon+[dyhi,methi]

    zerojet = 'njet == 0'
    onejet  = 'njet == 1'
    vbf     = '(njet >= 2 && njet <= 3 && (jetpt3 <= 30 || !(jetpt3 > 30 && (  (jeteta1-jeteta3 > 0 && jeteta2-jeteta3 < 0) || (jeteta2-jeteta3 > 0 && jeteta1-jeteta3 < 0))))) '



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
flavorCuts['all'] = '1'			   #'channel>-1'
flavorCuts['mm']  = 'channel == 0' #'channel>-0.5 && channel<0.5'
flavorCuts['ee']  = 'channel == 1' #'channel> 0.5 && channel<1.5'
flavorCuts['em']  = 'channel == 2' #'channel> 1.5 && channel<2.5'
flavorCuts['me']  = 'channel == 3' #'channel> 2.5 && channel<4.5'
flavorCuts['sf']  = 'channel < 1.5'
flavorCuts['of']  = 'channel > 1.5' 

channels = {}
channels['0j']    = ('0j',['mm','ee','em','me'])
channels['1j']    = ('1j',['mm','ee','em','me'])
channels['of_0j'] = ('0j',['em','me'])
channels['of_1j'] = ('1j',['em','me'])
channels['sf_0j'] = ('0j',['mm','ee'])
channels['sf_1j'] = ('1j',['mm','ee'])
channels['of_0j'] = ('0j',['em','me'])
channels['2j']    = ('2j',['mm','ee','em','me'])

# here we could do something like 
#  def cathegories + cuts
#  def di-flavors + cuts
#  def channels as combinations of cats and flavs, then derive the cut from there

#  __  __               ___     _      
# |  \/  |__ _ ______  / __|  _| |_ ___
# | |\/| / _` (_-<_-< | (_| || |  _(_-<
# |_|  |_\__,_/__/__/  \___\_,_|\__/__/
#                                      

# # masses                = [ 110 , 115 , 118 , 120 , 122 , 124 , 126 , 128 , 130 , 135 , 140 , 150 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600]
# shapecuts = {}
# shapecuts['mllmax_bdt']  = [ 70  , 70  , 70  , 70  , 70  , 70  , 80  , 80  , 80  , 90  , 90  , 100 , 100 , 100 , 110 , 120 , 130 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600 ]
# shapecuts['pt1min']      = [ 20  , 20  , 20  , 20  , 21  , 22  , 23  , 24  , 25  , 25  , 25  , 27  , 30  , 34  , 36  , 38  , 40  , 55  , 70  , 80  , 90  , 110 , 120 , 130 , 140 ]
# shapecuts['pt2min']      = [ 10  , 10  , 10  , 10  , 10  , 10  , 10  , 10  , 10  , 12  , 15  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  ]
# shapecuts['mllmax']      = [ 40  , 40  , 40  , 40  , 41  , 42  , 43  , 44  , 45  , 45  , 45  , 50  , 50  , 50  , 60  , 80  , 90  , 150 , 200 , 250 , 300 , 350 , 400 , 450 , 500 ]
# shapecuts['dphimax']     = [ 115 , 115 , 115 , 115 , 110 , 105 , 100 , 95  , 90  , 90  , 90  , 90  , 60  , 60  , 70  , 90  , 100 , 140 , 175 , 175 , 175 , 175 , 175 , 175 , 175 ]
# # automatic conversion to radiants
# shapecuts['dphimax']     = [ str(phi)+'*pi/180' for phi in shapecuts['dphimax'] ]

# shapecuts['mt']          = [(80,110), (80,110), (80,115), (80,120), (80,121), (80,122), (80,123), (80,124), (80,125), (80,128), (80,130), (80,150), (90,160), (110,170), (120,180), (120,190), (120,200), (120,250), (120,300), (120,350), (120,400), (120,450), (120,500), (120,550), (120,600) ]


# masses                = [ 110 , 115 , 120 , 125 , 130 , 135 , 140 , 145 , 150 , 155 , 160 , 170 , 180 , 190 , 200 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600]
cutmap = {}                                                                     
cutmap['mllmax_bdt']  = [ 70  , 70  , 70  , 70  , 80  , 90  , 90  , 100 , 100 , 100 , 100 , 100 , 110 , 120 , 130 , 250 , 300 , 350 , 400 , 450 , 500 , 550 , 600 ]
cutmap['pt1min']      = [ 20  , 20  , 20  , 20  , 25  , 25  , 25  , 25  , 27  , 27  , 30  , 34  , 36  , 38  , 40  , 55  , 70  , 80  , 90  , 110 , 120 , 130 , 140 ]
cutmap['pt2min']      = [ 10  , 10  , 10  , 10  , 10  , 12  , 15  , 15  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  , 25  ]
cutmap['mllmax']      = [ 40  , 40  , 40  , 43  , 45  , 45  , 45  , 48  , 50  , 50  , 50  , 50  , 60  , 80  , 90  , 150 , 200 , 250 , 300 , 350 , 400 , 450 , 500 ]
cutmap['dphimax']     = [ 115 , 115 , 115 , 103 , 90  , 90  , 90  , 90  , 90  , 90  , 60  , 60  , 70  , 90  , 100 , 140 , 175 , 175 , 175 , 175 , 175 , 175 , 175 ]
# automatic conversion to radiants
cutmap['dphimax']     = [ str(phi)+'*pi/180' for phi in cutmap['dphimax'] ]

cutmap['mt']          = [(80,110),  (80,110),  (80,120),  (80,123),  (80,125),
                         (80,128),  (80,130),  (80,140),  (80,150),  (80,155),
                         (90,160),  (110,170), (120,180), (120,190), (120,200),
                         (120,250), (120,300), (120,350), (120,400), (120,450),
                         (120,500), (120,550), (120,600) ]

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

# basic
# _rawCuts = {}
# _rawCuts['base']        = 'trigger && nextra == 0 && mll > (12 + 8*sameflav) && (pt2 > 15 || !sameflav) && ptll > 45'
# _rawCuts['antiZ']	    = 'pfmet > 20 && zveto && mpmet > (20+(17+nvtx/2.)*sameflav) && ( dphiveto || ! sameflav)'
# _rawCuts['antiB']	    = 'bveto_mu && bveto_ip && ( njet == 0 || (njet !=0 && nbjet==0 ) )'

# # _rawCuts['antiZ:vbf']	= 'pfmet > 20 && zveto && mpmet > (20+(17+nvtx/2.)*sameflav) && (dphilljetjet<165*pi/180 || !sameflav)'
# _rawCuts['antiZ:vbf']	= 'pfmet > 20 && zveto && (dphilljetjet<165*pi/180 || !sameflav)'
# _rawCuts['antiB:vbf']	= 'bveto_mu && bveto_ip && jettche1<2.1 && jettche2<2.1'


# # combined
# _rawCuts['WW-level']    = _rawCuts['base']  + ' && ' + _rawCuts['antiB'] + ' && ' + _rawCuts['antiZ']
# _rawCuts['Z-ctrl-reg']  = _rawCuts['base']  + ' && ' + _rawCuts['antiB'] + ' && pfmet > 20 && zveto && mpmet>20 && mpmet<37 && (dphiveto || !sameflav)'
# _rawCuts['Z-ctrl-reg']  = _rawCuts['base']  + ' && ' + _rawCuts['antiB'] + ' && pfmet > 20 && zveto && mpmet>20 && (dphiveto || !sameflav)'

# _rawCuts['WW-level:vbf'] = _rawCuts['base']  + ' && ' + _rawCuts['antiB:vbf'] + ' && ' + _rawCuts['antiZ:vbf']

# _rawCuts['WW-ctrl-reg'] = _rawCuts['WW-level'] + ' && mll>100'
# _rawCuts['T-ctrl-reg']  = _rawCuts['base']  + ' && ' + _rawCuts['antiZ'] + ' && ' + '!( '+_rawCuts['antiB']+' )'
# _rawCuts['massZ']       = _rawCuts['base']  + ' && sameflav && !zveto && mpmet>20 && mpmet<37'
# _rawCuts['vetoZ']       = _rawCuts['base']  + ' && zveto && mpmet>20'

# _rawCuts['extra:vbf']     = 'abs(jeteta1)<4.5 && abs(jeteta2)<4.5 && njetvbf == 0  && abs(eta1 - (jeteta1+jeteta2)/2)/detajj < 0.5 && abs(eta2 - (jeteta1+jeteta2)/2)/detajj < 0.5'

# _rawcuts = {}
# _rawcuts['wwnomet'] = ' && '.join(wwcuts.wwnomet)
# _rawcuts['wwhi'] = ' && '.join(wwcuts.wwhi)
# _rawcuts['wwlo'] = ' && '.join(wwcuts.wwlo)



# selections = _rawCuts 
# del _rawCuts

def massSelections(mass):

    mthmin_bdt = 80.
    masscuts = dict([(cut,massDependantCutsbyVar[cut][mass]) for cut in massDependantCutsbyVar])

    sel = {}
    sel['ww-common']     = ' && '.join(wwcuts.wwcommon)
    sel['ww-himass']    = ' && '.join(wwcuts.wwhi)
    sel['ww-lomass']    = ' && '.join(wwcuts.wwlo)

    sel['ww-level']     = sel['ww-lomass'] if mass <= 140 else sel['ww-himass'] 
    sel['bdt-specific'] = 'mll < {0} && (mth > {1:.0f} && mth < {2:.0f})'.format(masscuts['mllmax_bdt'], mthmin_bdt, int(mass))

    hwwlvl = {}
    hwwlvl['mll']    = 'mll < {0}'.format(masscuts['mllmax'])
    hwwlvl['pt1']    = 'pt1 > {0:.1f}'.format(masscuts['pt1min'])
    hwwlvl['pt2']    = 'pt2 > {0:.1f}'.format(masscuts['pt2min'])
    hwwlvl['dphill'] = 'dphill < {0}'.format(masscuts['dphimax'])
    hwwlvl['mth']    = '(mth > {0:.1f} && mth < {1:.1f})'.format(masscuts['mt'][0], masscuts['mt'][1])

    sel['ww-selection']           = sel['ww-level']
    sel['hww-selection']          = ' && '.join([sel['ww-level']]+[cut for cut     in hwwlvl.itervalues()])
    sel['mll-selection']          = ' && '.join([sel['ww-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'mll'])
    sel['mth-selection']          = ' && '.join([sel['ww-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'mth'])
    sel['dphi-selection']         = ' && '.join([sel['ww-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'dphill'])
    sel['gammaMRStar-selection']  = ' && '.join([sel['ww-level']]+[cut for var,cut in hwwlvl.iteritems() if var != 'mll'])
    sel['bdt-selection']          = sel['ww-level']+' && '+sel['bdt-specific']
    sel['bdtl-selection']         = sel['bdt-selection']

    # TODO gammastar test
    sel['gammaMRStar-selection']  = sel['bdt-selection']

    return sel

