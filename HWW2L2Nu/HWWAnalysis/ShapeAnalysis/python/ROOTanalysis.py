import HWWAnalysis.Misc.odict as odict
from ROOTtree import TreeWorker
import os.path
import ROOT
import logging

#______________________________________________________________________________
class Labelled(object):
    ''' Generic base classes for objects which have a latex/tlatex representation'''
    def __init__(self,name,title=None,latex=None,tlatex=None):
        self.name    = name
        self._title  = title
        self._latex  = latex
        self._tlatex = tlatex

    #---
    def __str__(self):
        s = [self.name]
        if self._title: s.append(self._title)
        return self.__class__.__name__+'('+', '.join(s)+')'
    
    #---
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,self.name)

    #---
    def _getbyorder(self,attrs):
        for x in attrs:
            if getattr(self,x): return getattr(self,x)

    def __getattr__(self,key):
        if key=='title': 
            return self._getbyorder(['_title','name'])
        elif key == 'latex':
            return self._getbyorder(['_latex','_title','name'])
        elif key == 'tlatex':
            return self._getbyorder(['_tlatex','_title','name'])
        else:
            raise AttributeError('%s instance has no attribute \'%s\'' % (self.__class__.__name__,key) )

    def __setattr__(self,key,val):
        if key in ['title','latex','tlatex']:
            self.__dict__['_'+key] = val
        else:
            self.__dict__[key] = val

    #---
    def getTLatex(self):
        return ROOT.TLatex(0.,0.,self.tlatex)
#______________________________________________________________________________
class Sample(Labelled):
    '''
    How do we define files?

    [('latino',['pippo/pluto.root','pippo/topolino.root']), ('latino_bdt',['bdt/pluto.root','bdt/topolino.root'])]

    Latino(weight='baseW*effW',selection='',files=['pippo/'])
'''

    #---
    def __init__(self, **kwargs):

        super(Sample,self).__init__('')
        self.master       = (None,None)
        self.friends      = []
        self.preselection = ''
        self.weight       = ''

        for k,v in kwargs.iteritems():
            if not hasattr(self,k): continue
            setattr(self,k,v)    

    #---
    def __repr__(self):
        repr = []
        repr += [self.__class__.__name__+(' '+self.name if self.name else'') + (' also known as '+self._title if self._title else '')]
        repr += ['weight: \'%s\', preselection: \'%s\'' % (self.weight, self.preselection) ]
        repr += ['master: '+self.master[0]+'  files: '+str(self.master[1]) ]
        for i,friend in enumerate(self.friends):
            repr += [('friend: ' if i == 0 else ' '*8)+friend[0]+'  files: '+str(friend[1]) ]

        return '\n'.join(repr)

    def dump(self):
        print self.__repr__()

    #---
    def setmaster(self, name, files ):
        self.master = (name,files)

    #---
    def addfriend(self, name, files):
        self.friends.append( (name, files) )

    #---
    def trees(self):
        return [self.master]+self.friends

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
        item = odict.OrderedDict.__getitem__(self,key)
        if isinstance(item, odict.OrderedDict):
            return CutFlow(item)
        else:
            return item

    #---
    def __repr__(self):
        return '%s([%s])' % (self.__class__.__name__, ', '.join( 
            ['(%r, %r)' % (key, self[key].cut) for key in self._sequence]))
    
    __str__ = __repr__

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
        return '%s(%s)' % (self.__class__.__name__,self.cut)
    
  

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

    def makeSample( self, masterpath, **kwargs ):

        master = ('latino',[ os.path.join(masterpath,f) for f in self.files ])

        friends = []
        for key,path in kwargs.iteritems():
            friends.append( (key, [os.path.join(path,f) for f in self.files ]) )


        s = Sample( weight=self.weight, preselection=self.preselection, master=master, friends=friends )

        return s


import types
#______________________________________________________________________________
class TreeAnalyser:
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
            super(BufferedPlotter,self).__init__(*args,**kwargs)

        def __getitem__(self,val):
            elists = self._analyser._ensureentries()
            if isinstance(val,types.SliceType):
                pass
                plots = self._worker._plotsfromentries(name,varexp,elists,options,bins)
            else:
                pass
                plots = self._worker._plotsfromentries(name,varexp,elists,options,bins)



    #---
    def __init__(self, sample, cuts ):
        self._worker = self._makeworker(sample)
        self._cuts = cuts
        self._entries = None

    #---
    def __del__(self):
        if self._entries:
            for l in self._entries.itervalues():
                self._logger.debug( 'obj before %s',l.__repr__())
                l.IsA().Destructor(l)
                self._logger.debug( 'obj after  %s', l.__repr__())


    #---
    def __repr__(self):
        return self.__class__.__name__


    #---
    def __setattr__(self,key,value):
        if key == 'lumi':
            self._worker.setscale(value)
        else:
            self.__dict__[key] = value

    #---
    @staticmethod
    def _makeworker(sample):
        if not isinstance( sample, Sample):
            raise ValueError('sample must inherit from %s (found %s)' % (Sample.__name__, sample.__class__.__name__) )
        t = TreeWorker( sample.trees() )
        t.setselection( sample.preselection )
        t.setweight( sample.weight )
        return t


    #---
    def _ensureentries(self):
        if not self._entries:
            self._logger.info('Buffering the entries passing each cut')
            self._entries = self._worker._makeentrylists(self._cuts)
        return self._entries

    #---
    def entries(self):
        return self._worker.entries(self._cuts.string())

    #---
    def entriesflow(self):
        return [ (n,self._worker.entries(self._cuts[:i+1].string()))  for i,n in enumerate(self._cuts) ]

    #---
    def yields(self):
        return self._worker.yields(self._cuts.string())

    #---
    def yieldsflow(self):
        # make the entries
        elists = self._ensureentries()

        # add the weight and get the yields
        yields = self._worker._yieldsfromentries(elists)
        return yields
        
#         return self._worker.yieldsflow(odict.OrderedDict(self._cuts.list()))

    #---
    def plot(self, name, varexp, options='', bins=None, extra=None):
        cut = self._cuts.string()
        if extra:
            cut = '(%s) && (%s)' % (cut,extra)

        return self._worker.plot(name,varexp,cut,options,bins)

    #---
    def plotsflow(self, name, varexp, options='', bins=None, extra=None):
        # make the entries
        elists = self._ensureentries()
        
        # add the weight and get the yields
        plots = self._worker._plotsfromentries(name,varexp,elists,options,bins)
        return plots
#         return self._worker.plotsflow(name,varexp,odict.OrderedDict(self._cuts.list()), options, bins)

    #---
    def plotter(self,*args,**kwargs):
        return self.Plotter(self,*args,**kwargs)


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
    
    print a.entries()
    
    print a._worker._friends

    del a
    




