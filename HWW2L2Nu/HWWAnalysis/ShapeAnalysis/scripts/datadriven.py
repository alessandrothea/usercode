#!/usr/bin/env python

import hwwinfo
import os.path

ddPath = "/shome/thea/HWW/ShapeAnalysis/data/AnalFull2011_BDT/"

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
    def __init__(self, path):
        self._path = path

        self._read()

    def _read(self):
        print 'Reading data driven estimates from',self._path

        # data driven systematics
        readmap = {}
        readmap['Top']  = {'sf': ['mm','ee'], 'of':['em','me']}
        readmap['WW']   = {'sf': ['mm','ee'], 'of':['em','me']}
        readmap['ggWW'] = {'sf': ['mm','ee'], 'of':['em','me']}
        readmap['DYLL'] = {'sf':['ll']}


        # fill a tree of dicts
        # allCards[process][jets][channel][mass]

        ddcards = AlienDict()
        for p,flavors in readmap.iteritems():
            for njet in [0,1]:
                for fl,channels in flavors.iteritems():
                    cards = [ self._load(p,njet,ch) for ch in channels ]
                    masses = cards[0].keys()
#                     print masses

                    check = [ (masses == card.keys()) for card in cards ]

                    if check.count(False) > 0:
                        raise RuntimeError('XXXX')


                    for mass in masses:
                        # no data driven from WW/ggWW
                        if mass >= 200 and (p == 'WW' or p =='ggWW'): continue
                        value = None
                        for card in cards:
                            value = value+card[mass] if value else card[mass] 

                        ddcards[mass][njet][fl][p] = value

        ddcards.lock()
        self.estimates = ddcards

    def _load(self,process, jets, channel):
        ''' Read the Data driven datacar for a given process, jet bin, channel at all masses'''
        
        filename = self._path+'{0}Card_{1}_{2}j.txt'.format(process,channel,jets)
        if not os.path.exists(filename):
            raise RuntimeError('Card file '+filename+' doesn\'t exits')
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
        return card

    def get(self, mass, njet, flavor):
        return (self.estimates[mass][njet][flavor],(mass,njet,flavor))



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

    reader = DDCardReader(ddPath)

    ddcards = reader.estimates

    print ddcards['130'][0]['sf']['DYLL']
    print ddcards['160'][1]['of']['WW']
    print ddPath
    print '190',0,'of', reader.get('190',0,'of')
    print '190',1,'of', reader.get('190',1,'of')
    print '190',0,'sf', reader.get('190',0,'sf')
    print '190',1,'sf', reader.get('190',1,'sf')
    print '-'*100
    e,d = reader.get('190',0,'sf')
    eWW = e['WW']

    print '190',0,'sf', eWW.Nsig(), eWW.Usig(), eWW.delta/eWW.alpha

