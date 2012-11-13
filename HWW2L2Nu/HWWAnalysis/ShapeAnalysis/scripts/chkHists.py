#!/usr/bin/env python

import ROOT
import sys
import HWWAnalysis.Misc.ROOTAndUtils as utils
from HWWAnalysis.Misc.odict import OrderedDict
import optparse
import re
import console

recolors = re.compile('\\x1b\[[0-9;]*?[0-9]{2}m')

def screenlen( str ):
    plain = recolors.sub('',str)
    return len(plain)

def coljust( str, width, align='left' ):
    plain = recolors.sub('',str)
    dl = len(str)-len(plain)
    if align=='left':
        aligner = str.ljust
    elif align=='right':
        aligner = str.rjust
    elif align=='center':
        aligner = str.center
    else:
        raise ValueError('justificator: '+align+' not known')

    return aligner(width+dl)


#------------------------------------------------------------------------------
def GetHistPaths( path ):
    rootFile = ROOT.TFile.Open(path)

    finder = utils.ObjFinder('TH1D')

    names = finder.findRecursive(rootFile)

    plist = rootFile.Get('processes')
    processes = [ p.GetName() for p in plist ] if plist.__nonzero__() else None

    return rootFile,names,processes

#------------------------------------------------------------------------------
def PrintTable( table, title, missing, width, colhdr=None ):
    allNames=set()
    for arg,histograms in table.iteritems():
        allNames.update(set(histograms))

    labelLen = max(map(len,list(allNames)+[title]))

    hdr = []
    print '*'*labelLen
    for i,f in enumerate(table.iterkeys()):
        h = ['']*len(missing)
        fid = '[file %d]' % i
        print fid,'=',f
        h[-1]=fid
        hdr.append(h)
    print '*'*labelLen

    width = max( map(lambda x: max(map(len,x)),hdr)+[width] ) 
    
    line=''
    line += title.ljust(labelLen)
    for h in hdr:
        line+= ' | '+' '.join([coljust(x,width) for x in h])
    line += ' |'
    print line
    print '-'*len(line)
    if colhdr:
        line = ' '*labelLen
        line += (' | '+' '.join([coljust(x,width,'right') for x in colhdr]))*len(table)
        line += ' |'
        print line
        
        print '-'*len(line)
    sortNames = sorted(allNames)
    for name in sortNames:
        line = name.ljust(labelLen)
        for arg,entry in table.iteritems():
            if name in entry:
                tmp = entry[name]
            else:
                tmp = missing

            line += ' | '+' '.join([coljust(x,width,'right') for x in tmp])

        line += ' |'
        print line
    print '-'*screenlen(line)



if __name__ == '__main__':
    usage = 'usage: %prog [dir] [cmd]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-a','--all',dest='all',action='store_true',default=False)
    parser.add_option('-d','--diff',dest='diff',action='store_true',help='check different histograms among the files',default=False)
    parser.add_option('-s','--stat',dest='stat',action='store_true',help='check statistics',default=False)
    parser.add_option('-o','--over',dest='over',action='store_true',help='show under/overflow',default=False)
    (opt, args) = parser.parse_args()

    sys.argv.append('-b')

    files = OrderedDict()

    
    entries = OrderedDict()
    for arg in args:
        (file,names,processes) = GetHistPaths(arg)

        if processes and not opt.all:
            hp = [ 'histo_'+p for p in processes]
            names = [ n for n in names if n in hp ]
        
        files[arg] = (file,names,processes)


    if opt.diff:
        for arg,(file,names,processes) in files.iteritems():
            
            others = files.copy()
            del others[arg]
            ofiles = set()
            map(lambda x: ofiles.update(x[1]), others.itervalues())

            only = set(names)-ofiles
            print '-'*80
            print 'Histograms only in',arg,':'
            print '-'*80
            for h in only: print '   ',h
        sys.exit(0)



    entries = OrderedDict()

#     for arg in files:
#         (file,names,processes) = GetHistPaths(arg)

    for arg,(file,names,processes) in files.iteritems():
        entries[arg] = {}
        
        for name in sorted(names):
            h = file.Get(name)
            xax = h.GetXaxis()
            entries[arg][name] = [h.GetEntries(),h.Integral(),h.GetBinContent(0),h.GetBinContent(1),h.GetBinContent(h.GetNbinsX()),h.GetBinContent(h.GetNbinsX()+1)]
        file.Close()


    missing=['-']*6 if opt.over else ['-']*2

    if opt.stat:
        missing = ['-']
        zeroes = OrderedDict()
        lowstat = OrderedDict()
        lsheader = ['int/nentr','nentr','int']
        for arg in sorted(entries):
            zeroes[arg] = {}
            lowstat[arg] = {}
            histograms = entries[arg]
            for name,(n,i,uf,of,b1,bn) in histograms.iteritems():
                if not n:
                    zeroes[arg][name] = ['\x1b[41m'+console.colorize('white','0')]

                if opt.all or n > 0 and i/n > 1:
                    lowstat[arg][name] = [ '%.2f' % x for x in [i/n if n!=0 else -1,n,i] ]
            
        PrintTable(zeroes, 'zeroes',missing,5)
        PrintTable(lowstat,'lowstat',['-']*3,9,lsheader)
        sys.exit(0)
    else:
        lsheader = ['entries','I']
        if opt.over: lsheader += ['uf','b1','bn','of']
        table = OrderedDict()
        for arg in sorted(entries):
            table[arg] = {}
            histograms = entries[arg]
            for name,(n,i,uf,b1,bn,of) in histograms.iteritems():
                entry = ['%.f'%n,'%.3f'%i]
                if opt.over:
                    entry += ['%.3f'%x for x in (uf,b1,bn,of) ]
                table[arg][name]=entry
        PrintTable(table,'nentries',missing,5, lsheader)






