#!/usr/bin/env python

import optparse
import sys
import ROOT
import string
import re
import shlex
import csv
import os.path
import tempfile
import fnmatch
import copy
import HWWAnalysis.Misc.ROOTAndUtils as utils

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
        self.sFact = 1
        self.fillColor = ROOT.kBlack
        self.lineColor = ROOT.kBlack
        self.lineWidth = 1
        self.legend = ''
        self.file = None
        self.order = -1

class PlotReader:
    def __init__(self, filename, variables = {} ):
        self.filename = filename
        self.variables = variables
        self.metaPlots = None
        self.plots     = None
        self.load()

    def load(self): 
        template = string.Template(open(self.filename).read())

        spoolFile = tempfile.TemporaryFile()
        spoolFile.write(template.safe_substitute(self.variables))
        # rewind
        spoolFile.seek(0)

        f = utils.BlankCommentFile(spoolFile)
        rows = [shlex.split(line) for line in f]
    
        self.metaPlots= {}
        for r in rows:
            d = plotEntry()
            d.name = r[0]
            d.logX = int(r[1])
            d.logY = int(r[2])
            d.rebin = int(r[3])
            d.title = r[4]
            d.xtitle = r[5]
            d.ytitle = r[6]
            self.metaPlots[d.name] = d

    def match(self, rootfile):
        finder = utils.ObjFinder('TH1')
        paths = set(finder.find(rootfile))
    
        notFound = []
        self.plots = {}

        for name,metaPlot in self.metaPlots.iteritems():
#             print name
            matches = fnmatch.filter(paths,name)
            if len(matches) == 0:
                notFound.append(name)
            for m in matches:
                p = copy.copy(metaPlot)
                p.name = m
                self.plots[m] = p

#         print '\n'.join(self.plots.iterkeys())
        if len(notFound):
            raise RuntimeError('Histograms not found! '+','.join(notFound))

        return self.plots

class Plotter:
    def __init__(self):
        self.plots = {}
        self.dataSamples = []
        self.mcSamples = []
        self.virSamples = []
        self.luminosity = 0
        self.baseDir = ""
        self.outFile = None
        self.verbosity = 0
        self.variables = {}

    def __del__(self):
        if self.outFile:
            self.outFile.cd()
            ROOT.gStyle.Write('theStyle')
            self.outFile.Write()
            self.outFile.Close()
    
    def setVariables(self, varString ):
        tokens = varString.split(' ')
        for token in tokens:
            key,_,value = token.partition('=')
            if key == token:
                raise NameError('Malformed variable declaration '+arg)

            self.variables[key] = value

    def setLuminosity(self,lumi ):
        self.luminosity = lumi
        self.variables['luminosity'] = lumi


    def getTDir(self,path):
        if path == '':
            return self.outFile
        else:
            return self.outFile.Get(path)

    def openFile(self,filename):
        self.outFile = ROOT.TFile.Open(filename,'recreate')
        
        dirSet = set()
        for name in self.plots.iterkeys():
            path = os.path.dirname(name);
            subDirs = path.split('/')
            dir=''
            for p in subDirs:
                dir += p+'/'
                dirSet.add(dir[:-1])

        copyDirs = sorted(dirSet, key=lambda d: len(d))
        for d in copyDirs:
            parent = os.path.dirname(d)
            child = os.path.basename(d)
            
            self.getTDir(parent).mkdir(child)

        self.outFile.cd()
        

    def readPlots(self,plotFile):
        reader = PlotReader(plotFile, self.variables)
        f = self.mcSamples[0].file
        self.plots = reader.match(f)
    
    def readSamples(self,filename):

        self.dataSamples = []
        self.mcSamples = []
        self.virSamples = []
        
        template = string.Template(open(filename).read())

        spoolFile = tempfile.TemporaryFile()
        spoolFile.write(template.safe_substitute(self.variables))
        # rewind
        spoolFile.seek(0)

        f = utils.BlankCommentFile(spoolFile)
        rows = [shlex.split(line) for line in f]
        i = 0
        for r in rows:
            i += 1
            if (r[0],r[1]) == ('LUMI','='):
                # set the luminosity if not already set by cmd line
                if self.luminosity == 0:
                    self.setLuminosity(float(r[2]) )
                continue
            elif (r[0],r[1]) ==('PATH','='):
                # set if not already defined in cmd line
                if self.baseDir == '':
                    self.baseDir = r[2]
                continue
                
            e = sampleEntry()
            e.path      = r[0]
            type        = r[1]
            e.sum       = r[2]
            e.xSec      = float(r[3])
            e.sFact     = float(r[4])
            e.fillColor = eval(r[5])
            e.lineColor = eval(r[6])
            e.lineWidth = int(r[7])
            e.legend    = r[8]
            e.order = i
            
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
            e.entries = entries.GetBinContent(1)
            
        for e in self.mcSamples:
            fullPath = self.baseDir+'/'+e.path
            e.file = ROOT.TFile(fullPath)
            if not e.file.IsOpen():
                raise NameError('file '+e.path+' not found')
            entries = e.file.Get('entries')
            e.entries = entries.GetBinContent(1)

    def getHistograms(self,samples,name,prefix):
                
        plot = self.plots[name]
        if ( plot is None ):
            raise NameValue('Plot '+name+' not found');
        
        sentry = utils.TH1AddDirSentry()

        histograms = []
        for s in samples:
            h = s.file.Get(plot.name)
            if not h.__nonzero__():
                raise NameError('histogram '+plot.name+' not found in '+s.path)
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

            fact = s.sFact*self.luminosity/1000.
            h.Sumw2()
            h.Scale(fact)
            if self.verbosity > 1:
                print '%f\t%f\t%s'%(s.sFact, fact, s.path)

    def sum(self, histograms):#, samples):
        sentry = utils.TH1AddDirSentry()

        summed = []
        sumList = {}
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
            for h in hists:
                h0.Add(h)
            h0.SetFillColor(vs.fillColor)
            h0.SetLineColor(vs.lineColor)
            h0.SetLineWidth(vs.lineWidth)
            
            summed.append( (h0,vs) )
            
        # re-sort the array on the file's order
        sumsorted = sorted( summed, key=lambda pair: pair[1].order)
        # return histograms;
        return sumsorted
    
    def makeLegend(self, data = [], mc = []):
                
        allSamples = []
        allSamples.extend(data)
        allSamples.extend(mc)
        
        entries = [ ROOT.TLatex(0,0,sample.legend) for (h,sample) in allSamples ]
        
        shrink = 0.7
        Dx = shrink * max([txt.GetXsize() for txt in entries])        
        dy = shrink * entries[0].GetYsize()
        rows = len(entries)+1
        
        x1 = 0.885
        y1 = 0.885
        
        x0 = x1-Dx
        y0 = y1-dy*1.1*rows
        
        legend = ROOT.TLegend(x0,y0,x1,y1)
        legend.SetFillColor(ROOT.kWhite)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)

        for (h,s) in data:
            legend.AddEntry(h, s.legend,'p')
       
        for (h,s) in mc:

            legend.AddEntry(h,s.legend,'f')
        
        return legend

    def makeCMSText(self):
        lines = [ 'CMS Preliminary','#sqrt{s}=7 TeV']

        entries = [ ROOT.TLatex(0,0,line) for line in lines ]
        
        shrink = 0.7
        Dx = shrink * max([txt.GetXsize() for txt in entries])
        dy = shrink*entries[0].GetYsize()

        x0 = 0.115
        y1 = 0.885

        x1 = x0 + Dx
        y0 = y1-dy*len(lines)-0.01*(len(lines)-1)

        pave = ROOT.TPaveText(x0,y0,x1,y1,'ndc')
        pave.SetFillColor(ROOT.kRed)
        pave.SetBorderSize(0)
        pave.SetFillStyle(0)

        pave.SetName('preliminary')

        for line in lines:
            pave.InsertText(line)

        return pave
        l = ROOT.TLatex(0.5,0.5,'CMS')
        l.SetTextSize(0.7*l.GetTextSize())
        l.SetBit(ROOT.TLatex.kTextNDC)
        l.SetTextAlign(13)
        l.SetNDC()

        x0 = 0.11
        y0 = 0.89

        txts = []

        l1 = l.Clone()
        l1.SetText(x0,y0,'CMS Preliminary')
        txts.append(l1)
        l2 = l.Clone()
        l2.SetText(x0, y0-1.1*l.GetYsize(),'#sqrt{s} = 7 TeV')
        txts.append(l2)

        return txts

    
    def makeDataMCPlot(self,name):

        # save the old dir
        oldDir = ROOT.gDirectory
        #and go to the new one
        path = os.path.dirname(name)
        self.getTDir(path).cd()

        # but don't write the plots
        sentry = utils.TH1AddDirSentry()
        pl = self.plots[name]
        data = self.getDataHistograms(name)
        mc   = self.getMCHistograms(name)
        
        self.normalize(mc) #, self.mcSamples)
        
        mc   = self.sum(mc) #,self.mcSamples)
        (data0, sample0) = data[0]
        baseName = os.path.basename(name)
        stack = ROOT.THStack('mcstack_'+baseName,data0.GetTitle())
            
        if pl.rebin != 1:
            data0.Rebin(pl.rebin)
        mcMinima = []    
        for (h,s) in mc:
            if pl.rebin != 1:
                h.Rebin(pl.rebin)
            mcMinima.append(h.GetMinimum())
            stack.Add(h,'hist')
            
        cName = 'c_'+baseName
        c = ROOT.TCanvas(cName,cName,-2)
#         print c.GetWw(),c.GetWh()
        c.SetTicks();
        c.Size(30,30)
#         print '- logx =', pl.logX, ': logy =',pl.logY
        maxY = ROOT.TMath.Max(data0.GetMaximum(),stack.GetMaximum())
        minY = ROOT.TMath.Min(data0.GetMinimum(),min(mcMinima))
        
        if pl.logX is 1:
            c.SetLogx()
            
        if pl.logY is 1 and not (maxY == minY == 0):
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
        frame.SetTitle(pl.title if pl.title != 'self' else data0.GetTitle())
        frame.SetXTitle(pl.xtitle if pl.xtitle != 'self' else data0.GetXaxis().GetTitle())
        frame.SetYTitle(pl.ytitle if pl.xtitle != 'self' else data0.GetYaxis().GetTitle())
        frame.Draw()
        data0.SetFillColor(1);
        data0.SetMarkerColor(1);
        data0.SetMarkerStyle(20);
        data0.SetMarkerSize(0.7);
        
        stack.Draw('same')
        data0.Draw('e1 same')

        legend = self.makeLegend(data,mc)
        legend.Draw()

        txt = self.makeCMSText()
        txt.Draw()

        c.Write()
        oldDir.cd()
        
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
    parser.add_option('-v', dest='verbosity', help='Verbose output',  action='count')
    parser.add_option('--path', dest='basePath', help='path to root files')
    parser.add_option('--luminosity', dest='luminosity', help='luminosity')
    parser.add_option('--optVars',dest='optVars',help='Optional variables')
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
#     ROOT.gSystem.Load("lib/libHWWNtuple.so")
    
    ROOT.gStyle.SetTitleAlign(21)
    ROOT.gStyle.SetTitleX(0.5)
    ROOT.gStyle.SetTitleY(0.9)
    ROOT.gStyle.SetFrameLineWidth(2)
    ROOT.gStyle.SetTitleStyle(0)
    ROOT.gStyle.SetTitleFont(42,"xyz")
    ROOT.gStyle.SetTitleFont(42,"")
    ROOT.gStyle.SetLabelFont(42,"xyz")
    ROOT.gStyle.SetTextFont(42)   
    ROOT.gStyle.SetFillColor(ROOT.kWhite)   
    
    p = Plotter()
    p.verbosity = opt.verbosity

    p.setVariables( opt.optVars )

    # custom luminosity
    if opt.luminosity:
        p.setLuminosity( float(opt.luminosity) )

    #custom path
    if opt.basePath:
        p.baseDir = opt.basePath

    try:

        p.readSamples(opt.sampleList)
        p.connect()
        p.readPlots(opt.plotList)

        p.openFile(opt.outputFile)
#         sys.exit(0)
        #name = 'fullSelection/llCounters'
#         out.cd()
        if opt.mode=='data':
            for name in sorted(p.plots.iterkeys()):
                print 'Making',name
                p.makeDataMCPlot(name)
        elif opt.mode=='mc':
            for name in p.plots.iterkeys():
                print name
                p.makeMCStackPlot(name,opt.nostack)
       
    except ValueError as e:
        print 'ValueError',e
    except NameError as e:
        print 'NameError',e
    print 'lumi =',p.luminosity
    


if __name__ == '__main__':
    main()
