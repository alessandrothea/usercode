#!/usr/bin/env python

import FWCore.ParameterSet.Config as cms
from HWWAnalysis.Misc.odict import OrderedDict
import os.path

singleMuDataPaths = cms.vstring(
   "1-163261:HLT_Mu15_v*",
   "163262-165099:HLT_Mu24_v*",
   "165102-173235:HLT_Mu30_v*",
   "173236-175972:HLT_Mu40_v*",
   "175973-999999:HLT_Mu40_eta2p1_v*",
   "163262-170901:HLT_IsoMu17_v*",
   "171050-175910:HLT_IsoMu20_v*",
   "175911-175921:HLT_IsoMu24_v*",
   "175922-999999:HLT_IsoMu24_eta2p1_v*",
)
doubleMuDataPaths = cms.vstring(
   "1-165208:HLT_DoubleMu7_v*",
   "165364-178419:HLT_Mu13_Mu8_v*",
   "178420-999999:HLT_Mu17_Mu8_v*",
   "178420-999999:HLT_Mu17_TkMu8_v*",
)
doubleElDataPaths = cms.vstring(
   "1-170901:HLT_Ele17_CaloIdL_CaloIsoVL_Ele8_CaloIdL_CaloIsoVL_v*",
   "171050-999999:HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_v*",
)
muEGDataPaths     = cms.vstring(
   "1-175972:HLT_Mu17_Ele8_CaloIdL_v*",
   "175973-999999:HLT_Mu17_Ele8_CaloIdT_CaloIsoVL_v*",
   "1-167913:HLT_Mu8_Ele17_CaloIdL_v*",
   "167914-999999:HLT_Mu8_Ele17_CaloIdT_CaloIsoVL_v*",
)
singleElDataPaths = cms.vstring(
   "1-164237:HLT_Ele27_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_v*",
   "165085-166967:HLT_Ele32_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_v*",
   "166968-170901:HLT_Ele52_CaloIdVT_TrkIdT_v*",
   "170902-178419:HLT_Ele65_CaloIdVT_TrkIdT_v*",
   "178420-999999:HLT_Ele80_CaloIdVT_TrkIdT_v*",
)

import sys
import os
import os.path
import re
import optparse
import ROOT
import threading
import time

class LumiDownloader(threading.Thread):
    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.cmd = cmd
    
    def run(self):
        print self.cmd
#         print 'sleeping 5 secs'
#         time.sleep(5.)
        os.system(self.cmd)

class Scanner():
    def __init__(self, label, paths, json, tmp):
        self.label = label
        self.json  = json
        self.tmpDir = tmp
        self.pRegex = re.compile('(\d*)-(\d*):(.*)')
        self.splitJson = False
        self.force = False
        self._build(paths)

        fields = [' *(\d+) ',        # run number
                  ' *(\d+) ',        # ls
                  ' *([^ ]+) ',      # hlt
                  ' *([^ ]+) ',      # l1seed
                  ' *(\d+) ',        # hlt prescale
                  ' *(\d+) ',        # l1 prescale
                  ' *([0-9\.]+) ',    # recorded
                  ' *([0-9\.]+) ',    # effective
                 ]

        self.lRegex = re.compile('\|'+'\|'.join(fields)+'\|')


    def _build(self, paths):
        jsonDir = self.tmpDir+'jsons/'
        lumiDir = self.tmpDir+'lumi/'
        os.system('mkdir -p '+self.tmpDir)
        os.system('mkdir -p '+jsonDir)
        os.system('mkdir -p '+lumiDir)

        (jBase,jExt) = os.path.splitext(self.json)
        self.paths = OrderedDict()
        for p in paths:
            runMin,runMax,hlt = self.pRegex.match(p).group(1,2,3)
            # patch
            json = jsonDir+jBase+'.'+runMin+'-'+runMax+'.'+hlt.replace('*','X')+'.json' if self.splitJson else self.json
            lumi = lumiDir+jBase+'.'+runMin+'-'+runMax+'.'+hlt.replace('*','X')+'.lumi' if self.splitJson else lumiDir+jBase+'.'+hlt.replace('*','X')+'.lumi'
            self.paths[hlt] = dict(
                [('runMin',runMin),
                 ('runMax',runMax),
                 ('json',json),
                 ('lumi',lumi)
                ])
        #     hltPathRange[hlt] = (runMin,runMax,json,lumi)
    
    def dload(self):
        self.start = time.time()
        for p,info in self.paths.iteritems():
            print p, self.paths[p]
            if not os.path.exists(info['lumi']) or self.force:
                cmd =  'lumiCalc2.py -i '+info['json']+' -hltpath "'+p+'" lumibyls >& '+info['lumi'] 
                d = LumiDownloader(cmd)
                d.start() 

        self._monitor()

    def __del__(self):
        pass

    def _monitor(self):
        while threading.activeCount() > 1:
            time.sleep(10.)
#             print threading.activeCount() 
            now = start = time.time()
            print '\rActive threads',threading.activeCount(),' - Elapsed time: ',(now-self.start),
            sys.stdout.flush()

    def analyze(self):
        for p, info in self.paths.iteritems():
            nLumiSections = 0
            lumiRecordedByRun = {}
            lumiPrescaledByRun = {}
    #         print '-'+hltName+'---------------------------------'
            allRuns = {}
            hltRunsPS = {}
            l1seedRunsPS = {}
            runMin = int(info['runMin'])
            runMax = int(info['runMax'])
            firstRun = 999999
            lastRun = 1

            lumiFile = open(info['lumi'])
            for line in lumiFile:
                m = self.lRegex.match(line)
                if m is None:
                #             print 'NoMatch',line
                    continue
                (run,ls,hlt,l1,psHlt,psL1,recL, effL) = m.group(1,2,3,4,5,6,7,8)
                nLumiSections += 1
                recordedLumi = float(recL)

                iRun = int(run)
                firstRun = min(firstRun,iRun)
                lastRun  = max(lastRun, iRun)
    #             if iRun < runMin or iRun > runMax:
    #                 raise RuntimeError('porcazzoccola')
                if iRun not in allRuns:
                    allRuns[iRun] = 1
                    lumiRecordedByRun[iRun] = recordedLumi
                else:
                    allRuns[iRun] += 1
                    lumiRecordedByRun[iRun] += recordedLumi

                # 1 no prescale
                # 0 completely masked
                if psHlt != '1':
                    if iRun not in hltRunsPS:
                        hltRunsPS[iRun] = 1
                    else:
                        hltRunsPS[iRun] += 1 

        #             print  (run,ls,hlt,l1,psHlt,psL1)
                if psL1 != '1':
                    if iRun not in l1seedRunsPS:
                        l1seedRunsPS[iRun] = 1
                    else:
                        l1seedRunsPS[iRun] += 1 
                
                # count the lost luminosity
                if psHlt != '1':# or psL1 != '1':
                    if iRun not in lumiPrescaledByRun:
                        lumiPrescaledByRun[iRun] = recordedLumi 
                    else:
                        lumiPrescaledByRun[iRun] += recordedLumi 

    #         print 'summary'
    #         print '\nRuns:\n','{'+', '.join([ str(r)+': '+str(allRuns[r]) for r in sorted(allRuns)])+'}'
    #         print '\nHLTPrescaled:\n','{'+', '.join([ str(r)+': '+str(hltRunsPS[r]) for r in sorted(hltRunsPS)])+'}'
    #         print '\nL1Prescaled:\n','{'+', '.join([ str(r)+': '+str(l1seedRunsPS[r]) for r in sorted(l1seedRunsPS)])+'}'


            if nLumiSections == 0:
                raise RuntimeError('No lumisections found for HLT path '+p)
            
            info['hltRunsPS'] = hltRunsPS
            info['l1seedRunsPS'] = l1seedRunsPS
            info['firstRun'] = firstRun 
            info['lastRun'] = lastRun
            info['nLumiSections'] = nLumiSections
            info['lumiRecordedByRun'] = lumiRecordedByRun
            info['lumiPrescaledByRun'] = lumiPrescaledByRun

    def details(self,label):
        print '*'*100
        print '* {0:<96} *'.format(label)
        print '*'*100
        for p, info in self.paths.iteritems():
            print 'Hlt Path:',p
            rangeMin = int(info['runMin'])
            rangeMax = int(info['runMax'])
            firstRun = info['firstRun']
            lastRun  = info['lastRun']
            print '   Range of existance: ({0},{1})'.format(firstRun,lastRun)
            print '   HWW active range: ({0},{1})'.format(rangeMin,rangeMax)
            hltPSRuns = info['hltRunsPS']
            l1PSRuns  = info['l1seedRunsPS']
            sortedHltRunsPS     = sorted(hltPSRuns)
            sortedL1seedRunsPS  = sorted(l1PSRuns)

            hltPSInRange = [ x for x in sortedHltRunsPS if (x >= rangeMin and x <= rangeMax)]
            l1PSInRange = [ x for x in sortedL1seedRunsPS if (x >= rangeMin and x <= rangeMax)]

            print '   Prescaled runs -'
            print '   Active range: [{0}][{1}]'.format(len(hltPSInRange),len(l1PSInRange))
            print '   + HLT [{0}]:'.format(len(hltPSInRange)),', '.join(['{0}[{1}]'.format(p,hltPSRuns[p]) for p in hltPSInRange])
            print '   + L1  [{0}]:'.format(len(l1PSInRange)),', '.join(['{0}[{1}]'.format(p,l1PSRuns[p]) for p in l1PSInRange])
            print '   Full range: [{0}][{1}]'.format(len(hltPSRuns),len(l1PSRuns))
            print '   + HLT [{0}]:'.format(len(hltPSRuns)),', '.join(['{0}[{1}]'.format(p,hltPSRuns[p]) for p in hltPSRuns])
            print '   + L1  [{0}]:'.format(len(l1PSRuns)),', '.join(['{0}[{1}]'.format(p,l1PSRuns[p]) for p in l1PSRuns])

            print '-'*100


    def summarize(self,label):
        ljust = 45
        print '\n-- Summary',label,'--------------------'
        print 'HLT path'.ljust(ljust),' runMin-runMax: [hltNrange|l1Nrange] (hlt1st,hlt2nd,hltlast,hltN|l11st,l12nd,l1last,l1N )'
        for p, info in self.paths.iteritems():
            runMin    = int(info['runMin'])
            runMax    = int(info['runMax'])
            hltRunsPS = info['hltRunsPS']
            l1seedPS  = info['l1seedRunsPS']
            sortedHltRunsPS     = sorted(hltRunsPS)
            sortedL1seedRunsPS  = sorted(l1seedPS)
            lumiRecordedByRun   = info['lumiRecordedByRun']
            lumiPrescaledByRun  = info['lumiPrescaledByRun']

        #         onePercent = info['nLumiSections']*0.01
        #         print onePercent

            hltPSDump    = [
                '%d[%d],' % (sortedHltRunsPS[0],hltRunsPS[sortedHltRunsPS[0]])  if sortedHltRunsPS else 'None',
                '%d[%d]...' % (sortedHltRunsPS[1],hltRunsPS[sortedHltRunsPS[1]])  if len(sortedHltRunsPS)>1 else 'None',
                '%d[%d]' % (sortedHltRunsPS[-1],hltRunsPS[sortedHltRunsPS[-1]])  if sortedHltRunsPS else 'None',
                str(len(sortedHltRunsPS)),
            ]
            l1seedPSDump = [
                '%d[%d],' % (sortedL1seedRunsPS[0],l1seedPS[sortedL1seedRunsPS[0]])  if sortedL1seedRunsPS else 'None',
                '%d[%d]...' % (sortedL1seedRunsPS[1],l1seedPS[sortedL1seedRunsPS[1]])  if len(sortedL1seedRunsPS)>1 else 'None',
                '%d[%d]' % (sortedL1seedRunsPS[-1],l1seedPS[sortedL1seedRunsPS[-1]])  if sortedL1seedRunsPS else 'None',
                str(len(sortedL1seedRunsPS)),
            ]

            hltPSInRange = [ x for x in sortedHltRunsPS if (x >= runMin and x <= runMax)]
            l1seedPSInRange = [ x for x in sortedL1seedRunsPS if (x >= runMin and x <= runMax)]
            
            print p.ljust(ljust),(str(runMin)+'-'+str(runMax)).ljust(13),
            print (': ['+str(len(hltPSInRange))+'|'+str(len(l1seedPSInRange))+']').ljust(10),
            print '('+(' '.join(hltPSDump)).ljust(20),'|',' '.join(l1seedPSDump),')'


        #         print 'xx',first,min(hltRunsPS)
        #         print 'xx',last,max(hltRunsPS)
        #         print last-first+1

    def makeplots(self,out):
        for p, info in self.paths.iteritems():
            runMin    = int(info['runMin'])
            runMax    = int(info['runMax'])
            hltRunsPS = info['hltRunsPS']
            l1seedPS  = info['l1seedRunsPS']
            sortedHltRunsPS     = sorted(hltRunsPS)
            sortedL1seedRunsPS  = sorted(l1seedPS)
            lumiRecordedByRun   = info['lumiRecordedByRun']
            lumiPrescaledByRun  = info['lumiPrescaledByRun']

            out.cd()
            first = info['firstRun']
            last = info['lastRun']
            
            name = p.replace('*','X')
            hHlt = ROOT.TH1F(name,p+';Run #R;# of prescaled LS',last-first+1, first, last+1)
            hHlt.SetBit(ROOT.TH1.kNoStats)
            xax = hHlt.GetXaxis()
            for run,nls in hltRunsPS.iteritems():
                hHlt.Fill(run,nls)
                xax.SetBinLabel(xax.FindBin(run),str(run))
            xax.SetBinLabel(1,str(first))
            xax.SetBinLabel(xax.GetNbins(),str(last))
            hHlt.Write()

            totLumi = 0
            preLumi = 0 
            hPrescaledLumiFraction = ROOT.TH1D(name+'_lumiFrac',p+' Prescaled/Recorded;Run #R;prescaled/recorded',last-first+1, first, last+1)
            hPrescaledLumiFraction.SetBit(ROOT.TH1.kNoStats)
            hPrescaledLumiFraction.SetLineColor(ROOT.kRed)
            hPrescaledLumiFraction.SetLineWidth(2)
            xax = hPrescaledLumiFraction.GetXaxis()

            ratio = 0.
            xMin = int(xax.GetXmin())
            xMax = int(xax.GetXmax())
            for iRun in xrange(xMin,xMax):
                run = int(iRun)
                if run not in lumiRecordedByRun:
                    hPrescaledLumiFraction.SetBinContent(xax.FindBin(run), ratio )
                    continue
                totLumi += lumiRecordedByRun[run]
                if run in lumiPrescaledByRun:
                    preLumi += lumiPrescaledByRun[run]
                    xax.SetBinLabel(xax.FindBin(run),str(run))
                ratio = preLumi/totLumi
                hPrescaledLumiFraction.SetBinContent(xax.FindBin(run), ratio )

            xax.SetBinLabel(1,str(first))
            xax.SetBinLabel(xax.GetNbins(),str(last))
            hPrescaledLumiFraction.Write()





if __name__ == '__main__':
    motherJson='certifiedToScan.json'
    cwd = os.getcwd()
    tmpDir  = cwd+'/psdata/'


    allPaths = OrderedDict([
        ('singleMu',singleMuDataPaths),
#         ('singleEl',singleElDataPaths),
#         ('doubleEl',doubleElDataPaths),
#         ('doubleMu',doubleMuDataPaths),
#         ('muEg',muEGDataPaths),
    ])

    out = ROOT.TFile.Open('psPlots.root','recreate')
    for p,list in allPaths.iteritems():
        s = Scanner(p,list,motherJson,tmpDir)
        s.analyze()
        s.details(p)
        s.summarize(p)
        s.makeplots(out)
    out.Close()
    sys.exit(0)

