#!/usr/bin/env python
import checkpython
import optparse
import jobtools
import re

def plainStr( theStr ):
    # match the escape codes
    regex = re.compile('\\x1b\[[0-9;]*?[0-9]{2}m')
    return regex.sub('',theStr)
    
def main():
    usage = 'Usage: %prog [options] session'
    parser = optparse.OptionParser(usage)

    parser.add_option('-d', '--database', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-g', '--group', dest='sessionGroup', help='Comma separated list of groups')

    (opt, args) = parser.parse_args()

    m = jobtools.Manager(opt.database)
    m.connect()

    sessions = m.getListOfSessions(group=opt.sessionGroup)
    
    hline = '-'*80
#    print hline
#    print str('| name\tLabel\t\tnJobs\tstatus').expandtabs(15)
#    print hline
    table = []
    padding = 0
    table.append(['name','status','label','groups','nJobs'])
    for s in sessions:
        table.append([s.name,jobtools.colState(s.status),s.label,s.groups,str(s.nJobs)])
 
    
    widths = [0]*len(table[0])
    for j in range(len(table[0])):
        widths[j] = max([len(plainStr(row[j])) for row in table])

#    print widths
    print hline
    for row in table[0:1]:
        print '| ',
        for i in range(len(row)):
            print row[i].ljust(widths[i]+padding),
        print
    print hline

    for row in table[1:]:
        print '| ',
        for i in range(len(row)):
            dL = len(row[i])-len(plainStr(row[i]))
            print row[i].ljust(widths[i]+padding+dL),
        print
    print hline 

if __name__ == '__main__':
    main()
