#!/bin/env python



from tree.gardening         import gardener_cli
from tree.gardening         import ModuleManager,Pruner,Grafter,AliasGrafter,RootWeighter
from tree.pileup            import PUpper
from tree.ww                import WWPruner, WWFlagsGrafter
from tree.efficiencies      import EffLepFiller,EffTrgFiller
from tree.susyVar           import SusyVarFiller
from tree.mTVar             import MTVarFiller
from tree.ChessVariable     import ChessVarGrafter
from tree.unBoostedVar      import UnBoostedVarFiller
from tree.WobblyBinVariable import WobblyBinVarGrafter
from tree.likelihoodQGVar   import likelihoodQGVarFiller
from tree.susyVar2B2LMET    import SusyVar2B2LMETFiller
from tree.dymvaVar          import DymvaVarFiller
from tree.xyShift           import XYShiftVarFiller
from tree.higgsLineShape    import HiggsLineshapeWeightAdder
from tree.jetHiggsVar       import JetHiggsVarFiller
# from tree.vbfMVAVar         import VbfMVAVarFiller
from tree.manyJetsHiggsVar  import ManyJetsHiggsVarFiller


if __name__ == '__main__':

    
    modules = ModuleManager()
    modules['filter']           = Pruner()
    modules['adder']            = Grafter()
    modules['alias']            = AliasGrafter()
    modules['rootweighter']     = RootWeighter()
    modules['wwfilter']         = WWPruner()
    modules['wwflagger']        = WWFlagsGrafter()
    modules['puadder']          = PUpper()
    modules['effwfiller']       = EffLepFiller()
    modules['efftfiller']       = EffTrgFiller()
    modules['susyVar']          = SusyVarFiller()
    modules['mTVar']            = MTVarFiller()
    modules['chessVar']         = ChessVarGrafter()
    modules['unBoostedVar']     = UnBoostedVarFiller()
    modules['WobblyBinVar']     = WobblyBinVarGrafter()
    modules['likelihoodQGVar']  = likelihoodQGVarFiller()
    modules['susyVar2B2LMET']   = SusyVar2B2LMETFiller()
    modules['dymvaVar']         = DymvaVarFiller()
    modules['xyShift']          = XYShiftVarFiller()
    modules['higgsLS']          = HiggsLineshapeWeightAdder()
    modules['jetHiggsVar']      = JetHiggsVarFiller()
#     modules['vbfMVAVar']        = VbfMVAVarFiller()
    modules['manyJetsHiggsVar'] = ManyJetsHiggsVarFiller()

    gardener_cli( modules )
