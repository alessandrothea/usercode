#!/bin/env python

import HWWAnalysis.Misc.ROOTAndUtils as utils

class PadDesigner(object):
    ''' this class is meant to provide an interface to design the layout of a
    canvas/pad in terms of pixels or equivalent units, overcaming the intrinsic
    ROOT issue of describing the pads in relative units
    
    
    Possible approach: 
    define pads first (w,h) and then ask the designer to produce a canvas where
    to accomodate them.  maybe define the a grid where to accomodate the pads,
    and then the pads inside?  where to define the pad size? in the grid
    definition?

    Then designer then will be in charge to produce the canvas with the pads
    inside. Each one already set to fulfill the constraints.  '''
    def __init__(self):
        pass

class H1DiffPlotter:
    def __init__(self, **kwargs):
        import ROOT
        self._ratio   = 0.7
        self._outer   = 0.1
        self._inner   = 0.02
        self._marg    = 0.1
        self._ltitle  = ''
        self._rtitle  = ''
        self._ytitle2 = 'ratio'
        self._legsize = (0.2,0.2)
        self._colors  = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen]
        self._h0      = None
#         self._h1      = None
        self._hists   = []
        self._pad0    = None
        self._pad1    = None
        self._legend  = None
        self._logx    = False
        self._logy    = False
        self._stack   = None
        self._dstack   = None

        for k,v in kwargs.iteritems():
            if not hasattr(self,'_'+k): continue
            setattr(self,'_'+k,v)

    #---
    def __del__(self):
        del self._h0
#         del self._h1

    @staticmethod
    def _resize(x,ratio):
        x.SetLabelSize(x.GetLabelSize()*ratio/(1-ratio))
        x.SetTitleSize(x.GetTitleSize()*ratio/(1-ratio))

    #---
    def set(self, h0, *hs ):
        if not hs:
            raise RuntimeError('cannot compare only 1 histogram')
        n = h0.GetDimension()
        if True in [ h.GetDimension() != n for h in hs ]:
            raise ValueError('Cannot compare histograms with different dimensions')
        sentry = utils.TH1AddDirSentry()
        self._h0 = h0.Clone()
#         self._h1 = h[0].Clone()
        self._hists = [ h.Clone() for h in hs ]


    #---
    def draw(self, options='hist'):
        import ROOT
        if not ROOT.gPad.func():
            raise RuntimeError('No active pad defined')

        thePad = ROOT.gPad.func()
        thePad.cd()

        self._pad0 = ROOT.TPad('pad0','pad0',0.,(1-self._ratio),1.,1.)
        self._pad0.SetLogx( 1 if self._logx else 0 )
        self._pad0.SetLogy( 1 if self._logy else 0 )
        self._pad0.SetTopMargin(self._outer/self._ratio)
        self._pad0.SetBottomMargin(self._inner/self._ratio)
        self._pad0.SetTicks()
        self._pad0.Draw()

        self._pad0.cd()

        hists = [self._h0] + self._hists
        ndim = hists[0].GetDimension()

        marker = 24 if ndim == 1 else 1
        map(lambda h: ROOT.TH1.SetLineWidth(h,2),hists)
        map(lambda h: ROOT.TH1.SetMarkerStyle(h,marker),hists)

        for i,h in enumerate(hists):
            h.SetLineColor(self._colors[i])
            h.SetMarkerColor(self._colors[i])

        
        self._stack = None

        stack = ROOT.THStack('overlap','')
        ROOT.SetOwnership(stack,True)

        map(stack.Add,hists)
        stack.Draw('nostack')
        stack.GetXaxis().SetLabelSize(0.00)
        stack.GetYaxis().SetTitle(self._h0.GetYaxis().GetTitle())

        anchor = (1-self._marg,1-self._outer/self._ratio)


        self._legend = None
        legend = ROOT.TLegend(anchor[0]-self._legsize[0],anchor[1]-self._legsize[1],anchor[0],anchor[1],'','NDC')
        legend.SetFillColor(ROOT.kWhite)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        # leg.SetNColumns(2)
        for h in hists: legend.AddEntry(h,'','pl')
        legend.Draw()
        self._legend = legend


        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextAlign(12)
        l.DrawLatex(ROOT.gPad.GetLeftMargin(),1-(0.5*self._outer/self._ratio),self._ltitle)
        l.SetTextAlign(32)
        l.DrawLatex(1-ROOT.gPad.GetRightMargin(),1-(0.5*self._outer/self._ratio),self._rtitle)

        self._stack = stack


        #- pad2 ---

        sentry = utils.TH1AddDirSentry()
#         print thePad
        thePad.cd()
        self._pad1 = ROOT.TPad('pad1','pad1',0.,0.0,1.,(1-self._ratio))
        self._pad1.SetTopMargin(self._inner/(1-self._ratio))
        self._pad1.SetBottomMargin(self._outer/(1-self._ratio))
        self._pad1.SetTicks()
        self._pad1.SetGridy()
        self._pad1.Draw()

        self._pad1.cd()

        hdiffs = []
        colors = self._colors[1:] if len(self._hists) > 1 else [ROOT.kBlack] 
        for i,h in enumerate(self._hists):
            hd = h.Clone('diff'+h.GetName())
            hd.Divide(self._h0)
            hd.SetMarkerStyle(20)
            hd.SetLineWidth(1)
#             hd.SetLineColor(ROOT.kBlack)
#             hd.SetMarkerColor(ROOT.kBlack)
            hd.SetLineColor(colors[i])
            hd.SetMarkerColor(colors[i])
            hdiffs.append(hd)

        self._dstack = None

        dstack = ROOT.THStack('diffs','')
        ROOT.SetOwnership(dstack,False)

        map(dstack.Add,hdiffs)
        dstack.Draw('nostack')

        ax = dstack.GetXaxis()
        ay = dstack.GetYaxis()
        ax.SetTitle(self._h0.GetXaxis().GetTitle())
        ay.SetTitle(self._ytitle2)
        ay.SetTitleOffset(ay.GetTitleOffset()/self._ratio*(1-self._ratio) )
        self._resize(ax,self._ratio)
        self._resize(ay,self._ratio)

        self._dstack = dstack

if __name__ == '__main__':
    import os.path
    
    import ROOT
    ROOT.TH1.SetDefaultSumw2()
    mypath = os.path.dirname(os.path.abspath(__file__))
    ROOT.gInterpreter.ExecuteMacro(mypath+'/LatinoStyle2.C')
    def resize(x,ratio):
        x.SetLabelSize(x.GetLabelSize()*ratio/(1-ratio))
        x.SetTitleSize(x.GetTitleSize()*ratio/(1-ratio))

    h1 = ROOT.TH1F('aa','aaaaaaaa;ax;ayo\'',100,0,100)
    h2 = ROOT.TH1F('bb','bbbbbbbb;bx;by',100,0,100)

    hFill = ROOT.TH1F.Fill
    gaus = ROOT.gRandom.Gaus

    entries = 100000

    for i in xrange(entries):
        hFill(h1,gaus(50,10))
        hFill(h2,gaus(51,10))

    c = ROOT.TCanvas('xx','xx')

    diff = H1DiffPlotter()
    diff.set(h2,h1)

    diff._ltitle = "la rava"
    diff._rtitle = "e la fava"

    diff.draw()

    c.Print('H1DiffTester.pdf')

    import sys
    sys.exit(0)



#helper plot class
class plot:
    def __init__(self, name='',title='',formula='', **kwargs):
        self.name    = name
        self.title   = title
        self.formula = formula
        self.bins    = None
        self.options = ''
        self.logx    = False
        self.logy    = False

        for k,v in kwargs.iteritems():
            if not hasattr(self,k): continue
            setattr(self,k,v)

