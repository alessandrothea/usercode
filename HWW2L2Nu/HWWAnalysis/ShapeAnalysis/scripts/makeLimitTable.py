#!/usr/bin/env python

import sys
import os
import ROOT
from ROOT import *
import HWWAnalysis.Misc.odict as odict
import optparse


 
tagname = 'comb_shape'


# basepath = '/shome/jueugste/cmssw/CMSSW_4_2_8_patch3/src/LimitResults/input_shape_mt'
# basepath = '/shome/thea/HWW/Limits/LimitResults'
basepath = 'limits/'
#samplename = [
#    'higgsCombineHWW.Asymptotic.mH120.root',
#    'higgsCombineHWW.Asymptotic.mH130.root',
#    ]

samplename = os.listdir(basepath)
samplename.sort()

points = ['minus2sigma', 'minus1sigma', 'median', 'plus1sigma', 'plus2sigma','observed']

def openTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f

def getTree( file, tree ):
    t = file.Get(tree)
    if not t.__nonzero__():
        raise NameError('Tree '+str(tree)+' doesn\'t exist in '+file.GetName())
    return t

## def readSamplesList(file):
##     print 'reading: '+file 
##     file = open(file)
##     for line in file:
##         if (line[0] == '#'):
##             continue
## #        s = line.split(':')
##         samplename.append(line.split('\n')[1])


def getValue(file, q):
    ## -1: observed limit
    ## 0.5: median expected
    ## 0.16/0.84: +- 1 sigma
    ## 0.025/0.975: +- 2 sigma
    cut = ''
    if q is 'median':
        cut = 'quantileExpected==0.5'
    if q is 'observed':
        cut = 'quantileExpected==-1.'
    if q is 'minus1sigma':
        cut = 'quantileExpected>0.15 && quantileExpected<0.17'
    if q is 'minus2sigma':
        cut = 'quantileExpected>0.022 && quantileExpected<0.027'
    if q is 'plus1sigma':
        cut = 'quantileExpected>0.83 && quantileExpected<0.86'
    if q is 'plus2sigma':
        cut = 'quantileExpected>0.97 && quantileExpected<0.98'
        
    tree = getTree(file,'limit')
    command = 'limit>>h'
    tree.Draw(command,cut)
    hist = gDirectory.Get("h")
    value = hist.GetMean()
    hist.Delete()
    return value

def printTable(file, table):
    ## latex table
    print >> file, r'\documentclass[a4paper]{article}'
    print >> file, r'\begin{document}'
    print >> file, r'\pagestyle{empty}'
    print >> file, r'\begin{tabular}{|c|cccc|}'
    print >> file, r'\hline'
    print >> file, r'Higgs mass [$\mathrm{GeV/c^2}$] & Observed & Median & $68\%$ Range & $95\%$ Range \\'
    print >> file, r'\hline'
    print >> file, r'\hline'
    for mass in table:
        myline = {}
        myline.update(table[mass])
        myline['mass'] = mass.replace('mH','')
#         print myline
        print >> file, r' {mass} & {observed:.2f} & {median:.2f} & [{minus1sigma:.2f}, {plus1sigma:.2f}] & [{minus2sigma:.2f}, {plus2sigma:.2f}] \\'.format(**myline)
#         print >> file, mass.replace('mH','')+' & '+str('%.2f' % table[mass]['minus2sigma'])+' & '+str('%.2f' % table[mass]['minus1sigma'])+' & '+str('%.2f' % table[mass]['mean'])+' & '+str('%.2f' % table[mass]['plus1sigma'])+' & '+str('%.2f' % table[mass]['plus2sigma'])+r' \\'
    print >> file, r'\hline'
    print >> file, r'\end{tabular}'
    print >> file, r'\end{document}'  

def main():
    usage = 'usage: %prog [dir] [cmd]'
    parser = optparse.OptionParser(usage)
    (opt, args) = parser.parse_args()
    
    tags = {
        'allcomb':'allcomb',
        'comb':'comb',
        'comb_0j':'comb_0j',
        'comb_1j':'comb_1j',
        'of_0j':'of_0j',
        'of_1j':'of_1j',
        'sf_0j':'sf_0j',
        'sf_1j':'sf_1j',
    }

    if not args or args[0] not in tags:
        print args
        parser.error('tag must be '+' '.join(tags.keys()))

    tag = args[0]
    if tag not in tags:
        print 'Tag not recognized'
        sys.exit(-1)

    tagname = tags[tag]+'_shape'
##    readSamplesList('limitTableSamples.input')

#     print samplename
    print tagname

    table = odict.OrderedDict()
    #table = {}
    for sample in samplename:
        if not '.root' in sample:
            continue
        if not tagname in sample:
            continue
        line = {}
        print sample
        path = basepath+'/'+sample
        f = openTFile(path)

        for point in points:
            value = getValue(f,point)
#             print point, value
            line[point] = value

        mass = sample.split('.')[-2]
        table[mass] = line

    ## latex table
#     print r'\documentclass[a4paper]{article}'
#     print r'\begin{document}'
#     print r'\begin{tabular}{|c|c|c|c|c|c|}'
#     print r'\hline'
#     print r'mass [$\mathrm{GeV/c^2}$] & $-95\%$ & $-68\%$ & mean & $+68\%$ & $+95\%$ \\'
#     print r'\hline'
#     print r'\hline'
#     for mass in table:
#         print mass.replace('mH','')+' & '+str('%.3f' % table[mass]['minus2sigma'])+' & '+str('%.3f' % table[mass]['minus1sigma'])+' & '+str('%.3f' % table[mass]['mean'])+' & '+str('%.3f' % table[mass]['plus1sigma'])+' & '+str('%.3f' % table[mass]['plus2sigma'])+r' \\'
#     print r'\hline'
#     print r'\end{tabular}'
#     print r'\end{document}'     

    printTable(sys.stdout, table)
    latex = open(basepath+'/'+tagname+'.tex','w')
    printTable(latex,table)
    latex.close()


    ## summary file
    summary = open(basepath+'/'+tagname+'.summary', 'w')
    for mass in table:
#        summary.write(mass.replace('mH','')+' '+str('%.3f' % table[mass]['observed'])+' 99. '+str('%.3f' % table[mass]['mean'])+' '+str('%.3f' % table[mass]['minus2sigma'])+' '+str('%.3f' % table[mass]['plus1sigma'])+' '+str('%.3f' % table[mass]['minus1sigma'])+' '+str('%.3f' % table[mass]['plus2sigma'])+'\n')
        summary.write(mass.replace('mH','')+' '+str('%.4f' % table[mass]['observed'])+' 99. '+str('%.4f' % table[mass]['median'])+' '+str('%.4f' % table[mass]['minus1sigma'])+' '+str('%.4f' % table[mass]['plus1sigma'])+' '+str('%.4f' % table[mass]['minus2sigma'])+' '+str('%.4f' % table[mass]['plus2sigma'])+'\n')

    summary.close()

if __name__ == '__main__':
    main()







## hww-1.55fb.mH120.comb.txt
## Observed Limit: r < 3.5430
## Expected  2.5%: r < 1.2811
## Expected 16.0%: r < 1.7041
## Expected 50.0%: r < 2.3613
## Expected 84.0%: r < 3.2799
## Expected 97.5%: r < 4.3577


## hww-1.55fb.mH130.comb.txt
## Observed Limit: r < 1.7859
## Expected  2.5%: r < 0.6184
## Expected 16.0%: r < 0.8226
## Expected 50.0%: r < 1.1398
## Expected 84.0%: r < 1.5832
## Expected 97.5%: r < 2.1035
