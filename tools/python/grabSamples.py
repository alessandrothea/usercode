#!/usr/bin/env python

import optparse
import csv
import subprocess
import re
import os
import threading
import time
import sys
import psitools

sema = threading.Semaphore(3)

class Chdir:         
    def __init__( self, newPath ):  
        self.savedPath = os.getcwd()
        os.chdir(newPath)

    def __del__( self ):
        os.chdir( self.savedPath )

class Dataset:
    def __init__(self, id, nick, ver, name):
        self.id = id
        self.nick = nick
        self.ver  = ver
        self.name = name
        self.transfer = False

#     def __str__(self):
#         pass
#         return '[%(id)s] %(nick)s %(ver)s %(name)d' % self.__dict__

class ThreadTransfer( threading.Thread ):
    def __init__(self, ds, site, blacklist):
        threading.Thread.__init__(self)
        self.dataset = ds
        self.site = site
        self.kill = False
        self.code = None
        self.blacklist = blacklist
        self.t1 = 0.
        self.t2 = 0.

    def run(self):
        sema.acquire()
        if self.kill:
            print ' * Transfer',self.dataset.nick,'aborted'
            sema.release()
            return

        self.t1 = time.time()
        self.t2 = self.t1
        print ' - Starting transfer',self.dataset.nick
        wd = os.getcwd()+'/'+self.dataset.id
        try:
            if not os.path.exists(wd):
                os.mkdir(wd)
            cmd = ['dbs_transferRegister.py','--to-site=%s' % self.site,self.dataset.name]
            if self.blacklist is not None:
                cmd.append('--bl-sites=%s' % self.blacklist) 
            print 'CMD =',' '.join(cmd)
            logFile = open(wd+'/grab.log','w')
            dbsTransfer = subprocess.Popen(cmd, cwd=wd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retcode = None
            while( not retcode ): 
                retcode = dbsTransfer.poll()
#                 print 'retcode',retcode
#                 print 'kill',self.kill
                if retcode is not None:
                    self.code = retcode
                    break
                if self.kill:
                    try:
                        dbsTransfer.kill()
                    except OSError:
                        pass
                    break
                else:
                    time.sleep(1.)

                out = psitools.readAllSoFar(dbsTransfer)
                logFile.write(out)
                logFile.flush()
#                 os.fsync(logFile)


        finally:
            self.t2 = time.time()
            print ' + Transfer',self.dataset.nick,'completed' if not self.kill else 'killed'
            sema.release()


class Grabber:
    def __init__(self, csvFile, destination, ids):
        self.versions = set()
        self.datasets = []
        self.existingDatasets = []
        self.ids = ids
        self.csvFile = csvFile
        self.destination = destination
        self.threads = []
        self.blacklist = None
        
    def configure(self):
        reader = csv.reader(open(self.csvFile,'rb'),delimiter=',')
        header = reader.next()
        l = len(header)
#         print 'header len',l,header
        print ','.join(header)

        cols = dict(zip(header,range(len(header))))
        print cols
        for row in reader:
            if len(row) != l:
                continue
            d = Dataset(row[cols['ID']],row[cols['Nickname']],row[cols['Skim Version']],row[cols['Output Dataset']])
            self.datasets.append(d);

            if d.ver == '':
#                 print 'Dataset',d.nick,'doesn\'t have a valid version number'
                raise ValueError('Dataset '+d.nick+' doesn\'t have a valid version number')
                

#             print d
            self.versions.add(d.ver)

#         print self.versions
        for v in self.versions:
            self.existingDatasets.extend( getExistingDatasets(v, self.destination) )

#         print  self.existingDatasets

        for  ds in self.datasets:
            if ds.name in self.existingDatasets:
                continue
            numId = int(re.search('[0-9]+',ds.id).group(0))
            if not numId in self.ids:
                continue

            print 'Queuing',ds.nick, ds.id,'for transfer'
            ds.transfer = True

    def start(self):
        for ds in self.datasets:
            if ds.transfer:
                t = ThreadTransfer(ds,self.destination, self.blacklist)
                self.threads.append(t)
                t.start()

        while threading.activeCount() > 1:
            time.sleep(.1)

    def kill(self):
        for t in self.threads:
            t.kill = True

        while threading.activeCount() > 1:
            time.sleep(.1)

    def summary(self):
        for t in self.threads:
            if t.code==0:
                exitstr = 'OK'
            if t.code==None:
                exitstr = 'Error, job killed?'
            else:
                exitstr = 'Error(%d)' % t.code

            timeStr = time.strftime('%a, %d %b %Y %H:%M:%S',time.gmtime(t.t1))
            print t.dataset.id,t.dataset.nick,t.site,timeStr,'[',t.t2-t.t1,']',exitstr


def getExistingDatasets(version, site):

    cmd=['dbs', 
         'search',
         '--url=http://cmsdbsprod.cern.ch/cms_dbs_ph_analysis_02/servlet/DBSServlet',
         '--query=find dataset where dataset like /*%s* and site like %s' % (version,site)]
    print ' '.join(cmd)
    dbsQuery = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout,stderr) = dbsQuery.communicate()
    outRows = stdout.splitlines()

    # no dataset found
    if len(outRows) == 1:
        return []

    for i in range(4):
        outRows.pop(0)

    print '---'
    print '\n'.join(outRows)
    print '---'

    return outRows
    


if __name__ == '__main__':
    usage = 'usage: %prog [options] <file.csv>'
    parser = optparse.OptionParser(usage)
    parser.add_option('--site', '-s', dest='site', help='Destination. Can be [t3psi,t2cscs]')
    parser.add_option('--ids',  '-i', dest='ids',  help='Dataset ids to be grabbed from the spreadsheet', default='')
    parser.add_option('--bl-sites', '-b', dest='blSites', help='Blacklisted sites')

    (opt,args) = parser.parse_args()

    if len(args) == 0:
        parser.error('Input csv file not defined')

    csvFile = args[0]
    if opt.site == 't3psi':
        site = 'T3_CH_PSI'
    elif opt.site == 't2cscs':
        site = 'T2_CH_CSCS'
    else:
        parser.error('site can be either t3psi or t2cscs')

    ids = psitools.strToNumbers(opt.ids)
    print ' - Ids considered for transfer: ', opt.ids
#     print '   ',','.join([str(id) for id in ids])
#     print ','.join(ids)

    try:
        g = Grabber(csvFile, site, ids)
        g.blacklist = opt.blSites
        g.configure()
        g.start()
    except ValueError as v:
        print v
        g.kill()
    except KeyboardInterrupt:
        print 'Ctrl-C detected. Terminate them all'
        g.kill()
    finally:
        print 'The End'
        print '--- Transfer Summary'
        g.summary()

