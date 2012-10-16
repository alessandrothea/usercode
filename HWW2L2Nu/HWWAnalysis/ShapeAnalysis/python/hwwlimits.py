
dcnames = {}
dcnames['chans'] = ['of_0j','of_1j','of_2j','sf_0j','sf_1j','sf_2j']
dcnames['of']    = ['of_0j','of_1j','comb_of']
dcnames['sf']    = ['sf_0j','sf_1j','comb_sf']
dcnames['shape'] = ['comb_0j1j','comb_0j','comb_1j','comb_of','comb_sf']
dcnames['full']  = ['comb_0j1j2j']

dcnames['0j1j'] = (dcnames['chans']+
                   dcnames['chans'])

dcnames['all']  = (dcnames['chans']+
                   dcnames['shape']+
                   dcnames['full']+
                   dcnames['of']+
                   dcnames['sf'])

