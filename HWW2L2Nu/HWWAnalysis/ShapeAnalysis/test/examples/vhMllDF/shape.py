#
# VH shape   DF    Mll
#



#
# deve chiamarsi "shape.py"
#

tag='mll_vh'
lumi=19.602
chans=['of_vh2j']

variable='mll'

selection='vh-shape'
#  -> cerca vh-shape-selection
# da hwwinfo


range='vhMll-range'


# dataset to use: Data2012, Data2012A, Data2012B, SI125
dataset='Data2012'
#dataset='SI125'
#simask='SM'  --> serve ad iniettare un subset dei segnali

mcset='vh_of'

energy = '8TeV'

# signals samples to use
sigset='SM'
# mass=125


# errore statistico

# in mkmerged
# unified  -> shift globale
# bybin ---> bin bin bin

statmode='unified'
#statmode='bybin'


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






