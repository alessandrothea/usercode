#!/usr/bin/env python
'''
Created on Dec 3, 2010

@author: ale
'''
import checkpython
import optparse
import jobtools
import os, subprocess

def runQstat():
    qstat = subprocess.Popen(['qstat'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout,stderr) = qstat.communicate()
    
    if len(stdout)==0:
        return None
    # split in lines
    outLines = stdout.splitlines()
    
    # remove header
    outLines.pop(0)
    outLines.pop(0)
    
    q = []
    for line in outLines:
        q.append(line.split())
    
    return q
    
    
def main():


    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-n', '--sessionName', dest='sessionName', help='Name of the session', default='mySession')

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
    qstatOut = runQstat()
    

    for job in jobs:
        print ' Checking '+job.name() 
        if job.status == jobtools.kSubmitted or job.status == jobtools.kRunning:
            # check if the job is still in the queue
            found = False
            if qstatOut:
                for line in qstatOut:
                    found = line[2] == job.name()
                    if found:
                        break
            if found:
                # check fi the job is still there
                print ' Job '+job.name()+' is currently Queued/Running'
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
        elif job.status == jobtools.kCompleted or job.status == jobtools.kFailed:
            print '|   ',job.name(), 'is', jobtools.JobLabel(job.status)
    print hline
    m.disconnect()

if __name__ == '__main__':
    main()