#!/usr/bin/env python
import checkpython
import optparse
import jobtools

def main():
    usage = 'Usage: %prog [options] session'
    parser = optparse.OptionParser(usage)

    parser.add_option('-d', '--database', dest='database', help='Database path', default=jobtools.jmDBPath())
    (opt, args) = parser.parse_args()

    m = jobtools.Manager(opt.database)
    m.connect()

    m.showAllSessions()

    m.disconnect()
    
    

if __name__ == '__main__':
    main()
