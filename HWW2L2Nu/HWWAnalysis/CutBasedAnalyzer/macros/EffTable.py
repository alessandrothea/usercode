#!/usr/bin/env python
import sys
import optparse
import math
import odict


args = sys.argv[:]
sys.argv.append( '-b' )
import ROOT
ROOT.gROOT.SetBatch()

#print args, len(args)

if len(args) is not 2:
    print '   Usage: %prog <path>'
    sys.exit(0)

# ROOT.gSystem.Load('lib/libHWWNtuple.so')

f = ROOT.TFile(args[1])

fStates = ['mm','me','em','ee','ll']

d = {}
prefix='fullSelection/'
# prefix='diLepSel/'
for s in fStates:
    d[s] = odict.OrderedDict()
    print '\n-',s+'Counters'
    name = prefix+s+'Counters'
    counters = f.Get(name)
    if not counters.__nonzero__():
        raise NameError('histogram '+name+' not found in '+args[1])
    lastBin = counters.GetNbinsX()
    print 'Entries:',counters.GetBinContent(1)
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
        
        d[s][labelAbs] = '%.1f+-%.1f' % ( theBin, math.sqrt(theBin) )
        print '  %s = %d - %.3f%% (%.3f%%)' % (labelAbs.ljust(20), theBin,absEff, relEff)
        
print '+ Cut'.ljust(34),' | '.join([ s.ljust(20) for s in fStates ])

for lab in d['ll'].iterkeys():
    print '-',lab.ljust(30),'=',' | '.join( [ d[s][lab].ljust(20) for s in fStates ]) 

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
