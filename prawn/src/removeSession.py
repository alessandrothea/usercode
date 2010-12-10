#!/usr/bin/env python
'''
Created on Dec 3, 2010

@author: ale
'''
import checkpython
import optparse
import jobtools
import os

def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    (opt, args) = parser.parse_args()
    
    if opt.sessionName is None:
        parser.error('Please specify what session to remove')
    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    m = jobtools.Manager(dbPath)
    m.connect()
    m.removeSession(opt.sessionName)
    m.disconnect()
    
    
if __name__ == "__main__":
    main()