#!/usr/bin/env python
'''
Created on Dec 3, 2010

@author: ale
'''
import checkpython
import optparse
import PrawnTools
import qsubtools
import os
import console


        
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=PrawnTools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-g', '--group', dest='sessionGroup', help='Comma separated list of groups')

    (opt, args) = parser.parse_args()
    
    if opt.sessionName is None and opt.sessionGroup is None:
        parser.error('Please define either the session or the group')
   
    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    m = PrawnTools.Manager(dbPath)
    m.connect()
    
    ses = m.getListOfSessions(opt.sessionName, opt.sessionGroup)
    jobMap = qsubtools.runQstatXML()
    
    for s in ses:
        jobs = m.getJobs(s.name)
    
        hline = '-'*80
        print hline
        print '| Session ['+s.name+']:','mode:',s.mode,' nJobs:',s.nJobs,' epJ:',str(s.eventsPerJob),' queue:',s.queue
#        print hline
        
        (completed, updated) = checkJobs(jobs, jobMap)

        m.updateJobCodes(s.name, updated)
        if completed:
            m.setSessionStatus(s.name, PrawnTools.kCompleted)

    print hline
    m.disconnect()


def printTable( states ):

    for (state,jobs) in states.iteritems():
        print '|   ',PrawnTools.colState(state),':',','.join([str(j.jid) for j in jobs]) 

def checkJobs( jobs, jMap ):
    isCompleted = True
    updated = []
    
    hasCreated   = False;
    hasSubmitted = False;
    hasRunning   = False;
    hasCompleted = False;
    
    states = {}
    for job in jobs:
        if job.status == PrawnTools.kSubmitted or job.status == PrawnTools.kRunning:
            # check if the job is still in the queue
            if job.name() in jMap:
                # check if the job is still there
                state = jMap[job.name()]['state']
                if 'w' in state:
                    # ok, still waiting
                    job.status = PrawnTools.kSubmitted
                    updated.append(job)
                elif 'r' in state:
                    # running, update the status
                    job.status = PrawnTools.kRunning
                    updated.append(job)
                else:
                    print 'Reported job status is',state
                
            elif os.path.exists(job.exitPath): 
                # not there, check if it is finished
                job.exitCode = int(open(job.exitPath).read())
                job.status = PrawnTools.kCompleted if job.exitCode==0 else PrawnTools.kFailed
                updated.append(job)
            else:
                # lost?
                print ' Job '+job.name()+' does not exist in the queue and no exit code file was found. Unknown'
        elif job.status == PrawnTools.kUnknown and os.path.exists(job.exitPath):
            print ' The exitCode file has appeared. Registering the exit status'
            job.exitCode = int(open(job.exitPath).read())
            job.status = PrawnTools.kCompleted if job.exitCode==0 else PrawnTools.kFailed
            updated.append(job)

        if job.status not in states.keys():
            states[job.status] = []
        
        states[job.status].append( job )
        
        isCompleted &= job.status == PrawnTools.kCompleted

    printTable( states )    
    return (isCompleted, updated)

if __name__ == '__main__':
    main()