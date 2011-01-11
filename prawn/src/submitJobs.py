#!/usr/bin/env python
import checkpython
import optparse
import jobtools
import os, sys, subprocess

def main():
    usage = 'Usage: %prog [options] jobs'
    parser = optparse.OptionParser(usage)
    
    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-a', '--all', dest='all', help='Selects all jobs', action='store_true')
    parser.add_option('-n', '--dryRun', dest='dry', help='Dry run, produces the files but doesn\'t submit', action='store_true')
    parser.add_option('-r', '--resubmit', dest='resubmit', help='Resubmit jobs', action='store_true')
    parser.add_option('-j', '--jobs', dest='jobs',help='Jobs to process',default='')
    (opt, args) = parser.parse_args()

    if opt.sessionName is None:
        parser.error('The session name is undefined')
    
    try:
        numbers = jobtools.strToNumbers(opt.jobs)
    except ValueError as e:
        parser.error('Error: '+str(e))

    hline = '-'*80

    allJobs = len(numbers) == 0
    m = jobtools.Manager(opt.database)
    m.connect()

    try: 
        s = m.getSession( opt.sessionName )
        jobs = m.getJobs( opt.sessionName )
    except ValueError as e:
        print '\n  Error : '+str(e)+'\n'
        return

    if s.status is not jobtools.kCreated and not opt.resubmit:
        parser.error('The session is already submitted. Use -r to resubmit.')
    #print 'Session',s
    #print s.outputDir
    
    updated = submitSession(s,jobs,opt,numbers)
#    updated = []
#        
#    print hline
#    print '| Creating scripts for session',s.name
#    print hline
#
#    for job in jobs:
#        if not allJobs and job.jid not in numbers:
#            continue
#        
#        print '| ',job.name(),'...',
#        # makes destination directories
#        job.mkDirs()
#        # dump the script into the destination folder
#        script = open(job.scriptPath,'w')
#        script.write(job.script)
#        script.close()
#        # make it executable
#        os.chmod(job.scriptPath, 0755)
#        
#        #dump the input files into the input folder 
#        inputFile = open(job.inputFile,'w')
#        inputFile.write(job.fileList)
#        inputFile.close()
#        
#        print 'done'
#    print hline
#        
#    for job in jobs:
#        if not allJobs and job.jid not in numbers:
#            continue
#        
#        print '| Submitting job',job.name()+'...',
#        sys.stdout.flush()
#        if not opt.dry:
#            if job.status is not jobtools.kCreated and not opt.resubmit:
#                parser.error('The job '+job.name()+' is already submitted. Use -r to resubmit.')
#            qsub = subprocess.Popen(['qsub',job.scriptPath,'-o',job.stdOutPath,'-e',job.stdErrPath],
#                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#            qsub.communicate()
#            if qsub.returncode is not 0:
#                print 'Warning: qsub returned',qsub.returncode
#            
#            job.status = jobtools.kSubmitted
#            job.exitCode = None
#            updated.append(job)
#        print 'Done'
#
#    print hline
    m.updateJobCodes(s.name, updated)
    m.setSessionStatus(s.name, jobtools.kSubmitted) 
    m.disconnect()
    
    if opt.dry:
        print 'Dry run: the files for',s.name,'jobs',numbers,' have been created.'

def submitSession( session, jobs, opt, jNums=[] ):
    updated = []
    
    hline = '-'*80
    allJobs = len(jNums) == 0
       
    print hline
    print '| Creating scripts for session',session.name
    print hline

    for job in jobs:
        if not allJobs and job.jid not in jNums:
            continue
        
        print '| ',job.name(),'...',
        # makes destination directories
        job.mkDirs()
        # dump the script into the destination folder
        script = open(job.scriptPath,'w')
        script.write(job.script)
        script.close()
        # make it executable
        os.chmod(job.scriptPath, 0755)
        
        #dump the input files into the input folder 
        inputFile = open(job.inputFile,'w')
        inputFile.write(job.fileList)
        inputFile.close()
        
        print 'done'
    print hline
        
    for job in jobs:
        if not allJobs and job.jid not in jNums:
            continue
        
        print '| Submitting job',job.name()+'...',
        sys.stdout.flush()
        if not opt.dry:
            if job.status is not jobtools.kCreated and not opt.resubmit:
                raise Exception('The job '+job.name()+' is already submitted. Use -r to resubmit.')
            qsub = subprocess.Popen(['qsub',job.scriptPath,'-o',job.stdOutPath,'-e',job.stdErrPath],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            qsub.communicate()
            if qsub.returncode is not 0:
                print 'Warning: qsub returned',qsub.returncode
            
            job.status = jobtools.kSubmitted
            job.exitCode = None
            updated.append(job)
        print 'Done'

    print hline
    return updated

if __name__ == '__main__':
    main()
