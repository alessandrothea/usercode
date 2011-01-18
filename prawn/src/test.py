#!/usr/bin/env python
'''
Created on Dec 6, 2010

@author: ale
'''
import optparse
import jobtools
import os

def main():


    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-g', '--groups', dest='sessionGroups', help='Comma separated list of groups')

    (opt, args) = parser.parse_args()
    
#    if opt.sessionName is None:
#        parser.error('The session name is undefined')
    
    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    m = jobtools.Manager(dbPath)
    m.connect()
    
    ses = m.getListOfSessions(opt.sessionName, opt.sessionGroups)
    
    
    for s in ses:
        print s.name
#    s = m.getSession(opt.sessionName)
#    jobs = m.getJobs(s.name)
#    
#    hline = '-'*80
#    print hline
#    print '| Checking jobs for session ['+s.name+']'
#    print hline
#    print '|  mode:',s.mode,' nJobs:',s.nJobs,' epJ:',str(s.eventsPerJob),' queue:',s.queue
#    print hline
#    
#    nLoop = 100;
#    for job in jobs:
#        print 'Testing',job.name()
#        print 'os.path.exist',nLoop
#        for i in range(nLoop):
#            os.path.exists(job.exitPath)
#    
##        print job.status
##        print 'state writing'
##        for i in range(nLoop):
##            m.setJobStatus(s.name, job.jid, job.status)
##        
##        print 'exit code writing'
##        for i in range(nLoop):
##            m.setJobExitCode(s.name, job.jid, job.exitCode)
#    print 'job status/exitCode'
#    for i in range(nLoop):
#        m.updateJobCodes(s.name,jobs)
#    print hline
#    m.disconnect()


if __name__ == '__main__':
    main()
        