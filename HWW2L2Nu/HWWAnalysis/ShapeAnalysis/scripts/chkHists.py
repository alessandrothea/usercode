#!/usr/bin/env python

import ROOT
import sys
import HWWAnalysis.Misc.ROOTAndUtils as utils
from HWWAnalysis.Misc.odict import OrderedDict
import optparse
import re


def GetHistograms( path ):
#     print path
    rootFile = ROOT.TFile.Open(path)

    finder = utils.ObjFinder("TH1D")

    names = finder.findRecursive(rootFile)
    return rootFile,names

if __name__ == '__main__':
    usage = 'usage: %prog [dir] [cmd]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-a','--all',dest='all',action='store_true',default=False)
    (opt, args) = parser.parse_args()

    files = {}
    
    allNames=set()
    for arg in args:
        (file,names) = GetHistograms(arg)
        files[arg] = (file,names)
        allNames.update(set(names))

    for arg,(file,names) in files.iteritems():
        missing =allNames-set(names)
        if len(missing) != 0:
            print 'Missing histograms in',arg
            print '   ',', '.join(missing)

#     namesPerFile = [ names for path,(file,names) in files.iteritems() ]
#     if not namesPerFile:
#         raise RuntimeError('No arguments define? No histograms')
#     if not len(namesPerFile)==namesPerFile.count(namesPerFile[0]):
#         print 'Histogram name mismatch:'
#         for path,(file,names) in files.iteritems():
#             print path,', '.join(names)

#     print 'Histogram names consistency check: OK'

#     check histogram list
    entries = OrderedDict()

    for arg in files:
        (file,names) = GetHistograms(arg)
#         print '*'*80
        entries[arg] = {}
        
        for name in sorted(names):
            h = file.Get(name)
            xax = h.GetXaxis()
#             entries[arg][name] = [h.GetEntries(),h.Integral(),xax.GetNbins(),xax.GetXmin(), xax.GetXmax()]
            entries[arg][name] = [h.GetEntries(),h.Integral()]
#             print 'name {0:<20} {1:<10} {2:<10}'.format(name,h.GetEntries(),h.Integral())

    nomRegex  = re.compile('^histo_([^_]+)$')
    colfmt = '{0:<15}'

    hdr = []
    print '*'*80
    for i,f in enumerate(entries.iterkeys()):
        fid = 'file'+str(i)
        print fid,'=',f
        hdr.append([fid,''])
    print '*'*80
    
    line=''

    print
#     print ' '*40,' '.join([colfmt.format(h) for h in hdr])
    line += ' '*40
    for h in hdr:
        line+= ' | '+' '.join([colfmt.format(x) for x in h])
    line += ' |'
    print line
    print '-'*len(line)
    sortNames = sorted(allNames)
    for name in sortNames:
        if not ( opt.all or nomRegex.match(name)):
            continue
        line = name.ljust(40)
#         print name.ljust(40),
        for arg,entry in entries.iteritems():
            if name in entry:
                tmp = entry[name]
            else:
                tmp = ['-']*2

            line += ' | '+' '.join([colfmt.format(x) for x in tmp])
#             print '|',' '.join([colfmt.format(x) for x in tmp]),

#         print ' |'
        line += ' |'
        print line
    print '-'*len(line)

