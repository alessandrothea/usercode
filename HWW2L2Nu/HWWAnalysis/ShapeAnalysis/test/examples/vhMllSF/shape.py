#
# VH cut based   SF  ::   for shape DF
#


tag='vh_cutBased'

lumi=19.602
chans=['sf_vh2j']

mcset='vh_sf'
dataset='Data2012'

energy = '8TeV'

sigset='SM'

#variable='mll' # remember, y:x
variable='1' # remember, y:x
selection='vh'

range = (1,0,2)

xlabel='events'

# rebin=10
rebin=1

# directories
path_latino = '/data2/amassiro/VBF/Summer12/28Jan2013/Shape/tree_skim_wwmin/'
path_dd     = '/data2/amassiro/VBF/Summer12/28Jan2013/Shape/dd/Mll_2012_20fb/'

# other directories
path_shape_raw='raw'
path_shape_merged='merged'

