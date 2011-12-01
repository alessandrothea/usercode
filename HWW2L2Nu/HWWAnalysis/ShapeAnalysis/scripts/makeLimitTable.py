#!/usr/bin/env python

import sys
import os
import ROOT
from ROOT import *
import HWWAnalysis.Misc.odict as odict
import optparse
import re


 
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
        print >> file, r' {mass} & {observed:.2f} & {median:.2f} & [{minus1sigma:.2f}, {plus1sigma:.2f}] & [{minus2sigma:.2f}, {plus2sigma:.2f}] \\'.format(mass=mass,**(table[mass]))
    print >> file, r'\hline'
    print >> file, r'\end{tabular}'
    print >> file, r'\end{document}'  

def main():
    usage = 'usage: %prog [dir] [cmd]'
    parser = optparse.OptionParser(usage)
    (opt, args) = parser.parse_args()
    
    tags = {
        'comb_0j1j2j':'comb_0j1j2j',
        'comb_0j1j':'comb_0j1j',
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

    reMass = re.compile('.+\.mH(\d+)\.(.*)root')
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

#         mass = sample.split('.')[-2]

        m = reMass.match(sample)
        if not m: 
            raise ValueError('Mass label not found in '+sample)

        mass = int(m.group(1))

        table[mass] = line

    printTable(sys.stdout, table)
    latex = open(basepath+'/'+tagname+'.tex','w')
    printTable(latex,table)
    latex.close()


    ## summary file
    summary = open(basepath+'/'+tagname+'.summary', 'w')
    for mass in table:
        summary.write('{mass} {observed:.3f} 99 {median:.3f} {minus1sigma:.3f} {plus1sigma:.3f} {minus2sigma:.3f} {plus2sigma:.3f}\n'.format( mass=mass, **(table[mass]) ) )

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
