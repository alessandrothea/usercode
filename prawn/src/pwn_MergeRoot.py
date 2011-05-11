#!/usr/bin/env python
'''
Created on Dec 13, 2010

@author: ale
'''

import checkpython
import PrawnTools
import optparse
import os.path
import subprocess

def main():
    usage = 'Usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=PrawnTools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-g', '--groups', dest='sessionGroups', help='Comma separated list of groups')
    parser.add_option('-f', '--force', dest='force', action='store_true', default=False)
    parser.add_option('-w', '--overwrite', dest='overWrite', action='store_true', default=False,help='')
    
    (opt, args) = parser.parse_args()

    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    
    if opt.sessionName is None and opt.sessionGroups is None:
        parser.error('Please define either the session or the group')
        
    m = PrawnTools.Manager(dbPath)
        
    m.connect()

    hline ='-'*80
    
    ses = m.getListOfSessions(opt.sessionName, opt.sessionGroups)
    for s in ses:
        jobs = m.getJobs(s.name)
        path = s.name+'.root'
        print hline
        print '|  Merging root files for session',s.name
        print hline
        mergeJobs(jobs, path, opt.overWrite, opt.force)
        print '|  Done'
        print hline
  
def mergeJobs( jobs, path, overWrite=False, force=False ):
    hline ='-'*80
#    rootFiles = [job.outputFile for job in jobs]
    rootFiles = filter(os.path.exists,[job.outputFile for job in jobs])
#    filter(os.path.exists,rootFiles)
    if not force:
        #check all the files have been completed
        for job in jobs:
            if job.status is not PrawnTools.kCompleted and not force:
                print '|  Not all jobs are completed'
                print hline
                return
    
#    print rootFiles
    cmd = ['hadd']
    if overWrite:
        cmd.append('-f')
    cmd.append(path)
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