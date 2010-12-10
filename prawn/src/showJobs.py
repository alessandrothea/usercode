#!/usr/bin/env python
import checkpython
import optparse
import jobtools
import os

def main():
    usage = 'Usage: %prog [options] session jobs'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-a', '--all', dest='all', help='Selects all jobs', action='store_true')
    parser.add_option('-v', '--verbose', dest='verbose', help='Verbose output', action='store_true')
    (opt, args) = parser.parse_args()

    dbPath     = os.path.abspath(os.path.expanduser(opt.database))


    m = jobtools.Manager(dbPath)
    
    m.connect()
    try:
        session = m.getSession(opt.sessionName)
        jobs = m.getJobs(session.name)
    except ValueError as e:
        print '\n  Error : '+str(e)+'\n'
        return 
        

    hline = '-'*80
    print hline
    print '| Displaying jobs for session ['+session.name+']'
    print hline
    print '|  mode:',session.mode,' nJobs:',session.nJobs,' epJ:',str(session.eventsPerJob),' queue:',session.queue
    print hline
    print '|  id,Name,(Status,ExitCode),firstEvent,nEvents'
    print hline
    for job in jobs:
        print '| ',job.jid,job.name(),'('+jobtools.JobLabel[job.status]+','+str(job.exitCode)+')',job.firstEvent,job.nEvents,job.scriptPath,job.outputFile,job.stdOutPath
#        print '| ',job.jid,job.name(),'('+str(job.status)+','+str(job.exitCode)+')',job.firstEvent,job.nEvents,job.scriptPath,job.outputFile,job.stdOutPath
        if opt.verbose: 
            print '|  inputFile  = ',job.inputFile
            print '|  outputFile = ',job.outputFile
            print '|  scriptPath = ',job.scriptPath 
            print '|  exitPath   = ',job.exitPath
            print '|  stdOutPath = ',job.stdOutPath
            print '|  stdErrPath = ',job.stdErrPath
            lines = job.script.split('\n')
            for line in lines:
                print '|   ',line
    print hline

    m.disconnect()
    
    


if __name__ == '__main__':
    main()
