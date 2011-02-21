#!/usr/bin/env python

import optparse
import sys
import ROOT
import shutil
import os
import re

MAX_NMUS     = 30
MAX_NELES    = 20
MAX_NGENLEPT = 100
MAX_NJETS    = 100
MAX_NPHOS    = 50
MAX_NTRKS    = 500
MAX_HLTOBJ   = 10
MAX_NVRTX    = 25

def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-t', '--treeName', dest='treeName', help='Name of the tree', )
    parser.add_option('-p', '--path', dest='path', help='Path to the rootfile', )

    (opt, args) = parser.parse_args()
    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()

    className = 'ETHZNtupleReader'

    if opt.treeName is None or opt.path is None:
        parser.error('Please define both the tree and the path')

    print sys.argv[0]
    chain = ROOT.TChain(opt.treeName)
    chain.Add(opt.path)
    print 'Reading',opt.path
    print 'Nentries:',chain.GetEntries()

    chain.MakeClass(className)

    #patch the arrays
    print "Patching arrays"
    oldH = open(className+'.h')
    data = oldH.read()
    oldH.close()
    
    data = re.sub(r'\[[0-9]*\](; *//\[[NGenLeptons]*\])','['+str(MAX_NGENLEPT)+r']\1',data)

    data = re.sub(r'\[[0-9]*\](; *//\[[NMus]*\])',       '['+str(MAX_NMUS)+r']\1',data)
    data = re.sub(r'\[[0-9]*\](; *//\[[NEles]*\])',      '['+str(MAX_NELES)+r']\1',data)
    data = re.sub(r'\[[0-9]*\](; *//\[[NPhotons]*\])',   '['+str(MAX_NPHOS)+r']\1',data)

    data = re.sub(r'\[[0-9]*\](; *//\[[NJets]*\])',      '['+str(MAX_NJETS)+r']\1',data)
    data = re.sub(r'\[[0-9]*\](; *//\[[PFNJets]*\])',    '['+str(MAX_NJETS)+r']\1',data)
    data = re.sub(r'\[[0-9]*\](; *//\[[CANJets]*\])',    '['+str(MAX_NJETS)+r']\1',data)
    data = re.sub(r'\[[0-9]*\](; *//\[[JPTNJets]*\])',   '['+str(MAX_NJETS)+r']\1',data)

    data = re.sub(r'\[[0-9]*\](; *//\[[NTracks]*\])',    '['+str(MAX_NTRKS)+r']\1',data)
    data = re.sub(r'\[[0-9]*\](; *//\[[NPaths]*\])',     '['+str(MAX_HLTOBJ)+r']\1',data)
    data = re.sub(r'\[[0-9]*\](; *//\[[NVrtx]*\])',      '['+str(MAX_NVRTX)+r']\1',data)
    
    newH = open(className+'.h','w')
    newH.write(data)
    newH.close()

    scriptDir = os.path.dirname(sys.argv[0])+'/'
    if os.path.exists(className+'.h'):
        shutil.move(className+'.h',scriptDir+'../include/'+className+'.h')
    if os.path.exists(className+'.C'):
        shutil.move(className+'.C',scriptDir+'../src/'+className+'.cc')
    

if __name__ == '__main__':
    main()


