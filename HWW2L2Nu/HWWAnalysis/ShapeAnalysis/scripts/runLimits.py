#!/usr/bin/env python

import sys
import os.path
import hwwinfo
import hwwtools
import optparse
import fnmatch
import subprocess
import hwwlimits

indir  = 'datacards/'
outdir = 'limits/'
def main():

    usage = '''usage: %prog [opts] dctag'''
    parser = optparse.OptionParser(usage)
    parser.add_option('-s','--stepping',dest='stepping',help='Switch stepping on ', action='store_true', default=False)
    parser.add_option('-1',dest='minuit1',help='Minuit ', action='store_true', default=False)
    parser.add_option('-n',dest='dryrun',help='Dry run ', action='store_true', default=False)
    parser.add_option('-o',dest='observed',help='Observed only', action='store_true', default=False)
    parser.add_option('--prefix','-p',dest='prefix',help='prefix',default=None)
    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)

    (opt, args) = parser.parse_args()
    print 'Running with lumi',opt.lumi
    
    constraints = {
        '*':'--rMin=0.01'
    }

    if len(args) != 1:
        parser.error('One and only one datacard tag at the time')

    tag = args[0]

    if tag not in hwwlimits.dcnames['all']:
        parser.error('Wrong tag: '+', '.join(sorted(hwwlimits.dcnames['all'])))

    tmpl = 'hww-{lumi:.2f}fb.mH{mass}.{tag}_shape.txt'
#     masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]
    masses = opt.mass

    if opt.prefix:
        os.chdir(opt.prefix)
        print 'Running in ',os.getcwd()

    if not os.path.exists(indir):
        print 'Error: datacard directory',indir,'not found'
        sys.exit(-1)

    allcards = [(mass,os.path.join(indir,tmpl.format(mass=mass, tag=tag, lumi=opt.lumi))) for mass in masses] 
    for mass,card in allcards:
        if ((int(opt.lumi)<10 or int(opt.lumi)>22) and (int(mass)==145 or int(mass)==155)): continue
        if not os.path.exists(card):
            print 'Error: missing datacard: '+card
            sys.exit(-1)

    os.system('mkdir -p '+outdir)

    tagname = 'HWW_'+tag+'_shape'
    for mass,card in allcards:
        print opt.lumi, mass
        if ((int(opt.lumi)<10 or int(opt.lumi)>22) and (int(mass)==145 or int(mass)==155)): continue
        exe  = 'combine -v 2 -M Asymptotic'
        flags = ' -n %s -m %s %s'%(tagname,mass,card)
        if opt.stepping:
            flags = ' --minosAlgo stepping'+flags
        if opt.minuit1:
            flags = ' --minimizerAlgo Minuit'+flags
        if opt.observed:
            flags = ' --run observed'+flags
        for c,flag in constraints.iteritems():
            if fnmatch.fnmatch(str(mass),c):
                flags = ' '+flag+flags

        command = exe+flags

        print '-'*50
        print command
        if opt.dryrun: continue
        code = os.system(command)
        move = 'mv higgsCombine%s.Asymptotic.mH%d.root %s' % (tagname,mass,outdir)
        print move
        os.system(move)
        
        if code: sys.exit(code)

if __name__ == '__main__':
    main()

