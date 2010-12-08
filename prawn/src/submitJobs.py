#!/usr/bin/env python
import checkpython
import optparse
import jobtools
import os, subprocess

def main():
    usage = 'Usage: %prog [options] jobs'
    parser = optparse.OptionParser(usage)
    
    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-n', '--sessionName', dest='sessionName', help='Name of the session', default='mySession')
    parser.add_option('-a', '--all', dest='all', help='Selects all jobs', action='store_true')
    (opt, args) = parser.parse_args()

    try:
        numbers = jobtools.argsToNumbers(args)
    except ValueError as e:
        parser.error('Error: '+str(e))

    print opt.sessionName,numbers
    hline = '-'*80

    m = jobtools.Manager(opt.database)
    m.connect()

    try: 
        s = m.getSession( opt.sessionName )
        jobs = m.getJobs( opt.sessionName )
    except ValueError as e:
        print '\n  Error : '+str(e)+'\n'
        return

    #print 'Session',s
    #print s.outputDir
        
    print hline
    print '| Creating scripts for session',s.name
    print hline

    for job in jobs:
        if len(numbers) != 0 and job.jid not in numbers:
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
        
        tmpFiles = [job.stdOutPath,job.stdErrPath,job.exitPath]
        for file in tmpFiles:
            if os.path.exists(file): 
                os.remove(file)
        print 'done'
    print hline
        
    for job in jobs:
        if len(numbers) != 0 and job.jid not in numbers:
            continue
        
        print '| Submitting job',job.name()+'...',
#        print 'qsub',job.scriptPath,'-o',job.stdOutPath,'-e',job.stdErrPath
        qsub = subprocess.Popen(['qsub',job.scriptPath,'-o',job.stdOutPath,'-e',job.stdErrPath],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        subprocess.call(['qsub',job.scriptPath,'-o',job.stdOutPath,'-e',job.stdErrPath])  
        m.setJobStatus(s.name, job.jid, jobtools.kSubmitted)
        m.setJobExitCode(s.name, job.jid, None)
        print 'Done'
        
    print hline    
    m.disconnect()

if __name__ == '__main__':
    main()
