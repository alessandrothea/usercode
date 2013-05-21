#!/bin/env python

# TAxis mistery quantities

# labeloffset: TAxis wants it in units of the pad height(width) for the x(y) axis. The value in pixel must be divided by height-top-bottom (width-left-right)
# ticklength : The lenght is computed as fraction of the pad length times the ratio between the axis length and the total length of the other axis
#              i.e.: tick_x = k*axis_x/(axis_y/height)
# titleoffset: to be written
#        left,right,top,bottom = self._margins
#        lax = self._w-left-right
#        lay = self._h-top-bottom
#        style['ticklength']  *= self._w/float(lax*self._h)
#        style['labeloffset'] /= float(self._h-top-bottom)
#        style['titleoffset'] *= self._obj.GetWh()/(1.6*self._h*style['titlesize']) if style['titlesize'] else 0
#
# TLatex BoxSize:
# for some reasons GetBoundingBox returns 0
#
# TLatex::GetXsize(), TLatex::GetYsize() are working, but the result have to be converted
#
#        pw = pad.GetWw()*pad.GetWNDC()
#        ph = pad.GetWh()*pad.GetHNDC()
#
#        uxmin = pad.GetUxmin()
#        uxmax = pad.GetUxmax()
#        uymin = pad.GetUymin()
#        uymax = pad.GetUymax()
#
#        dx = (uxmax-uxmin)/(1-pad.GetLeftMargin()-pad.GetRightMargin())
#        dy = (uymax-uymin)/(1-pad.GetTopMargin()-pad.GetBottomMargin())
#
#        pxlength = dummy.GetXsize()*pw/(ph*dx)
#        pxheight = dummy.GetYsize()*pw/(ph*dx)

import ROOT
import uuid
import sys
import copy
import logging

_tcanvas_winframe_width  = 4
_tcanvas_winframe_height = 28

def _makecanvas(name,title,w,h):
    '''What about usign TCanvas.SetCanvasSize to ensure the correct geometry?'''
    return ROOT.TCanvas(name,title, w+_tcanvas_winframe_width, h+_tcanvas_winframe_height)


class StyleSetter:
    _log = logging.getLogger('StyleSetter')

    _setters = {
        ROOT.TAttAxis:[
            ('labelfamily' , ROOT.TAxis.SetLabelFont),
            ('labelsize'   , ROOT.TAxis.SetLabelSize),
            ('labeloffset' , ROOT.TAxis.SetLabelOffset),
            ('titlefamily' , ROOT.TAxis.SetTitleFont),
            ('titlesize'   , ROOT.TAxis.SetTitleSize),
            ('titleoffset' , ROOT.TAxis.SetTitleOffset),
            ('ticklength'  , ROOT.TAxis.SetTickLength),
            ('ndivisions'  , ROOT.TAxis.SetNdivisions),
        ],

        ROOT.TAttText:[
            ('textfamily',ROOT.TAttText.SetTextFont),
            ('textsize'  ,ROOT.TAttText.SetTextSize),
            ('textcolor' ,ROOT.TAttText.SetTextColor),
            ('textangle' ,ROOT.TAttText.SetTextAngle),
            ('textalign' ,ROOT.TAttText.SetTextAlign),
        ],

        ROOT.TAttLine:[
            ('linecolor' ,ROOT.TAttLine.SetLineColor),
            ('linestyle' ,ROOT.TAttLine.SetLineStyle),
            ('linewidth' ,ROOT.TAttLine.SetLineWidth),
        ],

        ROOT.TAttFill:[
            ('fillcolor' ,ROOT.TAttFill.SetFillColor),
            ('fillstyle' ,ROOT.TAttFill.SetFillStyle),
            ('fillstyle' ,ROOT.TAttFill.SetFillStyle),
        ],
    }

    def __init__(self, **opts ):
        self._opts = opts

    def apply(self, tobj, **opts):

        myopts = self._opts.copy()
        myopts.update( opts )

        for cls,methods in self._setters.iteritems():
            if not isinstance(tobj,cls): continue

            for l,m in methods:
                x = myopts.get(l,None)
                if not x is None:
                    m(tobj,x)

#_______________________________________________________________________________
#     ____            __
#    / __ \____ _____/ /
#   / /_/ / __ `/ __  /
#  / ____/ /_/ / /_/ /
# /_/    \__,_/\__,_/
#
class Pad(object):
    _log = logging.getLogger('Pad')

    _axisstyle = {
        'labelfamily' : 4,
        'labelsize'   : 20,
        'labeloffset' : 2,
        'titlefamily' : 4,
        'titlesize'   : 25,
        'titleoffset' : 30.,
        'ticklength'  : 10,
        'ndivisions'  : 505,
    }
    #---
    def __init__(self, name, width=500, height=500, **opts ):
        self._name = name
        self._w = width
        self._h = height
        self._align = ('c','m') # lcr
        self._showtitle = False
        self._showstats = False
        self._obj = None

        self._margins = (60,60,60,60)
        self._xaxis = self._axisstyle.copy()
        self._yaxis = self._axisstyle.copy()

        # temp solution

        for n,o in opts.iteritems():
            attr = '_'+n
            if not hasattr(self,attr): continue
            if n == 'xaxis' or n == 'yaxis':
                getattr(self,attr).update(o)
            else:
                setattr(self,attr,o)
        self._build()

    #---
    def _build(self):
        m = self._margins
        if isinstance(m,tuple):
            if len(m) == 1:
                m = (m[0],m[0],m[0],m[0])
            elif len(m) == 2:
                m = (m[0],m[0],m[1],m[1])
            elif len(m) == 4:
                pass
            else:
                raise ValueError('margins must be a 1,2,4 length tuple')
        self._margins = m

    @property
    def xaxis(self): return xaxis

    @property
    def yaxis(self): return yaxis

    def __str__(self):
        return '%s(\'%s\',w=%d,h=%d,obj=%s)' % (self.__class__.__name__,self._name,self._w,self._h,self._obj)

    #---
    def __getattr__(self,name):
        if not self._obj:
            raise AttributeError('%s not found' % name)
        return getattr(self._obj,name)


    #---
    def _applypadstyle(self):

        left,right,top,bottom = self._margins
        fh,fw = float(self._h),float(self._w)

        if not top    is None : self._obj.SetTopMargin    ( top/fh )
        if not bottom is None : self._obj.SetBottomMargin ( bottom/fh )
        if not left   is None : self._obj.SetLeftMargin   ( left/fw )
        if not right  is None : self._obj.SetRightMargin  ( right/fw )

    #---
    def _applyframestyle(self):

        h = None
        for o in self._obj.GetListOfPrimitives():
            if not (isinstance(o,ROOT.TH1) or isinstance(o,ROOT.THStack) or isinstance(o,ROOT.TMultiGraph)): continue
            h = o
            break

        if not h: return

        if not self._showtitle:
            frame = h.GetHistogram() if isinstance(h, ROOT.THStack) or isinstance(h,ROOT.TMultiGraph) else h
            frame.SetBit(ROOT.TH1.kNoTitle)

            for o in self._obj.GetListOfPrimitives():
                if isinstance(o,ROOT.TPaveText) and o.GetName()=='title':
                    ROOT.SetOwnership(o,True)
                    del o

        if not self._showstats:
            frame.SetBit(ROOT.TH1.kNoStats)
            o = h.FindObject('stats')
            if o.__nonzero__():
                ROOT.SetOwnership(o,True)
                del o

        left,right,top,bottom = self._margins
        lax = self._w-left-right
        lay = self._h-top-bottom

        setter = StyleSetter()

        # TODO massive cleanup needed
        xax = h.GetXaxis()
        style = self._xaxis.copy()
        style['ticklength']  *= self._w/float(lax*self._h)
        style['labeloffset'] /= float(self._h-top-bottom)

        # alwyas variable size fonts
        style['titlefamily']  = style['titlefamily']*10+2
        #print 'bu',style['titleoffset'], style['titlesize']
        #TODO careful the order here is important, as titleoffset is using titlesize in pixels
        style['titleoffset'] *= 1./(1.6*style['titlesize']) if style['titlesize'] else 0
        style['titlesize']   /= float(self._h)
        style['labelfamily']  = style['labelfamily']*10+2
        style['labelsize']   /= float(self._h)
        #print '->>>oioioioioi',style['titlefamily'],style['titlesize'],style['titleoffset']

        setter.apply(xax,**style)
        self._log.debug('tick xaxis: %s => %s',self._xaxis['ticklength']),style['ticklength']


        yax = h.GetYaxis()
        style = self._yaxis.copy()
        style['ticklength']   *= self._h/float(lay*self._w)
        style['labeloffset']  /= float(self._w-left-right)
        #style['titleoffset'] *= self._obj.GetWh()/(1.6*self._w*style['titlesize']) if style['titlesize'] else 0

        style['titlefamily']  = style['titlefamily']*10+2
        #print 'bu',style['titleoffset'], style['titlesize']
        #style['titleoffset'] *= 1./(1.6*style['titlesize']) if style['titlesize'] else 0
        style['titleoffset'] *= self._h/(1.6*style['titlesize']*self._w) if style['titlesize'] else 0
        style['titlesize']   /= float(self._h)
        style['labelfamily']  = style['labelfamily']*10+2
        style['labelsize']   /= float(self._h)
        #print '->>> Y',style['titlefamily'],style['titlesize'],style['titleoffset']

        setter.apply(yax,**style)
        self._log.debug('tick yaxis: %s =>  %s',self._yaxis['ticklength'])

class Canvas(object):
    _log = logging.getLogger('Canvas')

    #---
    def __init__(self, minsize=(0,0)):
        self._minsize = minsize
        self._pads = []
        self._gridX = {} #new
        self._hrows = []
        self._wcols = []
        self._obj = None


    #---
    def __getattr__(self,name):
        if not self._obj:
            raise AttributeError
        return getattr(self._obj,name)

    # the alignement should be decided here
    def attach(self, pad, i, j ):
        #if ( i < 0 and i > self._nx ) or ( j < 0 and j > self._ny ):
            #raise IndexError('Index out of bounds (%d,%d) not in [0,%d],[0,%d]' % (i,j,self._nx,self._ny))

        #old = self._grid[i][j]
        #if not old is None: self._pads.pop(old)

        self._gridX[i,j] = pad #new
        if not pad: return

        self._pads.append(pad)

    def __setitem__(self,key,value):
        if not isinstance(key,tuple):
            raise TypeError('XXXX')

        if len(key) != 2:
            raise RuntimeError('Wrong dimension')

        self.attach( value, *key )

    #---
    def get(self,i,j):
        pad = self._gridX[i,j] if (i,j) in self._gridX else None

        return pad

    #---
    def __getitem__(self, key):
        if not isinstance(key,tuple):
            raise TypeError('XXXX')

        if len(key) != 2:
            raise RuntimeError('Wrong dimension')

        return self.get( *key )

    #---
    def _computesize(self): # new

        nx = max( i for i,j in self._gridX.iterkeys())+1
        ny = max( j for i,j in self._gridX.iterkeys())+1

        #print nx,ny,self._gridX.keys()

        mw,mh = self._minsize
        hrows = [mh]*ny
        wcols = [mw]*nx

        for (i,j),pad in self._gridX.iteritems():
            if not pad: continue
            wcols[i] = max(wcols[i],pad._w)
            hrows[j] = max(hrows[j],pad._h)
            #print wcols[i],hrows[j]

        self._hrows = hrows
        self._wcols = wcols
        h = sum(self._hrows)
        w = sum(self._wcols)
        return w,h

    #---
    def size(self):
        return self._computesize()

    #---
    def _getanchors(self,i,j):
        return sum(self._wcols[0:i]),sum(self._hrows[0:j])

    #---
    def makecanvas(self, name=None, title=None):

        if not name : name = 'canvas_'+str(uuid.uuid1())
        if not title: title = name

        w,h = self._computesize() #new

        fw,fh = float(w),float(h)
#         c = ROOT.TCanvas(name,title, w+4, h+28)
        c = _makecanvas(name,title,w,h)
        c.Draw()

        k = 2

        for (i,j),pad in self._gridX.iteritems():
            if not pad: continue

            # assule left-top alignement
            x0,y0 = self._getanchors(i,j)
            x1,y1 = x0+pad._w,y0+pad._h

            gw,gh = self._wcols[i],self._hrows[j]
#                 print i,j,gw,gh,pad._w,pad._h

            ha,va = pad._align

            if   va == 't':
                pass
            elif va == 'm':
                y0 += (gh-pad._h)/2.
                y1 += (gh-pad._h)/2.
            elif va == 'b':
                y0 += gh-pad._h
                y1 += gh-pad._h
            else:
                raise KeyError('Unknown vertical alignement %s', va)

            if   ha == 'l':
                pass
            elif ha == 'c':
                x0 += (gw-pad._w)/2.
                x1 += (gw-pad._w)/2.
            elif ha == 'r':
                x0 += gw-pad._w
                x1 += gw-pad._w
            else:
                raise KeyError('Unknown horizontal alignement %s', ha)

            pname = 'pad_%d_%d' % (i,j)

#                 print pname,' [%d,%d][%d,%d] - [%d,%d][%d,%d]'% (x0,x1,y0,y1,x0,x1,(h-y1),(h-y0)), k
#                 print pname,x0/fw,(h-y0)/fh,x1/fw,(h-y1)/fh, k
            tpad = ROOT.TPad(pname,pname,x0/fw,(h-y1)/fh,x1/fw,(h-y0)/fh)#, k)
            tpad.Draw()
            pad._obj = tpad
            pad._applypadstyle()
            k += 1


        self._obj = c
        return c

    #---
    def applystyle(self):

        map(Pad._applyframestyle,self._pads)


#_______________________________________________________________________________
#     __                              __
#    / /   ___  ____ ____  ____  ____/ /
#   / /   / _ \/ __ `/ _ \/ __ \/ __  /
#  / /___/  __/ /_/ /  __/ / / / /_/ /
# /_____/\___/\__, /\___/_/ /_/\__,_/
#            /____/
class Legend(object):
    _log = logging.getLogger('Legend')

    _legendstyle = {
        'textfamily' : 4,
        'textsize'   : 20,
        'textcolor'  : ROOT.kBlack,
    }

    #---
    def __init__(self, nx, ny, boxsize, **opts):
        self._boxsize = boxsize
        self._nx = nx
        self._ny = ny

        self._labelwidth = None
        self._anchor = (0,0)
        self._align = ('c','m')
        self._style = self._legendstyle.copy()

        for n,o in opts.iteritems():
            attr = '_'+n
            if not hasattr(self,attr): continue
            if n == 'style':
                getattr(self,attr).update(o)
            else:
                setattr(self,attr,o)

        self._grid = [[None]*ny for i in xrange(nx)]
        self._legends = []
        self._sequence = [ (i,j) for i in xrange(self._nx) for j in xrange(self._ny) ]
        self._cursor = 0
        self._maxlabelwidth = 0

    #---
    def _rootstyle(self):
        '''Convert the pixel-based style into ROOT parameters'''

        # extract the pad height
        pad = ROOT.gPad.func()
        ph = pad.GetWh()*pad.GetHNDC()

        style = self._style.copy()
        style['textfamily'] = style['textfamily']*10+2
        style['textsize']  /= ph
        return style

    #---
    @property
    def sequence(self):
        return self._sequence[:]

    #---
    @sequence.setter
    def sequence(self,value):

        if len(set(value)) != len(value):
            raise RuntimeError('There are duplicates in the new sequence!')

        if len(value) > self._nx*self._ny:
            raise ValueError('New sequence longer than label')

        self._sequence = value

    #---
    def _updatebox(self):
        '''Recalculate the legend box parameters'''
        # apply the style to all the elements first
        for leg in self._legends:
            self._applystyle(leg)

        # extract the pad size
        pad = ROOT.gPad.func()
        pw = pad.GetWw()*pad.GetWNDC()
        ph = pad.GetWh()*pad.GetHNDC()

        #
        dummy = ROOT.TLatex(0,0,'')
        setter = StyleSetter(**(self._rootstyle()))
        setter.apply(dummy)


        uxmin = pad.GetUxmin()
        uxmax = pad.GetUxmax()
        uymin = pad.GetUymin()
        uymax = pad.GetUymax()

        dx = (uxmax-uxmin)/(1-pad.GetLeftMargin()-pad.GetRightMargin())
        dy = (uymax-uymin)/(1-pad.GetTopMargin()-pad.GetBottomMargin())

        # for each row and col check whether there is at lest an entry
        hrows = [False]*self._ny
        wcols = [False]*self._nx
        widths = []

        for i,col in enumerate(self._grid):
            for j,entry in enumerate(col):
                if not entry: continue
                wcols[i] = True
                hrows[j] = True
                (title,leg) = entry

                dummy.SetTitle(title)

#                 print pad.GetName(),dummy.GetTitle(),dummy.GetXsize()*pw/(ph*dx),dummy.GetYsize()/dy
                #widths.append( dummy.GetXsize()*pw/(ph*dx) )
                widths.append( dummy.GetXsize()*pw/(dx) )

        # add 10%
        self._maxlabelwidth = int(max(widths)*1.1)

        self._colcount = wcols.count(True)
        self._rowcount = hrows.count(True)


    #---
    def _getanchor(self,i,j):
        labelwidth = self._labelwidth if self._labelwidth is not None else self._maxlabelwidth
        x0,y0 = self._anchor[0]+i*(labelwidth+self._boxsize),self._anchor[1]+j*self._boxsize

        ha,va = self._align
        if   va == 't':
            pass
        elif va == 'm':
            y0 -= self._rowcount*self._boxsize/2.
        elif va == 'b':
            y0 -= self._rowcount*self._boxsize
        else:
            raise KeyError('Unknown vertical alignement %s', va)

        if   ha == 'l':
            pass
        elif ha == 'c':
            x0 -= self._colcount*(self._boxsize+labelwidth)/2.
        elif ha == 'r':
            x0 -= self._colcount*(self._boxsize+labelwidth)
        else:
            raise KeyError('Unknown horizontal alignement %s', ha)

        return x0,y0

    #---
    def _applystyle(self,leg):
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetMargin( 1 )

        methods = [
            ('textfamily'      , leg.SetTextFont),
            ('textsize'        , leg.SetTextSize),
        ]

        rstyle = self._rootstyle()
        for l,m in methods:
            x = rstyle.get(l,None)
            if not x is None: m(x)#; print x,m.__name__


    #---
    def addentry(self, obj, opt='', title=None, pos=None ):
        # override the appendion sequence
        if pos:
            i,j = pos
            if ( i < 0 and i > self._nx ) or ( j < 0 and j > self._ny ):
                raise IndexError('Index out of bounds (%d,%d) not in [0,%d],[0,%d]' % (i,j,self._nx,self._ny))
        else:
            if self._cursor >= len(self._sequence):
                raise IndexError('The legend is full!')

            i,j = self._sequence[self._cursor]

            self._cursor += 1

        if not self._grid[i][j] is None:
            raise RuntimeError('Entry (%d,%d) is already assigned' % (i,j))

        self._grid[i][j] = (obj,opt,title)

        leg = ROOT.TLegend( 0, 0, 1, 1 )
        title = obj.GetTitle() if title is None else title
        leg.AddEntry(obj,title,opt)

        #self._applystyle(leg)
        self._legends.append( leg )

        self._grid[i][j] = (title,leg)


    #---
    def _point(self, x,y):

        pad = ROOT.gPad.func()
        fw = pad.GetWw()*pad.GetWNDC()
        fh = pad.GetWh()*pad.GetHNDC()

        mxsize = 16
        mosize = 8

        u = x/fw
        v = (fh-y)/fh

        ul = (x+mxsize/2)/fw
        vl = (fh-(y-mxsize/2))/fh

        l = ROOT.TLatex(ul,vl,'(%d,%d)'% (x,y) )
        l.SetTextFont(44)
        l.SetTextSize(10)
        l.SetNDC()
        ROOT.SetOwnership(l,False)

        mx = ROOT.TMarker(u,v,ROOT.kPlus)
        mx.SetNDC()
        mx.SetMarkerSize(mxsize/8.)
        mx.SetBit(ROOT.TMarker.kCanDelete)
        ROOT.SetOwnership(mx,False)

        mo = ROOT.TMarker(u,v,ROOT.kCircle)
        mo.SetNDC()
        mo.SetMarkerSize(mosize/8.)
        mo.SetBit(ROOT.TMarker.kCanDelete)
        ROOT.SetOwnership(mo,False)

        ms = ROOT.TList()
        ms.Add(mx)
        ms.Add(mo)
        ms.Add(l)

        ROOT.SetOwnership(ms,False)

        return ms

    #---
    def draw(self):

        self._updatebox()

        pad = ROOT.gPad.func()
        fw = pad.GetWw()*pad.GetWNDC()
        fh = pad.GetWh()*pad.GetHNDC()

        #self._point(*(self._anchor)).Draw()
        #m = ROOT.TMarker(0,0,ROOT.kPlus)
        #l = ROOT.TLatex()
        for i,col in enumerate(self._grid):
            for j,entry in enumerate(col):
                if not entry: continue
                title,leg = entry

                x0,y0 = self._getanchor(i,j)
                x1,y1 = x0+self._boxsize,y0+self._boxsize

                #self._point(x0,y0).Draw()
                #self._point(x1,y1).Draw()

                u0 = x0/fw
                v0 = (fh-y1)/fh
                u1 = x1/fw
                v1 = (fh-y0)/fh

                leg.SetX1( u0 )
                leg.SetY1( v0 )
                leg.SetX2( u1 )
                leg.SetY2( v1 )
                leg.Draw()

#     __          __
#    / /   ____ _/ /____  _  __
#   / /   / __ `/ __/ _ \| |/_/
#  / /___/ /_/ / /_/  __/>  <
# /_____/\__,_/\__/\___/_/|_|
#
class Latex:
    _latexstyle = {
            'textfamily':44,
            'textsize'  :20,
            'textcolor' :ROOT.kBlack,
        }
    _hcodes = {
        'l':10,
        'c':20,
        'r':30,
    }
    _vcodes = {
        'b':1,
        'm':2,
        't':3,
    }


    # ---
    def __init__(self,text,**opts):
        self._text   = text

        self._anchor = (0,0)
        self._align = ('c','m')
        self._style = self._latexstyle.copy()

        for n,o in opts.iteritems():
            attr = '_'+n
            if not hasattr(self,attr): continue
            if n == 'style':
                getattr(self,attr).update(o)
            else:
                setattr(self,attr,o)

        self._latex = ROOT.TLatex()
        self._latex.SetNDC()

    #---
    def _rootstyle(self):
        '''Convert the pixel-based style into ROOT parameters'''

        # extract the pad height
        pad = ROOT.gPad.func()
        ph = pad.GetWh()*pad.GetHNDC()

        style = self._style.copy()
        style['textfamily'] = style['textfamily']*10+2
        style['textsize']  /= ph
        return style

    # ---
    def draw(self):

        pad = ROOT.gPad.func()
        fw = float(pad.GetWw()*pad.GetWNDC())
        fh = float(pad.GetWh()*pad.GetHNDC())

        ha,va = self._align
        self._latex.SetTextAlign(self._hcodes[ha]+self._vcodes[va])

        setter = StyleSetter(**(self._rootstyle()))
        setter.apply(self._latex)

        x0,y0 = self._anchor
        self._latex.SetText( x0/fw, 1-(y0/fh), self._text )

        self._latex.Draw()


if __name__ == '__main__':

    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()

    c = Canvas(2,3)

    axst = {
    'labelfamily'       : 44,
    'labelsize'         : 20,
    'labeloffset'       : 0,
    'titlefamily'       : 44,
    'titlesize'         : 20,
    'titleoffset'       : 50,
    'ticklength'        : 10
    }
#     axst = {'label-family':42, 'label-size':0.04, }

    p0 = Pad('p0',200,500, margins=(20,80,80,20), xaxis = axst, yaxis = axst, align=('l','b')  )
    p1 = Pad('p1',500,500, margins=(80,20,20,20), xaxis = axst, yaxis = axst )
    p2 = Pad('p2',500,200, margins=(80,20,20,20), xaxis = axst, yaxis = axst )
    p3 = Pad('p3',500,200, margins=(80,20,20,80), xaxis = axst, yaxis = axst )
    p4 = Pad('p4',200,200, margins=(20,80,20,80), xaxis = axst, yaxis = axst )
    p5 = Pad('p5',200,200, margins=(20,80,80,20), xaxis = axst, yaxis = axst, align=('l','b') )
    p1._xaxis['label-size'] = 0.0
    p2._xaxis['label-size'] = 0.0
#     p3._xaxis['title-offset'] = 2.5
#     p4._xaxis['title-offset'] = 2.5

#     c.attach(p0,1,0)
    c[1,0] = p0
    c.attach(p1,0,0)
    c.attach(p2,0,1)
    c.attach(p3,0,2)
    c.attach(p4,1,2)
    c.attach(p5,1,1)


    tc = c.makecanvas()
    tc.SetName('aaa')

    bins = 10
    hdummy = ROOT.TH1F('dummy','',bins,0,bins)
    hs = ROOT.THStack('stack','stocazz')
    hcols = []
    for i in xrange(bins):
        h = hdummy.Clone('col%d' % i)
        h.SetTitle(h.GetName())
        h.SetFillColor(i+ROOT.kOrange)
        h.SetLineColor(i+ROOT.kOrange)
        h.SetFillStyle(3001)
        h.SetLineWidth(2)
        h.Fill(i,i)
        ROOT.SetOwnership(h,False)
        hs.Add(h)
        hcols.append(h)


    p1.cd()
    hs1 = hs.Clone('xxx')
    hs1.Draw()
    hs1.GetYaxis().SetTitle('y-axis')
    hs1.GetXaxis().SetTitle('x-axis')
#     hs.Draw()
    leg = Legend(4,4, 80,30, anchor=(90,30))
    sequence = leg.sequence
    sequence.remove( (1,3) )
    sequence.remove( (2,3) )
    sequence.remove( (2,2) )
    leg.sequence = sequence
    leg.addentry(hcols[0],'f')
    leg.addentry(hcols[1],'f')
    leg.addentry(hcols[2],'f')
    leg.addentry(hcols[3],'f')
    leg.addentry(hcols[4],'f')
    leg.addentry(hcols[5],'f')
    leg.addentry(hcols[6],'f')
    leg.addentry(hcols[7],'f')
    leg.addentry(hcols[8],'f')
    leg.addentry(hcols[9],'f')
    leg.draw()

    p2.cd()
    hs2 = hs.Clone('yyy')
    hs2.Draw()
    hs2.GetYaxis().SetTitle('y-axis')
#     hs.Draw()

    pad = c.get(0,2)
    pad.cd()
    d3 = hdummy.Clone('d3')
    d3.GetYaxis().SetTitle('y-axis')
    d3.GetXaxis().SetTitle('x-axis')
    d3.Draw()

    pad = c.get(1,2)
    pad.cd()
    d4 = hdummy.Clone('d4')
    d4.GetXaxis().SetTitle('x-axis')
    d4.Draw('Y+')

    pad = c.get(1,1)
    pad.cd()
    d5 = hdummy.Clone('d5')
    d5.GetXaxis().SetTitle('x-axis')
    d5.Draw('Y+')

#     p0.cd()
#     d0 = hdummy.Clone('d0')
#     d0.GetXaxis().SetTitle('x-axis')
#     d0.Draw('Y+')

    c.applystyle()

#     tc.ls()
    ROOT.gSystem.ProcessEvents()


#     tc.Print('des.png')
    tc.Print('des.pdf')
    tc.Print('des.root')




