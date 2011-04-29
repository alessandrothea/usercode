#!/usr/bin/env python
import checkpython
import optparse
import jobtools
import string
import os,sys
import ROOT
import re

#-----------------------------------------------------------------------
def getEntries( treeName, rootFiles ):

    ROOT.gROOT.SetBatch()
    chain = ROOT.TChain(treeName)
    print '|  Counting the number entries'
    for root in rootFiles:
        if not root:
            continue

#        print '|  Adding \''+root+'\''
        chain.Add(root)
    
#    print '|  Building the TChain...',
#    sys.stdout.flush()
#    chain.GetEntry(0)
#    print 'done'
    # return the number of events and the list of files
    print '|  ',chain.GetEntries(),'entries found'
    return chain.GetEntries()


#-----------------------------------------------------------------------
def main():
    usage = 'usage: %prog [options] <template file>'
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=jobtools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-l', '--label', dest='sessionLabel', help='Label for the session')
    parser.add_option('-g', '--groups', dest='sessionGroups', help='Column separated list of groups')
    
    parser.add_option('-m', '--mode', dest='sessionMode', help='Session mode [file,events]', default='file')
    parser.add_option('-i', '--inputFile', dest='inputFile', help='List of root files to process')
    parser.add_option('-q', '--queue', dest='queue', help='Name of the queue', default='all.q')
    parser.add_option('-w', '--workingDir', dest='workingDir', help='Working directory', default='.')
    parser.add_option('-o', '--outputDir', dest='outputDir', help='Output directory', default='.')
    parser.add_option('-t', '--treeName', dest='treeName', help='ROOT Tree name')
    parser.add_option('-j', '--nJobs', type='int', dest='nJobs', help='Number of jobs')

    (opt, args) = parser.parse_args()
    

#     print args
    if len(args) != 1:
        parser.error('Wrong number of arguments')
    
    if opt.sessionName is None:
        parser.error('The session name is undefined')

    if opt.sessionMode == 'events':
        if not opt.treeName:
            parser.error('The "events" mode requires treeName to be defined')
        if not opt.nJobs:
            parser.error('The "events" mode requires nJobs to be defined')


    # clean and trim the parameters
    if not opt.outputDir.endswith('/'):
        opt.outputDir = opt.outputDir+'/'
    if not opt.workingDir.endswith('/'):
        opt.workingDir = opt.workingDir+'/'
        
    opt.outputDir += opt.sessionName+'/'

    cmdLine    = os.path.basename(sys.argv[0])+' '+string.join(sys.argv[1:],' ')
    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    outputDir  = os.path.abspath(os.path.expanduser(opt.outputDir))
    workingDir = os.path.abspath(os.path.expanduser(opt.workingDir))
    inputFile  = os.path.abspath(os.path.expanduser(opt.inputFile))

    hline = '-'*80
    print hline
    print '| Creating session ['+opt.sessionName+']'
    print hline

    # expand the inputlist
    rootFiles = open(inputFile).read().split()
    rootFiles = [item.rstrip('\n') for item in rootFiles]
    #try to sort the files according to their CRAB job number
    try:
        rootFiles = sorted(rootFiles, key=lambda name: int(re.search('_([0-9]*)_([0-9]*)_[a-zA-Z0-9]{3}',name).group(1)) )
    except:
        #if it doesn't work, do a simple alphabetical sort
        print 'CRAB sorting failed'
        rootFiles.sort()
    
    inputFiles = string.join(rootFiles,'\n') 
#    print 'rootFiles =',rootFiles

    nFiles = len(rootFiles)
    # prepare the parameters according to the mode
    fileList = None
    nJobs = None
    eventsPerJob = None
    nTotEvents = 0


    if opt.sessionMode == 'file':
        nJobs = int(opt.nJobs)            
        if nJobs > nFiles:
            print '| Less jobs than files: nJobs set to',nFiles
            filesPerJob = 1
            nJobs = nFiles        
        filesPerJob = int(float(nFiles)/nJobs+0.5)
        fileList =  [rootFiles[i:i+filesPerJob] for i in range(0, len(rootFiles), filesPerJob)]
        nJobs = len(fileList)
        eventsPerJob = -1
        firstEvent = [0]*nJobs
#        for subList in fileList:
#            print getEntries(opt.treeName, subList) 
    elif opt.sessionMode == 'events':
        nJobs = int(opt.nJobs)
        filesPerJob = 0 # all
        fileList = [rootFiles]*nJobs
        nTotEvents = getEntries(opt.treeName, rootFiles) 
        eventsPerJob = int(nTotEvents/nJobs)
        firstEvent = range(0,nTotEvents,eventsPerJob)
        firstEvent[-1]=nTotEvents-eventsPerJob*(nJobs-1)
    else:
        parser.error('Mode '+opt.sessionMode+' not supported')

    theTemplate = open(args[0]).read()

    # fill the new session
    label = opt.sessionLabel is None and opt.sessionName or opt.sessionLabel
        
    s = jobtools.Session(opt.sessionName, label, opt.sessionGroups, cmdLine, opt.sessionMode, inputFiles,
        nJobs, nTotEvents, eventsPerJob, opt.queue, workingDir, outputDir)
    s.template = theTemplate

    # open the db
    m = jobtools.Manager(dbPath)

    # read template
    tmpl = string.Template(theTemplate)
    print '|  Connect to',m.dbPath,
    sys.stdout.flush()
    m.connect()
    print 'done.'
    print '|  label:',s.label
    print '|  groups:',s.groups
    print '|  nJobs:',s.nJobs
    print '|  mode:',s.mode
    print '|  nTotEvents:',s.nTotEvents
#    print '|  allFiles:',s.allFiles
    print '|  queue: ',s.queue
    print hline
       
    try:
        m.insertNewSession(s)
    except ValueError as e:
        print '\nError: ',e,'\n'
        return -1

    print '|  Creating',nJobs,'job(s)'
    for i in range(nJobs):
        job = m.makeNextJob(s.name)
        job.fileList  = string.join(fileList[i],'\n')
        job.firstEvent = firstEvent[i]
        # set nEvents to 0 (= all) for the last event
        job.nEvents    = i is not nJobs-1 and eventsPerJob or s.nTotEvents-job.firstEvent
        job.inputFile  = s.outputDir+'/input/'+job.name()+'.input'
        job.outputFile = s.outputDir+'/res/'+job.name()+'.root'
        job.scriptPath = s.outputDir+'/scripts/'+job.name()+'.sh'
        job.stdOutPath = s.outputDir+'/log/'+job.name()+'.out'
        job.stdErrPath = s.outputDir+'/log/'+job.name()+'.err'
        job.exitPath   = s.outputDir+'/tmp/'+job.name()+'.status'


        jDict = s.__dict__
        jDict.update(job.__dict__)
        jDict['jobName'] = job.name()
        job.script = tmpl.safe_substitute(jDict)
        job.script += '\n'+'echo $? > '+job.exitPath
        m.insertNewJob(job)
        eventStr = s.mode is 'file' and 'all events' or str(job.nEvents)+'events (firstEvent ='+str(job.firstEvent)+')'
        print '|  Job \''+job.name()+'\' added to session',s.name,'with',len(fileList[i]),'files and',eventStr
    
    m.setSessionStatus(s.name, jobtools.kCreated)
    print hline
    m.disconnect()

if __name__ == "__main__":
    sys.exit(main())

