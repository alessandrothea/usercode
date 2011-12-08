#!/usr/bin/env python

import optparse
import hwwinfo
import os
import datetime

usage = 'usage: %prog [dir] [cmd]'
parser = optparse.OptionParser(usage)
(opt, args) = parser.parse_args()

datacards = {}
datacards['split'] = ['of_0j', 'of_1j', 'sf_0j', 'sf_1j']
datacards['shape'] = ['comb_0j1j','comb_0j','comb_1j']
datacards['full']  = ['comb_0j1j2j']

datacards['all'] = datacards['split']+datacards['shape']+datacards['full']

if len(args) < 1:
    parser.error('Check the usage!')

bins = datacards['split']
if len(args) > 1:
    if args[1] not in datacards['all']+datacards.keys():
        parser.error('Supported datacards: '+', '.join(datacards['all']+datacards.keys()) )
    else:
        bins = [ args[1] ] if args[1] not in datacards else datacards[args[1]]

logfile = open('qexe.log','a')
print >> logfile,'-'*100
print >> logfile,'choochoo! It\'s ',datetime.datetime.today()
print >> logfile,'-'*100
logfile.close()

for bin in bins:
    for mass in hwwinfo.masses:
        os.system('qexe.py -t '+bin+'_'+str(mass)+' "runLimits.py -s -m '+str(mass)+' '+bin+' -p '+args[0]+'"')
 
os.system('watch \'tail -n 30 qexe.log;echo Remaining jobs: `qstat | wc -l`; qstat\'')

