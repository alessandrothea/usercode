import HWWAnalysis.Misc.odict as odict
from .tree import TreeWorker, ChainWorker, TreeView, ChainView, Sample
from .base import Labelled
import os.path
import ROOT
import logging
import copy
import itertools
import pdb


#______________________________________________________________________________
# bridge class for the current sad
class Latino:

    # ---
    def __init__(self, **kwargs):

        self.weight       = ''
        self.preselection = ''
        self.files        = []

        for k,v in kwargs.iteritems():
            if not hasattr(self,k): continue
            setattr(self,k,v)

    # ---
    def __repr__(self):
        return 'Latino(\'%s\', \'%s\', %s)' % (self.weight, self.preselection, str(self.files) )

    # ---
    def __add__(self,other):
        if self.weight != other.weight or self.preselection != other.preselection:
            raise ValueError('self and other are mismatching weight/preselection')

        return Latino(weight = self.weight, preselection = self.preselection, files = self.files+other.files)

    # ---
    def makeSample( self, masterpath ):

        files = [ os.path.join(masterpath,f) for f in self.files ]

#         friends = []
#         for key,path in kwargs.iteritems():
#             friends.append( (key, [os.path.join(path,f) for f in self.files ]) )


        s = Sample('latino', files)
        s.weight       = self.weight
        s.preselection = self.preselection

        return s


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
    def keyat(self,index):
        return self._sequence[index]

    #---
    def itemat(self,index):
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
class AnalysisView(object):
    '''
    Proxy class to add functionalities to the bare View
    Used to include postprocessors
    Not yet used so far
    '''
    # ---
    def __init__(self,view,**kwargs):
        self._view = view
        self._filters = []

        self.__build(**kwargs)

    # ---
    def __build(self,**kwargs):
        for k,v in kwargs.iteritems():
            arg = '_'+k
            if not hasattr(self,arg): raise AttributeError('No '+arg+' attribute')
            setattr(self,arg,v)

    # ---
    def __getattr__( self, name ):
        return getattr( self._view, name )

    # ---
    def plot(self, name, varexp, options='', bins=None, extra=None, postprocess=None):
        p = self._view.plot(name,varexp,extra,options,bins)

        # make a list with all processors
        procs = self._filters if not postprocess else (self._filters+[postprocess])

        # apply post creation filters
        for proc in procs: proc(p)

        return p

    # ---
    def spawn(self,*args, **kwargs):
        child = self._view.spawn(*args,**kwargs)

        v = AnalysisView(child)
        # this way the proxy is synced with the parent
        v._filters = self._filters
        return v



import types
#______________________________________________________________________________
#   ______               ___                __
#  /_  __/_______  ___  /   |  ____  ____ _/ /_  __________  _____
#   / / / ___/ _ \/ _ \/ /| | / __ \/ __ `/ / / / / ___/ _ \/ ___/
#  / / / /  /  __/  __/ ___ |/ / / / /_/ / / /_/ (__  )  __/ /
# /_/ /_/   \___/\___/_/  |_/_/ /_/\__,_/_/\__, /____/\___/_/
#                                         /____/
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
    _log = logging.getLogger('TreeAnalyser')

    #---
    def __init__(self, samples=None, cuts=None ):
        self._cuts      = cuts
        self._views     = None
        self._modified  = True
        self._worker    = None
        self._cview     = None
        self._aview     = None
        self._filters = []

        self.__build(samples)

    def __build(self, samples):
        # build the
        self._worker = ChainWorker.fromsamples(*samples) if samples else None
        self._cview  = ChainView(self._worker)

        self._aview  = AnalysisView(self._cview, filters=self._filters)

    #---
    def __del__(self):
        self._deleteentries()

    #---
    def __repr__(self):
        return '%s( %s )' % (self.__class__.__name__,self._cuts)

    #---
    def __copy__(self):
        self._log.debug('-GremlinS-')

        other            = TreeAnalyser()
        other._cuts      = copy.deepcopy(self._cuts)
        other._views     = copy.deepcopy(self._views)
        other._worker    = self._worker
        other._modified  = self._modified
        other._cview     = self._cview
        other._aview     = self._aview

        other._filters = copy.deepcopy(self._filters)

        return other

    def __deepcopy__(self,memo):
        return self.__copy__()

    def clone(self):
        return self.__copy__()

    #---
    @property
    def filters(self):
        return self._filters

    #---
    @property
    def lumi(self):
        return self._lumi

    #---
    @lumi.setter
    def lumi(self,lumi):
        self._lumi = lumi
        self._worker.scale = self._lumi

    #---
    @property
    def cuts(self):
        return self._cuts

    @property
    def worker(self):
        return self._worker

    #---
    @property
    def views(self):
        self._ensureviews()
        return self._views

    #---
    def cutstring(self,name, extra=None):
        i = self._cuts.index(name)

        cuts = self._cuts[0:i+1].rawlist()

        if extra: cuts.append(extra)

        return self._worker._cutexpr(cuts)

    #---
    def _deleteentries(self):
        # does it delete the list?
        self._views = None

    # ---
    def _ensureviews(self, force=False):
        if force: self._deleteentries()

        if not self._views:
            self._views = odict.OrderedDict()
            self._modified = True

        if self._modified:
            self._log.debug('modified cuts!')
            self._purgeviews(self._cuts, self._views)
            self._growviews(self._cuts, self._views)
            self._modified = False
        return self._views

    # ---
    def _growviews(self, cutflow, views ):
        # does it need to depend on cutflow and views?
        self._log.debug('growing viewlist')
        # explect cutflow to be longer than

        nv = len(views)
        nc = len(cutflow)
        if nv == nc : return views
        elif nv > nc : raise ValueError('WTF!')

        # last is the last valid view, used to grow the list
        #last = views.values()[-1] if nv > 0 else ChainView(self._worker)
        last = views.values()[-1] if nv > 0 else self._cview

        newcuts = cutflow[nv:]
        self._log.debug('appending %s', newcuts)
        for i,(n,c) in enumerate(newcuts.iteritems()):
            m = last.spawn(c,'elist%d' % (i+nv) )
            last = m
            views[n] = m

        return views

    # ---
    def _purgeviews(self, cutflow, views ):
        # does it need to depend on cutflow and views?

        self._log.debug('purging viewlist')
        # check the keys
        nv = len(views)


        if len(cutflow) == 0:
            # the new list is empty! what do we do?
            numok = 0
        else:
            k = 0
            matches = False
            # find the first mismatching cut
            for k, ( n,m ) in enumerate(itertools.izip(cutflow.iterkeys(),views.iterkeys())):
                matches =  ( n == m ) and ( str(cutflow[n]) == str(views[m].cut) )
                if not matches: break
            if k==0 and not matches:
                # disagreement at the first match
                numok = 0
            elif not matches:
                numok = k
            else:
                numok = k+1

        # purge the rest of elists
        if numok < nv:
            for n in views.keys()[numok:nv]:
                self._log.debug('Deleting %s',n)
                del views[n]

        if self._log.isEnabledFor(logging.DEBUG):
            self._log.debug('views left')
            for i,(n,l) in enumerate(views.iteritems()):
                self._log.debug('- %d %s,%d', i,n,l.entries())

        return views


    #---
    def bufferentries(self, force=False):
        '''buffer the entries'''
        self._ensureviews( force )

    #---
    def append(self,name,cut):
        '''append a new cut, and if the entrylist has been already made, update it'''
        self._cuts[name] = cut
        self._modified = True

    #---
    def extend(self,cuts):
        if isinstance(cuts, odict.OrderedDict):
            citer = cuts.iteritems()
        elif isinstance(cuts,list) and all(isinstance(o,tuple) for o in cuts):
            citer = iter(cuts)

        for n,c in citer:
            self.append(n,c)
    #---
    def remove(self,name):
        '''remove a cut, and if the entrylist has been already made, update it'''
        del self._cuts[name]
        self._modified = True

    #---
    def update(self, cutflow):
        self._cuts.update(cutflow)
        self._modified = True

    #---
    def entries(self,cut=None):
        return self._worker.entries(cut)

    #---
    def selectedentries(self,cut=None):
        views = self._ensureviews()

        # check that the cutlist is not empty
        if not views:
            return self._worker.entries(cut)
        else:
            return views[views.keys()[-1]].entries(cut)

    #---
    def entriesflow(self,cut=None):
        '''TODO: use the entrylist'''

        self._ensureviews()
        return odict.OrderedDict([ (n, v.entries(cut)) for n,v in self._views.iteritems()])

    #---
    def yields(self, extra=None):
        # make the entries
        views = self._ensureviews()

        # using elist[:] doesn't clone the TEntryList, but inserts the reference only.
        if not views:
            return self._worker.yields(extra)
        else:
            return views[views.keys()[-1]].yields(extra)

    #---
    def yieldsflow(self, extra=None):
        # make the entries
        views = self._ensureviews()

        if not views: return odict.OrderedDict()

        return odict.OrderedDict([( n,v.yields(extra) ) for n,v in views.iteritems()])

    #---
    def plot(self, name, varexp, options='', bins=None, extra=None, postprocess=None):
        # make the entries
        views = self._ensureviews()

        if not views:
            # here I might want to use a view anyway
            #v = ChainView(self._worker)
            v = self._cview
        else:
            v = views[views.keys()[-1]]

        p = v.plot(name,varexp,extra,options,bins)

        # make a list with all processors
        procs = self._filters if not postprocess else (self._filters+[postprocess])

        # apply post creation filters
        for proc in procs: proc(p)

        return p

    #---
    def plotsflow(self, name, varexp, options='', bins=None, extra=None, postprocess=None):
        '''
        Create a flow of plots
        Always call View.plot
        '''
        # make the entries
        views = self._ensureviews()

        # add the weight and get the yields
        if not views: return odict.OrderedDict()

        plots =  odict.OrderedDict([( n,v.plot('%s_%s' % (name,n),varexp,extra,options,bins) ) for n,v in views.iteritems()])

        # make a list with all processors
        procs = self._filters if not postprocess else (self._filters+[postprocess])

        # apply post creation filters
        for p in plots.itervalues():
            for proc in procs: proc(p)

        return plots


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





