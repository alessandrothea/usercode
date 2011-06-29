import os.path

masses = set(['120',
              '130',
              '140',
              '150',
              '160',
              '170',
              '180',
              '190',
              '200',
              '210',
              '220',
              '230',
              '250',
              '300',
              '350',
              '400',
              '450',
              '500',
              '550',
              '600'
             ])

def higgsPtFactorFile( mass ): 
    if not mass in masses:
        raise ValueError('Scale factors for mass '+mass+' not supported')

    path  = 'HiggsAnalysis/HiggsToWW2Leptons/data/kfactors_Std/'
    path += 'kfactors_mh'+mass+'_ren'+mass+'_fac'+mass+'.dat'

#     path = 'WWAnalysis/Misc/Scales/scalefactor.mh'+str(mass)+'.dat'
    return path
