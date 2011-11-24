#!/usr/bin/env python

import optparse
import hwwinfo
import os

usage = 'usage: %prog [dir] [cmd]'
parser = optparse.OptionParser(usage)
(opt, args) = parser.parse_args()

datacards = {}
datacards['split'] = ['of_0j', 'of_1j', 'sf_0j', 'sf_1j']
datacards['combined']=['comb','comb_0j','comb_1j','allcomb']

datacards['all'] = datacards['split']+datacards['combined']

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
 
os.system('watch "tail -n 30 qexe.log;echo \'Remaining jobs:\';qstat | wc -l; qstat"')


# if [ $# -ne $EXPECTED_ARGS ]
# then
#     echo "Usage: `basename $0` dir"
#     exit $E_BADARGS
# fi

# for bin in of_0j of_1j sf_0j sf_1j
# # for bin in comb comb_0j comb_1j;
# do
#     for m in $masses;
#     do qexe.py -t ${bin}_${m} "runLimits.py -p noshape -m ${m} $bin -p $1"
#     done
# done

# watch 'tail -n 30 qexe.log; qstat'
