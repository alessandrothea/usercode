#!/usr/bin/env python

import optparse
import sys
import PrawnTools
import string

class RequiredOptions:
    def __init__(self, args, required):
        missing = []
        for r in required:
            if r not in args.keys() or args[r] is None:
                missing.append(r)

        if len(missing) != 0:
            raise ValueError('Required option are missing: '+' '.join(missing))

        self.__dict__ = dict(args.items())

def updateSession( options, args ):
    required = ['database']
    opt = RequiredOptions(options, required);
    
    if not opt.sessionName and not opt.sessionGroups:
        raise NameError('Session or group must be defined')
        
    dummy = PrawnTools.Session()
    toUpdate = {}
    for arg in args:
        key,_,value = arg.partition('=')
        if key == arg:
            raise NameError('Malformed argument '+arg)
        
        if not hasattr(dummy,key):
            raise NameError('Session doesn\'t have attribute '+key)
        
        toUpdate[key] = value
            
    m = PrawnTools.Manager(opt.database)
    m.connect()
    ses = m.getListOfSessions(opt.sessionName,opt.sessionGroups)
    for s in ses:
        for key,val in toUpdate.iteritems():
            setattr(s,key,val)
#            print key, val
        
        m.updateSession(s)
        m.removeAllJobs(s.name)
        print '|  Session',s.name,'updated'
        if not opt.noJobs:
            m.generateJobs(s)
    
    m.disconnect()
    
    

if __name__ == "__main__":
    dummy = PrawnTools.Session()
    usage = 'usage: %prog [options] <key=value>\n\
    Where key can be:\n\
    '+','.join(dummy.__dict__.iterkeys())
    parser = optparse.OptionParser(usage)

    parser.add_option('--dbpath', dest='database', help='Database path', default=PrawnTools.jmDBPath())
    parser.add_option('-s', '--session', dest='sessionName', help='Name of the session')
    parser.add_option('-g', '--groups', dest='sessionGroups', help='Column separated list of groups')
    parser.add_option('-n', '--noJobs', dest='noJobs', action='store_true', help='Don\t regenerate the jobs after updating the session')
       
    (opt, args) = parser.parse_args()
    
    if not opt.sessionName and not opt.sessionGroups:
        parser.error('Session or Grous must be defined')
    
    sys.exit(updateSession( opt.__dict__, args ))