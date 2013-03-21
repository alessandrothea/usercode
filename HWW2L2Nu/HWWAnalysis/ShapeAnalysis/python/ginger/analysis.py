import HWWAnalysis.Misc.odict as odict
from .tree import TreeWorker, Sample
from .base import Labelled
import os.path
import ROOT
import logging
import copy
import pdb



#______________________________________________________________________________
class CutFlow(odict.OrderedDict):

    #---
    def __init__(self, init_val=(), strict=False):
        odict.OrderedDict.__init__(self,(), strict) 
        self._import(init_val)
    
    #---
    def _import(self,l):
        if isinstance(l,list):
            for item in l:
                if isinstance(item,tuple) and len(item)==2:
                    self[item[0]] = item[1]
                elif isinstance(item,str):
                    self[item] = item
                else:
                    raise ValueError('CutFlow: list entry not supported: '+item.__class__.__name__)
        elif isinstance(l,odict.OrderedDict):
            for key,val in l.iteritems():
                self[key] = val
        elif isinstance(l,tuple):
            pass
        else:
            raise ValueError('CutFlow: init value not supported: '+l.__class__.__name__)


    #---
    def __setitem__(self, key, val):
        if isinstance(val,str):
            val = Cut(val)    
        elif not isinstance(val,Cut):
            raise TypeError('CutFlow need CutSteps')
        
        val.name = key

        odict.OrderedDict.__setitem__(self,key,val)

    #---
    def __getitem__(self, key):
        """
        Allows slicing. Returns an OrderedDict if you slice.
        >>> b = OrderedDict([(7, 0), (6, 1), (5, 2), (4, 3), (3, 4), (2, 5), (1, 6)])
        >>> b[::-1]
        OrderedDict([(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)])
        >>> b[2:5]
        OrderedDict([(5, 2), (4, 3), (3, 4)])
        >>> type(b[2:4])
        <class '__main__.OrderedDict'>
        """

        if isinstance(key,slice) and (isinstance(key.start,str) or key.start == None) and (isinstance(key.stop,str) or key.stop == None):
            istart = self.index(key.start) if key.start else None
            istop  = self.index(key.stop ) if key.stop  else None
            istep  = key.step if key.step else None
            item = odict.OrderedDict.__getitem__(self,slice(istart,istop,istep))
        else:
            item = odict.OrderedDict.__getitem__(self,key)
        if isinstance(item, odict.OrderedDict):
            return CutFlow(item)
        else:
            return item

    #---
    def __repr__(self):
        return '%s([%s])' % (self.__class__.__name__, ', '.join( 
            ['(%r, %r)' % (key, self[key].cut) for key in self.iterkeys()]))
    
    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join( 
            ['%d: %s = %r' % (i,key, self[key].cut) for i,key in enumerate(self.iterkeys())]))


    #---
    def at(self,index):
        return self.__getitem__(self._sequence[index])

    #---
    def collapse(self,name):
        cut = self.string()
        self.clear()
        self.__setitem__(name,cut)

    #---
    def insert(self, index, key, value):

        if isinstance(value,str):
            value = Cut(value)

        odict.OrderedDict.insert(self, index, key, value)

    #---
    def rename(self, old_key, new_key):

        odict.OrderedDict.rename(self,old_key,new_key)

        self.__getitem__(new_key).name = new_key

    #---
    def string(self):
        return ' && '.join( [ '(%s)' % step.cut for step in self.itervalues() ] ) 

    #---
    def list(self):
        return [ (step.name,step.cut) for step in self.itervalues() ]

    #---
    def rawlist(self):
        return [ step.cut for step in self.itervalues() ]


#______________________________________________________________________________
class Cut(Labelled):
    def __init__(self, cut, **kwargs):
        super(Cut,self).__init__('')
        self.cut = cut

        for k,v in kwargs.iteritems():
            if not hasattr(self,k): continue
            setattr(self,k,v)    

    def __str__(self):
        return self.cut

    def __repr__(self):
        if self.name:
            repr = '%s(\'%s\':\'%s\')' % (self.__class__.__name__,self.name,self.cut)
        else:
            repr = '%s(\'%s\')' % (self.__class__.__name__,self.cut)

        return repr
    
  

#______________________________________________________________________________
class Latino:

    def __init__(self, **kwargs):

        self.weight       = ''
        self.preselection = ''
        self.files        = []

        for k,v in kwargs.iteritems():
            if not hasattr(self,k): continue
            setattr(self,k,v)   

    def __repr__(self):
        return 'Latino(\'%s\', \'%s\', %s)' % (self.weight, self.preselection, str(self.files) )

    def __add__(self,other):
        if self.weight != other.weight or self.preselection != other.preselection:
            raise ValueError('self and other are mismatching weight/preselection')

        return Latino(weight = self.weight, preselection = self.preselection, files = self.files+other.files)

    def makeSample( self, masterpath ):

        files = [ os.path.join(masterpath,f) for f in self.files ]

#         friends = []
#         for key,path in kwargs.iteritems():
#             friends.append( (key, [os.path.join(path,f) for f in self.files ]) )


        s = Sample('latino', files)
        s.weight       = self.weight
        s.preselection = self.preselection

        return s


import types
#______________________________________________________________________________
class TreeAnalyser(object):
    '''
    TODO: Add the capability of adding analysis steps:
        It can happen to have multiple selections chains with a partial selection overlap
        
        the goal would be to be capable of:

        mother = TreeAnalyser(sample, cuts)
        mother.bufferentries()

        child1 = mother.clone()
        child1['stepA'] = 'pt > 100'
        child2 = mother.clone()
        child2['stepB'] = 'pt < 100'
    '''
    _logger = logging.getLogger('TreeAnalyser')

    #---
    class Plotter(object):
        def __init__(self,analyser,name,var,bins=None,extra=None):
            self._analyser = analyser
            self._name     = name
            self._var      = var
            self._bins     = bins
            self._extra    = extra

        def __getitem__(self,val):
            print val 
            if isinstance(val,types.SliceType):
                plots = []
                flow = self._analyser._cuts
                fkeys = flow.keys()
                # get the ids of the elements in the slice
                ids = [flow._sequence.index(i) for i in flow._sequence[val]]

                for i in ids:
                    cut = flow[:i+1].string()
                    print 'cut',cut
                    h = self._analyser._worker.plot( '%s_%s' % (self._name,fkeys[i]),self._var, cut, bins=self._bins)
                    plots.append(h)
                    print h

                return plots
            else:
                print 'Making hists up to val'
                cut = self._analyser._cuts[:val].string()
                return self._analyser._worker.plot(self._name,self._var, cut)

    class BufferedPlotter(Plotter):
        def __init__(self,*args,**kwargs):
            super(TreeAnalyser.BufferedPlotter,self).__init__(*args,**kwargs)

        def __getitem__(self,val):
            elists = self._analyser._ensureentries()
            if isinstance(val,types.SliceType):
                pass
                plots = self._worker._plotsfromentries(name,varexp,elists,options,bins)
            else:
                pass
                plots = self._worker._plotsfromentries(name,varexp,elists,options,bins)



    #---
    def __init__(self, sample=None, cuts=None ):
        self._cuts       = cuts
        self._entrylists = None
        self._modified   = True
        self._worker     =  TreeWorker.fromsample(sample) if sample else None

    #---
    def __del__(self):
        self._deleteentries()


    #---
    def __repr__(self):
        return '%s( %s )' % (self.__class__.__name__,self._cuts)

    
    #---
    def __copy__(self):
        self._logger.debug('-GremlinS-')

        other             = TreeAnalyser()
        other._cuts       = copy.deepcopy(self._cuts)
        other._entrylists = odict.OrderedDict( [ ( n, l.Clone() ) for n,l in self._entrylists.iteritems() ] ) if self._entrylists else None
        other._worker     = self._worker
        other._modified   = self._modified

        return other

    def __deepcopy__(self,memo):
        return self.__copy__()
        
    def clone(self):
        return self.__copy__()

    #---
    def __setattr__(self,key,value):
        if key == 'lumi':
            self._worker.setscale(value)
        else:
            self.__dict__[key] = value

    #---
    @property
    def cuts(self):
        return self._cuts

    @property
    def worker(self):
        return self._worker

    #---
    def cutstring(self,name, extra=None):
        i = self._cuts.index(name)

        cuts = self._cuts[0:i+1].rawlist()

        if extra: cuts.append(extra)

        return self._worker._cutexpr(cuts)


    #---
    def _deleteentries(self):
        if self._entrylists:
            for l in self._entrylists.itervalues():
                self._logger.debug( 'obj before %s',l.__repr__())
                l.IsA().Destructor(l)
                self._logger.debug( 'obj after  %s', l.__repr__())
            self._entrylists = None

    #---
    def _ensureentries(self, force=False):
        if force:
            self._deleteentries()

#         pdb.set_trace()

        if not self._entrylists:
            self._logger.info('--Buffering the entries passing each cut--')
            self._entrylists = self._worker._makeentrylists(self._cuts)
            self._logger.debug('---------------------------------------')
        elif self._modified:
            self._logger.info('--Updating the entries passing each cut--')
            self._worker._updateentrylists(self._cuts,self._entrylists)
            self._logger.debug('---------------------------------------')

        self._modified = False

        return self._entrylists

    #---
    def bufferentries(self, force=False):
        '''buffer the entries'''
        self._ensureentries( force )

    #---
    def append(self,name,cut):
        '''append a new cut, and if the entrylist has been already made, update it'''
        self._cuts[name] = cut
        self._modified = True

#         if self._entrylists:
#             self._worker._updateentrylists(self._cuts,self._entrylists)

    def entries(self):
        return self._worker.entries()
        
    #---
    def selectedentries(self):
        self._ensureentries()
        
        # check that the cutlist is not empty
        if len(self._entrylists) == 0:
            return self._worker.entries() 
        else:
            return self._entrylists[self._entrylists.keys()[-1]].GetN()
#         return self._worker.entries(self._cuts.string())

    #---
    def entriesflow(self):
        '''TODO: use the entrylist'''

        self._ensureentries()
        return odict.OrderedDict([ (n, l.GetN()) for n,l in self._entrylists.iteritems()])

    #---
    def yields(self, extra=None):
        # make the entries
        elists = self._ensureentries()
        
        # using elist[:] doesn't clone the TEntryList, but inserts the reference only.
        yields = self._worker._yieldsfromentries(elists[-1:],extra=extra)
        return yields.values()[0]

    #---
    def yieldsflow(self, extra=None):
        # make the entries
        elists = self._ensureentries()

        # add the weight and get the yields
        yields = self._worker._yieldsfromentries(elists,extra=extra)
        return yields
        
    #---
    def plot(self, name, varexp, options='', bins=None, extra=None):

        base = self._cuts.string()
        cut = ' && '.join(['(%s)' % c for c in (base,extra) if c])

        return self._worker.plot(name,varexp,cut,options,bins)

    #---
    def plotsflow(self, name, varexp, options='', bins=None, extra=None):
        # make the entries
        elists = self._ensureentries()
        
        # add the weight and get the yields
        plots = self._worker._plotsfromentries(name,varexp,elists,options,bins)
        return plots

    #---
    def plotter(self,*args,**kwargs):

        buffered = kwargs.pop('buffered',False)
        
        if buffered:
            cls = self.BufferedPlotter
        else:
            cls = self.Plotter

        print args
        return cls(self,*args,**kwargs)


if __name__ == '__main__':

    basepath = '/shome/thea/HWW/work/shape2012/trees/latino_skim' 

    flow = CutFlow()

    flow['mll'] = Cut('mll > 12','m_{ll} > 12')
    flow['mpmet'] = Cut('mpmet > 45','mp \slash{E}', 'mp #slash{E}')
    flow['njet'] = Cut('njet == 0')
    flow['mpmet'] = 'mpmet > 45'

    print flow
    print flow[:1].items()
    del flow['mll']
    print flow
    print flow.string()
    print flow.list()

    samples = hwwsamples2g.samples(125,'Data2012')

    l = samples['DYLL']

    print 'AAAA: ',l

    s = l.makeSample( basepath,latinobdt='/shome/thea/HWW/work/shape2012/trees/bdt_skim/mva_MH125_1j' )

    print s

    a = TreeAnalyser(s,None)
    
    print a.selectedentries()
    
    print a._worker._friends

    del a
    




