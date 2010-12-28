'''
Created on Dec 13, 2010

@author: ale
'''
import subprocess
import xml.etree.ElementTree

def runQstat():
    qstat = subprocess.Popen(['qstat'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout,stderr) = qstat.communicate()
    
    if len(stdout)==0:
        return None
    # split in lines
    outLines = stdout.splitlines()
    
    # remove header
    outLines.pop(0)
    outLines.pop(0)
    
    q = []
    for line in outLines:
        q.append(line.split())
    
    return q
    
def runQstatXML():
    qstat = subprocess.Popen(['qstat','-xml'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout,stderr) = qstat.communicate()
    
    if len(stdout)==0:
        return None
    
    element = xml.etree.ElementTree.XML(stdout)
#    qJobs = []
#    qNames =[]
    jMap = {}
    
    for e in element.findall('.//job_list'):
        qJob = {}
        name = e.find('JB_name').text
#        qNames.append(name)
        qJob['name'] = name
        qJob['owner'] = e.find('JB_owner').text
        qJob['priority'] = e.find('JAT_prio').text
        qJob['state'] = e.find('state').text
        qJob['submissionTime'] = e.find('JB_submission_time').text if e.find('JB_submission_time') is not None else None 
        qJob['startTime'] = e.find('JAT_start_time').text if e.find('JAT_start_time') is not None else None
        qJob['queueName'] = e.find('queue_name').text if e.find('queue_name') is not None else None
#        qJobs.append(qJob)
        
        jMap[name] = qJob
    
#    return (qNames,qJobs)
    return jMap