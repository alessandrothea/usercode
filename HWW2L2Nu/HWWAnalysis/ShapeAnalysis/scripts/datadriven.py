#!/usr/bin/env python

import hwwinfo
import logging
import os.path


class AlienDict(dict):
    """Implementation of perl's autovivification feature."""
    def __init__(self,*args, **kwargs):
        # init the dict
        super(self.__class__,self).__init__(self, *args, **kwargs)
        self._lock = False
    
    def lock(self):
        self._lock = True
        for a in self.itervalues():
            if type(a) == type(self):
                a.lock()

    def unlock(self):
        self._lock = False
        for a in self.itervalues():
            if type(a) == type(self):
                a.unlock()

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            if self._lock:
                raise
            else:
                value = self[item] = type(self)()
                return value

class DDCardReader:
    _logger = logging.getLogger("DDCardReader")
    def __init__(self, path):
        self._path = path

        self.iszombie = False
        self._read()

    def _read(self):
        if not self._path:
            print 'No datadriven'
            self.iszombie = True
            return

        print 'Reading data driven estimates from',self._path

        # data driven systematics
#         readmap = {}
#         readmap['Top']  = {'sf': ['mm','ee'], 'of':['em','me']}
#         readmap['WW']   = {'sf': ['mm','ee'], 'of':['em','me']}
#         readmap['ggWW'] = {'sf': ['mm','ee'], 'of':['em','me']}
#         readmap['DYLL'] = {'sf': ['ll']}


        # DYLL: Top -> {of_0j: [('em','0j'),('me','0j')], of_1j: [('em','1j'),('me','1j')], sf_0j: [('ee','0j'),('mm','0j')], sf_1j: [('ee','1j'),('mm','1j')], 2j: [('em','1j'),('me','1j'),('ee','0j'),('mm','0j')]}
        
#         basemapping = {'of_0j': ('0j',['em','me']), 'of_1j': ('1j',['em','me']), 
#                        'sf_0j': ('0j',['mm','ee']), 'sf_1j': ('1j',['mm','ee']), 
#                        '2j':   ('2j',['ll']) }
#         llmapping = {'sf_0j': ('0j',['ll']), 
#                      'sf_1j': ('1j',['ll']), 
#                      '2j':   ('2j',['ll']) }
        basemapping = {'of_0j': ('0j',['of']), 'of_1j': ('1j',['of']), 
                       'sf_0j': ('0j',['sf']), 'sf_1j': ('1j',['sf']), 
                       '2j':   ('2j',['sf']) }
        llmapping = {'sf_0j': ('0j',['sf']), 
                     'sf_1j': ('1j',['sf']), 
                     '2j':   ('2j',['sf']) }

        readmap = {}
        readmap['Top']  = basemapping.copy()
        readmap['WW']   = basemapping.copy()
        readmap['ggWW'] = basemapping.copy()
        readmap['DYLL']   = llmapping.copy()


        ddcards = AlienDict()

        for p,mapping in readmap.iteritems():
            for ch,(cat,fls) in mapping.iteritems():
                self._logger.debug('- '+p+' '+ch+' '+cat+' '+str(fls))

                try:
                    cards = [ self._load(p,cat,fl) for fl in fls ]
                except IOError as ioe:
                    self._logger.info(str(ioe))
                    continue;

                masses = cards[0].keys()
                check = [ (masses == card.keys()) for card in cards ]

                if check.count(False) > 0:
                    raise RuntimeError('Sanity check failed')


                for mass in masses:
                    # no data driven from WW/ggWW
                    if mass >= 200 and (p == 'WW' or p =='ggWW'): continue
                    value = None
                    for card in cards:
                        value = value+card[mass] if value else card[mass] 

                    ddcards[mass][ch][p] = value

        ddcards.lock()
        self.estimates = ddcards

    def _load(self,process, cat, channel):
        ''' Read the Data driven datacar for a given process, jet bin, channel at all masses'''
        
        filename = self._path+'{0}Card_{1}_{2}.txt'.format(process,channel,cat)
        self._logger.debug('opening file: '+filename)
        cardFile = open(filename)
        card = {}
        for line in cardFile:
            # <mass> <events in ctrl region> <scale factor> <unc scale factor>
            tokens = line.split()
            mass = int(tokens[0])
            evInCtrlReg = int(float(tokens[1]))
            scale2Sig = float(tokens[2])
            scale2SigUnc = float(tokens[3])

    #         card[mass] = (evInCtrlReg, scale2Sig, scale2SigUnc)
            card[mass] = DDEntry(evInCtrlReg, scale2Sig, scale2SigUnc)
        cardFile.close()
        return card


    def get(self, mass, channel ):
        try:
            return (self.estimates[mass][channel],(mass,channel))
        except KeyError as ke:
            raise KeyError('{0} {1}'.format(mass,channel))

class DDEntry:
    def __init__(self,Nctr,alpha,delta):
        self.Nctr     = Nctr
        self.alpha = alpha
        self.delta = delta

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '(Nctr = {Nctr}, alpha = {alpha:.3f}, delta = {delta:.3f})'.format(**self.__dict__)

    def __add__(self,other):
        sum = DDEntry(0,0,0)
        if self.Nctr != other.Nctr:
            raise ValueError('Trying to add 2 entries with different Nctr: {0}, {1}'.format(self.Nctr,other.Nctr))
        
        sum.Nctr = self.Nctr
        sum.alpha = self.alpha+other.alpha
        sum.delta = self.delta+other.delta

        return sum

    def Nsig(self):
        return self.Nctr*self.alpha

    def Usig(self):
        return self.Nctr*self.delta
        

if __name__ == '__main__':
    print 'DDCardReader test'
    logging.basicConfig(level=logging.DEBUG)

    ddPath = "/shome/thea/HWW/work/shape2012/cmssw/data/Anal_WW/"
    reader = DDCardReader(ddPath)

    ddcards = reader.estimates

    print ddcards[130]['2j']['DYLL']
    print ddcards[130]['sf_0j']['DYLL']
    print ddcards[160]['of_1j']['WW']
    print ddPath
    print '190','of_0j', reader.get(190,'of_0j')
    print '190','of_1j', reader.get(190,'of_1j')
    print '190','sf_0j', reader.get(190,'sf_0j')
    print '190','sf_1j', reader.get(190,'sf_1j')
    print '-'*100
    e,d = reader.get(190,'sf_0j')
    eWW = e['WW']

    print '190',0,'sf', eWW.Nsig(), eWW.Usig(), eWW.delta/eWW.alpha

