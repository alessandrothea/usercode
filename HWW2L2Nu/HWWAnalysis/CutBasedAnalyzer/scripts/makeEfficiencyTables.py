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
import HWWAnalysis.Misc.odict as odict


class sampleEntry:
    def __init__(self):
        self.path = ''
#         self.entries = 0
        self.sum = "no"
        self.xSec = 0.
        self.sFact = 1
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
	dir = os.path.dirname(filename)
	if not os.path.exists(dir):
		os.system('mkdir -p '+dir)
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
#             entries = e.file.Get('entries')
#             if not entries.__nonzero__():
#                 raise NameError('histogram entries not found in '+fullPath)
#             e.entries = entries.GetBinContent(1)
            
        for e in self.mcSamples:
            fullPath = self.baseDir+'/'+e.path
            e.file = ROOT.TFile(fullPath)
            if not e.file.IsOpen() or not e.file.__nonzero__():
                raise NameError('file '+e.path+' not found')

#             entries = e.file.Get('entries')
#             if not entries.__nonzero__():
#                 raise NameError('histogram entries not found in '+fullPath)
#             e.entries = entries.GetBinContent(1)

    def getHistograms(self,samples,name,prefix):
                
##         plot = self.plots[name]
##         if ( plot is None ):
##             raise NameValue('Plot '+name+' not found');
        
        sentry = utils.TH1AddDirSentry()

        histograms = []
        for s in samples:
            h = s.file.Get(name)
            if not h.__nonzero__():
                raise NameError('histogram '+name+' not found in '+s.path)
            hClone = h.Clone(prefix+'_'+name)
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
#             h.Sumw2()
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
        lines = [ 'CMS Preliminary - #sqrt{s}=7 TeV']

        entries = [ ROOT.TLatex(0,0,line) for line in lines ]
        
        shrink = 0.7
        Dx = shrink * max([txt.GetXsize() for txt in entries])
        dy = shrink*entries[0].GetYsize()

        x0 = 0.1
        y0 = 0.9
#         x0 = 0.115
#         y1 = 0.885

        x1 = x0 + Dx
        y1 = y0+dy*len(lines)+0.01*(len(lines))

        pave = ROOT.TPaveText(x0,y0,x1,y1,'ndc')
        pave.SetFillColor(ROOT.kRed)
        pave.SetBorderSize(0)
        pave.SetMargin(0)
        pave.SetFillStyle(0)
        pave.SetTextAlign(11)

        pave.SetName('preliminary')

        for line in lines:
            pave.InsertText(line)

        return pave

    def makeTitle(self, title):
        lines = [ title ]

        entries = [ ROOT.TLatex(0,0,line) for line in lines ]
        
        shrink = 0.7
        Dx = shrink * max([txt.GetXsize() for txt in entries])
        dy = shrink*entries[0].GetYsize()

        x1 = 0.9
        y0 = 0.9

        x0 = x1 - Dx
        y1 = y0+dy*len(lines)+0.01*(len(lines))

        pave = ROOT.TPaveText(x0,y0,x1,y1,'ndc')
        pave.SetFillColor(ROOT.kRed)
        pave.SetBorderSize(0)
        pave.SetMargin(0)
        pave.SetFillStyle(0)
        pave.SetTextAlign(31)

        pave.SetName('title')

        for line in lines:
            pave.AddText(line)

        return pave



    def makeEfficiencyTable(self,name):

        print name
        
        # save the old dir
        oldDir = ROOT.gDirectory
        #and go to the new one
        path = os.path.dirname(name)
        
        # but don't write the plots
        sentry = utils.TH1AddDirSentry()

        data = self.getDataHistograms(name)
        mc   = self.getMCHistograms(name)
        
        self.normalize(mc) #, self.mcSamples)
        
        mc   = self.sum(mc) #,self.mcSamples)
        data = self.sum(data)

        (data0, sample0) = data[0]

        nbins = data0.GetNbinsX()

        print data0.GetBinContent(data0.GetNbinsX())

##         for (h,s) in mc:
##             print s.legend,h.GetBinContent(h.GetNbinsX())

        tableValue = odict.OrderedDict()
        efficiency = odict.OrderedDict()
        tableEntry = odict.OrderedDict()
        
        print '________________________________________________________________________________________________________________________________________________________________________________________________'
        print '| cut:'.ljust(18),sample0.legend.ljust(18),'|' .join(s.legend.ljust(18) for (h,s) in mc)
        print '________________________________________________________________________________________________________________________________________________________________________________________________'

        for i in range(nbins):
            j=i+1
            axis       = data0.GetXaxis()
            cut        = axis.GetBinLabel(j)

            tableValue[cut]      = odict.OrderedDict()
            efficiency[cut] = odict.OrderedDict()
            tableEntry[cut] = odict.OrderedDict()

            tableEntry[cut]['cut'] = cut

            preEntry = data0.GetBinContent(i)
            entry = data0.GetBinContent(j)
            tableValue[cut][sample0.path] = str('%.1f' % (entry))

            if (preEntry == 0):
                efficiency[cut][sample0.path] = str(0.0)
            else:
                efficiency[cut][sample0.path] = str('%.1f' % (100*(entry / preEntry)))

            tableEntry[cut][sample0.path] = tableValue[cut][sample0.path]+' ('+efficiency[cut][sample0.path]+'\%)'

            # get the MC
            for (h,s) in mc:
                preEntry = h.GetBinContent(i)
                entry = h.GetBinContent(j)
                tableValue[cut][s.path] = str('%.1f' % (entry))

                if (preEntry == 0):
                    efficiency[cut][s.path] = str(0.0)
                else:
                    efficiency[cut][s.path] = str('%.1f' % (100*(entry / preEntry)))

                tableEntry[cut][s.path] = tableValue[cut][s.path]+' ('+efficiency[cut][s.path]+'\%)'


##            print  cut.ljust(10),'|',tableValue[cut][sample0.path].ljust(10),'|',' | '.join( [ tableValue[cut][s.path].ljust(10) for (h,s) in mc]) 
            print  '|'+cut.ljust(18),'|',tableEntry[cut][sample0.path].ljust(18).replace('\%','%'),'|',' | '.join( [ tableEntry[cut][s.path].ljust(18).replace('\%','%') for (h,s) in mc])+'|' 
##             print  cut.ljust(20),efficiency[cut][sample0.path].ljust(20),' | '.join( [ efficiency[cut][s.path] for (h,s) in mc]) 
        print '________________________________________________________________________________________________________________________________________________________________________________________________'



            
            
        print r'\documentclass[a4paper]{article}'
        print r'\begin{document}'
        print r'\begin{tabular}{|'+'c|'*(len(mc)+2)+'}'
        print r'\hline'
        print ' & ',sample0.legend,' & $',' & $'.join(s.legend.replace('+-',' $\\pm$ ').replace('%','\%').replace('#','\\')+'$' for (h,s) in mc),r'\\'
        print r'\hline'
        for line in tableEntry.iterkeys():
            print tableEntry[line]['cut'],' & ',tableEntry[line][sample0.path],' & ',' & '.join( [ tableEntry[line][s.path] for (h,s) in mc ] ),r'\\'
        print r'\hline'
        print r'\end{tabular}'
        print r'\end{document}'

        
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
        data = self.sum(data)
#         print data
        (data0, sample0) = data[0]
        baseName = os.path.basename(name)
        stack = ROOT.THStack('mcstack_'+baseName,data0.GetTitle())
            
        if pl.rebin != 1:
            data0.Rebin(pl.rebin)
        
        # find the minima, move the following in a separate function
        mcMinima = []    
        for (h,s) in mc:
            if pl.rebin != 1:
                h.Rebin(pl.rebin)
            mcMinima.append(h.GetMinimum())
#             print h.GetName(),mcMinima[-1],mcMinimaNonZero[-1]
            stack.Add(h,'hist')

        # find the absolute minimum
        minima = [ h.GetMinimum() for h in stack.GetStack() ]
        minima.append(data0.GetMinimum())

        # find the 
        minimaNonZero = [ h.GetMinimum(0) for h in stack.GetStack() ]
        minimaNonZero.append(data0.GetMinimum(0))


#         minYMc = min(mcMinima)
        maxY = ROOT.TMath.Max(data0.GetMaximum(),stack.GetMaximum())
        minY = ROOT.TMath.Min(data0.GetMinimum(),min(mcMinima))
#         minY = ROOT.TMath.Min(data0.GetMinimum(),stack.GetStack().First().GetMinimum())
            
        cName = 'c_'+baseName
        c = ROOT.TCanvas(cName,cName,2)
#         print c.GetWw(),c.GetWh()
        c.SetTicks();
#         c.Size(30,30)
#         print '- logx =', pl.logX, ': logy =',pl.logY
        
        if pl.logX is 1:
            c.SetLogx()
            
        if pl.logY is 1 and not (maxY == minY == 0):
            c.SetLogy()
            if minY==0.:
                minY = min(minimaNonZero)
                # don't allow the min to go below 0.1 data min
                minY = max([minY, 0.1*data0.GetMinimum(0)])
#             maxY *= ROOT.TMath.Power(maxY/minY,0.1)
#             minY /= ROOT.TMath.Power(maxY/minY,0.1)
#         else:
#             maxY += (maxY-minY)*0.1
#             minY -= (maxY-minY)*0.1 if minY != 0. else 0;#-1111.

#         print 'minmax',minY, maxY

        maxY += (maxY-minY)*0.1
#         minY -= (maxY-minY)*0.1 if minY != 0. else 0
    
        minX = data0.GetXaxis().GetXmin()
        maxX = data0.GetXaxis().GetXmax()

#         frame = c.DrawFrame(minX, minY, maxX, maxY)
        frame = data0.Clone('frame')
        frame.SetFillStyle(0)
        frame.SetLineColor(ROOT.gStyle.GetFrameFillColor())
        frame.Reset()
        frame.SetBinContent(1,maxY)
        frame.SetBinContent(frame.GetNbinsX(),minY)
#         frame.SetMaximum(maxY)
#         frame.SetMinimum(minY)
        
#         frame.GetYaxis().SetLimits(minY,maxY)
        frame.SetBit(ROOT.TH1.kNoStats)
        frame.SetTitle(pl.title if pl.title != 'self' else data0.GetTitle())
        frame.SetXTitle(pl.xtitle if pl.xtitle != 'self' else data0.GetXaxis().GetTitle())
        frame.SetYTitle(pl.ytitle if pl.ytitle != 'self' else data0.GetYaxis().GetTitle())
        frame.Draw()
#         frame.GetPainter().PaintTitle()

        for d,s in data:
            d.SetFillColor(1);
            d.SetMarkerColor(1);
            d.SetMarkerStyle(20);
            d.SetMarkerSize(0.7);
        
        stack.Draw('same')
        for d,s in data:
            d.Draw('e1 same')

        title = self.makeTitle(frame.GetTitle() )
        title.Draw()

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
        c.ls()
        c.Write()




def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-s', '--sampleList', dest='sampleList', help='Path to the rootfile', )
    parser.add_option('-o', '--outputFile', dest='outputFile', help='new rootfile', )
##?    parser.add_option('-m', '--mode', dest='mode', help='mode [data,mc]', default='data')
    parser.add_option('-v', dest='verbosity', help='Verbose output',  action='count')
    parser.add_option('--path', dest='basePath', help='path to root files')
    parser.add_option('--luminosity', dest='luminosity', help='luminosity')
    parser.add_option('--optVars',dest='optVars',help='Optional variables')

    (opt, args) = parser.parse_args()

    if opt.sampleList is None:
        parser.error('No list of sample defined')
    if opt.outputFile is None:
        parser.error('No output file')
        
##?     if opt.mode != 'data' and opt.mode != 'mc':
##?         parser.error('Mode not recognized')
        
    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()
#     ROOT.gSystem.Load("lib/libHWWNtuple.so")
    
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
##?        p.readPlots(opt.plotList)



##?        p.openFile(opt.outputFile)


        electrons = 'ee/cutflow/yield'
        muons = 'mm/cutflow/yield'
        emu = 'em/cutflow/yield'
        mue = 'me/cutflow/yield'

##         data = p.getDataHistograms(electrons)
##         mc   = p.getMCHistograms(electrons)
##         p.makeEfficiencyTable(electrons)
##         data = p.getDataHistograms(muons)
##         mc   = p.getMCHistograms(muons)
##         p.makeEfficiencyTable(muons)
        data = p.getDataHistograms(emu)
        mc   = p.getMCHistograms(emu)
        p.makeEfficiencyTable(emu)
        data = p.getDataHistograms(mue)
        mc   = p.getMCHistograms(mue)
        p.makeEfficiencyTable(mue)

##         if opt.mode=='data':
##             for name in sorted(p.plots.iterkeys()):
##                 print 'Making',name
##                 p.makeDataMCPlot(name)
##         elif opt.mode=='mc':
##             for name in p.plots.iterkeys():
##                 print name
##                 p.makeMCStackPlot(name,opt.nostack)
       
    except ValueError as e:
        print 'ValueError',e
    except NameError as e:
        print 'NameError',e
    print 'lumi =',p.luminosity
    


if __name__ == '__main__':
    main()
