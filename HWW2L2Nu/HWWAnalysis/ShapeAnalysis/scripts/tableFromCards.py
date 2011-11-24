#!/usr/bin/env python

import re
from sys import argv
import os.path
from optparse import OptionParser
from math import sqrt,fabs
parser = OptionParser()
parser.add_option("-s", "--stat",   dest="stat",          default=False, action="store_true")  # ignore systematic uncertainties to consider statistical uncertainties only
parser.add_option("-S", "--force-shape", dest="shape",    default=False, action="store_true")  # ignore systematic uncertainties to consider statistical uncertainties only
parser.add_option("-a", "--asimov", dest="asimov",        default=False, action="store_true")
parser.add_option("-m", "--mass", dest="mass",            default=160, type="float")

(options, args) = parser.parse_args()
options.bin = True # fake that is a binary output, so that we parse shape lines

from HiggsAnalysis.CombinedLimit.DatacardParser import *

DC = parseCard(file(args[0]), options)
nuisToConsider = [ y for y in DC.systs if 'CMS' in y[0] or y[0] == 'FakeRate']
#nuisToConsider = [ y for y in DC.systs if 'CMS' in y[0] ]

# print nuisToConsider

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
#        print "%10s %10s %10.2f +/- %10.2f (rel = %10.2f)" % (x,y,DC.exp[x][y],DC.exp[x][y]*errors[x][y],errors[x][y])
        print "%10s %10s %10.2f +/- %-10.2f (rel = %-10.2f)" % (x,y,expected,expected*error,error)

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

jets = ['0j']
channels = ['sf']
#order = [ 'DYLL', 'Top', 'WJet','VV', 'WW', 'sum', 'signal', 'data'  ]
order = [ 'DYLL', 'Top', 'WJet','VV', 'ggWW', 'WW', 'sum', 'signal', 'data'  ]

samplesTemp = [ ['DYLL','DYTT'], ['Top'], ['WJet'], ['VV','Vg'], ['ggWW'], ['WW'], [], ['ggH','vbfH','wzttH'], [] ]

#samplesTemp = [ ['DYLL','DYTT'], ['Top'], ['WJet'], ['VV','Vg'], ['ggWW'], ['WW'], [], ['ggH','vbfH','wzttH'], [] ]
labelsTemp  = [ 'Z$\\/\\gamma*$', '$t\\bar{t}$/single $t$', 'W+jets', 'WZ+ZZ', 'ggWW', 'WW', "all bkg.", "signal", 'data' ]
#labelsTemp  = [ 'Z$\\/\\gamma*$', '$t\\bar{t}$/single $t$', 'W+jets', 'WZ+ZZ', 'ggWW', 'WW', "all bkg.", ("$m_H=%d$"%options.mass), 'data' ]
samples = dict(zip(order,samplesTemp))
labels = dict(zip(order,labelsTemp))

#     label = "shapeYields_%s_%s" % (jet,channels[0])
    size = "footnotesize"

    # Print the header
    line =""
    sums = {}
    errs = {}
    for samp in order:
        sums[samp] = 0
        errs[samp] = 0

    # Print the header
    if options.mass == 110:
        for samp in order:
            line += " & %s" % (labels[samp])
        line += "\\\\    \\hline "

    # print each row
    for chan in channels:
        totVal = totErr = 0
        # print the label
        line += str(options.mass)

        # grab the right yields from DC
        thisExp = None
        for x in DC.exp.keys(): 
            if jet in x and chan in x: 
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

        print line



