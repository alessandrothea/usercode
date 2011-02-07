#!/usr/bin/env python

import optparse
import sys
import ROOT
import shutil
import os

def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-t', '--treeName', dest='treeName', help='Name of the tree', )
    parser.add_option('-p', '--path', dest='path', help='Path to the rootfile', )

    (opt, args) = parser.parse_args()
    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()

    if opt.treeName is None or opt.path is None:
        parser.error('Please define both the tree and the path')

    print sys.argv[0]
    chain = ROOT.TChain(opt.treeName)
    chain.Add(opt.path)
    print 'Reading',opt.path
    print 'Nentries:',chain.GetEntries()

    chain.MakeClass('ETHZNtupleReader')

    scriptDir = os.path.dirname(sys.argv[0])+'/'
    if os.path.exists('ETHZNtupleReader.h'):
        shutil.move('ETHZNtupleReader.h',scriptDir+'../include/ETHZNtupleReader.h')
    if os.path.exists('ETHZNtupleReader.C'):
        shutil.move('ETHZNtupleReader.C',scriptDir+'../src/ETHZNtupleReader.cc')
    

if __name__ == '__main__':
    main()
