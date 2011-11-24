#!/usr/bin/env python

import sys
import ROOT
import os.path
import optparse

mypath = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    usage = 'usage: %prog indir outdir'
    parser = optparse.OptionParser(usage)
    parser.add_option('-d','--depth',dest='maxDepth',default=-1)
    (opt, args) = parser.parse_args()
    fileList = []
    if len(args) < 2:
        parser.error('2 arguments required')
    indir  = args[0] if args[0][-1] == '/' else args[0]+'/'
    outdir = args[1] if args[1][-1] == '/' else args[1]+'/'
    for root, subFolders, files in os.walk(indir):
        for file in files:
            if not file.endswith('.root'): continue
            fileList.append(os.path.join(root,file))
        print fileList

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()
    
    ROOT.gROOT.ProcessLine('.L '+mypath+'/SlimSkim.C+g')

    l = len(indir)
    
    selection = 'trigger && nextra == 0 && mll > 12 && mpmet> 20'

    for file in fileList:
        newfile = file.replace(indir,outdir)
        newdir  = os.path.dirname(newfile)
        if not os.path.exists(newdir):
            os.system('mkdir -p '+newdir)
        print file,newfile
        

        inputfile = file
        outputfile = newfile
        print 'Input: ',inputfile
        print 'Output:',outputfile
        entries = ROOT.SlimSkim(selection,inputfile, outputfile)
        print 'Input size: ',os.path.getsize(inputfile)
        print 'Output size:',os.path.getsize(outputfile)


