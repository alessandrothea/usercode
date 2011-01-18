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
    parser.add_option('-g', '--groups', dest='sessionGroups', help='Comma separated list of groups')

    (opt, args) = parser.parse_args()

    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    
    if opt.sessionName is None and opt.sessionGroups is None:
        parser.error('Please define either the session or the group')
        
    m = jobtools.Manager(dbPath)
        
    m.connect()

    hline ='-'*80
    
    ses = m.getListOfSessions(opt.sessionName, opt.sessionGroups)
    for s in ses:
        jobs = m.getJobs(s.name)
        path = s.name+'.root'
        print hline
        print '|  Merging root files for session',s.name
        print hline
        mergeJobs(jobs, path)
        print '|  Done'
        print hline
  
def mergeJobs( jobs, path ):
    hline ='-'*80
    rootFiles = [job.outputFile for job in jobs]
    for job in jobs:
        if job.status is not jobtools.kCompleted:
            print '|  Not all jobs are completed'
            print hline
            return
    
#    print rootFiles
    cmd = ['hadd',path]
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

    
if __name__ == "__main__":
    main()