import sqlite3
import os
import console
import string
import ROOT
 
kCreated   = 0
kSubmitted = 1
kRunning   = 2
kCompleted = 3
kFailed    = 4
kUnknown   = 5

StateLabel  = ['Created',  'Submitted','Running','Completed','Failed','Unknown']
StateColors = ['turquoise','yellow',   'blue',   'green',    'red',   'fuchsia']

def colState( state ):
    return console.colorize(StateColors[state], StateLabel[state] )
 
def jmDBPath():
    return os.path.expanduser('~/.prawn/database')
    

def strToNumbers( numString ):
    numbers = []
    if len(numString)==0:
        return numbers;
    
    items = numString.split(',')
    for item in items:
        nums = item.split('-')
        if len(nums) == 1:
            # single number
            numbers.append(int(item))
        elif len(nums) == 2:
            i = int(nums[0])
            j = int(nums[1])
            if i > j:
                raise ValueError('Invalid interval '+item)
            numbers.extend(range(i,j+1))
        else:
            raise ValueError('Argument '+item+'is not valid')

    return set(numbers)

#-----------------------------------------------------------------------
def getEntries( treeName, rootFiles ):

    ROOT.gROOT.SetBatch()
    chain = ROOT.TChain(treeName)
    print '|  Counting the number entries'
    for root in rootFiles:
        if not root:
            continue

        chain.Add(root)

    print '|  ',chain.GetEntries(),'entries found'
    return chain.GetEntries()

class Session:
    def __init__(self, name=None, label=None, groups=None, cmdLine=None, mode=None, allFiles=None, nJobs=None, 
        nTotEvents=None, eventsPerJob=None, optArgs='', queue=None, workingDir=None, 
        outputDir=None, softLimit=None, hardLimit=None, template=None):
        self.name       = name
        self.label      = label
        self.groups     = groups
        self.cmdLine    = cmdLine

        self.mode         = mode
        self.allFiles     = allFiles
        self.nJobs        = nJobs
        self.nTotEvents   = nTotEvents
        self.eventsPerJob = eventsPerJob
        self.optArgs      = optArgs
        
        self.queue        = queue
        self.workingDir   = workingDir
        self.outputDir    = outputDir
        self.softLimit    = softLimit
        self.hardLimit    = hardLimit
        self.template     = template
        self.status = 0

    def update(self, row):
        for key in self.__dict__.keys():
            if key not in row.keys():
                continue
            self.__dict__[key] = row[key]
        return self

    def __str__(self):
        return str(self.__dict__)
    
    def clean(self):
        top = self.outputDir
        if top == '/':
            raise ValueError('trying to delete "/"?!? Are you out of your mind?!?')
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

class Job:
    
    def __init__(self, sessionName, jid, script=None, firstEvent=0, nEvents=0,
                 inputFile=None, outputFile=None,
                 fileList=None, scriptPath=None, stdOutPath=None, exitPath=None,
                 stdErrPath=None):
        self.sessionName = sessionName
        self.jid         = jid
        self.script      = script
        self.firstEvent  = firstEvent
        self.nEvents     = nEvents

        self.fileList    = fileList
        self.inputFile   = inputFile
        self.outputFile  = outputFile
        self.scriptPath  = scriptPath
        self.stdOutPath  = stdOutPath
        self.stdErrPath  = stdErrPath
        self.exitPath    = exitPath
        self.status      = 0
        self.exitCode    = None

    def __str__(self):
        return str(self.__dict__)


    def update(self, row):
        for key in self.__dict__.keys():
            if key not in row.keys():
                continue
            self.__dict__[key] = row[key]

    def name(self):
        return self.sessionName+'_'+str(self.jid)

    def checkQueue(self):
        print 'Checking',self.name()

    def start(self):
        print 'Starting job',self.name()
        
    def mkDirs(self):
        dirs =[os.path.dirname(self.scriptPath),
               os.path.dirname(self.inputFile),
               os.path.dirname(self.outputFile),
               os.path.dirname(self.stdOutPath),
               os.path.dirname(self.stdErrPath),
               os.path.dirname(self.exitPath)]
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)
    
    def cleanFiles(self):
        files=[self.scriptPath,
               self.inputFile,
               self.outputFile,
               self.stdOutPath,
               self.stdErrPath,
               self.exitPath]
        
        for file in files:
            if os.path.exists(file):
                os.remove(file)

class Manager:
    """A Simple Job Manager"""
    def __init__(self, dbPath):
        self.dbPath=dbPath

    def drop(self):
        import os.path
        if os.path.exists(self.dbPath):
            os.remove(self.dbPath)

    def create(self):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        c.execute('''CREATE table session(
            name TEXT PRIMARY KEY ON CONFLICT ABORT,
            label TEXT,
            groups TEXT DEFAULT '',
            cmdLine TEXT, 
            mode TEXT NOT NULL,
            allFiles TEXT, 
            nJobs INTEGER DEFAULT 1 NOT NULL,
            nTotEvents INTEGER DEFAULT 0,
            eventsPerJob INTEGER DEFAULT 0,
            optArgs TEXT DEFAULT '',
            queue TEXT,
            workingDir TEXT,
            outputDir TEXT,
            softLimit REAL,
            hardLimit REAL,
            template TEXT,
            status INTEGER DEFAULT 0 NOT NULL)''')
        c.execute('''CREATE TABLE job(
            sessionName TEXT,
            jid INTEGER NOT NULL,
            status INTEGER DEFAULT '''+str(kCreated)+''' NOT NULL,
            script TEXT,
            fileList TEXT,
            firstEvent INTEGER NOT NULL,
            nEvents INTEGER,
            inputFile TEXT,
            outputFile TEXT,
            scriptPath TEXT,
            stdOutPath TEXT,
            stdErrPath TEXT,
            exitPath TEXT,
            exitCode INTEGER,
            FOREIGN KEY(sessionName) REFERENCES session(name),
            CONSTRAINT ses_jobId UNIQUE (sessionName,jid) ON CONFLICT ABORT)''')
        conn.commit()
        conn.close()

    def connect(self): 
        self.connection = sqlite3.connect(self.dbPath)
        self.connection.row_factory = sqlite3.Row

    def disconnect(self):
#         print self.connection.total_changes
        self.connection.close()

    def dump(self):
        print 'Current database is '+self.dbPath

    def insertNewSession(self, s):
        c = self.connection.cursor()
        c.execute('SELECT name FROM session WHERE name = :name',s.__dict__)
        if len(c.fetchall()) is not 0:
            raise ValueError('Session '+s.name+' already exists!')
        c.execute('INSERT INTO session(\
                  name, label, groups, cmdLine, mode, allFiles, nJobs, nTotEvents, eventsPerJob, optArgs, queue, workingDir, outputDir, softLimit, hardLimit, template) \
                  VALUES (\
                  :name,:label,:groups,:cmdLine,:mode,:allFiles,:nJobs,:nTotEvents,:eventsPerJob,:optArgs,:queue,:workingDir,:outputDir,:softLimit,:hardLimit,:template)',
                  s.__dict__)
        self.connection.commit()
    
    def updateSession(self,s):
        c = self.connection.cursor()
        c.execute('UPDATE OR ROLLBACK session SET\
        label = :label, groups = :groups, cmdLine = :cmdLine, mode = :mode, allFiles = :allFiles, nJobs = :nJobs, \
        nTotEvents = :nTotEvents, eventsPerJob = :eventsPerJob, optArgs = :optArgs, queue = :queue, \
        workingDir = :workingDir, outputDir = :outputDir, softLimit = :softLimit, hardLimit = :hardLimit, template = :template \
        WHERE name = :name',s.__dict__)
        self.connection.commit()

    def getSession(self, name):
        c = self.connection.cursor()
        c.execute('SELECT * FROM session where name = ?',(name,))
        row = c.fetchone()
        if not row:
            raise ValueError('Session ['+name+'] not found')
        s = Session()
        s.update(row)
        return s

    def getListOfSessions(self, session=None, groups=None ):
        
        #if session not defined, take all
        if not session:
            session = '%'
        
        gQuery = ''
        pars = (session,)

        if groups is not None:
            tags = []
            for group in groups.split(':'):
                if group == '':
                    continue
                tags.append(group)

            if len(tags) != 0:
                gQuery = ' '.join(['AND groups LIKE ?']*len(tags))
                dummy = [session]
                dummy.extend([ '%'+t+'%' for t in tags])
                pars = tuple(dummy) 

        
        query = 'SELECT * FROM session WHERE name LIKE ? '+gQuery+' ORDER BY name'
        
        c = self.connection.cursor()
            
        c.execute(query, pars)
        
        sessions=[ Session().update(row) for row in c.fetchall()]
        return sessions    
    
    def removeSession(self,name):
        
        self.removeAllJobs(name)
        c = self.connection.cursor()
        t = (name,)
#        if len(c.execute('SELECT jid FROM job WHERE sessionName = ?',t).fetchall()):
#            c.execute('DELETE FROM job WHERE sessionName=?',t)
#            print ' Jobs belonging to session ['+name+'] removed'
#        else:
#            print ' No job belonging to session ['+name+']  was found'

        if len(c.execute('SELECT name FROM session WHERE name = ?',t).fetchall()):
            c.execute('DELETE FROM session WHERE name=?',t)
            print ' Session ['+name+'] removed'
        else:
            print ' Session ['+name+']  does not exists'

        self.connection.commit()
        
    def removeAllJobs(self,sessionName):
        c= self.connection.cursor()
        t = (sessionName,)
        if len(c.execute('SELECT jid FROM job WHERE sessionName = ?',t).fetchall()):
            c.execute('DELETE FROM job WHERE sessionName=?',t)
            print ' Jobs belonging to session ['+sessionName+'] removed'
#        else:
#            print ' No job belonging to session ['+sessionName+']  was found'
        self.connection.commit()
            
    def setSessionStatus(self,sessionName, status):
        c = self.connection.cursor()
        c.execute('UPDATE session SET status = ? WHERE name = ?',(status, sessionName))
        self.connection.commit()
        
    def makeNextJob(self,sessionName):
        c = self.connection.cursor()
        # find the last jid registered for sid
        c.execute('SELECT max(jid) FROM job WHERE sessionName = ?',(sessionName,) )
        r = c.fetchone();
        jid = r[0]
        # if this is the first job, start from 1
        jid = jid==None and 1 or jid+1
        return Job(sessionName,jid)

    def insertNewJob(self,job):
        c = self.connection.cursor()
        
        c.execute('INSERT INTO job(sessionName, jid, status, script, fileList, firstEvent, nEvents, inputFile, outputFile, scriptPath, stdOutPath, stdErrPath, exitPath)\
                  VALUES (:sessionName,:jid,:status,:script,:fileList,:firstEvent,:nEvents,:inputFile,:outputFile,:scriptPath,:stdOutPath,:stdErrPath,:exitPath)',job.__dict__)
        self.connection.commit()
    
    def getJobs(self, sessionName,ids=None):
        c = self.connection.cursor()
        c.execute('SELECT name FROM session WHERE name = ?', (sessionName,))
        if len(c.fetchall()) != 1:
            raise ValueError('Session '+sessionName+' not found in the db')

        c.execute('SELECT * FROM job WHERE sessionName = ?', (sessionName,))
        jobs = []
        for row in c.fetchall():
            jid = row['jid']
            if ids != None and jid not in ids:
                continue
            job = Job(sessionName,jid)
            job.update(row)
            jobs.append(job)

        return jobs
    
    def getJobStatus(self,sessionName, jid):
        c = self.connection.cursor()
        c.execute('SELECT status FROM job WHERE sessionName = ? and jid = ',(sessionName,jid))
        return c.fetchone()['status']
    
    def setJobStatus(self,sessionName, jid, status):
        c = self.connection.cursor()
        c.execute('UPDATE job SET status = ? WHERE sessionName = ? AND jid = ?',(status, sessionName, jid))
        self.connection.commit()
        
    def setJobExitCode(self, sessionName, jid, exitCode):
        c = self.connection.cursor()
        c.execute('UPDATE job SET exitCode = ? WHERE sessionName = ? AND jid = ?',(exitCode, sessionName, jid))
        self.connection.commit()

    def updateJobCodes(self,sessionName,jobs):
        c = self.connection.cursor()
        tuples = [(job.status,job.exitCode,sessionName,job.jid) for job in jobs]
        c.executemany('UPDATE job SET status = ? , exitCode = ? WHERE sessionName = ? AND jid = ?',tuples)
        self.connection.commit()

    def printSession(self,sessionName):
        c = self.connection.cursor()
        c.execute('SELECT * FROM session WHERE name = ? ', (sessionName,))
        r = c.fetchone();
        print r.keys()
        print r
        for row in c.execute('SELECT * FROM job WHERE job.sessionName=?',(sessionName,)):
            print '----------------------------------------------------'
            print row.keys()
            print row
        
    def showAllSessions(self, opt=None):
        hline = '-'*80
        c = self.connection.cursor()
        c.execute('SELECT * FROM session WHERE status == 0')

        print hline
        print str('| name\t\tnJobs\tstatus').expandtabs(10)
        print hline
        for row in c.fetchall():
            line = '| \''+row['name']+'\'\t\t'+str(row['nJobs'])+'\t'+str(row['status'])
            print line.expandtabs(10)

        print hline

        return
        for row in c.fetchall():
            header = '- Session : '+row['name']+' '+hline
            header = header[0:80]

            print row.keys()
            print header
            print '|   .Status =',row['status']
            print '|   .Mode =',row['mode']
            print '|   .Queue =',row['queue']
            print '|   .NJobs =',row['nJobs']
            print '|   .EventsPerJob =', row['eventsPerJob']==0 and 'all' or row['eventsPerJob']
            print '|   .WorkingDir =',row['workingDir']
            print '|   .OutputDir =',row['outputDir']
            print hline
            print '|   .Template ='
            for line in row['template'].split('\n'):
                print '|     ',line
            print hline
            print '|   .Files ='
            for line in row['fileList'].split('\n'):
                print '|     ',line

            print hline

    def showJobsInSession(self, sessionName):
        hline = '-'*80
        c = self.connection.cursor()

        c.execute('SELECT * FROM job, session WHERE job.sessionName=?',(sessionName,))

        rows = c.fetchall()
        if len(rows) == 0:
            raise NameError('Session '+sessionName+' not found')
        print hline 
        for row in rows:
            print '|',str(row['jid']),sessionName+'_'+str(row['jid']),row['firstEvent'], row['nTotEvents'], row['inputFile'], row['outputFile']
            
        print hline 
        
    def generateJobs(self, session):
        hline = '-'*80
        # get the session
        # test creation?
        # remove old jobs
#        for (key,val) in session.__dict__.iteritems():
#            print key,val
        
        jobs = self.getJobs(session.name)
        if len(jobs) != 0:
            raise NameError('Jobs for session',session.name,'not deleted. Remove them first')
        
        rootFiles = session.allFiles.split()
        nFiles = len(rootFiles)
        # prepare the parameters according to the mode
        fileList = None
        nJobs = None
        eventsPerJob = None
        nTotEvents = 0
    
        if session.mode == 'file':
            nJobs = int(session.nJobs)
#            print 'nJobs',nJobs
            if nJobs > nFiles:
                print '| Less jobs than files: nJobs set to',nFiles
                filesPerJob = 1
                nJobs = nFiles        
            filesPerJob = int(float(nFiles)/nJobs+0.5)
            fileList =  [rootFiles[i:i+filesPerJob] for i in range(0, len(rootFiles), filesPerJob)]
            nJobs = len(fileList)
            eventsPerJob = -1
            firstEvent = [0]*nJobs
        elif session.mode == 'events':
            nJobs = int(session.nJobs)
            filesPerJob = 0 # all
            fileList = [rootFiles]*nJobs
            nTotEvents = getEntries(session.treeName, rootFiles) 
            eventsPerJob = int(nTotEvents/nJobs)
            firstEvent = range(0,nTotEvents,eventsPerJob)
            firstEvent[-1]=nTotEvents-eventsPerJob*(nJobs-1)
        else:
            pass
            
        print hline
        print '|  label:',session.label
        print '|  groups:',session.groups
        print '|  nJobs:',session.nJobs
        print '|  mode:',session.mode
        print '|  nTotEvents:',session.nTotEvents
        print '|  queue: ',session.queue
        print '|  optArgs: ',session.optArgs
        print hline
#        print '|  Removing old jobs'
#        self.removeAllJobs(session.name)
 
        tmpl = string.Template(session.template)
        print '|  Creating',nJobs,'job(s)'
        for i in range(nJobs):
            job = self.makeNextJob(session.name)
            job.fileList  = '\n'.join(fileList[i])
#            print job.fileList
            job.firstEvent = firstEvent[i]
            # set nEvents to 0 (= all) for the last event
            job.nEvents    = i is not nJobs-1 and eventsPerJob or session.nTotEvents-job.firstEvent
            job.inputFile  = session.outputDir+'/input/'+job.name()+'.input'
            job.outputFile = session.outputDir+'/res/'+job.name()+'.root'
            job.scriptPath = session.outputDir+'/scripts/'+job.name()+'.sh'
            job.stdOutPath = session.outputDir+'/log/'+job.name()+'.out'
            job.stdErrPath = session.outputDir+'/log/'+job.name()+'.err'
            job.exitPath   = session.outputDir+'/tmp/'+job.name()+'.status'
    
    
            jDict = session.__dict__
            jDict.update(job.__dict__)
            jDict['jobName'] = job.name()
            job.script = tmpl.safe_substitute(jDict)
            job.script += '\n'+'echo $? > '+job.exitPath
            self.insertNewJob(job)
            eventStr = session.mode is 'file' and 'all events' or str(job.nEvents)+' events (firstEvent = '+str(job.firstEvent)+')'
            print '|  Job \''+job.name()+'\' added to session',session.name,'with',len(fileList[i]),'files and',eventStr
    
        self.setSessionStatus(session.name, kCreated)
        print hline

    

