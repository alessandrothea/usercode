#!/usr/bin/env python
import sys
import optparse


args = sys.argv[:]
sys.argv.append( '-b' )
import ROOT
ROOT.gROOT.SetBatch()

#print args, len(args)

if len(args) is not 2:
    print '   Usage: selectEff <path>'
    sys.exit(0)

ROOT.gSystem.Load('lib/libHWWNtuple.so')

f = ROOT.TFile(args[1])

fStates = ['ll','ee','em','mm']

prefix='fullSelection/'

for s in fStates:
    print '\n-',s+'Counters'
    counters = f.Get(prefix+s+'Counters')
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
        
        print '  %s = %d - %.3f%% (%.3f%%)' % (labelAbs.ljust(15), theBin,absEff, relEff)
        

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