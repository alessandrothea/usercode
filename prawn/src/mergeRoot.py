#!/usr/bin/env python
'''
Created on Dec 13, 2010

@author: ale
'''

import checkpython
import jobtools
import optparse
import os, subprocess, sys

def main():
    usage = 'Usage: %prog [options] session jobs'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')

    (opt, args) = parser.parse_args()

    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    
    if opt.sessionName is None:
        parser.error('The session name is undefined')
        
    m = jobtools.Manager(dbPath)
        
    m.connect()
    try:
        session = m.getSession(opt.sessionName)
        jobs = m.getJobs(session.name)
    except ValueError as e:
        print '\n  Error : '+str(e)+'\n'
        return 

    hline ='-'*80

    print hline
    print '|  Merging root files for session',session.name
    print hline

    rootFiles = [job.outputFile for job in jobs]
    for job in jobs:
        if job.status is not jobtools.kCompleted:
            print '|  Not all jobs are completed'
            print hline
            sys.exit()
    
#    print rootFiles
    mergedFile = session.name+'.root'
    cmd = ['hadd',mergedFile]
    cmd.extend(rootFiles)
    hadd = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (stdout, stderr) = hadd.communicate()
    print '|  hadd return code:',hadd.returncode
    print hline
    if hadd.returncode is not 0:
        print '|  hadd stdout'
        print hline
        print stdout
        print hline
        print '|  hadd stderr'
        print hline
        print stderr
        print hline
    print '|  Done'
    print hline
    
if __name__ == "__main__":
    main()