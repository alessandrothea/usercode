'''
Created on Dec 6, 2010

@author: ale
'''
import subprocess, re

def myTest():
    print 'Test'
    subprocess.call(['echo','maremma','maiala','> /dev/null'])
    
    p = subprocess.Popen(['echo','maremma','maiala\naaaa'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    print '-'*80
    print stdout.split('\n')
    print '-'*80
    print stderr
    print '-'*80
    print p.returncode
    print '-'*80
    prog = re.compile('.*maiala')
    for line in stdout.split():
        result = prog.match(line)
        print result.string()
        
    return result
        