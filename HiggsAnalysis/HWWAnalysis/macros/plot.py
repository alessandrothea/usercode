#!/usr/bin/env python

import optparse
import sys
import ROOT
import string
import re
import shlex
import csv

class TH1AddDirSentry:
    def __init__(self):
        self.status = ROOT.TH1.AddDirectoryStatus()
        ROOT.TH1.AddDirectory(False)
        
    def __del__(self):
        ROOT.TH1.AddDirectory(self.status)

class BlankCommentFile:
    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        return self

    def next(self):
#        line = re.sub('#.*','',self.fp.next())
        line = self.fp.next().strip()
        if not line or line.startswith('#'):
#        if not line.strip() :
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
        self.entries = 0
        self.xSec = 0.
        self.kFact = 1
        self.color = ROOT.kBlack
        self.legend = ''
        self.file = None

class Plotter:
    def __init__(self):
        self.plots = {}
        self.dataSamples = []
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
        self.dataSamples = []
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
            e.color = eval(r[4])
            e.legend = r[5]
            
#            print type,e.__dict__
            if type == 'data':
                self.dataSamples.append(e)
            elif type == 'mc':
                self.mcSamples.append(e)
            else:
                raise NameError('Sample type '+type+' what?')
    
    def connect(self):
        for e in self.dataSamples:
            e.file = ROOT.TFile(e.path)
            if not e.file.IsOpen():
                raise NameError('file '+e.path+' not found')
            entries = e.file.Get('entries')
            #print entries
            e.entries = entries.GetBinContent(1)
#            print e.path,e.entries
            
        for e in self.mcSamples:
            e.file = ROOT.TFile(e.path)
            if not e.file.IsOpen():
                raise NameError('file '+e.path+' not found')
#            e.file.ls()
            entries = e.file.Get('entries')
#            print entries
            e.entries = entries.GetBinContent(1)

    def getHistograms(self,samples,name,prefix):
                
#        print self.plots
        plot = self.plots[name]
        if ( plot is None ):
            raise NameValue('Plot '+name+' not found');
        
#        ROOT.TH1.AddDirectory(False)
        sentry = TH1AddDirSentry()

        histograms = []
        for s in samples:
            h = s.file.Get(plot.name)
            if not h.__nonzero__():
                raise NameError('histogram '+plot.name+' not found in '+e.path)
            hClone = h.Clone(prefix+'_'+plot.name)
            hClone.SetFillColor(s.color)
            hClone.SetLineColor(1)
#            print s.color
            #hClone.Sumw2()
            histograms.append(hClone)

        return histograms

    def getDataHistograms(self,name):
        return self.getHistograms(self.dataSamples,name,"data")
    
    def getMCHistograms(self,name):
        return self.getHistograms(self.mcSamples,name,"mc")
    
    def normalize(self, histograms, samples ):
        if len(histograms) != len(samples):
            raise ValueError('Trying to normalize apples and carrots')
        
        for i in range(len(histograms)):
            s = samples[i]
            h = histograms[i]
            N = s.xSec*self.luminosity
            fact = N / s.entries
            h.Sumw2()
            h.Scale(fact)
            print '%f\t%d\t%f\t%s'%(s.xSec, N, fact, s.path)
            
    def makePlot(self,name):
        pl = self.plots[name]
        data = self.getDataHistograms(name)
        mc   = self.getMCHistograms(name)
        
        self.normalize(mc, self.mcSamples)
#        print data,len(data),mc,len(mc)
        stack = ROOT.THStack(data[0].GetName(),data[0].GetTitle())
        legend = ROOT.TLegend(0.7 ,0.7,0.95,0.95)
        legend.SetFillColor(ROOT.kWhite)
        legend.AddEntry(data[0], self.dataSamples[0].legend,'p')
        for i in range(len(mc)):
            stack.Add(mc[i],'hist')
            legend.AddEntry(mc[i],self.mcSamples[i].legend,'f')
        cName = 'c_'+name.replace('/','_')
        c = ROOT.TCanvas(cName)
        c.Set
        print '- logx =', pl.logX, ': logy =',pl.logY
        max = ROOT.TMath.Max(data[0].GetMaximum(),stack.GetMaximum())
        min = ROOT.TMath.Min(data[0].GetMinimum(),stack.GetMinimum())
        
        if pl.logX is 1:
            c.SetLogx()
            
        if pl.logY is 1:
            c.SetLogy()
            if min==0.:
                min = 1
            max *= ROOT.TMath.Power(max/min,0.1)
            min /= ROOT.TMath.Power(max/min,0.1)
        else:
            max += (max-min)*0.1
            min -= (max-min)*0.1

        frame = data[0].Clone('frame')
        frame.Reset()
        frame.SetMaximum(max)
        frame.SetMinimum(min)
        frame.SetBit(ROOT.TH1.kNoStats)
        frame.Draw()
        data[0].SetFillColor(1);
        data[0].SetMarkerColor(1);
        data[0].SetMarkerStyle(20);
        data[0].SetMarkerSize(0.7);
        
        stack.Draw('same')
        data[0].Draw('e1 same')

        legend.Draw()
        c.Write()

        
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-p', '--plotList', dest='plotList', help='Name of the tree', )
    parser.add_option('-s', '--sampleList', dest='sampleList', help='Path to the rootfile', )
    parser.add_option('-o', '--outputFile', dest='outputFile', help='new rootfile', )

    (opt, args) = parser.parse_args()

    if opt.plotList is None:
        parser.error('No plot list defined')
    if opt.sampleList is None:
        parser.error('No list of sample defined')
#    if opt.outputFile is None:
#        parser.error('No output file')
#        



    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()
    ROOT.gSystem.Load("lib/libHWWNtuple.so")
    
    out = ROOT.TFile.Open('results.root','recreate')
    
    p = Plotter()
    try:
        p.readPlots(opt.plotList)
        p.readSamples(opt.sampleList)
        p.connect()
        #name = 'fullSelection/llCounters'
        out.cd()
        for name in p.plots.iterkeys():
            p.makePlot(name)
       
    except ValueError as e:
        print e
    except NameError as e:
        print e
    out.Write()
    out.Close()
    print 'lumi =',p.luminosity
#    print len(p.samples)
#    print len(p.mcSamples)
    


if __name__ == '__main__':
    main()
