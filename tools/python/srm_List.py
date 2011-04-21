#!/bin/env python

from sys import exit, argv
import subprocess

import optparse

def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--site', '-s', dest='site', help='Site where files are located. Can be [t3psi,t2cscs]')

    (opt, args) = parser.parse_args()

    if not opt.site:
        parser.error('No site selected')

    if len(args)!=1:
        parser.error('Wrong number of arguments')

    dir = args[0]

    if opt.site == 't3psi':
        srmpath = "srm://t3se01.psi.ch:8443/srm/managerv2?SFN="
        rootpath = srmpath+'/pnfs/psi.ch/cms/trivcat/'
    elif opt.site == 't2cscs':
        srmpath = "srm://storage01.lcg.cscs.ch:8443/srm/managerv2?SFN="
        rootpath = srmpath+"/pnfs/lcg.cscs.ch/cms/trivcat/"
    else:
        parser.error('site can be either t3psi or t2cscs')

    srmPath = rootpath+dir
    print "srmls "+srmPath
    srmls = subprocess.Popen(['srmls',srmPath])
    srmls.wait()

if __name__ == '__main__':
    main()
