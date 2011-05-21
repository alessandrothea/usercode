#!/usr/bin/env python

import optparse
import sys
import ROOT
import array
import numpy
import os.path
from HWWAnalysis.Misc.ROOTAndUtils import TH1AddDirSentry

def openTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f

def getTree( file, tree ):
    t = file.Get(tree)
    if not t.__nonzero__():
        raise NameError('Tree '+tree+' doesn\'t exist in '+file)
    return t


def makeROC( signal, background ):
    print 'Signal:',signal
    print 'Background',background
    sigFile = openTFile(signal)
    bkgFile = openTFile(background)

    histograms = [
        ('bTags/combinedSecondaryVertex',      'Combined Secondary Vertex', ROOT.kMagenta, 23),
        ('bTags/combinedSecondaryVertexMVA',   'Combined Secondary Vertex MVA', ROOT.kBlue, 23),
        ('bTags/tkCountingHighEff',            'Track Counting High Efficiency', ROOT.kRed, 20),
        ('bTags/tkCountingHighPur',            'Track Counting High Purity', ROOT.kOrange, 21),
        ('bTags/jetBProbability',              'Jet Probability Btag', ROOT.kGreen, 22),
        ('bTags/jetProbability',               'B Jet Probability Btag', ROOT.kViolet, 21),
        ('bTags/simpleSecondaryVertexHighEff', 'Simple Secondary Vertex High Efficiency', ROOT.kTeal+3, 33),
        ('bTags/simpleSecondaryVertexHighPur', 'Simple Secondary Vertex High Purity', ROOT.kAzure+6, 34),
    ]

    ROOT.gStyle.SetPadLeftMargin(0.15)
    ROOT.gStyle.SetPadRightMargin(0.15)
    ROOT.gStyle.SetTitleOffset(1.8,'y')
    ROOT.gStyle.SetStripDecimals(False)

    c = ROOT.TCanvas('test','test')
    c.Size(24,20);
    theROC = ROOT.TMultiGraph()
    theROC.SetName('btagROC')
    theROC.SetTitle('Btag algorithms ROC')

    x0 = 0.43
    y0 = 0.13
    x1 = 0.83
    y1 = 0.43

    legend = ROOT.TLegend(x0,y0,x1,y1)
    legend.SetFillColor(ROOT.kWhite) 
    legend.SetBorderSize(0)

    for (hPath,title,col,mk) in histograms:
        hSig = sigFile.Get(hPath)
        if not hSig.__nonzero__():
            raise NameError('histogram '+hPath+' doesn\'t exist in '+sigFile.GetName())

        hBkg = bkgFile.Get(hPath)
        if not hSig.__nonzero__():
            raise NameError('histogram '+hPath+' doesn\'t exist in '+bkgFile.GetName())

        sigI = numpy.ndarray( (hSig.GetNbinsX(),),dtype=numpy.double, buffer=hSig.GetIntegral() )
        bkgI = numpy.ndarray( (hBkg.GetNbinsX(),),dtype=numpy.double, buffer=hBkg.GetIntegral() )

        g = ROOT.TGraph(len(sigI),bkgI,sigI)
        g.SetName(os.path.basename(hPath))
        g.SetTitle(title)
#         g.Draw('ap')
        g.SetMarkerColor(col)
        g.SetMarkerStyle(mk)
        theROC.Add(g)
#         g.GetXaxis().SetTitle('Background')
#         g.GetYaxis().SetTitle('Signal')
        legend.AddEntry(g,'','p')

    theROC.Draw('ap')
    theROC.GetXaxis().SetTitle('t#bar{t} Efficiency')
    theROC.GetYaxis().SetTitle('ggH_{160} Efficiency')
    theROC.GetXaxis().SetRangeUser(0.4,1.0)
    theROC.GetYaxis().SetRangeUser(0.96,1.0)
    theROC.GetYaxis().SetDecimals(True)
    legend.Draw()
    c.Print('btagROC.pdf')
    c.Print('btagROC.root')
    
    hSig = sigFile.Get('bTags/tkCountingHighEff')
    hBkg = bkgFile.Get('bTags/tkCountingHighEff')

    bin = hSig.FindBin(2.1)
    
    sigI = numpy.ndarray( (hSig.GetNbinsX(),),dtype=numpy.double, buffer=hSig.GetIntegral() )
    bkgI = numpy.ndarray( (hBkg.GetNbinsX(),),dtype=numpy.double, buffer=hBkg.GetIntegral() )

    print 'Eff 2.1 [S - B]: %.3f - %.3f' % (sigI[bin],bkgI[bin])
    


if __name__ == '__main__':
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--out', dest='outPath', help='Output Root File ', )

    (opt, args) = parser.parse_args()

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()
    ROOT.gSystem.Load('libFWCoreFWLite')
    ROOT.AutoLibraryLoader.enable()

    signal     = args[0]
    background = args[1]
    makeROC( signal, background );
