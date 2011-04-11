#!/usr/bin/env python

import sys
import ROOT
import array


canvases = []

def JVetoEff( rootFile ):
    global canvases
    f = ROOT.TFile.Open( rootFile )
    if not f.IsOpen():
        pass 
    
    name = 'pileUp/llNjetsNvrtx'
    jv = f.Get(name)
    if not jv.__nonzero__():
        raise NameError('histogram '+name+' not found in '+rootFile)
    #jv.Draw()
    
    nx = jv.GetNbinsX()
    ny = jv.GetNbinsY()

    yMin = jv.GetYaxis().GetXmin()
    yMax = jv.GetYaxis().GetXmax()
    ROOT.TH1.AddDirectory(False)
    hists = []
    x, ex = array.array('d'), array.array('d')
    y, ey = array.array('d'), array.array('d')
    
    for i in range(1,nx+1):
        h = ROOT.TH1F(jv.GetName()+'_'+str(i),jv.GetTitle(),ny,0,ny)
        ROOT.SetOwnership( h , False )
        for j in range(1,ny+1):
#            print i,j
            v = jv.GetBinContent(i,j)
            h.SetBinContent(j,v)
            h.GetXaxis().SetTitle(jv.GetYaxis().GetTitle())
        
        
        v, errV = 0, 0;
        zeroJets = h.GetBinContent(1)
        allJets  = h.Integral()
        if allJets != 0:

#            print h.Integral(),h.GetBinContent(1)
            if zeroJets != 0:
                v = zeroJets/allJets
                errV = v*ROOT.TMath.Sqrt(1/zeroJets+1/allJets)
            else:
                v = 0
                errV = 0
            y.append(v)
            x.append(i)
        
            ey.append(errV)
            ex.append(0)
        
#        print i,v
        hists.append(h)
#        print i,h.GetName()
    
#    print y
#    print ey
    
    c1 = ROOT.TCanvas()
    ROOT.SetOwnership( c1 , False )

    g = ROOT.TGraphErrors(len(x), x,y,ex,ey)
    ROOT.SetOwnership(g,False)
    
    g.SetTitle('Jet Veto efficiency')
    g.SetMarkerStyle(20)
    g.GetXaxis().SetTitle('n_{vrtx}')
    g.GetYaxis().SetTitle('efficiency')
    g.Draw('AP')

#    print hists
    stack = ROOT.THStack('aaa','aaa')
    ROOT.SetOwnership( stack, False )
    for h in hists:
#        print h
#        print h.GetName()
        stack.Add(h)

    return 

    c2 = ROOT.TCanvas()
    ROOT.SetOwnership( c2 , False )
    
#    print canvases
#    canvases = []    
#    c = ROOT.TCanvas()
#    canvases.append(c)
    stack.Draw('nostack')
    stack.GetXaxis().SetTitle(jv.GetYaxis().GetTitle())
#    hists[0].Draw()

    g = ROOT.TGraphErrors()

if __name__ == '__main__':
    
    args = sys.argv[:]
    sys.argv.append( '-b' )
    import ROOT
    ROOT.gROOT.SetBatch()
    if len(args) is not 2:
        print '   Usage: %s <path>' % sys.argv[0]
    sys.exit(0)
    
    try:
        JVetoEff( args[1] )
    except ValueError as e:
        print '\n  Error : '+str(e)+'\n'
                