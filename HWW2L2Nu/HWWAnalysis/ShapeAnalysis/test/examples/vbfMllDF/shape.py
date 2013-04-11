#
# VBF shape   DF    Mll
#


#
# deve chiamarsi "shape.py"
#

tag='mll_vbf'
lumi=19.602
chans=['of_2j']

variable='mll'

selection='vbf-shape'
#  -> cerca vbf-selection
# da hwwinfo


# 2D
#          x     |    y
# range=(10, 12, 312)
#range=(10, 12, 312)
range=(11, 12, 342)
#


dataset='Data2012'

mcset='vbf_of'


# errore statistico

# in mkmerged
# unified  -> shift globale
# bybin ---> bin bin bin

statmode='unified'

xlabel='m(ll) [GeV]'


# usato da mkmerged  -> li ricompatto dopo
# rebin=10
rebin=1

# directories
path_latino = '/data2/amassiro/VBF/Summer12/28Jan2013/Shape/tree_skim_wwmin/'
path_dd     = '/data2/amassiro/VBF/Summer12/28Jan2013/Shape/dd/Mll_2012_20fb/'



# output other directories
path_shape_raw='raw'
path_shape_merged='merged'






