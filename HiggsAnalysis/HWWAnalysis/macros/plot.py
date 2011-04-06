#!/usr/bin/env python

import optparse
import sys
import ROOT
import string
import re
import shlex
import csv

class BlankCommentFile:
    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        return self

    def next(self):
        line = re.sub('#.*','',self.fp.next())
        if not line.strip() :
            return self.next()
        return line

class plotEntry:
    def __init__(self):
        self.name = ''
        self.logX = False
        self.logY = False
        self.xAxis = 'x'

class sampleEntry:
    def __init__(self):
        self.path = ''
        self.xSec = 0.
        self.kFact = 1
        self.color = ROOT.kBlack
        self.legend = ''
        self.file = None

class Plotter:
    def __init__(self):
        self.plots = {}
        self.samples = []
        self.mcSamples = []
        self.luminosity = 0
        self.baseDir = ""
    
    def readPlots(self,file):
        f = BlankCommentFile(open(file,'r'))
        rows = [shlex.split(line) for line in f]
    
        self.plots= {}
        for r in rows:
            d = plotEntry()
            d.name = r[0]
            d.logX = int(r[1])
            d.logY = int(r[2])
            self.plots[d.name] = d
    
    def readSamples(self,file):
        self.samples = []
        self.mcSamples = []
        f = BlankCommentFile(open(file,'r'))
        rows = [shlex.split(line) for line in f]
        for r in rows:
            
            if (r[0],r[1]) == ('LUMI','='):
                self.luminosity = float(r[2])
                continue
            elif (r[0],r[1]) ==('PATH','='):
                self.baseDir = r[2]
                continue
                
            e = sampleEntry()
            e.path = self.baseDir+'/'+r[0]
            type = r[1]
            e.xSec  = float(r[2])
            e.kFact = float(r[3])
            e.color = int(r[4])
            e.legend = r[5]
            
#            print type,e.__dict__
            if type == 'data':
                self.samples.append(e)
            elif type == 'mc':
                self.mcSamples.append(e)
            else:
                raise NameError('Sample type '+type+' what?')
    
    def connect(self):
        for e in self.samples:
            e.file = ROOT.TFile(e.path)
            if not e.file.IsOpen():
                raise NameError('file '+e.path+' not found')
            
        for e in self.mcSamples:
            e.file = ROOT.TFile(e.path)
            if not e.file.IsOpen():
                raise NameError('file '+e.path+' not found')
#            e.file.ls()

    def getMCHistograms(self,name):
        
        print self.plots
        plot = self.plots[name]
        if ( plot is None ):
            raise NameValue('Plot '+name+' not found');
        
        ROOT.TH1.AddDirectory(False)

        histograms = []
        for e in self.mcSamples:
            h = e.file.Get(plot.name)
            if not h.__nonzero__():
                raise NameError('histogram '+plot.name+' not found in '+e.path)
            hClone = h.Clone('mc_'+plot.name)
#            hClone.Sumw2()
            histograms.append(hClone)

        return histograms
            
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-p', '--plotList', dest='plotList', help='Name of the tree', )
    parser.add_option('-s', '--sampleList', dest='sampleList', help='Path to the rootfile', )

    (opt, args) = parser.parse_args()

    if opt.plotList is None:
        parser.error('No file list')

    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()
    ROOT.gSystem.Load("lib/libHWWNtuple.so")
    
    p = Plotter()
    try:
        p.readPlots(opt.plotList)
        p.readSamples(opt.sampleList)
        p.connect()
        mc = p.getMCHistograms('llCounters')
        print mc
    except ValueError as e:
        print e
    except NameError as e:
        print e
        
    print 'lumi =',p.luminosity
#    print len(p.samples)
#    print len(p.mcSamples)
    


if __name__ == '__main__':
    main()
