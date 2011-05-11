#!/usr/bin/env python
import checkpython
import optparse
import PrawnTools
import re

def plainStr( theStr ):
    # match the escape codes
    regex = re.compile('\\x1b\[[0-9;]*?[0-9]{2}m')
    return regex.sub('',theStr)
    
def main():
    usage = 'Usage: %prog [options] session'
    parser = optparse.OptionParser(usage)

    parser.add_option('-d', '--database', dest='database', help='Database path', default=PrawnTools.jmDBPath())
    parser.add_option('-g', '--group', dest='sessionGroup', help='Comma separated list of groups')
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-v', dest='verbosity', help='Verbose output',  action='count')

    (opt, args) = parser.parse_args()

    m = PrawnTools.Manager(opt.database)
    m.connect()

    sessions = m.getListOfSessions(opt.sessionName,opt.sessionGroup)
    
    if opt.verbosity is None and opt.sessionName is None:
        printSummary(sessions)
    else:
        printDetails(sessions, opt.verbosity)
        
    
    
def printDetails( sessions, verbosity ):
    if verbosity is None:
        verbosity = 0
    hline = '-'*80
    for s in sessions:
        print hline
        print '|  Session:',s.name,'-',s.label,PrawnTools.colState(s.status)
        print hline
        print '|  Groups:',s.groups
        print '|  Mode:',s.mode,'Njobs:',s.nJobs
        print '|  Queue: ',s.queue
        print '|  Nevents:',s.nTotEvents
        print '|  Output dir:',s.outputDir
        print '|  Working dir:',s.workingDir
        print '|  Opt Args:',s.optArgs
        print hline
        print '|  Command Line:'
        print s.cmdLine
        print hline
        if verbosity > 1:
            print '|  File list:'
            print s.allFiles
            print hline
            print '|  Template:'
            print s.template
    
def printSummary( sessions ):
    hline = '-'*80
    table = []
    padding = 0
    table.append(['name','status','label','groups','nJobs'])
    for s in sessions:
        table.append([s.name,PrawnTools.colState(s.status),s.label,s.groups,str(s.nJobs)])
 
    
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
