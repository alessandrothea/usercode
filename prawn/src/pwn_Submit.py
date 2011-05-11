#!/usr/bin/env python
import checkpython
import optparse
import PrawnTools
import os, sys, subprocess
import console

def main():
    usage = 'Usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    
    parser.add_option('--dbpath', dest='database', help='Database path', default=PrawnTools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-g', '--groups', dest='sessionGroups', help='Comma separated list of groups')
    parser.add_option('-a', '--all', dest='all', help='Selects all jobs', action='store_true')
    parser.add_option('-n', '--dryRun', dest='dry', help='Dry run, produces the files but doesn\'t submit', action='store_true')
    parser.add_option('-r', '--resubmit', dest='resubmit', help='Resubmit jobs', action='store_true')
    parser.add_option('-j', '--jobs', dest='jobs',help='Jobs to process',default='')
    parser.add_option('-c', '--clean', dest='clean',help='Remove all the files in the output directory. Use with care')
    (opt, args) = parser.parse_args()

    if opt.sessionName is None and opt.sessionGroups is None:
        parser.error('Please define either the session or the group')
    
    try:
        numbers = PrawnTools.strToNumbers(opt.jobs)
    except ValueError as e:
        parser.error('Error: '+str(e))

    m = PrawnTools.Manager(opt.database)
    m.connect()

    try:
        ses = m.getListOfSessions(opt.sessionName, opt.sessionGroups)
    except:
        pass

        
    # preliminary loop: check the session status
    for s in ses:
        if s.status is not PrawnTools.kCreated and not opt.resubmit:
            parser.error('The session is already submitted. Use -r to resubmit.')

    # main loop
    for s in ses:
        try:
            jobs = m.getJobs(s.name)
        except ValueError as e:
            print '\m   Error: '+str(e)+'\n'
            return
        

        updated = submitSession(s,jobs,opt,numbers)
        
        if not opt.dry:
            m.updateJobCodes(s.name, updated)
            m.setSessionStatus(s.name, PrawnTools.kSubmitted) 

    m.disconnect()
    
    if opt.dry:
        print 'Dry run: Only the files for',s.name,'jobs',numbers,' have been created.'

def submitSession( session, jobs, opt, jNums=[] ):
    updated = []
    
    hline = '-'*80
    allJobs = len(jNums) == 0
       
    print hline
    print '| Session',console.colorize("teal", session.name)
    print '| Creating scripts',

    for job in jobs:
        if not allJobs and job.jid not in jNums:
            continue
        
#        print '| ',job.name(),'...',
        job.cleanFiles()
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
        
        print job.name(),
        sys.stdout.flush()
    print '...done'

    print '| Submitting jobs ',
        
    for job in jobs:
        if not allJobs and job.jid not in jNums:
            continue

        if not opt.dry:
            if job.status is not PrawnTools.kCreated and not opt.resubmit:
                raise Exception('The job '+job.name()+' is already submitted. Use -r to resubmit.')
            qsubCmd = ['qsub',job.scriptPath,'-q',session.queue,'-o',job.stdOutPath,'-e',job.stdErrPath]
#            print ' '.join(qsubCmd)
            qsub = subprocess.Popen(qsubCmd,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            qsub.communicate()
            if qsub.returncode is not 0:
                print 'Warning: qsub returned',qsub.returncode
            
            job.status = PrawnTools.kSubmitted
            job.exitCode = None
            updated.append(job)
        print job.name(),
        sys.stdout.flush()
    print '...done'
    print hline
    return updated

if __name__ == '__main__':
    main()
