#!/usr/bin/env python
import checkpython
import jobtools
import optparse
import os

def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-c', '--create', dest='create', help='Create a new db', action='store_true')
    parser.add_option('-d', '--drop', dest='drop', help='Drop the db', action='store_true')
    (opt, args) = parser.parse_args()

    dbPath = opt.database
    dbDir = os.path.dirname( dbPath )

    if opt.drop:
        if os.path.exists( dbPath ):
            os.remove(dbPath)
            print 'Database',dbPath,'removed'
    
    if opt.create:
        if not os.path.exists( dbDir ):
            os.makedirs( dbDir )
            print 'Directory',dbDir,'created'

        m = jobtools.Manager(dbPath)
        m.create()
        print 'Database',dbPath,'created'


if __name__ == "__main__":
    main()

