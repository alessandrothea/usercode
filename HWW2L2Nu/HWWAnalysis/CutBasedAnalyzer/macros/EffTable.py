#!/usr/bin/env python
import sys
import optparse
import math
import HWWAnalysis.Misc.odict
import string

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)

parser.add_option('-k', '--kfactor', dest='kfactor', help='Normalization factor', default='1.')
 
(opt, args) = parser.parse_args()

kfact = string.atof(opt.kfactor)

sys.argv.append( '-b' )
import ROOT
ROOT.gROOT.SetBatch()

#print args, len(args)

if len(args) is not 2:
    print '   Usage: %prog <path>'
    sys.exit(0)

f = ROOT.TFile(args[1])

fStates = ['mm','me','em','ee','ll']

d = {}
prefix='yieldAnalyzer/'
# prefix='diLepSel/'
for s in fStates:
    d[s] = odict.OrderedDict()

    name = prefix+s+'Yield'
    counters = f.Get(name)
    counters.Scale(kfact)
    if not counters.__nonzero__():
        raise NameError('histogram '+name+' not found in '+args[1])
    lastBin = counters.GetNbinsX()

    d[s]['entries'] = '%.2f' % counters.GetBinContent(1)
    for i in range(2,lastBin+1):
        ax = counters.GetXaxis()
        labelAbs = ax.GetBinLabel(i)
        labelRel = ax.GetBinLabel(i)+'/'+ax.GetBinLabel(i-1)
        
        entries = counters.GetBinContent(1)
        prevBin = counters.GetBinContent(i-1)
        theBin  = counters.GetBinContent(i)
        
        absEff = 100.*counters.GetBinContent(i)/entries
        #print prevBin==0,theBin==0
        if ( prevBin==0 or theBin==0):
            relEff = 0
        else:
            relEff = 100.*theBin/prevBin
        
#         d[s][labelAbs] = '%.1f+-%.1f' % ( theBin, math.sqrt(theBin) )
        d[s][labelAbs] = '%.1f' % ( theBin, )
#         print '  %s = %d - %.3f%% (%.3f%%)' % (labelAbs.ljust(20), theBin,absEff, relEff)
        
print '+ Cut'.ljust(34),' | '.join([ s.ljust(20) for s in fStates ])

# loop over the labels of the first column
for lab in d.iteritems().next().iterkeys():
    print '-',lab.ljust(30),'=',' | '.join( [ d[s][lab].ljust(20) for s in fStates ]) 

print r'\begin{tabular}{'+'l'*(len(fStates)+1)+'}'
for lab in d['ll'].iterkeys():
    print '$'+lab.replace('#','\\')+'$','&',' & '.join([ d[s][lab].replace('+-',' $\\pm$ ').replace('%','\%') for s in fStates ]  ),r'\\'
print r'\end{tabular}'


#if __name__ == '__main__':
#    
#    usage = 'usage: %prog [options]'
#    parser = optparse.OptionParser(usage)
#    
#    parser.add_option('-p', '--path', dest=plotPath, help='Path to the plot in the ROOTfile')
#    
#    (opt, args) = parser.parse_args()
#        
#    dumpEfficiencies( file, plotPath )
