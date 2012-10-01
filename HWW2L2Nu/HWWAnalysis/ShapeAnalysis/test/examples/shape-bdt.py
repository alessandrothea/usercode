lumi=5.064
rebin=10
chans=['of_0j','of_1j','sf_0j','sf_1j']

# 'mll' selection also exist, but use bdt for this one
variable='bdtl'
selection='bdt'

tag='bdt_bdtsel'
xlabel='BDT discriminant'
dataset='Data2012'

# directories
path_latino='/shome/mtakahashi/HWW/Tree/ShapeAna/tree_skim_wwcommon'
path_bdt='/shome/mtakahashi/HWW/Tree/ShapeAna/bdt_skim_wwcommon/mva_MH{mass}_{category}'
path_dd='/shome/mtakahashi/HWW/Data/dd/bdt_2012_51fb'
#path_latino_dd='/shome/mtakahashi/HWW/Tree/ShapeAna/tree_skim_ddskim'

# other directories
path_shape_raw='raw'
path_shape_merged='merged'

