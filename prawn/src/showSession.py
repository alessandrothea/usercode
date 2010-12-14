#!/usr/bin/env python
import checkpython
import optparse
import jobtools
import sys

def main():
    usage = 'Usage: %prog [options] session'
    parser = optparse.OptionParser(usage)

    parser.add_option('-d', '--database', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-g', '--groups', dest='sessionGroups', help='Comma separated list of groups')

    (opt, args) = parser.parse_args()

    m = jobtools.Manager(opt.database)
    m.connect()

    sessions = m.getAllSessions(opt.sessionGroups)
#    sessions = sorted(sessions, key=lambda s: s.name)
    
    hline = '-'*80
    print hline
    print str('| name\tLabel\t\tnJobs\tstatus').expandtabs(15)
    print hline
    table = []
    padding = 2
    table.append(['name','status','label','groups','nJobs'])
    for s in sessions:
        table.append([s.name,jobtools.JobLabel[s.status],s.label,s.groups,str(s.nJobs)])
#        line = '| \''+s.name+'\'\t\''+s.label+'\'\t'+s.groups+'\t'+str(s.nJobs)+'\t'+jobtools.JobLabel[s.status]
#        print line.expandtabs(15)
#        print hline
    
    widths = [0]*len(table[0])
    for j in range(len(table[0])):
        widths[j] = max([len(row[j]) for row in table])

#    print widths
    for row in table[0:0]:
        print hline
        print '| ',
        for i in range(len(row)):
            print row[i].ljust(widths[i]+padding),
        print
    for row in table[1:]:
#        print hline
        print '| ',
        for i in range(len(row)):
            print row[i].ljust(widths[i]+padding),
        print
    print hline 

if __name__ == '__main__':
    main()
