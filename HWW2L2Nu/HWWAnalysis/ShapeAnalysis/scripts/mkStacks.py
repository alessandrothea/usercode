#!/usr/bin/env python

import os
import optparse
import sys
import re
import hwwinfo
import hwwtools
import fnmatch


import ROOT
import HWWAnalysis.Misc.ROOTAndUtils as utils

#from ROOT import *

## legend title dictionary
legproc = {
    'ggWW':'gg #rightarrow WW',
    'WW':'qq #rightarrow WW',
    'ggH':'gg #rightarrow H',
    'Top':'Top',
    'wzttH':'ass. prod. H',
    'Vg':'V#gamma',
    'WJet':'W+Jets',
    'DYLL':'Z#rightarrow ll',
    'DYTT':'Z#rightarrow #tau #tau',
    'VV':'di-boson',
    'vbfH':'VBF H'
    }

legsyst = {
    'CMS_met':'#slashed{E}_{T}',
    ## '':'',
    ## '':'',
    ## '':'',
    ## '':'',
    ## '':'',
    ## '':'',
    ## '':'',
    }


def openTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f


def getHist(file, hist):
    h = file.Get(hist)
    if not h.__nonzero__():
        raise NameError('Histogram '+hist+' doesn\'t exist in '+str(file))
    return h


def getFiles(dir):
    list = os.listdir(dir)
    list.sort()
    ## remove non root files
    cleaned = [l for l in list if '.root' in l]
    return cleaned

def getNominals(file):
#     rootFile = ROOT.TFile.Open(file)
    finder = utils.ObjFinder("TH1D")
    names = finder.findRecursive(file)
    nomRegex  = re.compile('^histo_([^_]+)$')

    nominals = {}
    for name in names:
        if not nomRegex.match(name):
            continue
        h = getHist(file,name)
        nominals[name.replace('histo_','')] = h
                 
    return nominals

class variation:
    def __repr__(self):
        return str(self.__dict__)

def getNominalUpDown(file):
    finder = utils.ObjFinder("TH1D")
    names = finder.findRecursive(file)
    nomRegex  = re.compile('^histo_([^_]+)$')
    systRegex = re.compile('^histo_([^_]+)_(.+)(Up|Down)$')

    nominals = {}
    nomupdown = {}
    for name in names:
        if not nomRegex.match(name):
            continue
        h = getHist(file,name)
        nominals[name.replace('histo_','')] = h

    for name in names:
        m = systRegex.match(name)
        if not m: continue
        
        process,syst,var = m.group(1,2,3)

        if process not in nomupdown:
            nomupdown[process] = {}
        
        if not syst in nomupdown[process]:
            v =  variation()
            v.Nom = nominals[process]
            nomupdown[process][syst] = v

        hUpDown = getHist(file,name)
        setattr(nomupdown[process][syst],var,hUpDown)



#     for nom in nominals:
    return nomupdown

## def mergeHistos(nominals):
##     histos = {}
##     nominals['ggH'].ROOT.Add(nominals['vbfH'])
    
##     nominals['Data'] = 

    
def makeNominalPlots(file,outputdir, lumi, xlabel, ratio):

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    # open the file
    f = openTFile(file)

    # in one root file,there is one set of nominal
    # histograms to plot, so get those...

    reMass = re.compile('.+\.mH(\d+)\..+\.root')
    m = reMass.match(file)
    if not m: 
        raise RuntimeError('Mass label not found in '+file)
    mass = int(m.group(1))
#     mass = int(file.split('.')[2].replace('mH',''))

    nominals = getNominals(f)

#     print nominals


    histo = nominals['ggH']
    if 'vbfH' in nominals:
        histo.Add(nominals['vbfH'])
    nominals['HWW'] = histo

    histo = nominals['ggWW']
    histo.Add(nominals['WW'])
    nominals['WWsum'] = histo

    histo = nominals['Vg']
    histo.Add(nominals['VV'])
    nominals['VVsum'] = histo

    histo = nominals['DYLL'].Clone()
    if 'DYTT' in nominals:
        histo.Add(nominals['DYTT'])
    nominals['DYsum'] = histo

    plot = ROOT.MWLPlot()
    plot.setDataHist(nominals['Data'])
    plot.setHWWHist(nominals['HWW'])
    plot.setWWHist(nominals['WWsum'])  
    plot.setZJetsHist(nominals['DYsum'])
    plot.setTopHist(nominals['Top'])
    plot.setVVHist(nominals['VVsum'])
    plot.setWJetsHist(nominals['WJet'])


#    plot.setWZHist(nominals[])
##     plot.setZZHist(nominals[])
##     plot.setFakesHist(nominals[])


    cName = 'c_'+file.split('/')[-1].replace('.root','')
    c = ROOT.TCanvas(cName,cName) if ratio else ROOT.TCanvas(cName,cName,2)
    plot.setMass(mass)
    plot.setLumi(lumi)
    plot.setLabel(xlabel)
    plot.Draw(c,1,ratio)

#     c.ls()
    c.Print(outputdir+'/'+cName+'.pdf')
    c.Print(outputdir+'/'+cName+'.png')
#     c.Print(outputdir+'/'+cName+'.root')

#    c.Delete()

    f.Close()

def makeShapeUpDown(file,outputdir, xlabel, filter):

    # open the file
    f = openTFile(file)

    # in one root file,there is one set of nominal
    # histograms to plot, so get those...

    reMass = re.compile('.+\.mH(\d+)\..+\.root')
    m = reMass.match(file)
    if not m: 
        raise RuntimeError('Mass label not found in '+file)

    mass = int(m.group(1))
    print 'Detected mass',mass
    odir = outputdir+'/'+m.group(1)
    os.system('mkdir -p '+odir)
    
    (root,ext) = os.path.splitext(os.path.basename(file))
#     print root,ext
    
    updown = getNominalUpDown(f)
    for process,systs in updown.iteritems():
        for syst,vars in systs.iteritems():
            if not fnmatch.fnmatch(syst, filter):
                continue
            cName = 'c_'+root+'_'+process+'_'+syst
            fName = odir+'/'+cName
            exts = ['pdf','png']
            legheader = legproc[process]+', m_{H} = '+str(mass)+', '+root.split('_')[0].split('.')[-1]+' '+root.split('_')[1]
            c = printUpDown(cName,fName,exts,syst,vars,xlabel,legheader)
            
            
def plotCMSText():
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

def printUpDown( cName, fName, exts, syst, vars, xlabel ):
#     nom = vars.Nom.DrawClone()
#     nom.SetTitle('Shape systematics: '+syst)

#     up = vars.Up.DrawClone('same hist')
#     up.SetLineColor(ROOT.kRed)
#     up.SetLineWidth(2)

#     down = vars.Down.DrawClone('same hist')
#     down.SetLineColor(ROOT.kBlue)
#     down.SetLineWidth(2)

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)



    h_n = vars.Nom
    h_u = vars.Up
    h_d = vars.Down

    maxi = []
    mini = []
    maxi.append(h_n.GetMaximum())
    mini.append(h_n.GetMinimum())
    maxi.append(h_u.GetMaximum())
    mini.append(h_u.GetMinimum())
    maxi.append(h_d.GetMaximum())
    mini.append(h_d.GetMinimum())
    maxY = max(maxi)
    minY = min(mini)

    # new canvas
#     cName = 'c_'+baseName
    c = ROOT.TCanvas(cName,cName)
    c.SetTicks()

    frame = h_n.Clone('frame')
    frame.SetFillStyle(0)
    frame.SetLineColor(ROOT.gStyle.GetFrameFillColor())
    frame.Reset()
    frame.SetBinContent(1,maxY)
    frame.SetBinContent(frame.GetNbinsX(),minY)

    pad1 = ROOT.TPad()
    ROOT.SetOwnership(pad1, False)
    pad1.SetPad('pad1','pad1',0.0,0.4,1.0,1.0, 10)
    pad1.Draw('same')
    pad1.cd()
    pad1.SetTopMargin(0.11)
    pad1.SetLeftMargin(0.07)
    pad1.SetRightMargin(0.05)
    pad1.SetBottomMargin(0.15)
    
    c.cd()
    
    pad2 = ROOT.TPad()
    ROOT.SetOwnership(pad2, False)
    pad2.SetPad('pad2','pad2',0.0,0.,1.0,0.4,10)
    pad2.Draw()
    pad2.cd()
    pad2.SetTopMargin(0.11)
    pad2.SetLeftMargin(0.07)
    pad2.SetRightMargin(0.05)
    pad2.SetBottomMargin(0.15)
    

    c.cd()
    pad1.cd()

    frame = h_n.Clone('frame')
    frame.SetFillStyle(0)
    frame.SetLineColor(ROOT.gStyle.GetFrameFillColor())
    frame.Reset()
    frame.SetBinContent(1,maxY)
    frame.SetBinContent(frame.GetNbinsX(),minY)
    frame.SetBit(ROOT.TH1.kNoStats)
    frame.SetXTitle(xlabel)
    frame.SetYTitle('a. u.')
    frame.Draw()

    h_n.SetMarkerStyle(21)
    h_n.SetMarkerSize(0.5)
    h_u.SetLineColor(2)
    h_u.SetLineWidth(2)
    h_u.SetLineStyle(1)
    h_d.SetLineColor(4)
    h_d.SetLineWidth(2)
    h_d.SetLineStyle(2)

    h_n.GetYaxis().SetLabelFont(43) 
    h_n.GetXaxis().SetLabelFont(43) 
    h_n.GetYaxis().SetLabelSize(14) 
    h_n.GetXaxis().SetLabelSize(14) 
    h_n.GetYaxis().SetTitleFont(43) 
    h_n.GetXaxis().SetTitleFont(43) 
    h_n.GetYaxis().SetTitleSize(20) 
    h_n.GetXaxis().SetTitleSize(20) 
    h_n.GetYaxis().SetTitleOffset(2.1)
    h_n.GetXaxis().SetTitleOffset(2)

    h_d.GetYaxis().SetLabelFont(43) 
    h_d.GetXaxis().SetLabelFont(43) 
    h_d.GetYaxis().SetLabelSize(14) 
    h_d.GetXaxis().SetLabelSize(14) 
    h_d.GetYaxis().SetTitleFont(43) 
    h_d.GetXaxis().SetTitleFont(43) 
    h_d.GetYaxis().SetTitleSize(20) 
    h_d.GetXaxis().SetTitleSize(20) 
    h_d.GetYaxis().SetTitleOffset(2.1)
    h_d.GetXaxis().SetTitleOffset(2)

    h_u.GetYaxis().SetLabelFont(43) 
    h_u.GetXaxis().SetLabelFont(43) 
    h_u.GetYaxis().SetLabelSize(14) 
    h_u.GetXaxis().SetLabelSize(14) 
    h_u.GetYaxis().SetTitleFont(43) 
    h_u.GetXaxis().SetTitleFont(43) 
    h_u.GetYaxis().SetTitleSize(20) 
    h_u.GetXaxis().SetTitleSize(20) 
    h_u.GetYaxis().SetTitleOffset(2.1)
    h_u.GetXaxis().SetTitleOffset(2)

    ## h_n.Sumw2()
    ## h_u.Sumw2()
    ## h_d.Sumw2()

    h_u.Draw('hist same')
    h_d.Draw('hist same')
    h_n.Draw('e1 same')

    ## ratio
    pad2.cd()
    frame2 = h_n.Clone('frame2')
    frame2.SetFillStyle(0)
    frame2.SetLineColor(ROOT.gStyle.GetFrameFillColor())    
    frame2.Reset()
    frame2.SetBit(ROOT.TH1.kNoStats)
    frame2.SetBinContent(1,1.5)
    frame2.SetBinContent(frame2.GetNbinsX(),0.0)
    frame2.SetTitle('')
    frame2.SetLabelFont(43)
    frame2.SetLabelSize(12)
    frame2.SetXTitle('')
    frame2.SetYTitle('nominal / #pm1#sigma-shape')
    frame2.SetTitleSize(20)
##     frame2.SetYTitle('ratio')

    frame2.GetYaxis().SetLabelFont(43) 
    frame2.GetXaxis().SetLabelFont(43) 
    frame2.GetYaxis().SetLabelSize(14) 
    frame2.GetXaxis().SetLabelSize(14) 
    frame2.GetYaxis().SetTitleFont(43) 
    frame2.GetXaxis().SetTitleFont(43) 
    frame2.GetYaxis().SetTitleSize(20) 
    frame2.GetXaxis().SetTitleSize(20) 
    frame2.GetYaxis().SetTitleOffset(2.1)
    frame2.GetXaxis().SetTitleOffset(2)

    frame2.SetMaximum(1.99)
    frame2.SetMinimum(0.)

    frame2.Draw()

    ratios = []
    r_u = h_n.Clone()
    r_d = h_n.Clone()
    r_u.SetYTitle('ratio') 
    r_d.SetYTitle('ratio') 

    r_u.Divide(h_u)
    r_d.Divide(h_d)

    r_u.SetLineColor(2)
    r_u.SetLineWidth(2)
    r_u.SetLineStyle(1)
    r_d.SetLineColor(4)
    r_d.SetLineWidth(2)
    r_d.SetLineStyle(2)    

    r_u.GetYaxis().SetLabelFont(43) 
    r_u.GetXaxis().SetLabelFont(43) 
    r_u.GetYaxis().SetLabelSize(14) 
    r_u.GetXaxis().SetLabelSize(14) 
    r_u.GetYaxis().SetTitleFont(43) 
    r_u.GetXaxis().SetTitleFont(43) 
    r_u.GetYaxis().SetTitleSize(20) 
    r_u.GetXaxis().SetTitleSize(20) 
    r_u.GetYaxis().SetTitleOffset(2.1)
    r_u.GetXaxis().SetTitleOffset(2)

    r_d.GetYaxis().SetLabelFont(43) 
    r_d.GetXaxis().SetLabelFont(43) 
    r_d.GetYaxis().SetLabelSize(14) 
    r_d.GetXaxis().SetLabelSize(14) 
    r_d.GetYaxis().SetTitleFont(43) 
    r_d.GetXaxis().SetTitleFont(43) 
    r_d.GetYaxis().SetTitleSize(20) 
    r_d.GetXaxis().SetTitleSize(20) 
    r_d.GetYaxis().SetTitleOffset(2.1)
    r_d.GetXaxis().SetTitleOffset(2)

    ## ## stat errors
    ## statn = h_n.Clone('statistics')
    ## stat  = h_n.Clone('statistics')
    ## nbins = h_n.GetNbinsX()+1
    ## for i in range(1,nbins):
    ##     value = max(stat.GetBinContent(i), 1.+ r_u.GetBinError(i))
    ##     stat.SetBinContent(i,value)

    ##     stat2 = stat.Clone('statistics2')
    ##     for i in range(1,nbins):
    ##         stat2.SetBinContent(i,1.-(stat.GetBinContent(i)-1.))
    ##     stat.SetFillColor(22)
    ##     stat.SetLineColor(22)
    ##     stat.SetLineStyle(1)
    ##     stat.SetLineWidth(1)
    ##     stat.SetFillStyle(1001)
    ##     stat2.SetFillColor(10)
    ##     stat2.SetLineColor(22)
    ##     stat2.SetLineStyle(1)
    ##     stat2.SetLineWidth(1)
    ##     stat2.SetFillStyle(1001)
    ##     stat.Draw('hist same')
    ##     stat2.Draw('hist same')


    r_u.Draw('hist same')
    r_d.Draw('hist same')


    line = ROOT.TLine()
    line.SetX1(h_n.GetBinLowEdge(1))
    line.SetX2(h_n.GetBinLowEdge(h_n.GetNbinsX()+1))
    line.SetY1(1.)
    line.SetY2(1.)
    line.SetLineWidth(2)
    line.SetLineStyle(2)
    line.Draw('same')

    ## # legend
    ## x0 = 0.2
    ## x1 = 0.5
    ## y0 = 0.60
    ## y1 = 0.80

    # legend
    x0 = 0.2
    x1 = 0.5
    y0 = 0.60
    y1 = 0.80

    ## xax = h_n.GetXaxis()
    ## if h_n.GetMean() < (xax.GetXmax()-xax.GetXmin())/2.:
    ##     x0 = 0.5
    ##     x1 = 0.8


    pad1.cd()
    legend = ROOT.TLegend(x0,y0,x1,y1)
    legend.SetFillColor(ROOT.kWhite)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.AddEntry(h_n,'nominal shape')
    legend.AddEntry(h_u,'+1#sigma-shape')
    legend.AddEntry(h_d,'-1#sigma-shape')
    legend.SetHeader(legheader)
    legend.Draw()

    text = plotCMSText()
    text.Draw()

    for ext in exts:
        c.Print(fName+'.'+ext)


def main():



    ## option parser
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    
    parser.add_option('-i','--input',dest='inputdir',help='Input dir')
    parser.add_option('-m','--mass',dest='mass',help='Mass',default=-1)
    parser.add_option('-o','--output',dest='outputdir',help='Output dir',default='.')
    parser.add_option('-v','--variations',dest='variations',help='make the scale up/down stacks',action='store_true',default=False)
    parser.add_option('-x','--xlabel',dest='xlabel',help='X-axis label',default='')
    parser.add_option('-r','--ratio',dest='ratio',help='Plot the data/mc ration', action='store_false',default=True)
    parser.add_option('-l','--lumi', dest='lumi', type='float', help='Luminosity', default=None)
    parser.add_option('-f','--filter',dest='filter', help='Filter on the variations', default='*')
 

    hwwtools.loadOptDefaults(parser)
    (opt, args) = parser.parse_args()
    sys.argv.append('-b')

    if opt.inputdir is None:
        parser.error('No input file defined')

    inputdir = opt.inputdir
    outputdir = opt.outputdir
    mass = opt.mass    

    # get MWLPlot.C
    mypath = os.path.dirname(os.path.abspath(__file__))
#     print mypath
    ROOT.gInterpreter.ExecuteMacro(mypath+'/LatinoStyle2.C')
    ROOT.gROOT.ProcessLine('.L '+mypath+'/MWLPlot.C+g')


    filenames = getFiles(inputdir)
    # loop over all files
    for file in filenames:
        path = inputdir+'/'+file
        if str(mass) not in file and mass > 0:
            continue

        print 'Making',path
        if not opt.variations:
            makeNominalPlots(path, outputdir, opt.lumi, opt.xlabel, opt.ratio)
        else:
            makeShapeUpDown(path,outputdir, opt.xlabel, opt.filter)

    print 'Used options'
    print ', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()])

if __name__ == '__main__':

    main()

       
