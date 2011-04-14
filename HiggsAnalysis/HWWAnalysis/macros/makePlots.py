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
        self.title = 'title'
        self.xAxis = 'x'
        self.rebin = 1
        self.xtitle = ''
        self.ytitle = ''

class sampleEntry:
    def __init__(self):
        self.path = ''
        self.entries = 0
        self.sum = "no"
        self.xSec = 0.
        self.kFact = 1
        self.fillColor = ROOT.kBlack
        self.lineColor = ROOT.kBlack
        self.lineWidth = 1
        self.legend = ''
        self.file = None
        self.order = -1

class Plotter:
    def __init__(self):
        self.plots = {}
        self.dataSamples = []
        self.mcSamples = []
        self.virSamples = []
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
            d.rebin = int(r[3])
            d.title = r[4]
            d.xtitle = r[5]
            d.ytitle = r[6]
            self.plots[d.name] = d
    
    def readSamples(self,file):
        self.dataSamples = []
        self.mcSamples = []
        self.virSamples = []
        f = BlankCommentFile(open(file,'r'))
        rows = [shlex.split(line) for line in f]
        i = 0
        for r in rows:
            i += 1
            if (r[0],r[1]) == ('LUMI','='):
                self.luminosity = float(r[2])
                continue
            elif (r[0],r[1]) ==('PATH','='):
                self.baseDir = r[2]
                continue
                
            e = sampleEntry()
            e.path      = r[0]
            type        = r[1]
            e.sum       = r[2]
            e.xSec      = float(r[3])
            e.kFact     = float(r[4])
            e.fillColor = eval(r[5])
            e.lineColor = eval(r[6])
            e.lineWidth = int(r[7])
            e.legend    = r[8]
            e.order = i
            
#            print type,e.__dict__
            if type == 'data':
                self.dataSamples.append(e)
            elif type == 'mc':
                self.mcSamples.append(e)
            elif type == 'sum':
                self.virSamples.append(e)
            else:
                raise NameError('Sample type '+type+' what?')
    
    def connect(self):
        for e in self.dataSamples:
            fullPath = self.baseDir+'/'+e.path
            e.file = ROOT.TFile(fullPath)
            if not e.file.IsOpen():
                raise NameError('file '+e.path+' not found')
            entries = e.file.Get('entries')
            #print entries
            e.entries = entries.GetBinContent(1)
#            print e.path,e.entries
            
        for e in self.mcSamples:
            fullPath = self.baseDir+'/'+e.path
            e.file = ROOT.TFile(fullPath)
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
            hClone.UseCurrentStyle()
            hClone.SetFillColor(s.fillColor)
            hClone.SetLineColor(s.lineColor)
            hClone.SetLineWidth(s.lineWidth)

            histograms.append( (hClone,s) )

        return histograms

    def getDataHistograms(self,name):
        return self.getHistograms(self.dataSamples,name,"data")
    
    def getMCHistograms(self,name):
        return self.getHistograms(self.mcSamples,name,"mc")
    
    def normalize(self, histograms ):

        for (h,s) in histograms:

            N = s.xSec*self.luminosity
            fact = N / s.entries
            h.Sumw2()
            h.Scale(fact)
            print '%f\t%d\t%f\t%s'%(s.xSec, N, fact, s.path)
    
    def sum(self, histograms):#, samples):
#        if len(histograms) != len(samples):
#            raise ValueError('Trying to normalize apples and carrots')
        sentry = TH1AddDirSentry()

        summed = []
        sumList = {}
#        for i in range(len(histograms)):
        # make a map and remove the histograms not to sum
        
        for (h,s) in histograms:
            if s.sum == 'no':
                summed.append((h,s))
                continue
            if not s.sum in sumList:
                sumList[s.sum] = [h]
            else:
                sumList[s.sum].append(h)
        
        virKeys = [ sample.path for sample in self.virSamples]
        
        for name,hists in sumList.iteritems():
            if not name in virKeys:
                raise ValueError('Virtual sample '+name+' not defined')
            i = virKeys.index(name)
            vs = self.virSamples[i]
            h0 = hists[0].Clone(name)
            h0.Reset()
#            h0.Sumw2()
            for h in hists:
                h0.Add(h)
            h0.SetFillColor(vs.fillColor)
            h0.SetLineColor(vs.lineColor)
            h0.SetLineWidth(vs.lineWidth)
            
            summed.append( (h0,vs) )
            
        # re-sort the array on the file's order
        sumsorted = sorted( summed, key=lambda pair: pair[1].order)
#        print [(h.GetName(), s.path) for (h,s) in sumsorted]
        # return histograms;
        return sumsorted
    
    def makeLegend(self, data = [], mc = []):
                
        allSamples = []
        allSamples.extend(data)
        allSamples.extend(mc)
        
        entries = [ ROOT.TLatex(0,0,sample.legend) for (h,sample) in allSamples ]
        
        Dx = max([txt.GetXsize() for txt in entries])        
        dy = entries[0].GetYsize()
        rows = len(entries)+1
        
        x1 = 0.95
        y1 = 0.95
        
        x0 = x1-Dx
        y0 = y1-dy*1.1*rows
        
        legend = ROOT.TLegend(x0,y0,x1,y1)
        legend.SetFillColor(ROOT.kWhite)

        for (h,s) in data:
            legend.AddEntry(h, s.legend,'p')
       
        for (h,s) in mc:

            legend.AddEntry(h,s.legend,'f')
        
        return legend
    
    def makeDataMCPlot(self,name):
        pl = self.plots[name]
        data = self.getDataHistograms(name)
        mc   = self.getMCHistograms(name)
        
        self.normalize(mc) #, self.mcSamples)
        
        mc   = self.sum(mc) #,self.mcSamples)
        (data0, sample0) = data[0]
        stack = ROOT.THStack('mcstack_'+name,data0.GetTitle())
            
        if pl.rebin != 1:
            data0.Rebin(pl.rebin)
        mcMinima = []    
        for (h,s) in mc:
            if pl.rebin != 1:
                h.Rebin(pl.rebin)
            mcMinima.append(h.GetMinimum())
            stack.Add(h,'hist')
            

        cName = 'c_'+name.replace('/','_')
        c = ROOT.TCanvas(cName)
        c.SetTicks();
        print '- logx =', pl.logX, ': logy =',pl.logY
        maxY = ROOT.TMath.Max(data0.GetMaximum(),stack.GetMaximum())
        minY = ROOT.TMath.Min(data0.GetMinimum(),min(mcMinima))
        
        if pl.logX is 1:
            c.SetLogx()
            
        if pl.logY is 1:
            c.SetLogy()
            if minY==0.:
                minY = 0.1
            maxY *= ROOT.TMath.Power(maxY/minY,0.1)
            minY /= ROOT.TMath.Power(maxY/minY,0.1)
        else:
            maxY += (maxY-minY)*0.1
            minY -= (maxY-minY)*0.1
    

        frame = data0.Clone('frame')
        frame.Reset()
        frame.SetMaximum(maxY)
        frame.SetMinimum(minY)
        frame.GetYaxis().SetLimits(minY,maxY)
        frame.SetBit(ROOT.TH1.kNoStats)
        frame.SetTitle(pl.title)
        frame.SetXTitle(pl.xtitle)
        frame.SetYTitle(pl.ytitle)
        frame.Draw()
        data0.SetFillColor(1);
        data0.SetMarkerColor(1);
        data0.SetMarkerStyle(20);
        data0.SetMarkerSize(0.7);
        
        stack.Draw('same')
        data0.Draw('e1 same')

        legend = self.makeLegend(data,mc)
        legend.Draw()
        c.Write()
        
    def makeMCStackPlot(self,name,nostack):
        raise ValueError('I\'m broken')
        pl = self.plots[name]
        mc = self.getMCHistograms(name)
        
        
        self.normalize(mc, self.mcSamples)

        stName = name.replace('/','_')
        stack = ROOT.THStack(stName,pl.title)
                
        for i in range(len(mc)):
            stack.Add(mc[i],'hist')

        cName = 'c_'+name.replace('/','_')
        c = ROOT.TCanvas(cName)
        c.SetTicks();
        print '- logx =', pl.logX, ': logy =',pl.logY
#        max = ROOT.TMath.Max(data[0].GetMaximum(),stack.GetMaximum())
#        min = ROOT.TMath.Min(data[0].GetMinimum(),stack.GetMinimum())
        
        if pl.logX is 1:
            c.SetLogx()
            
        if pl.logY is 1:
            c.SetLogy()
        
        opt = ''
        if nostack:
            opt = opt+'nostack'
        stack.Draw(opt)

        legend = self.makeLegend(mc=mc)
        legend.Draw()
        c.Write()

        
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-p', '--plotList', dest='plotList', help='Name of the tree', )
    parser.add_option('-s', '--sampleList', dest='sampleList', help='Path to the rootfile', )
    parser.add_option('-o', '--outputFile', dest='outputFile', help='new rootfile', )
    parser.add_option('-m', '--mode', dest='mode', help='mode [data,mc]', default='data')
    parser.add_option('--nostack', dest='nostack', help='nostack', action="store_true")

    (opt, args) = parser.parse_args()

    if opt.plotList is None:
        parser.error('No plot list defined')
    if opt.sampleList is None:
        parser.error('No list of sample defined')
    if opt.outputFile is None:
        parser.error('No output file')
        
    if opt.mode != 'data' and opt.mode != 'mc':
        parser.error('Mode not recognized')
        
    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()
    ROOT.gSystem.Load("lib/libHWWNtuple.so")
    
    ROOT.gStyle.SetTitleAlign(21)
    ROOT.gStyle.SetTitleX(0.5)
    ROOT.gStyle.SetTitleY(0.9)
    ROOT.gStyle.SetFrameLineWidth(2)
    ROOT.gStyle.SetTitleStyle(0)
    ROOT.gStyle.SetTitleFont(42,"xyz")
    ROOT.gStyle.SetTitleFont(42,"")
    ROOT.gStyle.SetLabelFont(42,"xyz")
    ROOT.gStyle.SetTextFont(42)   
    
    out = ROOT.TFile.Open(opt.outputFile,'recreate')
    
    p = Plotter()
    try:
        p.readPlots(opt.plotList)
        p.readSamples(opt.sampleList)
        p.connect()
        #name = 'fullSelection/llCounters'
        out.cd()
        if opt.mode=='data':
            for name in p.plots.iterkeys():
                p.makeDataMCPlot(name)
        elif opt.mode=='mc':
            for name in p.plots.iterkeys():
                print name
                p.makeMCStackPlot(name,opt.nostack)
       
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
