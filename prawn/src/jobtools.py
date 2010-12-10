import sqlite3
import os
 
kCreated   = 0
kSubmitted = 1
kRunning   = 2
kCompleted = 3
kFailed    = 4
kUnknown   = 5
 
JobLabel = ['Created','Submitted','Running','Completed','Failed','Unknown']
 
def jmDBPath():
    return os.path.expanduser('~/.prawn/database')
    

def argsToNumbers( args ):
    numbers = []
    for arg in args:
        items = arg.split(',')
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


class Session:
    def __init__(self, name=None, mode=None, fileList=None, nJobs=None, 
        nTotEvents=None, eventsPerJob=None, queue=None, workingDir=None, 
        outputDir=None, softLimit=None, hardLimit=None, template=None):
        self.name       = name

        self.mode         = mode
        self.fileList     = fileList
        self.nJobs        = nJobs
        self.nTotEvents   = nTotEvents
        self.eventsPerJob = eventsPerJob
        
        self.queue        = queue
        self.workingDir   = workingDir
        self.outputDir    = outputDir
        self.softLimit    = softLimit
        self.hardLimit    = hardLimit
        self.template     = template

    def update(self, row):
        for key in self.__dict__.keys():
            if key not in row.keys():
                continue
            self.__dict__[key] = row[key]

    def __str__(self):
        return str(self.__dict__)


class Job:
    
    def __init__(self, sessionName, jid, script=None, firstEvent=0, nEvents=0, 
                 inputputFile=None, outputFile=None,
                 scriptPath=None, stdOutPath=None, exitPath=None,
                 stdErrPath=None):
        self.sessionName = sessionName
        self.jid         = jid
        self.script      = script
        self.firstEvent  = firstEvent
        self.nEvents     = nEvents
        self.inputFile   = outputFile
        self.outputFile  = outputFile
        self.scriptPath  = scriptPath
        self.stdOutPath  = stdOutPath
        self.stdErrPath  = stdErrPath
        self.exitPath    = exitPath
        self.status      = 0
        self.exitCode  = None

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
               os.path.dirname(self.outputFile),
               os.path.dirname(self.stdOutPath),
               os.path.dirname(self.stdErrPath),
               os.path.dirname(self.exitPath)]
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

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
            mode TEXT NOT NULL,
            fileList TEXT, 
            nJobs INTEGER DEFAULT 1 NOT NULL,
            nTotEvents INTEGER DEFAULT 0,
            eventsPerJob INTEGER DEFAULT 0,
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
                  name, mode, fileList, nJobs, nTotEvents, eventsPerJob, queue, workingDir, outputDir, softLimit, hardLimit, template) \
                  VALUES (\
                  :name,:mode,:fileList,:nJobs,:nTotEvents,:eventsPerJob,:queue,:workingDir,:outputDir,:softLimit,:hardLimit,:template)', s.__dict__)
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
    
    def removeSession(self,name):
        c = self.connection.cursor()
        t = (name,)
        if len(c.execute('SELECT jid FROM job WHERE sessionName = ?',t).fetchall()):
            c.execute('DELETE FROM job WHERE sessionName=?',t)
            print ' Jobs belonging to session ['+name+'] removed'
        else:
            print ' No job belonging to session ['+name+']  was found'

        if len(c.execute('SELECT name FROM session WHERE name = ?',t).fetchall()):
            c.execute('DELETE FROM session WHERE name=?',t)
            print ' Session ['+name+'] removed'
        else:
            print ' Session ['+name+']  does not exists'

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
        
        c.execute('INSERT INTO job(sessionName, jid, status, script, firstEvent, nEvents, inputFile, outputFile, scriptPath, stdOutPath, stdErrPath, exitPath)\
                  VALUES (:sessionName, :jid, :status, :script, :firstEvent, :nEvents, :inputFile, :outputFile, :scriptPath, :stdOutPath, :stdErrPath, :exitPath)',job.__dict__)
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
        


