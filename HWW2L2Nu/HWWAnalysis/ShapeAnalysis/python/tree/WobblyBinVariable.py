from tree.gardening import Grafter,Pruner 
from hwwinfo import wwcuts
import optparse
import numpy

#
# Esample:
#
#    gardener.py  WobblyBinVar  /data2/amassiro/VBF/Data/All21Aug2012_temp_1/latino_085_WgammaToLNuG.root  /data2/amassiro/VBF/Data/All21Aug2012_temp_3/latino_085_WgammaToLNuG_TESTIFITWORKS.root \
#    --branch=WobblyBinVar1D \
#    --var=pt1 \
#    --bin=10,100,200,300 \
#    --varoverflow=1 \
#    --varunderflow=0
#
#
#      \ \        /       |      |      |             __ )  _)
#       \ \  \   /  _ \   __ \   __ \   |  |   |      __ \   |  __ \
#        \ \  \ /  (   |  |   |  |   |  |  |   |      |   |  |  |   |
#         \_/\_/  \___/  _.__/  _.__/  _| \__, |     ____/  _| _|  _|
#                                         ____/
#
#


class WobblyBinVarGrafter(Grafter):

    def help(self):
        return 'Add the chessboard variable'

    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        group.add_option('-b',  '--branch',              dest='branch',        help='Name of the new variable',    default='varChess')
        group.add_option('-A',  '--var',                 dest='var',           help='Name of variable',            default='pt1')
        group.add_option('-B',  '--bin',                 dest='bin',           help='Bin edges',                   default='10,12,13,16,200,30000')
        group.add_option('-E',  '--varoverflow',         dest='varoverflow',   help='Overflow variable',           default='0')
        group.add_option('-P',  '--varunderflow',        dest='varunderflow',  help='Underflow variable',          default='0')

        parser.add_option_group(group)
        return group
        pass

    def checkOptions(self, opts):
        # create the options in 'adder style'
        branch   = opts.branch


        var            = opts.var
        binString      = opts.bin
        varoverflow    = int(opts.varoverflow)
        varunderflow   = int(opts.varunderflow)

        #bin            = [float(t) for t in binString.split(',') ]
        bin            = [str(t) for t in binString.split(',') ]

        varnumBin      = len(bin)


        class options: pass


        WobblyBinVarOpt = options()

####################
#
#    Wobbly Bin Variable  #
#
#    bins with variable width
#
#           [  )  [  ) [  )
#             1  2  3
#
#              var
#
#    + possible overflow & underflow
#
#
# e.g. : unverflow or overflow
#
#          - )  [ )  [ )  [ )
#
#             1 |  2  3  4
#
#              var
#
#          - )  [ )  [ )  [ ) [ -
#
#             1 |  2  3  4 | 5
#
#              var
#
#
#

        varnumBin -= 1

        totformula = branch + '/F= 0'


        for iBin in xrange(0, varnumBin):
            value = iBin + 1
            formula = ' + (' + var + '>=' + bin[iBin] + '&&' + var + '<' + bin[iBin+1] + ') * ' + str(iBin + 1)

            totformula += formula

        if (varunderflow==1) :
            totformula += ' + (' + var + '<' + bin[0] + ') * (-1)'

        if (varoverflow==1) :
            totformula += ' + (' + var + '>=' + bin[varnumBin] + ') * (' + str(varnumBin+2) + ')'


        print totformula

        WobblyBinVarOpt.variables = [
            totformula
        ]

        super(WobblyBinVarGrafter,self).checkOptions(WobblyBinVarOpt)


    def help(self):
        return '''Add chessboard variable'''




