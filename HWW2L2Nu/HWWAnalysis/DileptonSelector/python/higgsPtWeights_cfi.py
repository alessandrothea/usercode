import os.path
import FWCore.ParameterSet.Config as cms

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

def higgsPtKFactorFile( mass ): 
    if not mass in masses:
        raise ValueError('Scale factors for mass '+mass+' not supported')

    path  = 'HiggsAnalysis/HiggsToWW2Leptons/data/kfactors_Std/'
    path += 'kfactors_mh'+mass+'_ren'+mass+'_fac'+mass+'.dat'

#     path = 'WWAnalysis/Misc/Scales/scalefactor.mh'+str(mass)+'.dat'
    return path


#-------------------------------------------------------------------------------
#  _   _                    _   ________         _                 
# | | | |                  | | / /|  ___|       | |                
# | |_| |_      ____      _| |/ / | |_ __ _  ___| |_ ___  _ __ ___ 
# |  _  \ \ /\ / /\ \ /\ / /    \ |  _/ _` |/ __| __/ _ \| '__/ __|
# | | | |\ V  V /  \ V  V /| |\  \| || (_| | (__| || (_) | |  \__ \
# \_| |_/ \_/\_/    \_/\_/ \_| \_/\_| \__,_|\___|\__\___/|_|  |___/

def addHiggsPtWeights( process, higgsMass ):
    scaleFile = higgsPtKFactorFile( higgsMass)
    process.higgsPtWeights = cms.EDProducer('HWWKFactorProducer',
        genParticlesTag = cms.InputTag('prunedGen'),
        inputFilename = cms.untracked.string( scaleFile ),
        ProcessID = cms.untracked.int32(10010),
        Debug =cms.untracked.bool(False)
    )
    print 'Rescaling pt for higgs mass '+higgsMass+' using '+ scaleFile
#     process.pLep += process.higgsPtWeights



