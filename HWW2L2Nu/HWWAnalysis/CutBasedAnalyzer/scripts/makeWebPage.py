#!/usr/bin/env python

import sys
import HWWAnalysis.Misc.ROOTAndUtils as utils
import optparse
import ROOT
import shutil
import os.path
import tempfile

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)

# add option for the output directory
parser.add_option('-o','--output',dest='webRoot',help='Destination directory', default='webplots')
parser.add_option('--tgz',dest='tgz',help='make a tar', action='store_true')
# add option for the output graphics
# add the option of the php file

(opt, args) = parser.parse_args()

if len(args) != 1:
    parser.error('Wrong number of arguments')

plotFile = args[0]

plotRoot = ROOT.TFile.Open(plotFile)


finder = utils.ObjFinder('TCanvas')

objPaths = set(finder.find(plotRoot))

# print objPaths

rootDir= opt.webRoot
rootDir= os.path.expanduser(rootDir)

if opt.tgz:
    rootDir = tempfile.mkdtemp('webplots')

if rootDir[-1] != '/':
    rootDir += '/'

dirs = set()
for p in objPaths:
    dirs.add(os.path.dirname(p))

goodiesPath = os.getenv('CMSSW_BASE')+'/src/HWWAnalysis/Misc/goodies/'
php = goodiesPath+'index.php'

if not os.path.exists(php):
    print 'Warning:',php,'not found'

print dirs
for d in dirs:
    newdir = rootDir+d
    os.system('mkdir -p '+newdir)
    shutil.copy2(php,newdir)

for p in objPaths:
    canvas = plotRoot.Get(p)
    canvas.Size(40.,40.)
    basename = canvas.GetName().replace(' ','_')
#     for logY in [0,1]:
    for ext in ['png','pdf']:
#             print os.path.dirname(p),basename,logY,ext
#             canvas.SetLogy(logY)
#             scale = 'log' if logY==1 else 'lin'
#             canvas.Print(rootDir+os.path.dirname(p)+'/'+basename+'_'+scale+'.'+ext)
        canvas.Print(rootDir+os.path.dirname(p)+'/'+basename+'.'+ext)

if opt.tgz:
    tarFile = os.path.basename(plotFile)+'.tgz'
    cwd = os.getcwd()
    os.chdir(rootDir)
    os.system('tar cvfz '+tarFile+' *')
    shutil.copy2(rootDir+tarFile,cwd)
    shutil.rmtree(rootDir)

