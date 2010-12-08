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
    usage = 'usage: %prog [options] <template file>'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-n', '--sessionName', dest='sessionName', help='Name of the session', default='mySession')
    (opt, args) = parser.parse_args()
    
    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    
    try:
        numbers = jobtools.argsToNumbers(args)
    except ValueError as e:
        parser.error('Error: '+str(e))

    print opt.sessionName,numbers

    m = jobtools.Manager(dbPath)
    m.connect()
    
    m.removeSession(opt.sessionName)
    m.disconnect()

if __name__ == '__main__':
    main()