from tree.gardening import Grafter,Pruner 
from hwwinfo import wwcuts
import optparse
import numpy

#   _      ___      ________              _____         _____         
#  | | /| / / | /| / / __/ /__ ____ ____ / ___/______ _/ _/ /____ ____
#  | |/ |/ /| |/ |/ / _// / _ `/ _ `(_-</ (_ / __/ _ `/ _/ __/ -_) __/
#  |__/|__/ |__/|__/_/ /_/\_,_/\_, /___/\___/_/  \_,_/_/ \__/\__/_/   
#                             /___/                                   

class WWFlagsGrafter(Grafter):

    def help(self):
        return 'Add the flags at ww, ww+0j,ww+1j, ww+2j levels, hi and lo mass'

    def addOptions(self,parser):
        return None

    def checkOptions(self, opts):
        # create the options in 'adder style'
        class options: pass

        wwopt = options()

        wwopt.variables = [
            'wwsel/I='     +' && '.join(wwcuts.wwcommon),
            'wwsel0j/I='   +' && '.join(wwcuts.wwcommon+[wwcuts.zerojet]),
            'wwsel1j/I='   +' && '.join(wwcuts.wwcommon+[wwcuts.onejet]),
            'wwsel2j/I='   +' && '.join(wwcuts.wwcommon+[wwcuts.vbf]),

            'wwsel_hi/I='  +' && '.join(wwcuts.wwcommon),
            'wwsel0j_hi/I='+' && '.join(wwcuts.wwcommon+[wwcuts.zerojet]),
            'wwsel1j_hi/I='+' && '.join(wwcuts.wwcommon+[wwcuts.onejet]),
            'wwsel2j_hi/I='+' && '.join(wwcuts.wwcommon+[wwcuts.vbf]),
        ]

        super(WWFlagsGrafter,self).checkOptions(wwopt)
  
#   _      ___      _____                       
#  | | /| / / | /| / / _ \______ _____  ___ ____
#  | |/ |/ /| |/ |/ / ___/ __/ // / _ \/ -_) __/
#  |__/|__/ |__/|__/_/  /_/  \_,_/_//_/\__/_/   
#                                               

class WWPruner(Pruner):
    levels = ['wwcommon','wwmin']

    def help(self):
        return '''Filters the tree according to the command line options. wwcommon, wwmin flags are understood'''


    def addOptions(self,parser):
        description= self.help()
        group = super(WWPruner,self).addOptions(parser)
        group.set_description(description)
        return group

    def connect(self, tree, input):
        super(WWPruner,self).connect(tree,input)

        for l in self.levels:
            self.itree.SetAlias(l,' && '.join(getattr(wwcuts,l)))


