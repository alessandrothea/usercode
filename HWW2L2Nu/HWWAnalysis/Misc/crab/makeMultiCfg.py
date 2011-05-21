#!/usr/bin/env python

import os.path
import optparse 
import psitools 
import odict
import HWWAnalysis.Misc.Datasets as hww
import ConfigParser

def substitute( filein, fileout, dictionary ):
    print dictionary
    input = open(filein)
    output = open(fileout,'w')
    for s in input:
        dummy = s
        for key,value in dictionary.iteritems():
            dummy = dummy.replace(key,str(value))

        output.write(dummy)

    input.close()
    output.close()

if __name__ == '__main__':
    usage = 'usage: %prog '
    parser = optparse.OptionParser(usage)
    parser.add_option('-i', '--ids',     dest='ids',  help='Dataset ids to be include', default='')
    parser.add_option('-c', '--cfg',     dest='crabcfg',  help='crab config file') 
    parser.add_option('-p', '--py',      dest='pset',  help='python pset file') 
    parser.add_option('--publish', dest='publish',  action='store_true', help='publish') 

    (opt,args) = parser.parse_args()

    cfgfile = args[0] if len(args)!=0 else 'multicrab.cfg'

    if not os.path.exists(opt.crabcfg):
        raise NameError('File '+opt.crabcfg+' does not exists')

    version = 'R414_S1_V06_S2_V02_S3_V00'
    crabparser = ConfigParser.ConfigParser()
    crabparser.read(opt.crabcfg)

    crabdir = os.path.dirname(opt.crabcfg)
    if crabdir == '':
        crabdir = '.'
    pypath = crabparser.get('CMSSW','pset')

    if pypath[0]!='/':
        print 'relative'
        pypath = crabdir+'/'+pypath

    

    print 'crabdir =',crabdir
    print 'pypath  =',pypath

    toReplace = {}
    toReplace['RMMEMC'] = True
    toReplace['RMME41X'] = True
    toReplace['RMMEFAKE'] = None
    toReplace['RMMEGlobalTag'] = 'xxx'
    toReplace['RMMEFN'] = 'yyy'
    
    multiparser = ConfigParser.ConfigParser( dict_type=odict.OrderedDict)

    multiparser.add_section('MULTICRAB')
    multiparser.set('MULTICRAB','cfg',opt.crabcfg)

    multiparser.add_section('COMMON')
    multiparser.set('COMMON','CMSSW.total_number_of_events','-1')
#     multiparser.set('COMMON','CMSSW.pset',pypath)
    multiparser.set('COMMON','USER.ui_working_dir','./jobs')

    tmpPath = 'tmp'
    if not os.path.exists(tmpPath):
        os.mkdir(tmpPath)

    if opt.publish:
        multiparser.set('COMMON','USER.publish_data','1')

    for i in psitools.strToNumbers(opt.ids):
        if not hww.datasets.has_key(i):
            continue
        d = hww.datasets[i]
        print '- Adding',d

        toReplace['RMMEMC'] = not d.isData
        toReplace['RMMEGlobalTag'] = d.gtag
        toReplace['RMMEGlobalTag'] = d.nick+'.root'
        # create a new skim python file
        newpy = tmpPath+'/'+os.path.splitext(os.path.basename(pypath))[0]+'_'+d.nick+'.py'
        substitute(pypath, newpy, toReplace )

        multiparser.add_section(d.nick)
        multiparser.set(d.nick, 'CMSSW.pset',newpy)
        multiparser.set(d.nick, 'CMSSW.datasetpath', d.parent)
        multiparser.set(d.nick, 'CMSSW.number_of_jobs',d.njobs)
#         multiparser.set(d.nick, 'CMSSW.pycfg_params', 'outputFile='+d.nick+'.root')
        if d.isData:
            multiparser.set(d.nick,'CMSSW.total_number_of_lumis','-1')

        if opt.publish:
            tag = version+'_ID'+d.id+'_'+d.nick
            multiparser.set(d.nick,'USER.publish_data_name',tag)

    print cfgfile
    configfile = open(cfgfile, 'wb')
    multiparser.write(configfile)
