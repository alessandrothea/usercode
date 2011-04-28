#!/usr/bin/env python

import optparse
import sys
import ROOT

def printCanvases( rootFile ):
    f = ROOT.TFile.Open( rootFile )
    if not f.IsOpen():
        raise ValueError('me cago')
    
    keys = f.GetListOfKeys()
    canvases = []
    for key in keys:
#        print key
        if key.GetClassName() == 'TCanvas':
            canvases.append(key.ReadObj())

    for c in canvases:
        c.Draw()
        c.Print(c.GetName()+".pdf")
    
if __name__ == '__main__':
    
    if len(sys.argv) is not 2:
        print '   Usage: %s <path>' % sys.argv[0]
        sys.exit(0)

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()
    
    try:
        printCanvases( sys.argv[1] )
    except ValueError as e:
        print '\n  Error : '+str(e)+'\n'
