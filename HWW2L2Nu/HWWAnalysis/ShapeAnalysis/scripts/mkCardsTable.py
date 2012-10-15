#!/usr/bin/env python
import os
import optparse
import HiggsAnalysis.CombinedLimit.DatacardParser as cardparser
from math import sqrt,fabs
import glob

allowedtags = ['sf_0j','sf_1j','of_0j','of_1j','comb_0j', 'comb_1j', 'comb']

#basedir = '/shome/jueugste/cmssw/CMSSW_4_2_4/src/HWWAnalysis/CutBasedAnalyzer'

def findVals(samp,thisExp,thisErr):
    val = 0
    err = 0
    for s in samp:
        for k in thisExp:
            if s in k:
                if s == 'WW' and k == 'ggWW':
                    continue

                val += thisExp[k]

                try:
                    e = thisErr[k]
                except KeyError:
                    e = 0

#                err += val*val*thisErr[k]*thisErr[k]
                err += val*val*e*e
    return (val,sqrt(err))

class Options: pass

order = [ 'DYLL', 'Top', 'WJet','VV', 'ggWW', 'WW', 'sum', 'signal', 'data'  ]
samplesTemp = [ ['DYLL','DYTT'], ['Top'], ['WJet'], ['VV','Vg'], ['ggWW'], ['WW'], [], ['ggH','vbfH','wzttH'], [] ]
labelsTemp  = [ 'Z$\\/\\gamma*$', '$t\\bar{t}$/single $t$', 'W+jets', 'WZ+ZZ', 'ggWW', 'WW', "all bkg.", "signal", 'data' ]

samples = dict(zip(order,samplesTemp))
labels = dict(zip(order,labelsTemp))


def getSummary( filename, mass ):

    # get the defaults from 
    dummyp = optparse.OptionParser('dummy')
    cardparser.addDatacardParserOptions(dummyp)
    (options, dumbargs) = dummyp.parse_args([])

    DC = cardparser.parseCard(file(filename), options)
    nuisToConsider = [ y for y in DC.systs if 'CMS' in y[0] or y[0] == 'FakeRate']

    errors = {}
    for nuis in nuisToConsider:
        if nuis[2] == 'gmN': gmN = nuis[3][0]
        else               : gmN = 0
        for channel in nuis[4]:
            if channel not in errors.keys(): errors[channel] = {}
            for process in nuis[4][channel]:
                if nuis[4][channel][process] == 0: continue
                if gmN != 0:
                    newError = nuis[4][channel][process] * sqrt(gmN) / DC.exp[channel][process]
                else:
                    newError = fabs(1-nuis[4][channel][process])
    #             print process,nuis[4][channel][process],gmN,newError
                if process in errors[channel].keys():
                    errors[channel][process] += newError*newError
                else:
                    errors[channel][process] = newError*newError




    for channel in errors:
        for process in errors[channel]:
            errors[channel][process] = sqrt(errors[channel][process])

    for x in DC.exp:
        if '0j' not in x and '1j' not in x: continue
        for y in DC.exp[x]:
            try:
                expected = DC.exp[x][y]
            except KeyError:
                expected = 0.
                
            try: error = errors[x][y]
            except KeyError:
                error = 0.
            print "%10s %10s %10.2f +/- %-10.2f (rel = %-10.2f)" % (x,y,expected,expected*error,error)

    sums = {}
    errs = {}
    for samp in order:
        sums[samp] = 0
        errs[samp] = 0

#     jet = '0'
#     chan = 'sf'

    totVal = totErr = 0
    line = ''
    # print the label
    line += str(mass)

    # grab the right yields from DC
    thisExp = None
    for x in DC.exp.keys(): 
#         if jet in x and chan in x: 
        thisExp = DC.exp[x]
        thisErr = errors[x]
        thisDat = DC.obs[x]
    if not thisExp: 
        print "WTF"



    # print each contribution
    for i,samp in enumerate(order):
        if samp in ['signal','sum','data']: continue;
        (val,err) = findVals(samples[samp],thisExp,thisErr)
        totVal += val; totErr += err*err;
        line += " & $%.1f\pm%.1f$" % (val,err)
        sums[samp] += val; errs[samp] += err*err
        sums['sum'] += val; errs['sum'] += err*err
    line += " & $%.1f\pm%.1f$" % (totVal,sqrt(totErr))
    (val,err) = findVals(samples['signal'],thisExp,thisErr)
    sums['signal'] += val; errs['signal'] += err*err
    line += " & $%.1f\pm%.1f$" %  (val,err)
    line += " & $%d$ \\\\" % thisDat
    sums['data'] += thisDat

    return line


def main():

    usage = 'usage: %prog tag -i dir -o dir'
    parser = optparse.OptionParser(usage)
    
    parser.add_option('-i','--input', dest='inputdir', help='Input directory')   
    parser.add_option('-o','--output',dest='outputdir',help='Output directory')   

    (opt, args) = parser.parse_args()
    
    if opt.inputdir is None:
        parser.error('No input directory defined')
    if not args:
        parser.error('No tag defined: '+' '.join(allowedtags))

    tag = args[0]
    dir = opt.inputdir
    outdir = opt.outputdir

    if outdir:
        if outdir[:-1]!='/':
            outdir += '/'
        os.system('mkdir -p '+outdir)

#     filenames = os.listdir(dir)
    filenames = glob.glob(dir+'*'+tag+'*.txt')
    filenames.sort()
    print filenames
    flavor = 'same' if 'sf' in tag else 'opposite'
    njets = 'zero' if '0' in tag else 'one'
    caption = '''
    Background contributions and data yields for 4.63 $\mathrm{fb^{-1}}$ of integrated 
    luminosity after the BDT selection in the '''+njets +' jet bin for the '+flavor+''' flavor final states.
    The data-driven corrections are applied.'''
    label = 'yields_'+tag
    texpath = label+'.tex'
    print texpath
    texfile = open(texpath,'w')

    print >> texfile, r'\documentclass[a4paper]{article}'
    print >> texfile, r'\usepackage[landscape]{geometry}'
    print >> texfile, r'\begin{document}'
    print >> texfile, r'\pagestyle{empty}'
    print >> texfile, r'\begin{table}[h!]\begin{center}'
    print >> texfile, r'\caption{{ {0} \label{{ {1} }} }}'.format(caption,label)
    print >> texfile, r'\begin{tabular}{|c|c|c|c|c|c|c|c|c||c|}'
    print >> texfile, r'\hline' 
    print >> texfile, r'\footnotesize'
    print >> texfile, 'Mass &',r' & '.join(order),r'\\'
    print >> texfile, r'\hline'
    
    for file in filenames:
        print '-'*80
        print file
        print '-'*80
#         if 'comb_shape' not in file:
#             continue
        mass = file.split('.')[-3].replace('mH','')

        print >> texfile,getSummary(file,int(mass))

    print >> texfile, r'\hline'
    print >> texfile, r'\end{tabular}'
    print >> texfile, r'\end{center}'
    print >> texfile, r'\end{table}'
    print >> texfile, r'\end{document}' 

    texfile.close()

    os.system('mv '+label+'.tex '+outdir)
 

if __name__ == '__main__':
    main()

       
