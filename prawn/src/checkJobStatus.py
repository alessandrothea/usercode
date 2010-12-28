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
import console


        
def main():


    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')

    (opt, args) = parser.parse_args()
    
    if opt.sessionName is None:
        parser.error('The session name is undefined')
    
    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    m = jobtools.Manager(dbPath)
    m.connect()
    s = m.getSession(opt.sessionName)
    jobs = m.getJobs(s.name)
    updated = []
    
    hline = '-'*80
    print hline
    print '| Checking jobs for session ['+s.name+']'
    print hline
    print '|  mode:',s.mode,' nJobs:',s.nJobs,' epJ:',str(s.eventsPerJob),' queue:',s.queue
    print hline
    jMap = qsubtools.runQstatXML()
    
    isCompleted = True
    for job in jobs:
        if job.status == jobtools.kSubmitted or job.status == jobtools.kRunning:
            # check if the job is still in the queue
            if job.name() in jMap:
                # check if the job is still there
                state = jMap[job.name()]['state']
                if 'w' in state:
                    # ok, still waiting
                    job.status = jobtools.kSubmitted
                    updated.append(job)
                elif 'r' in state:
                    # running, update the status
                    job.status = jobtools.kRunning
                    updated.append(job)
                else:
                    print 'Reported job status is',state
                
            elif os.path.exists(job.exitPath): 
                # not there, check if it is finished
                job.exitCode = int(open(job.exitPath).read())
                job.status = jobtools.kCompleted if job.exitCode==0 else jobtools.kFailed
                updated.append(job)
            else:
                # lost?
                print ' Job '+job.name()+' does not exist in the queue and no exit code file was found. Unknown'
        elif job.status == jobtools.kUnknown and os.path.exists(job.exitPath):
            print ' The exitCode file has appeared. Registering the exit status'
            job.exitCode = int(open(job.exitPath).read())
            job.status = jobtools.kCompleted if job.exitCode==0 else jobtools.kFailed
            updated.append(job)

        print '|   ',job.name(), 'is', jobtools.colState(job.status),'(code',job.exitCode,')'
        isCompleted &= job.status == jobtools.kCompleted
    
    m.updateJobCodes(s.name, updated)
    if isCompleted:
        m.setSessionStatus(s.name, jobtools.kCompleted)

    print hline
    m.disconnect()

if __name__ == '__main__':
    main()