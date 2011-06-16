#!/usr/bin/env python
'''
Created on Dec 3, 2010

@author: ale
'''
import checkpython
import optparse
import jobtools
import qsubtools
import os


        
def main():


    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')

    (opt, args) = parser.parse_args()
    
    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    m = jobtools.Manager(dbPath)
    m.connect()
    s = m.getSession(opt.sessionName)
    jobs = m.getJobs(s.name)
    
    hline = '-'*80
    print hline
    print '| Checking jobs for session ['+s.name+']'
    print hline
    print '|  mode:',s.mode,' nJobs:',s.nJobs,' epJ:',str(s.eventsPerJob),' queue:',s.queue
    print hline
    (qNames, qJobs) = qsubtools.runQstatXML()
    
    isCompleted = True
    for job in jobs:
#        print ' Checking '+job.name() 
        if job.status == jobtools.kSubmitted or job.status == jobtools.kRunning:
            # check if the job is still in the queue
#            print job.exitPath,  os.path.exists(job.exitPath)
            if job.name() in qNames:
                # check fi the job is still there
#                print ' Job '+job.name()+' is currently Queued/Running'
                job.status = jobtools.kRunning
                m.setJobStatus(s.name, job.jid, job.status)
            elif os.path.exists(job.exitPath): 
                # not there, check if it is finished
                print ' exitCode file found. Registering the exit status'
                exitCode = int(open(job.exitPath).read())
                status = jobtools.kCompleted if exitCode==0 else jobtools.kFailed
                m.setJobStatus(s.name, job.jid, status)
                m.setJobExitCode(s.name, job.jid, exitCode)
            else:
                # lost?
                print ' Job '+job.name()+' does not exist in the queue and no exit code file was found. Unknown'
                m.setJobStatus(s.name, job.jid, jobtools.kUnknown)
                m.setJobExitCode(s.name, job.jid, None)
        elif job.status == jobtools.kUnknown and os.path.exists(job.exitPath):
            print ' The exitCode file has appeared. Registering the exit status'
            exitCode = int(open(job.exitPath).read())
            status = jobtools.kCompleted if exitCode==0 else jobtools.kFailed
            m.setJobStatus(s.name, job.jid, status)
            m.setJobExitCode(s.name, job.jid, exitCode)
        print '|   ',job.name(), 'is', jobtools.JobLabel[job.status]
        isCompleted &= job.status == jobtools.kCompleted
    if isCompleted:
        m.setSessionStatus(s.name, jobtools.kCompleted)

    print hline
    m.disconnect()

if __name__ == '__main__':
    main()