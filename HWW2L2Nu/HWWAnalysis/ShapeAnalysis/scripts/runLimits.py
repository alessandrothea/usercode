#!/usr/bin/env python

import sys
import os
import hwwinfo
import optparse
import fnmatch
import subprocess

inputDir = 'datacards/'
outputDir = 'limits/'
def main():

    usage = 'usage: %prog [dir] [cmd]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-s','--stepping',dest='stepping',help='Switch stepping on ', action='store_true', default=False)
    parser.add_option('-1',dest='minuit1',help='Minuit ', action='store_true', default=False)
    parser.add_option('--prefix','-p',dest='prefix',help='prefix',default=None)
    hwwinfo.addOptions(parser)
    hwwinfo.loadOptDefaults(parser)

    (opt, args) = parser.parse_args()
    print 'Running with lumi',opt.lumi
    

    tags = {
        'comb':'comb',
        'allcomb':'allcomb',
        'comb_0j':'comb_0j',
        'comb_1j':'comb_1j',
        'of_0j':'of_0j',
        'of_1j':'of_1j',
        'sf_0j':'sf_0j',
        'sf_1j':'sf_1j',
    }

    constraints = {
        '*':'--rMin=0.01'
#         '110':'--rMax ',
#         '115':'--rMax 50',
#         '120':'--rMax 40',
#         '130':'--rMin 0.01 --rMax 20',
#         '140':'--rMax 8',
#         '150':'--rMax 8',
#         '160':'--rMax 8',
#         '170':'--rMax 8',
#         '180':'--rMax 8 --rMin 0.1',
# #         '190':'--rMax 8 --rMin 0.1',
#         '200':'--rMax 10 --rMin 0.1',
# #         '300':'--rMax 10 --rMin=0.5',
#         '400':'--rMin=0.1',
    }

    if len(args) < 1 or args[0] not in tags:
        parser.error('tag can be '+' '.join(tags.keys()))

    tag = args[0]

    print opt.__dict__
    lumistr = '{lumi:.2f}'.format(lumi=opt.lumi)
    tmpl = 'hww-'+lumistr+'fb.mH{mass}.{tag}_shape.txt'
    masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]
    allcards = [tmpl.format(mass = mass, tag = tags[tag] ) for mass in masses] 

    print allcards
    if opt.prefix:
        os.chdir(opt.prefix)
#         subprocess.call('echo AAA $PWD',shell=True)
#     return
        print 'Running in ',os.getcwd()
    os.system('mkdir -p '+outputDir)

    if not os.path.exists(inputDir):
        print 'Error: datacard directory',inputDir,'not found'

    tagname = 'HWW_'+tags[tag]+'_shape'
    for card in allcards:
        mass = card.split('.')[-3].replace('mH','')
        exe  = 'combine -v 2 -M Asymptotic'
        flags = ' -n '+tagname+' -m '+mass+' '+inputDir+'/'+card
        if opt.stepping:
            flags = ' --minosAlgo stepping'+flags
        if opt.minuit1:
            flags = ' --minimizerAlgo Minuit'+flags
        for c,flag in constraints.iteritems():
            if fnmatch.fnmatch(str(mass),c):
                flags = ' '+flag+flags

#         if mass in constraints:
#             flags = ' '+constraints[mass]+flags
        command = exe+flags

        print '-'*50
        print command
        print '-'*50
        subprocess.call(command, shell=True)
        print 'mv higgsCombine'+tagname+'.Asymptotic.mH'+mass+'.root '+outputDir
        subprocess.call( 'mv higgsCombine'+tagname+'.Asymptotic.mH'+mass+'.root '+outputDir, shell=True)
        
if __name__ == '__main__':
    main()

