from tree.gardening import Grafter,Pruner 
from hwwinfo import wwcuts
import optparse
import numpy

#
# Esample:
#
#    gardener.py  chessVar  /data2/amassiro/VBF/Data/All21Aug2012_temp_1/latino_085_WgammaToLNuG.root  /data2/amassiro/VBF/Data/All21Aug2012_temp_2/latino_085_WgammaToLNuG_TESTIFITWORKS.root \
#    --branch=chessVar2D \
#    --varA=pt1 \
#    --varAnumBin=2 \
#    --varAmin=10.123 \
#    --varAmax=234.543 \
#    --varAoverflow=0 \
#    --varAunderflow=1 \
#    --varB=pt1 \
#    --varBnumBin=2 \
#    --varBmin=10.123 \
#    --varBmax=234.543 \
#    --varBoverflow=1 \
#    --varBunderflow=0 
#

#
#      ___|  |                                               _)         |      | 
#     |      __ \    _ \   __|   __|     \ \   /  _` |   __|  |   _` |  __ \   |   _ \
#     |      | | |   __/ \__ \ \__ \      \ \ /  (   |  |     |  (   |  |   |  |   __/
#    \____| _| |_| \___| ____/ ____/       \_/  \__,_| _|    _| \__,_| _.__/  _| \___|
#


class ChessVarGrafter(Grafter):

    def help(self):
        return 'Add the chessboard variable'

    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        group.add_option('-b',     '--branch',           dest='branch',        help='Name of the new variable',    default='varChess')
        group.add_option('-A',  '--varA',                dest='varA',          help='Name of variable A',          default='pt1')
        group.add_option('-B',  '--varAnumBin',          dest='varAnumBin',    help='Numbers of bins variable A',  default='10')
        group.add_option('-C', '--varAmin',              dest='varAmin',       help='Min variable A',              default='0')
        group.add_option('-D', '--varAmax',              dest='varAmax',       help='Max variable A',              default='100')
        group.add_option('-E',  '--varAoverflow',        dest='varAoverflow',  help='Overflow variable A',         default='0')
        group.add_option('-P',  '--varAunderflow',       dest='varAunderflow', help='Underflow variable A',        default='0')

        group.add_option('-G',  '--varB',                dest='varB',          help='Name of variable B',          default='pt2')
        group.add_option('-H',  '--varBnumBin',          dest='varBnumBin',    help='Numbers of bins variable B',  default='10')
        group.add_option('-I', '--varBmin',              dest='varBmin',       help='Min variable B',              default='0')
        group.add_option('-L', '--varBmax',              dest='varBmax',       help='Max variable B',              default='100')
        group.add_option('-M',  '--varBoverflow',        dest='varBoverflow',  help='Overflow variable B',         default='0')
        group.add_option('-N',  '--varBunderflow',       dest='varBunderflow', help='Underflow variable B',        default='0')

        parser.add_option_group(group)
        return group
        pass

    def checkOptions(self, opts):
        # create the options in 'adder style'
        branch   = opts.branch


        varA            = opts.varA
        varAnumBin      = float(opts.varAnumBin)
        varAmin         = float(opts.varAmin)
        varAmax         = float(opts.varAmax)
        varAoverflow    = int(opts.varAoverflow)
        varAunderflow   = int(opts.varAunderflow)

        varB            = opts.varB
        varBnumBin      = float(opts.varBnumBin)
        varBmin         = float(opts.varBmin)
        varBmax         = float(opts.varBmax)
        varBoverflow    = int(opts.varBoverflow)
        varBunderflow   = int(opts.varBunderflow)

        class options: pass


        chessVarOpt = options()

####################
#
#    Chessboard    #
#
#            13 14 15 16
#             9 10 11 12
#      varB   5  6  7  8
#             1  2  3  4
#
#              varA
#
#    + possible overflow & underflow
#
#
# e.g. : overflow for varB and underflow for varA
#
#
#            13 | 14 15 16
#           -------------
#             9 | 10 11 12
#      varB   5 |  6  7  8
#             1 |  2  3  4
#
#              varA

#
#
# e.g. : overflow for varB and underflow for varA and overflow for varA
#
#            13 | 14 15 | 16
#           ----------------
#             9 | 10 11 | 12
#      varB   5 |  6  7 |  8
#             1 |  2  3 |  4
#
#              varA
#
#
# e.g. : overflow for varB and underflow for B and underflow for varA and overflow for varA
#
#            13 | 14 15 | 16
#           ----------------
#             9 | 10 11 | 12
#      varB   5 |  6  7 |  8
#           ----------------
#             1 |  2  3 |  4
#
#              varA
#
#
#

        widthA = (varAmax - varAmin) / varAnumBin
        widthB = (varBmax - varBmin) / varBnumBin

        totformula = branch + '/F= 0' 

#        for iBinB in xrange(0, varBnumBin):
#            for iBinA in xrange(0, varAnumBin):
#               value = iBinA + iBinB*varBnumBin + 1
#               minA  = iBinA*widthA
#               maxA  = (iBinA+1)*widthA
#               minB  = iBinB*widthB
#               maxB  = (iBinB+1)*widthB
#
#               formula = ' + (' + varA + '>' + str(minA) + '&&' + varA + '<=' + str(maxA) + '&&' + varB + '>' + str(minB) + '&&' + varB + '<=' + str(maxB) + ')*' + str(value) + ' '
#
#               totformula += formula
#


        totformula += ' + '
        totformula += '   (' + varA + ' > ' + str(varAmin) + ' && ' + varA + '<=' + str(varAmax)
        totformula += ' && ' + varB + ' > ' + str(varBmin) + ' && ' + varB + '<=' + str(varBmax)
        totformula += ' ) * '


        if (varBunderflow==1) :
          varBnumBin += 1
          varBmin -= widthB

        if (varBoverflow==1) :
          varBnumBin += 1
          varBmax += widthB

        if (varAunderflow==1) :
          varAnumBin += 1
          varAmin -= widthA

        if (varAoverflow==1) :
          varAnumBin += 1
          varAmax += widthA


        totformula +=                        ' ( TMath::Ceil( (' + varA + '-' + str(varAmin) + ')/(' + str(varAmax) +' - ' + str(varAmin) + ') * ' + str(varAnumBin) +' ) + '
        totformula +=   str(varAnumBin) + ' *    TMath::Ceil( (' + varB + '-' + str(varBmin) + ')/(' + str(varBmax) +' - ' + str(varBmin) + ') * ' + str(varBnumBin) +' )   )'


        # to deal with underflow and overflow
        for iBinB in xrange(0, varBnumBin):
           for iBinA in xrange(0, varAnumBin):
               value = iBinA + iBinB*varAnumBin + 1
               minA  = varAmin + iBinA*widthA
               maxA  = varAmin + (iBinA+1)*widthA
               minB  = varBmin + iBinB*widthB
               maxB  = varBmin + (iBinB+1)*widthB

               formula = ' '

               dosomething = 0

               if (iBinA==0) :
                    if (varAunderflow==1) :
                        formula += ' + (' + varA + '<=' + str(maxA) + ' '
                        dosomething = 1
                    else :
                        formula += ' + (' + varA + '>' + str(minA) + '&&' + varA + '<=' + str(maxA) + ' '

               if (iBinA==(varAnumBin-1)) :
                   if (varAoverflow==1) :
                       formula += ' + (' + varA + '>' + str(minA) + ' '
                       dosomething = 1
                   else :
                       formula += ' + (' + varA + '>' + str(minA) + '&&' + varA + '<=' + str(maxA) + ' '

               if (iBinA!=0 and iBinA!=(varAnumBin-1)) :
                   formula += ' + (' + varA + '>' + str(minA) + '&&' + varA + '<=' + str(maxA) + ' '

               if (iBinB==0) :
                   if (varBunderflow==1) :
                       formula += ' && ' + varB + '<=' + str(maxB) + ' )'
                       dosomething = 1
                   else :
                       formula += ' && ' + varB + '>' + str(minB) + '&&' + varB + '<=' + str(maxB) + ' )'

               if (iBinB==(varBnumBin-1)) :
                   if (varBoverflow==1) :
                       formula += ' && ' + varB + '>' + str(minB) + ' )'
                       dosomething = 1
                   else :
                       formula += ' && ' + varB + '>' + str(minB) + '&&' + varB + '<=' + str(maxB) + ' )'

               if (iBinB!=0 and iBinB!=(varBnumBin-1)) :
                   formula += ' && ' + varB + '>' + str(minB) + '&&' + varB + '<=' + str(maxB) + ' )'

               #if (iBinA==0) :
                 #if (varAunderflow==1) :
                   #formula += ' + (' + varA + '<=' + str(maxA) + ' '
                   #dosomething = 1

               #if (iBinA==(varAnumBin-1)) :
                 #if (varAoverflow==1) :
                   #formula += ' + (' + varA + '>' + str(minA) + ' '
                   #dosomething = 1

               #if (iBinB==0) :
                 #if (varBunderflow==1) :
                   #formula += ' && ' + varB + '<=' + str(maxB) + ' )'
                   #dosomething = 1

               #if (iBinB==(varBnumBin-1)) :
                 #if (varBoverflow==1) :
                   #formula += ' && ' + varB + '>' + str(minB) + ' )'
                   #dosomething = 1

               if dosomething == 1 :
                   formula += '*' + str(value) + ' '
                   totformula += formula


        print ' Calculate ...'
        print totformula

        chessVarOpt.variables = [
            totformula
        ]

        super(ChessVarGrafter,self).checkOptions(chessVarOpt)


    def help(self):
        return '''Add chessboard variable'''




