#!/usr/bin/env python

import optparse
import hwwinfo
import os
import datetime

usage = 'usage: %prog <options>'
parser = optparse.OptionParser(usage)
parser.add_option('--prefix','-p',dest='prefix',help='prefix',default=None)
(opt, args) = parser.parse_args()

datacards = {}
datacards['chans'] = ['of_0j','of_1j','sf_0j','sf_1j']
datacards['of']    = ['of_0j','of_1j','comb_of']
datacards['sf']    = ['sf_0j','sf_1j','comb_sf']
datacards['shape'] = ['comb_0j1j','comb_0j','comb_1j','comb_of','comb_sf']
datacards['full']  = ['comb_0j1j2j']

datacards['all']  = datacards['chans']+datacards['shape']+datacards['full']+datacards['of']+datacards['sf']
datacards['0j1j'] = datacards['chans']+datacards['shape']

if len(args) < 1:
    parser.error('Check the usage!')

prefix = opt.prefix
prefix = prefix if prefix[-1] != '/' else prefix[:-1]

bins = datacards['chans']
if len(args) >= 1:
    if args[0] not in (datacards['all']+datacards.keys()):
        parser.error('Supported datacards: '+', '.join(datacards['all']+datacards.keys()) )
    else:
        bins = [ args[0] ] if args[0] not in datacards else datacards[args[0]]

logfile = open('qexe.log','a')
print >> logfile,'-'*100
print >> logfile,'choochoo! It\'s ',datetime.datetime.today()
print >> logfile,'-'*100
logfile.close()

for bin in bins:
    for mass in hwwinfo.masses:
        os.system('qexe.py -t '+prefix+'_'+bin+'_'+str(mass)+' "runLimits.py -s -m '+str(mass)+' '+bin+' -p '+prefix+'"')
 
os.system('watch \'tail -n 30 qexe.log;echo Remaining jobs: `qstat | wc -l`; qstat\'')

