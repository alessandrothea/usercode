#!/usr/bin/env python

import ROOT
import sys
import os.path
import operator
import optparse
from HWWAnalysis.Misc.odict import OrderedDict

colors = [ROOT.kOrange+7, ROOT.kSpring-1, ROOT.kAzure-3, ROOT.kViolet-5, ROOT.kRed+1,ROOT.kCyan-3, ROOT.kPink-9,ROOT.kGreen+3, ROOT.kBlack]
    
class limitPoint: pass

def readsummary( path ):
    if not os.path.exists(path):
        raise ValueError('Summary file '+path+' not found')

    summary = []
    f = open(path)
    for line in f:
        tokens = line.split()
        #expect 7 columns (1 fake)
        if len(tokens) != 8:
            raise ValueError('Expected 7 entries, '+str(len(tokens))+' found')
        
        p = limitPoint()
        p.mass = int(tokens[0])
        p.obs = float(tokens[1])
        p.median = float(tokens[3])
        # exp 68
        p.exp68down = float(tokens[4])
        p.exp68up   = float(tokens[5])
        p.dExp68down = p.median-p.exp68down
        p.dExp68up   = p.exp68up-p.median

        # exp 95
        p.exp95down = float(tokens[6])
        p.exp95up   = float(tokens[7])
        p.dExp95down = p.median-p.exp95down
        p.dExp95up   = p.exp95up-p.median
        summary.append(p)

    f.close()
    return summary

def drawsave( multi, legend, name, drawopt='', line=True ):
    c = ROOT.TCanvas('dummy','dummy')
    multi.Draw(drawopt)
    c.Modified()
    c.Update()

    xax = multi.GetXaxis()
    yax = multi.GetYaxis()
    x1 = xax.GetXmin()
    x2 = xax.GetXmax()

    multi.GetXaxis().SetTitle("Higgs mass [GeV/c^{2}]");
    if line:
        yax.SetTitle("95% Limit on #sigma/#sigma_{SM} ");
        yax.SetRangeUser(0,5.)
        theLine = ROOT.TGraph(2)
        theLine.SetName('theLine')
        theLine.SetPoint(0,1,1)
        theLine.SetPoint(1,700,1)
        theLine.SetLineWidth(2)
        theLine.Draw('L')

    legend.Draw()

    c.Modified()
    c.Update()
    for ext in ['pdf','png']:
        c.SaveAs(name+'.'+ext)
#     c.SaveAs('.png')
#     c.SaveAs('.root')


#     if line:
    xax.SetRangeUser(110,150)
    if line:
        yax.SetRangeUser(0,5)
    c.Modified()
    c.Update()
    for ext in ['pdf','png']:
        c.SaveAs(name+'_zoom.'+ext)
#     c.SaveAs(name+'_zoom.png')

def medianPlot( summary, label ):
    n = len(summary)
    median = ROOT.TGraph(n)
    median.SetNameTitle(label+'ExpMedian',label+' median expected')
    for i,p in enumerate(summary):
        median.SetPoint(i,p.mass,p.median)

    median.SetLineWidth(2)
    return median

def observedPlot( summary, label ):
    n = len(summary)
    observed = ROOT.TGraph(n)
    observed.SetNameTitle(label+'observed',label+' observed')
    for i,p in enumerate(summary):
        observed.SetPoint(i,p.mass,p.obs)

#     observed.SetLineWidth(2)
    return observed

def updownPlots( summary, cl, label  ):
    n = len(summary)
    up   = ROOT.TGraph(n)
    up.SetNameTitle(label+'Exp'+cl+'up',label+' expected '+cl+'% upper bound')
    up.SetLineWidth(2)

    down = ROOT.TGraph(n)
    down.SetNameTitle(label+'Exp'+cl+'down',label+' expected '+cl+'% lower bound')
    down.SetLineWidth(2)

    upattr = 'exp'+cl+'up'
    downattr = 'exp'+cl+'down'
    for i,p in enumerate(summary):
        up.SetPoint(i,p.mass, getattr(p,upattr))
        down.SetPoint(i,p.mass, getattr(p,downattr))
    
    return (up,down)

def rangeBandPlot( summary, cl, label ):
    n = len(summary)
    band = ROOT.TGraphAsymmErrors(n)
    band.SetNameTitle(label+'Exp'+cl,label+' expected '+cl+'% range')

    upattr = 'dExp'+cl+'up'
    downattr = 'dExp'+cl+'down'
    for i,p in enumerate(summary):
        band.SetPoint(i,p.mass, p.median)
        band.SetPointError(i,0.,0.,getattr(p,downattr), getattr(p,upattr))
    
    return band

def bandWidthPlots( summary, cl, label  ):
    n = len(summary)
    width   = ROOT.TGraph(n)
    width.SetNameTitle(label+'Exp'+cl+'bandwidth',label+' expected '+cl+'% bandwidth')
    width.SetLineWidth(2)

    upattr = 'dExp'+cl+'up'
    downattr = 'dExp'+cl+'down'
    for i,p in enumerate(summary):
        width.SetPoint(i,p.mass, getattr(p,upattr)+getattr(p,downattr))
    
    return width

def diffMedExp(refsummary,summary,label):
    n = len(summary)
    diffmed = ROOT.TGraph(n)
    diffmed.SetNameTitle(label+'ExpMedian',label+' median expected')
    for i,p in enumerate(summary):
        r = refsummary[i]
        diffmed.SetPoint(i,p.mass,(p.median-r.median)/r.median)

    diffmed.SetLineWidth(2)
    return diffmed



def setlinecolor( col, *args ):
    for arg in args:
        arg.SetLineColor(col)

def setfillcolor( col, *args ):
    for arg in args:
        arg.SetFillColor(col)

def setlinestyle( style, *args ):
    for arg in args:
        arg.SetFillStyle(style)

def setAtt(name, value, *args):
    f = operator.methodcaller(name, value)
#     print f, args
    for arg in args:
        f(arg)


def overlap( deck, tag, reference=None, prefix=None ):
    '''Overlap the limits from different working areas'''

    obsrvd   = ROOT.TMultiGraph('observed','Observed')
    expctd   = ROOT.TMultiGraph('expected','Expected')
    medExp   = ROOT.TMultiGraph('medExp','Median Expected')
    ran68    = ROOT.TMultiGraph('ran68','68% expected range')
    ran95    = ROOT.TMultiGraph('ran95','95% expected range')
    width68  = ROOT.TMultiGraph('width68','68% range width')
    width95  = ROOT.TMultiGraph('width95','95% range width')

    diffMed      = ROOT.TMultiGraph('medExp','Median Expected difference')
    diffWidth68  = ROOT.TMultiGraph('width68','68% range width difference')
    diffWidth95  = ROOT.TMultiGraph('width95','95% range width difference')




    x1 = 0.85
    y1 = 0.85

    x0 = 0.45
    y0 = 0.55

    legend = ROOT.TLegend(x0,y0,x1,y1)
    legend.SetFillColor(ROOT.kWhite)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    if reference:
        label,path = reference
        refsummary = readsummary(path+'/limits/'+tag+'_shape.summary')
#         print refsummary
        obs = observedPlot(refsummary,label) 
        med = medianPlot(refsummary, label)
        band68 = rangeBandPlot(refsummary, '68', label)
        band95 = rangeBandPlot(refsummary, '95', label)

        obs.SetMarkerStyle(21)
        
        setAtt('SetLineColor', ROOT.kGray, med, band68, band95)
#         setlinecolor(ROOT.kGray+2, med, band68, band95)
        setfillcolor(ROOT.kGreen-10, band68, band95)
        setfillcolor(ROOT.kYellow-10, band95)

        medClone = med.Clone()
        medExp.Add(band95.Clone(),'3')
        medExp.Add(band68.Clone(),'3')
        medExp.Add(medClone)

        obsrvd.Add(band95.Clone(),'3')
        obsrvd.Add(band68.Clone(),'3')
        obsrvd.Add(med.Clone())
        obsrvd.Add(obs,'LP')

        ran68.Add(band95.Clone(),'3')
        ran68.Add(band68.Clone(),'3')
        ran68.Add(med.Clone())

        ran95.Add(band95.Clone(),'3')
        ran95.Add(band68.Clone(),'3')
        ran95.Add(med.Clone())

        if reference:
            dmed = diffMedExp(refsummary,refsummary,label)
            setAtt('SetLineColor',ROOT.kGray,dmed)
            diffMed.Add(dmed)
        legend.AddEntry(medClone,label,'L')



    for i,(l,d) in enumerate(decks.iteritems()):
        print i,l
        summary = readsummary(d+'/limits/'+tag+'_shape.summary')

        obs = observedPlot(summary,l)
        med = medianPlot(summary,l)
        up68, down68 = updownPlots(summary, '68', l)
        up95, down95 = updownPlots(summary, '95', l)
        bw68 = bandWidthPlots(summary, '68', l) 
        bw95 = bandWidthPlots(summary, '95', l) 

#         med.SetLineColor( colors[i] )
        setlinecolor(colors[i], obs, med, up68, down68, up95, down95, bw68, bw95)

        medExp.Add(med)
        obsrvd.Add(obs)
        ran68.Add(up68)
        ran68.Add(down68)
        ran95.Add(up95)
        ran95.Add(down95)
        width68.Add(bw68)
        width95.Add(bw95)

        # make the full
        expctd.Add(med.Clone())
        up68prime   = up68.Clone()
        down68prime = down68.Clone()
        setAtt('SetLineStyle',2,up68prime, down68prime)
        up95prime   = up95.Clone()
        down95prime = down95.Clone()
        setAtt('SetLineStyle',3,up95prime, down95prime)

        expctd.Add(up68prime)
        expctd.Add(down68prime)
        expctd.Add(up95prime)
        expctd.Add(down95prime)

        legend.AddEntry(med,l,'L')

        if reference:
            dmed = diffMedExp(refsummary,summary,l)
            setAtt('SetLineColor',colors[i],dmed)
            diffMed.Add(dmed)


    
    if prefix:
        outprefix = os.path.join(prefix,tag)
        if not os.path.exists(prefix):
            os.makedirs(prefix)
    else:
        outprefix = tag

    
 
    drawsave(obsrvd,legend,outprefix+'_observed','AL')
#     drawsave(expctd,legend,outprefix+'_expected')
    drawsave(medExp,legend,outprefix+'_expMedian','AL')
#     drawsave(width68,legend,outprefix+'_bandwidth68')
#     drawsave(width95,legend,outprefix+'_bandwidth95')
#     drawsave(ran68,legend,outprefix+'_exp68Range')
#     drawsave(ran95,legend,outprefix+'_exp95Range')

    diffMed.Draw('A')

    ROOT.gPad.ls()
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
    diffMed.GetYaxis().SetTitle('Median, relative difference')
    drawsave(diffMed,legend,outprefix+'_diffExpMedian','AL',False)
    

def overlapOld( decks, tag ):
    '''Overlap the limits from different working areas'''

    medExp = ROOT.TMultiGraph('medExp','Median Expected')
    ran68  = ROOT.TMultiGraph('ran68','68% expected range')
    ran95  = ROOT.TMultiGraph('ran95','95% expected range')

    x1 = 0.85
    y1 = 0.85

    x0 = 0.65
    y0 = 0.65

    legend = ROOT.TLegend(x0,y0,x1,y1)
    legend.SetFillColor(ROOT.kWhite)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)


    graphs = []
    for i,(l,d) in enumerate(decks.iteritems()):
        
        summary = readsummary(d+'/limits/'+tag+'_shape.summary')
        # build 3 graphs
        
        n = len(summary)
        gExpMedian = ROOT.TGraph(n)
        gExp68up   = ROOT.TGraph(n)
        gExp68down = ROOT.TGraph(n)
        gExp95up   = ROOT.TGraph(n)
        gExp95down = ROOT.TGraph(n)
        gExp68     = ROOT.TGraphAsymmErrors(n)
        gExp95     = ROOT.TGraphAsymmErrors(n)

        gExpMedian.SetNameTitle(l+'ExpMedian',l+' median expected')
        
        gExp68.SetNameTitle(l+'Exp68',l+' expected 68% range')
        gExp68up.SetNameTitle(l+'Exp68up',l+' expected 68% upper bound')
        gExp68down.SetNameTitle(l+'Exp68down',l+' expected 68% lower bound')

        gExp95.SetNameTitle(l+'Exp95',l+' median 95% range')
        gExp95up.SetNameTitle(l+'Exp95up',l+' expected 95% upper bound')
        gExp95down.SetNameTitle(l+'Exp95down',l+' expected 95% lower bound')

        # colors
        gExpMedian.SetLineColor(colors[i])

        gExp68up.SetLineColor(colors[i])
        gExp68down.SetLineColor(colors[i])
        gExp68up.SetLineWidth(2)
        gExp68down.SetLineWidth(2)
#         gExp68up.SetLineStyle(7)
#         gExp68down.SetLineStyle(7)

        gExp95up.SetLineColor(colors[i])
        gExp95down.SetLineColor(colors[i])
        gExp95up.SetLineWidth(2)
        gExp95down.SetLineWidth(2)
#         gExp95up.SetLineStyle(9)
#         gExp95down.SetLineStyle(9)
        
        # fill

        gExp68.SetFillColor(colors[i])
        gExp68.SetFillStyle(3001)
        gExp95.SetFillColor(colors[i])
        gExp95.SetFillStyle(3609)
        for i,p in enumerate(summary):
            gExpMedian.SetPoint(i,p.mass,p.median)
            gExp68up.SetPoint(i,p.mass, p.exp68up)
            gExp68down.SetPoint(i,p.mass, p.exp68down)
            gExp95up.SetPoint(i,p.mass, p.exp95up)
            gExp95down.SetPoint(i,p.mass, p.exp95down)

            gExp68.SetPoint(i,p.mass, p.median)
            gExp68.SetPointError(i,0.,0.,p.dExp68down, p.dExp68up)
            gExp95.SetPoint(i,p.mass, p.median)
            gExp95.SetPointError(i,0.,0.,p.dExp95down, p.dExp95up)

        
        gExpMedian.SetLineWidth(2)
        medExp.Add(gExpMedian)
        ran68.Add(gExp68up)
        ran68.Add(gExp68down)
        ran95.Add(gExp95up)
        ran95.Add(gExp95down)
#         ran68.Add(gExp68,'3')
#         ran95.Add(gExp95,'3')
        legend.AddEntry(gExpMedian,l,'L')
    
    drawsave(medExp,legend,tag+'_expMedian')
    drawsave(ran68,legend,tag+'_exp68Range')
    drawsave(ran95,legend,tag+'_exp95Range')
    

if __name__ == '__main__':

    usage = 'Usage: %prog -t <tag> deck1 deck2 deck3'
    parser = optparse.OptionParser(usage)
    parser.add_option('-r','--reference',dest='reference',help='Compare to a reference histogram', default=None)
    parser.add_option('-t','--tag',dest='tag',help='Defint the tag to process', default=None)
    parser.add_option('-o','--out',dest='out',help='Output directory',default=None)
    
    (opt, args) = parser.parse_args()
    if not opt.tag:
        parser.print_help()
        parser.error('Tag not defined, check the usage')

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()

    decks = OrderedDict()
    for arg in args:
        if '=' not in arg:
            decks[os.path.basename(arg if arg[-1] != '/' else arg[:-1])] = arg
            continue

        i = arg.index('=')
        decks[arg[:i]]=arg[i+1:]

    print decks
    doexist = zip(map(os.path.exists,decks.itervalues()),decks.itervalues())

    dontexist = filter( lambda x: not x[0], doexist )

    if dontexist:
        raise ValueError('workareas not found:'+' '.join(map(operator.itemgetter(1),dontexist)))

    ref = None
    if opt.reference:
        if '=' not in opt.reference:
            ref = ( os.path.basename(arg if arg[-1] != '/' else arg[:-1]), opt.reference)
        else:
            i = opt.reference.index('=')
            ref = (opt.reference[:i],opt.reference[i+1:])

        
    overlap( decks, opt.tag, ref, opt.out )

