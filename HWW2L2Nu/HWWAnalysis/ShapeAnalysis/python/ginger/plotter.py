#!/bin/env python

import HWWAnalysis.Misc.ROOTAndUtils as utils
from painter import Canvas,Pad,Legend,Latex
import ROOT
import array

class H1RatioPlotter(object):

    class mystyle(object):
        def __init__(self):
            from ROOT import kRed,kOrange,kAzure
            from ROOT import kFullCircle, kOpenCircle

            self.scalemax  = 1.
            self.ltitle    = ''
            self.rtitle    = ''
            self.ytitle2   = 'ratio'
            self.colors    = [kRed+1      , kOrange+7   , kAzure-6    , kAzure+9    , kOrange+7   , kOrange-2  ]
            self.markers   = [kFullCircle , kOpenCircle , kFullCircle , kOpenCircle , kFullCircle , kFullCircle]
            self.fills     = [0           , 0           , 0           , 0           , 0           , 0          ]
            self.plotratio = True

            # lenghts
            self.left        = 100
            self.right       = 75
            self.top         = 75
            self.bottom      = 100

            self.gap         = 5
            self.width       = 500
            self.heightf0    = 500
            self.heightf1    = 200

            self.linewidth   = 2
            self.markersize  = 10
            self.textsize    = 30
            self.titley      = 60

            self.legmargin   = 25
            self.legboxsize  = 50
            self.legtextsize = 30

            self.axsty = {
                'labelfamily' : 4,
                'labelsize'   : 30,
                'labeloffset' : 5,
                'titlefamily' : 4,
                'titlesize'   : 30,
                'titleoffset' : 75,
                'ticklength'  : 20,
                'ndivisions'  : 505,
            }

            self.errsty      = 3005
            self.errcol      = ROOT.kGray+1

            self.logx        = False
            self.logy        = False

            self.morelogx    = False
            self.morelogy    = False

            self.userrangex = (0.,0.)

            self.yrange = (0.,0.)

            # something more active
            self._legalign  = ('l','t')

        @property
        def legalign(self): return self._legalign

        @legalign.setter
        def legalign(self, align):
            ha,va = align
            if ha not in 'lr': raise ValueError('Align can only be \'l\' or \'r\'')
            if va not in 'tb': raise ValueError('Align can only be \'t\' or \'b\'')
            self._legalign = align

        def scale(self,factor):
            self.left        = int(factor*self.left)
            self.right       = int(factor*self.right)
            self.top         = int(factor*self.top)
            self.bottom      = int(factor*self.bottom)

            self.gap         = int(factor*self.gap)
            self.width       = int(factor*self.width)
            self.heightf0    = int(factor*self.heightf0)
            self.heightf1    = int(factor*self.heightf1)

            self.linewidth   = int(factor*self.linewidth)
            self.markersize  = int(factor*self.markersize)
            self.textsize    = int(factor*self.textsize)
            self.titley      = int(factor*self.titley)

            self.legmargin   = int(factor*self.legmargin)
            self.legboxsize  = int(factor*self.legboxsize)
            self.legtextsize = int(factor*self.legtextsize)



            self.axsty['labelsize'   ] = int(factor*self.axsty['labelsize'   ])
            self.axsty['labeloffset' ] = int(factor*self.axsty['labeloffset' ])
            self.axsty['titlesize'   ] = int(factor*self.axsty['titlesize'   ])
            self.axsty['titleoffset' ] = int(factor*self.axsty['titleoffset' ])
            self.axsty['ticklength'  ] = int(factor*self.axsty['ticklength'  ])


    def __init__(self, **kwargs):

        from ROOT import kRed,kOrange,kAzure
        from ROOT import kFullCircle, kOpenCircle

        self.__dict__['_style'] = self.mystyle()

        for k,v in kwargs.iteritems():
            if not hasattr(self._style,k): raise AttributeError('No '+k+' style attribute')
            setattr(self._style,k,v)

        self._h0     = None
        self._hists  = []
        self._canvas = None
        self._pad0   = None
        self._pad1   = None
        self._legend = None
        self._stack  = None
        self._dstack = None

    # ---
    def __getattr__(self,name):
        if hasattr(self,'_style'):
            return getattr(self._style,name)
        else:
            raise AttributeError('Attribute '+name+' not found')

    # ---
    def __setattr__(self,name,value):
        # if the name starts with '_' it is a data member
        if name[0] != '_' and hasattr(self,'_style') and hasattr(self._style,name):
#             print 'setting opt:',name,value
            return setattr(self._style,name,value)
        else:
            self.__dict__[name] = value

    #---
    def set(self, h0, *hs ):
        if not hs:
            raise RuntimeError('cannot compare only 1 histogram')
        n = h0.GetDimension()
        if True in [ h.GetDimension() != n for h in hs ]:
            raise ValueError('Cannot compare histograms with different dimensions')
        sentry = utils.TH1AddDirSentry()
        self._h0 = h0.Clone()
        self._hists = [ h.Clone() for h in hs ]

    #---
    @staticmethod
    def _setrangeuser( ax, urange ):
        lb  = ax.FindBin( urange[0] )
        ub  = ax.FindBin( urange[1] )
        print lb,ub
        ax.SetRange( lb,ub )

    #---
    def plot(self, options=''):

        style = self._style

        left       = style.left
        right      = style.right
        top        = style.top
        bottom     = style.bottom

        gap        = style.gap
        width      = style.width
        heightf0   = style.heightf0
        heightf1   = style.heightf1

        linewidth  = style.linewidth
        markersize = style.markersize
        textsize   = style.textsize
        legmargin  = style.legmargin
        titley     = style.titley

        axsty      = style.axsty

        # pads size
        pw = width+left+right
        ph = heightf0+top+bottom

        ph0 = heightf0+top+gap
        ph1 = heightf1+gap+bottom


        xaxsty = axsty.copy()
        xaxsty['labelsize'] = 0

        yaxsty = axsty.copy()
        yaxsty['ndivisions'] = 505


        c = Canvas()
        if style.plotratio:
            self._pad0 = c[0,0] = Pad('p0',pw,ph0,margins=(left,right, top,    gap), xaxis=xaxsty, yaxis=axsty)
            self._pad1 = c[0,1] = Pad('p0',pw,ph1,margins=(left,right, gap, bottom), xaxis=axsty,  yaxis=yaxsty)
        else:
            self._pad0 = c[0,0] = Pad('p0',pw,ph ,margins=(left,right, top, bottom), xaxis=axsty, yaxis=axsty)

        c.makecanvas()
        self._canvas = c

        # ---
        # main plot
        self._pad0.cd()
        self._pad0.SetLogx(style.logx)
        self._pad0.SetLogy(style.logy)

        hists = [self._h0] + self._hists
        ndim = hists[0].GetDimension()

        map(lambda h: ROOT.TH1.SetLineWidth(h,linewidth),hists)

        # border between frame and legend

        ha,va = style.legalign
        x0 = (left+legmargin) if ha == 'l' else (left+width   -legmargin)
        y0 = (top +legmargin) if va == 't' else (top +heightf0-legmargin)
        leg = Legend(1,len(hists),style.legboxsize,anchor=(x0,y0), style={'textsize':self.legtextsize}, align=style.legalign)

        # ROOT marker size 1 = 8px. Convert pixel to root size
        markersize /= 8.

        from itertools import izip

        for h,col,mrk,fll in izip(hists,style.colors,style.markers,style.fills):
            h.SetFillStyle  (fll)
            h.SetFillColor  (col)
            h.SetLineColor  (col)
            h.SetMarkerColor(col)
            h.SetMarkerStyle(mrk)
            h.SetMarkerSize (markersize)
            leg.addentry( h, 'pl')

        stack = ROOT.THStack('overlap','')

        map(stack.Add,hists)
        stack.Draw('nostack %s' % options)

        stack.GetXaxis().SetTitle(self._h0.GetXaxis().GetTitle())
        stack.GetXaxis().SetMoreLogLabels(style.morelogx)

        stack.GetYaxis().SetTitle(self._h0.GetYaxis().GetTitle())
        stack.GetYaxis().SetMoreLogLabels(style.morelogy)

#         if style.userrangex != (0.,0.): self._setrangeuser( stack.GetXaxis(), style )
        if style.userrangex != (0.,0.): stack.GetXaxis().SetRangeUser(*(style.userrangex) )

        if style.yrange != (0.,0.):
            stack.SetMinimum(style.yrange[0] )
            stack.SetMaximum(style.yrange[1] )

        elif style.scalemax != 1:  stack.SetMaximum(style.scalemax*stack.GetMaximum('nostack '+options))


        self._stack = stack

        leg.draw()
        self._legend = leg

        #title left
        self._ltitleobj = Latex(style.ltitle, anchor=(left,titley),     align=('l','b'), style={'textsize':textsize} )
        self._ltitleobj.draw()

        #rtitle
        self._rtitleobj = Latex(style.rtitle, anchor=(pw-right,titley), align=('r','b'), style={'textsize':textsize} )
        self._rtitleobj.draw()

        if style.plotratio:
            # kill the xtitle of the upper plot
            self._stack.GetXaxis().SetTitle('')

            # ---
            # ratio plot
            self._pad1.cd()
            self._pad1.SetLogx(style.logx)
            h0 = self._h0
            nbins = h0.GetNbinsX()
            xax   = h0.GetXaxis()

            sentry = utils.TH1AddDirSentry()

            # create the h0 to hx rato
            hratios = []
            colors  = [style.errcol]     + (style.colors[1:]  if len(self._hists) > 1 else [ROOT.kBlack]     )
            markers = [ROOT.kFullCircle] + (style.markers[1:] if len(self._hists) > 1 else [ROOT.kFullCircle])
            allh    = [self._h0]+self._hists

            for hx,col,mrk in izip(allh,colors,markers):
                hr = hx.Clone('ratio_%s_%s' % (hx.GetName(),h.GetName()) )

                # divide by hand to preserve the errors
                for k in xrange(nbins+2):
                    br,er = hr.GetBinContent(k),hr.GetBinError(k)
                    b0  = h0.GetBinContent(k)
                    if b0 == 0:
                        # empty h0 bin
                        br = 0
                        er = 0
                    else:
                        br /= b0
                        er /= b0

                    hr.SetBinContent(k,br)
                    hr.SetBinError(k,er)

                hr.SetLineWidth   (linewidth)
                hr.SetMarkerSize  (markersize)
                hr.SetMarkerStyle (mrk)
                hr.SetLineColor   (col)
                hr.SetMarkerColor (col)
                hratios.append(hr)

            dstack = ROOT.THStack('ratios','ratios')
            ROOT.SetOwnership(dstack,True)

            # and then the ratios
            herr = hratios[0]
            herr.SetNameTitle('err0','zero errors')
            herr.SetMarkerSize(0)
            herr.SetMarkerColor(style.errcol)
            herr.SetFillStyle(0)
            herr.SetFillColor(style.errcol)
            herr.SetLineColor(style.errcol)

            # error borders
            herrUp = herr.Clone('errup')
            herrDw = herr.Clone('errdw')

            herrUp.Reset()
            herrDw.Reset()

            for k in xrange(nbins+2):
                b,e = herr.GetBinContent(k),herr.GetBinError(k)
                herrUp.SetAt( 1+e, k)
                herrDw.SetAt( 1-e, k)

            herr.SetFillStyle(style.errsty)

            # build the stack
            dstack.Add(herr,'E2')
            dstack.Add(herrUp,'hist')
            dstack.Add(herrDw,'hist')
            map(dstack.Add,hratios[1:])

            dstack.Draw('nostack %s' % options )
            dstack.SetMinimum(0.)
            dstack.SetMaximum(2.)

            ax = dstack.GetXaxis()
            ay = dstack.GetYaxis()
            ax.SetTitle(h0.GetXaxis().GetTitle())
            ax.SetMoreLogLabels(style.morelogx)
            ay.SetTitle(style.ytitle2)

            self._dstack = dstack

            line = ROOT.TGraph(2)
            line.SetNameTitle('oneline','oneline')
            line.SetPoint(0,ax.GetXmin(),1)
            line.SetPoint(1,ax.GetXmax(),1)
            line.SetBit(ROOT.kCanDelete)
            ROOT.SetOwnership(line,False)
            line.Draw()

#             if style.userrangex != (0.,0.): self._setrangeuser( ax, style )
            if style.userrangex != (0.,0.): ax.SetRangeUser(*(style.userrangex) )

        c.applystyle()

        return c

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

