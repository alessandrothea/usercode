from abc import ABCMeta, abstractmethod
import ROOT
import HWWAnalysis.Misc.odict as odict
import math
import copy

# Sample
# AbsDataSet
# AbsPlotter
# AbsDataSet
# CompositeDataSet
# DataSet

# Dataset
# TreeWorker
# ChainWorker

# TView
# TChain

# _____________________________________________________________________________
# __  ___      __    __
# \ \/ (_)__  / /___/ /
#  \  / / _ \/ / __  /
#  / / /  __/ / /_/ /
# /_/_/\___/_/\__,_/
#

class Yield:
    '''
    Class to describe yields and errors
    A value with its error
    '''
    def __init__(self, y=0., ey=0.):
        self.value = y
        self.error = ey

    #---
    def __add__(self,other):

        value = self.value+other.value
        error = math.sqrt(self.error**2 +other.error**2)

        return Yield(value,error)

    #---
    def __sub__(self,other):

        value = self.value-other.value
        error = math.sqrt(self.error**2 +other.error**2)

        return Yield(value,error)

    #---
    def __mul__(self,other):

        value = self.value*other.value
        error = math.sqrt( (self.error/self.value)**2+(other.error/other.value)**2 )*value

        return Yield(value,error)

    #---
    def __div__(self,other):

        value = self.value/other.value
        error = math.sqrt( (self.error/self.value)**2+(other.error/other.value)**2 )*value

        return Yield(value,error)

    #---
    def __radd__(self,other):
        '''
        Right addition used in cases as
        0 + y = y
        (useful in cases as sum([y1,y2,...,yN])
        '''
        if isinstance(other,float) or isinstance(other,int):
            return Yield(other + self.value, self.error)
        else:
            raise ValueError('Right addition with type \'%s\' not supported' % other.__class__.__name__)
    #---
    def __rmul__(self,other):
        if isinstance(other,float) or isinstance(other,int):
            return Yield(other * self.value, other * self.error)
        else:
            raise ValueError('Right multiplication with type \'%s\' not supported' % other.__class__.__name__)

    #---
    def __repr__(self):
        return '(%s+-%s)' % (self.value, self.error)

    #---
    def __str__(self):
        x = int(math.floor(math.log10(self.error))) if self.error!=0 else 0
        y = int(math.floor(math.log10(self.value))) if self.error!=0 else 0
        k = min(x,y)
        if k < 4 and k >= 0:
            return ('%.2f +- %.2f') % (self.value, self.error)
        if k < 0 and k > -4:
            return ('%.'+str(-k+1)+'f +- %.'+str(-k+1)+'f') % (self.value, self.error)
        else:
            e = float(10**k)
            return '(%.2f +- %.2f)E%d' % (self.value/e, self.error/e, k)

# _____________________________________________________________________________
#     ____      __            ____
#    /  _/___  / /____  _____/ __/___ _________
#    / // __ \/ __/ _ \/ ___/ /_/ __ `/ ___/ _ \
#  _/ // / / / /_/  __/ /  / __/ /_/ / /__/  __/
# /___/_/ /_/\__/\___/_/  /_/  \__,_/\___/\___/
#
class AbsSet(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def entries(self): #, *args, **kwargs):
        ''' '''

    @abstractmethod
    def plot(self): #, *args, **kwargs):
        ''' '''

    @abstractmethod
    def project(self):
        ''' '''

    @abstractmethod
    def yields(self):
        ''' '''

# ---
class Chained:

    def __init__(self, theclass, *args):
        import inspect
        if not inspect.isclass(theclass):
            raise TypeError('the class must be a class!')

        if not all( map(isinstance,args,[theclass]*len(args))):
            raise TypeError('not all object are of class '+str(theclass))

        self._oclass = theclass
        self._objs   = list(args)

    def __iter__(self):
        return self._objs.__iter__()

    def __getitem__(self,i):
        return self._objs[i]

    def add(self,*args):
        aliens = [o for o in args if not isinstance(o,AbsSet)]
        if aliens:
            raise ValueError('Alien arguments %s! ' % aliens)
        self._objs.extend(args)

    def remove(self,i):
        return self._objs.pop(i)

    #---
    # here are the methods providing the default sum
    def entries(self,cut=None):
        return sum([ o.entries(cut) for o in self._objs  ])

    #---
    def yields(self, cut='', options='', *args, **kwargs):
        if not self._objs: return Yield(0,0)

        first = self._objs[0].yields(cut,options,*args,**kwargs)
        for o in self._objs[1:]:
            first += o.yields(cut,options,*args,**kwargs)

        return first


    #---
    def plot(self, name, varexp, cut='', options='', bins=None, *args, **kwargs):
        if not self._objs: return ROOT.TH1D()

        # for the future (>2.7)
        # import numbers
        # len(bins) == 1 and isinstance(bins[0], numbers.Number)
        # check for TTree aout-binnig
        if (
            # fully free binning
            bins is None or
            # free x binning
            ( len(bins) == 1 and isinstance(bins[0], (int,float)) ) or
            # free y binning
            ( len(bins) == 4 and isinstance(bins[3], (int,float)) )
           ):
            # ValueError('Automatic binning not supported by ChainWorker
            # (yet)')
            print '\n-->',name,varexp,cut,options,bins,args, kwargs
            raise ValueError('Automatic binning not supported by ChainWorker (yet)')

        first = self._objs[0].plot(name,varexp,cut,options,bins,*args,**kwargs)
        for o in self._objs[1:]:
            hx = o.plot(name,varexp,cut,options,bins,*args,**kwargs)
            first.Add(hx)

        return first


    #---
    def project(self, name, varexp, cut='', options='', bins=None, *args, **kwargs):
        for o in self._objs:
            o.project(name, varexp, cut, options, bins, *args, **kwargs)

#_______________________________________________________________________________
# ---
class AbsWorker(AbsSet):

    # TODO better name?
    @abstractmethod
    def spawnview(self):
        ''' '''

    @abstractmethod
    def views(self):
        ''' '''

    # ward against unwanted copies: Overloading left to child classes if
    # required
    def __copy__(self):
        raise RuntimeError('Can\'t copy a %s' % self.__class__.__name__)

    def __deepcopy__(self,memo):
        raise RuntimeError('Can\'t copy a %s' % self.__class__.__name__)

#---
class AbsView(AbsSet):

    @abstractmethod
    def spawn(self):
        ''' '''

    # ward against unwanted copies: Overloading left to child classes if
    # required
    def __copy__(self):
        raise RuntimeError('Can\'t copy a %s' % self.__class__.__name__)

    def __deepcopy__(self,memo):
        raise RuntimeError('Can\'t copy a %s' % self.__class__.__name__)

# #_______________________________________________________________________________
# #---
# class TreeWorker(AbsWorker):

#     def __init__(self, name=''):
#         self._name = name

#     def entries(self,cut=''):
#         return 5.

#     def yields(self, cut='', options='', *args, **kwargs):
#         return Yield(3,1)

#     def plot(self, name, varexp, cut='', options='', bins=None, *args, **kwargs):
#         h = ROOT.TH1D(name,varexp,5,0,1)
#         h.Fill(ROOT.gRandom.Rndm())
#         return h

#     def views(self,cuts):
#         if not cuts: return odict.OrderedDict()
#         views = odict.OrderedDict()
#         for c in cuts:
#             views[c] = TreeView(self,c,self._name)

#         return views

#     def project(self, h, varexp, cut='', options='', *args, **kwargs):
#         h.Fill(ROOT.gRandom.Rndm())
#         return h


# #---
# class ChainWorker(Chained,AbsWorker):

#     def __init__(self,*samples):
#         '''  '''
#         super(ChainWorker,self).__init__(TreeWorker,*samples)

#     def views(self,cuts):

#         # put the treeviews in a temporary container
#         allviews = [ o.views(cuts) for o in self._objs ]
#         # but what we need are the
#         alliters = [ v.itervalues() for v in allviews ]

#         import itertools
#         chainviews=odict.OrderedDict()
#         # make an iterator with everything inside
#         # cut,tview1,tview2,...,tviewN
#         # to repack them as
#         # cut,cview
#         for it in itertools.izip(cuts,*alliters):
#
#             # create a new view
#             cv = ChainView()

#             # add all the treeviews
#             cv.add( *it[1:] )

#             #add it to the list of views
#             chainviews[it[0]] = cv

#         return chainviews

#     @staticmethod
#     def fromsamples( *samples ):
#         ''' build each sample into a TreeWorker and add them together'''

#         trees = [TreeWorker.fromsample(s) for s in samples]
#         return ChainWorker(trees)



# #_______________________________________________________________________________
# #---
# class TreeView(AbsView):

#     def __init__(self, tree, cut='', name=None):
#         self._worker = tree
#         self._cut    = cut
#         self._name   = name

#     def __repr__(self):
#         return "'%s(%r:%r)'" % (self.__class__.__name__,self._name,self._cut)

#    # ---
#     def entries(self,extra=None):
#         # get the entries from worker after setting the entrylist
#         return self._worker.entries(extra)

#     # ---
#     def yields(self, extra='', options='', *args, **kwargs):
#         # set temporarily my entrlylist
#         return self._worker.yields(extra, options, *args, **kwargs)

#     # ---
#     def plot(self, name, varexp, extra='', options='', bins=None, *args, **kwargs):
#         # set temporarily my entrlylist
#         return self._worker.plot(name, varexp, extra, options, bins, *args, **kwargs)

#     # ---
#     def project(self, h, varexp, extra='', options='', *args, **kwargs):
#         # set temporarily my entrlylist
#         self._worker.project(h, varexp, cut, option, *args, **kwargs)

#     # ---
#     def spawn(self,cut,name=None):
#         return TreeView( self._worker )

# #---
# class ChainView(Chained,AbsView):

#     # ---
#     def __init__(self,chain=None, *args, **kwargs):
#         super(ChainView,self).__init__(TreeView)
#
#         # used by copy operations (default constructor)
#         if chain is None: return

#         views = [TreeView(t,*args,**kwargs) for t in chain]
#         self.add(*views)

#     # ---
#     def spawn(self,*args, **kwargs):

#         child = ChainView()

#         views = [ o.spawn(*args, **kwargs) for o in self._objs]
#
#         child.add(*views)

#         return child

