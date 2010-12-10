#!/usr/bin/env python
import checkpython
import optparse
import jobtools
import string
import os,sys

#-----------------------------------------------------------------------
def getEntries( treeName, rootFiles ):
    import ROOT 
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
    parser.add_option('-i', '--inputFile', dest='inputFile', help='List of root files to process')
    parser.add_option('-m', '--mode', dest='sessionMode', help='Session mode [file,events]', default='file')
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
        parser.error('Please specify a session')

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

    dbPath     = os.path.abspath(os.path.expanduser(opt.database))
    outputDir  = os.path.abspath(os.path.expanduser(opt.outputDir))
    workingDir = os.path.abspath(os.path.expanduser(opt.workingDir))
    inputFile  = os.path.abspath(os.path.expanduser(opt.inputFile))

    hline = '-'*80
    print hline
    print '| Creating session ['+opt.sessionName+']'
    print hline

    # expand the inputlist
    rootFiles = open(inputFile).readlines()
    rootFiles = [item.rstrip('\n') for item in rootFiles]
    inputFiles = string.join(rootFiles,'\n') 
#    print 'rootFiles =',rootFiles

    # prepare the parameters according to the mode
    fileList = None
    nJobs = None
    eventsPerJob = None
    nTotEvents = 0

    if opt.sessionMode == 'file':
        fileList = rootFiles
        nJobs = len(fileList)
        eventsPerJob = 0
        firstEvent = [0]*nJobs
    elif opt.sessionMode == 'events':
        nJobs = int(opt.nJobs)
        fileList = [inputFile]*nJobs
        nTotEvents = getEntries(opt.treeName, rootFiles) 
        eventsPerJob = int(nTotEvents/nJobs)
        firstEvent = range(0,nTotEvents,eventsPerJob)
        firstEvent[-1]=nTotEvents-eventsPerJob*(nJobs-1)
    else:
        parser.error('Mode '+opt.sessionMode+' not supported')

    theTemplate = open(args[0]).read()

    # fill the new session
    s = jobtools.Session(opt.sessionName, opt.sessionMode, inputFiles,
        nJobs, nTotEvents, eventsPerJob, opt.queue, workingDir, outputDir)
    s.template = theTemplate

    # open the db
    m = jobtools.Manager(dbPath)

    # read template
    tmpl = string.Template(theTemplate)
    print ' Connect to '+m.dbPath
    m.connect()
    print '|  nJobs:',s.nJobs
    print '|  mode:',s.mode
    print '|  nTotEvents:',s.nTotEvents
    print '|  fileList:',s.fileList
    print '|  queue: ',s.queue
    print hline
       
    try:
        m.insertNewSession(s)
    except ValueError as e:
        print '\nError: ',e,'\n'
        return

    print '|  Creating',nJobs,'job(s)'
    for i in range(nJobs):
        job = m.makeNextJob(s.name)
        job.inputFile  = fileList[i]
        job.outputFile = s.outputDir+'/root/'+job.name()+'.root'
        job.firstEvent = firstEvent[i]
        # set nEvents to 0 (= all) for the last event
        job.nEvents    = i is not nJobs-1 and eventsPerJob or s.nTotEvents-job.firstEvent
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
        print '|  Job \''+job.name()+'\' added to session',s.name,'with',job.nEvents,'events (firstEvent =',job.firstEvent,')'
    
    
    print hline

if __name__ == "__main__":
    main()

