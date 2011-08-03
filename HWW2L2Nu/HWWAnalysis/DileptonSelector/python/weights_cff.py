from HWWAnalysis.DileptonSelector.pileupSpring2011_cfi import puWeights
from HWWAnalysis.DileptonSelector.higgsPtWeights_cfi import addHiggsPtWeights

import FWCore.ParameterSet.Config as cms

#--------------------------------------------------------------------
#  _    _      _       _     _       
# | |  | |    (_)     | |   | |      
# | |  | | ___ _  __ _| |__ | |_ ___ 
# | |/\| |/ _ \ |/ _` | '_ \| __/ __|
# \  /\  /  __/ | (_| | | | | |_\__ \
#  \/  \/ \___|_|\__, |_| |_|\__|___/
#                 __/ |              
#                |___/               

def addWeightsOptions( options ):
    options.register ( 'flatPuWeights',
                  False,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.bool,
                  'Set to true to force all the weights to 1')

    options.register ( 'higgsPtWeights',
                  None,
                  opts.VarParsing.multiplicity.singleton,
                  opts.VarParsing.varType.string,
                  'if not none apply the pt weights for the corresponding higgs mass')


def addWeights( process, pileUpLabel, higgsMass=None, summary=None  ):
    if pileUpLabel == 'Flat':
        print ' - Weights: Forcing all the PU eventWeights to 1.'
    else:
        print ' - Weights: '+pileUpLabel

    process.weightsCollector =  cms.EDProducer('WeightsCollector')

    process.puWeights = process.weightsCollector.clone(
        puInfoSrc = cms.InputTag('addPileupInfo'),
        pileupWeights = cms.vdouble(puWeights[pileUpLabel]),
    )
    #always add the object, in order to generate the map
    process.ptWeights = process.weightsCollector.clone()
    process.weightSequence = cms.Sequence( process.puWeights*process.ptWeights )

    if higgsMass:
        addHiggsPtWeights( process, higgsMass )
        print ' - Weights: Adding the pt eventWeights for mass '+higgsMass
        process.ptWeights.ptWeightSrc = cms.InputTag('higgsPtWeights')
        # put the ptweight in front of the collector
        process.weightSequence.replace(process.ptWeights, process.higgsPtWeights*process.ptWeights)

    if summary:
        process.eventWeights = process.weightsCollector.clone(
            puInfoSrc     = process.puWeights.puInfoSrc,
            pileupWeights = process.puWeights.pileupWeights,
        )

        if higgsMass:
            process.eventWeights.ptWeights.ptWeightSrc

        process.weightSequence += process.eventWeights


