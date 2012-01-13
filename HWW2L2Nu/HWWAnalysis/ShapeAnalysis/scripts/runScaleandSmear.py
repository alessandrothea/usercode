#!/usr/bin/env python
  
import os
import optparse


## list with the root files to process
runOver = [
    'ggToH140toWWto2L2Nu',
    'ggToH160toWWto2L2Nu',
#    'DYtoElEl',
    ]

fulltag = [
    'muonScale',
    'electronScale',
    'metResolution',
    'leptonEfficiency',
    'jetEnergyScale',
    'electronResolution',
    ]

directions = [
    'down',
    'up',
    ]

 
def main():
 
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
       
    parser.set_defaults(overwrite=False)
    parser.add_option('-i', '--inputDir',   dest='inputDir',   help='Input directory',)
    parser.add_option('-o', '--outputDir',  dest='outputDir',  help='Output directory',)
  
    (opt, args) = parser.parse_args()
  
    if opt.inputDir is None:
        parser.error('No input directory defined')
    if opt.outputDir is None:
        parser.error('No output directory defined')
  
    inputDir = opt.inputDir
    outputDir = opt.outputDir

    print 'Input directory: '+inputDir
    print 'Output directory: '+outputDir

    os.system('mkdir -p '+outputDir)
    for tag in fulltag:
        for dir in directions:
            ## FIXME: change to resolution
            if 'Resolution' in tag and dir is 'up':
                continue
            if 'Resolution' in tag and dir is 'down':
##                 os.system('mkdir '+outputDir+'/'+tag+'_'+dir)
                os.system('mkdir -p '+outputDir+'/'+tag)
                continue
            else:
                os.system('mkdir -p '+outputDir+'/'+tag+'_'+dir)
    
  
        
    ## get all root files in the input directory
    allFiles = os.listdir(inputDir)
##     allFiles = [
##         'latino_1140_ggToH140toWWto2L2Nu.root',
##         'latino_1160_ggToH160toWWto2L2Nu.root',
##         'latino_1180_ggToH180toWWto2L2Nu.root',
##         ]
    files = []
    for file in allFiles:
        if file.endswith('.root') == False:
            continue
        else:
            files.append(file)
            


            
    jobs = []
    for file in files:
        for tag in fulltag:
            for dir in directions:
                  ## FIXME: change to resolution
                if 'Resolution' in tag and dir is 'up':
##                if 'Efficiency' in tag and dir is 'up':
                    continue
                
#                print './scaleAndSmearTree.py -i '+inputDir+'/'+file+' -o blu/bla/'+file.replace('.root','_eRes.root')+' -t latino -a electronResolution -d down'
                    
                title = file.replace('.root','')
                
                ## write a batch submssion file
                print 'sub_'+title+'.sh'
##                     subfile = open(outputDir+'/'+tag+'_'+dir+'/sub_'+file.replace('.root','_')+tag+'_'+dir+'.sh','w')
                if 'Resolution' in tag:
                    subfile = open(outputDir+'/'+tag+'/sub_'+file.replace('.root','.sh'),'w')
                else:
                    subfile = open(outputDir+'/'+tag+'_'+dir+'/sub_'+file.replace('.root','.sh'),'w')
                subfile.write('#!/bin/bash\n')
                subfile.write('#$ -N '+title+'.root'+'\n')
                subfile.write('#$ -q short.q,all.q\n')
                subfile.write('#$ -cwd\n')
                if 'Resolution' in tag:
                    subfile.write('#$ -o '+outputDir+'/'+tag+'/'+title+'.out'+'\n')
                    subfile.write('#$ -e '+outputDir+'/'+tag+'/'+title+'.err'+'\n')
                else:
                    subfile.write('#$ -o '+outputDir+'/'+tag+'_'+dir+'/'+title+'.out'+'\n')
                    subfile.write('#$ -e '+outputDir+'/'+tag+'_'+dir+'/'+title+'.err'+'\n')
                subfile.write('source $VO_CMS_SW_DIR/cmsset_default.sh\n')
                subfile.write('export SCRAM_ARCH=slc5_amd64_gcc434\n')
                subfile.write('cd /shome/jueugste/cmssw/CMSSW_4_2_4/src/\n')
                subfile.write('eval `scramv1 ru -sh`\n')
                #                subfile.write('source $HOME/bin/rc/dcap.sh\n')
                subfile.write('cd /shome/jueugste/HWWSystematics/\n')
                if 'Resolution' in tag:
                    subfile.write('./scaleAndSmearTree.py -i '+inputDir+'/'+file+' -o '+outputDir+'/'+tag+'/'+file+' -t latino -a '+tag+' -d '+dir+'\n')
                    #subfile.write('mv '+outputDir+'/'+tag+'/'+file+' /scratch/jueugste/syst_scenario1/'+tag+'/'+file+'\n')
                else:
                    subfile.write('./scaleAndSmearTree.py -i '+inputDir+'/'+file+' -o '+outputDir+'/'+tag+'_'+dir+'/'+file+' -t latino -a '+tag+' -d '+dir+'\n')
                    #subfile.write('mv '+outputDir+'/'+tag+'_'+dir+'/'+file+' /scratch/jueugste/syst_scenario1/'+tag+'_'+dir+'/'+file+'\n')
                subfile.close()
                if 'Resolution' in tag:
                    jobs.append(outputDir+'/'+tag+'/sub_'+file.replace('.root','.sh'))
                else:
                    jobs.append(outputDir+'/'+tag+'_'+dir+'/sub_'+file.replace('.root','.sh'))
                 
## submit the jobs
    for job in jobs:
        os.system('qsub '+job)
        print('qsub '+job)

                
if __name__ == '__main__':
    main()
