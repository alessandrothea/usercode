#!/usr/bin/env python

import sys
import glob
import tempfile
import optparse
import hwwinfo
import shutil
import tarfile

def pack():
    usage = 'usage: %prog -p path'
    parser = optparse.OptionParser(usage)
    parser.add_option('--prefix','-p',dest='prefix',help='prefix',default=None)
    hwwinfo.addOptions(parser)
    hwwinfo.loadOptDefaults(parser)

    (opt, args) = parser.parse_args()

    if not opt.prefix:
        parser.error('Prefix not defined: check the usage')
    prefix = opt.prefix if opt.prefix[-1] != '/' else opt.prefix[:-1]
    
    tmppath = tempfile.mkdtemp('_pack_'+prefix)
    shutil.copytree(prefix+'/datacards',tmppath+'/datacards')
    
    tarname = tmppath+'/'+prefix+'.tgz'
    tar = tarfile.open(tarname,mode='w:gz')
    tar.add(tmppath+'/datacards')
    tar.close()
    shutil.move(tarname,'.')

#     shutil.rmtree(tmppath)
    print tmppath

if __name__ == '__main__':
    pack()

