#!/usr/bin/env python


import ctypes
import os.path
import HWWAnalysis.Misc.ROOTAndUtils as utils
import HWWAnalysis.Misc.odict as odict
import logging
import math
import uuid
import re
import numpy
import array
import ROOT
import copy
from .base import Labelled

# _____________________________________________________________________________
#    __  ____  _ __    
#   / / / / /_(_) /____
#  / / / / __/ / / ___/
# / /_/ / /_/ / (__  ) 
# \____/\__/_/_/____/  
#                      

# ---
def _bins2hclass( bins ):
    '''
    Fixed bin width
    bins = (nx,xmin,xmax)
    bins = (nx,xmin,xmax, ny,ymin,ymax)
    Variable bin width
    bins = ([x0,...,xn])
    bins = ([x0,...,xn],[y0,...,ym])
    
    '''

    from array import array
    if not bins:
        return name,0
    elif not ( isinstance(bins, tuple) ):
        raise RuntimeError('bin must be an ntuple or an arryas')

    l = len(bins)
    # 1D variable binning
    if l == 1 and isinstance(bins[0],list):
        ndim=1
        hclass = ROOT.TH1D
        xbins = bins[0]
        hargs = (len(xbins)-1, array('d',xbins))
    elif l == 2 and  isinstance(bins[0],list) and  isinstance(bins[1],list):
        ndim=2
        hclass = ROOT.TH2D
        xbins = bins[0]
        ybins = bins[1]
        hargs = (len(xbins)-1, array('d',xbins),
                len(ybins)-1, array('d',ybins))
    elif l == 3:
        # nx,xmin,xmax
        ndim=1
        hclass = ROOT.TH1D
        hargs = bins
    elif l == 6:
        # nx,xmin,xmax,ny,ymin,ymax
        ndim=2
        hclass = ROOT.TH2D
        hargs = bins
    else:
        # only 1d or 2 d hist
        raise RuntimeError('What a mess!!! bin malformed!')
    
    return ndim,hclass,hargs

# _____________________________________________________________________________
def _buildchain(treeName,files):
    tree = ROOT.TChain(treeName)
    for path in files:
        # if # is in the path, it's a zipfile!
        filepath = path if '#' not in path else path[:path.index('#')]
        if not os.path.exists(filepath):
            raise RuntimeError('File '+filepath+' doesn\'t exists')
        tree.Add(path) 

    return tree


# ______________________________________________________________________________
#    _____                       __   
#   / ___/____ _____ ___  ____  / /__ 
#   \__ \/ __ `/ __ `__ \/ __ \/ / _ \
#  ___/ / /_/ / / / / / / /_/ / /  __/
# /____/\__,_/_/ /_/ /_/ .___/_/\___/ 
#                     /_/             

class Sample(Labelled):
    '''
    A container for the information to make a TreeWorker

    name: the tree name/path in the rootfile
    files: list of rootfiles
    friends: list of tuples of friend name and files [(fnameA,['c.root','d.root']),('fnameB',[])]
    '''

    #---
    def __init__(self, name, files, preselection='', weight='', scale=1., friends=[]):

        super(Sample,self).__init__('')
        self.name         = name
        self.files        = files
        self.preselection = preselection
        self.weight       = weight
        self.friends      = friends

    #---
    def __repr__(self):
        repr = []
        repr += [self.__class__.__name__+(' '+self.name if self.name else'') + (' also known as '+self._title if self._title else '')]
        repr += ['weight: \'%s\', preselection: \'%s\'' % (self.weight, self.preselection) ]
        repr += ['name: '+self.name+'  files: '+str(self.files) ]
        for i,friend in enumerate(self.friends):
            repr += [('friend: ' if i == 0 else ' '*8)+friend[0]+'  files: '+str(friend[1]) ]

        return '\n'.join(repr)

    __str__ = __repr__

    def dump(self):
        print self.__repr__()

    #---
    def addfriend(self, name, files):
        self.friends.append( (name, files) )


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
    def __init__(self, y, ey):
        self.value = y 
        self.error  = ey

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
    def __rmul__(self,other):
        if isinstance(other,float) or isinstance(other,int):
            return Yield(other * self.value, other * self.error)
        else:
            raise ValueError('Right multiplication with type \'%s\' not supported' % other.__class__.__name__)

    #---
    def __repr__(self):
        return '(%s+/-%s)' % (self.value, self.error)

    #---
    def __str__(self):
        return '%s +/- %s' % (self.value, self.error)



# _____________________________________________________________________________
#    ______             _       __           __            
#   /_  __/_______  ___| |     / /___  _____/ /_____  _____
#    / / / ___/ _ \/ _ \ | /| / / __ \/ ___/ //_/ _ \/ ___/
#   / / / /  /  __/  __/ |/ |/ / /_/ / /  / ,< /  __/ /    
#  /_/ /_/   \___/\___/|__/|__/\____/_/  /_/|_|\___/_/     
#                                                          
class TreeWorker:
    '''
    t = TreeWorker( tree='latino',files=['a.root','b.root'], selection='x <1', weight='3*x', friends=[('bdt',['c.root','d.root']),...]

    t = TreeWorker('latino', ['a.root','b.root'] )
    t.addfriend('bdt',['c.root','d.root'])
    t.setweight('3*x')
    t.setselection('x < 1')

    t = TreeWorker.fromSample( sample )
    '''
    _log = logging.getLogger('TreeWorker')
    #---

    # ---
    def __init__(self, name, files, selection='', weight='', scale=1., friends=None):

        self._chain = _buildchain(name, files)
        self._chain.GetEntries()
        self._elist     = None
        self._friends   = []

        self._weight    = weight
        self._selection = selection
        self._scale     = scale
        if friends: self._link(friends)

        self.setselection(self._selection)

    # ---
    @staticmethod
    def fromsample( sample ):
        if not isinstance( sample, Sample):
            raise ValueError('sample must inherit from %s (found %s)' % (Sample.__name__, sample.__class__.__name__) )
        t = TreeWorker( sample.name, sample.files )
        t.setselection( sample.preselection )
        t.setweight( sample.weight )
        return t

    #---
    def __repr__(self):
        return '%s(%s,s=%r,w=%r)' % (self.__class__.__name__,self._chain.GetName(),self._selection,self._weight)

    __str__ = __repr__


    #---
    def _link(self,friends):
        for ftree,ffilenames in friends:
            self.addfriend(free,ffilenames)

    #---
    def addfriend(name,files):
        fchain = _buildchain(ftree,ffilenames)
        if self._chain.GetEntriesFast() != fchain.GetEntries():
            raise RuntimeError('Mismatching number of entries: '
                               +self._chain.GetName()+'('+str(self._chain.GetEntriesFast())+'), '
                               +fchain.GetName()+'('+str(fchain.GetEntriesFast())+')')
        self._chain.AddFriend(fchain)
        self._friends.append(fchain)

    #---
    def __del__(self):
        if hasattr(self,'_friends'):
            for fchain in self._friends:
                self._chain.RemoveFriend(fchain)
                ROOT.SetOwnership(fchain,True)
                del fchain

    #---
    def __getattr__(self,name):
        return getattr(self._chain,name)

    #---
    def _makeentrylist(self,label,cut):

        cutexpr = self._cutexpr(cut)
        self._plot('>>'+label,cutexpr,'entrylist')
        
        l = ROOT.gDirectory.Get(label)
        # detach the list
        l.SetDirectory(0x0)
        # ensure the ownership
        ROOT.SetOwnership(l,True)

        return l

    # ---
    def views(self,cuts):
        if not cuts: return odict.OrderedDict()
        views = odict.OrderedDict()
        last = TreeView(self)
        for i,(n,c) in enumerate(cuts.iteritems()):
            m = last.spawn(c,'elist%d' % (i+nv) )
            last = m  
            views[n] = m

        return views
        

    #---
#V0     def _makeentrylists(self, cuts, cnt=0):
#V0         '''make a list of entries from an ordered dict of strings'''
#V0         elists = odict.OrderedDict()
#V0         for i,(name,acut) in enumerate(cuts.iteritems()):
#V0             cut = self._cutexpr(acut)
#V0             elabel = 'elist%d' % (cnt+i)

#V0             l = self._makeentrylist(elabel,cut)
#V0             # store it
#V0             elists[name] = l
#V0             # activate it
#V0             self._chain.SetEntryList(l)

#V0             self._log.debug('%s -> %d',l.GetName(),l.GetN())

#V0         # restore the preselection
#V0         self._chain.SetEntryList(self._elist if self._elist else 0x0)
#V0         return elists

#V0     #---
#V0     def _updateentrylists(self, cuts, elists):
#V0         '''merge it with _makeentrylists?'''
#V0         
#V0         # check the keys
#V0         lentries = len(elists)

#V0         # find the first mismatching cut
#V0         for i, ( n,m ) in enumerate(zip(cuts.iterkeys(),elists.iterkeys())):
#V0             if not ( ( n == m ) and ( self._cutexpr(cuts[n]) == elists[m].GetTitle() ) ): break
#V0         elast = elists[n] 
#V0         numok = i+1

#V0         # purge the rest of elists
#V0         if numok < lentries:
#V0             for n in elists.keys()[numok:lentries]:
#V0                 self._log.debug('Deleting %s',n)
#V0                 del elists[n]

#V0         for i,(n,l) in enumerate(elists.iteritems()):
#V0             self._log.debug('- %d %s,%d', i,n,l.GetN())

#V0         # setting the last common
#V0         self._chain.SetEntryList(elast)

#V0         newcuts = cuts[numok:]
#V0         # create the missing entrllists 
#V0         newlist = self._makeentrylists(newcuts,numok)
#V0         elists.update(newlist)

#V0         # restore the preselection
#V0         self._chain.SetEntryList(self._elist if self._elist else 0x0)
#V0         return elists

    #---
    def _delroots(self,roots):
        for l in roots.itervalues():
            self._log.debug( 'obj before %s',l.__repr__())
            l.IsA().Destructor(l)
            self._log.debug( 'obj after  %s', l.__repr__())

    #---
    def setweight(self,w):
        self._weight = str(w)

    #---
    def setscale(self,s):
        self._scale = float(s)

    #---
    def setselection(self,c):
        # shall we work in a protected directory?
        self._selection = str(c)
        # make an entrylist with only the selected events
        name = 'selection'
        
        self._chain.SetEntryList(0x0)

        if self._elist: del self._elist

        #no selection, stop here
        if not self._selection: return
        self._log.debug( 'applying worker selection %s', self._selection )

        self._chain.Draw('>> '+name, self._selection, 'entrylist')

        elist = ROOT.gDirectory.Get(name)
        # detach the list
        elist.SetDirectory(0x0)
        # ensure the ownership
        ROOT.SetOwnership(elist,True)
        # activate it
        self._chain.SetEntryList(elist)

        self._elist = elist

    #---
    def getminmax(self,var,binsize=0):
        # check var is one of the branches, otherwise it doesn't work
        import math
        xmin,xmax = self._chain.GetMinimum(var),self._chain.GetMaximum(var)
        
        if binsize > 0:
            xmin,xmax = math.floor(xmin/binsize)*binsize,math.ceil(xmax/binsize)*binsize

        return xmin,xmax

    #---
    def entries(self,cut=None):
        if not cut:
            el = self._chain.GetEntryList() 
            if el.__nonzero__(): return el.GetN()
            else:                return self._chain.GetEntries()
        else:
            # super simple projection
            return self._chain.Draw('1.', cut,'goff')

    #---
    def draw(self, *args, **kwargs):
        '''Direct access to the chain Draw. Is it really necessary?'''
        return self._chain.Draw(*args, **kwargs)
    
    #--
    def _cutexpr(self,cuts,addweight=True,addselection=False):
        '''
        makes a cut string or a list of cuts into the cutsrting to be used with
        the TTree, adding the weight
        '''

        # ignore unitary weights
        w = self._weight if addweight and self._weight != '1' else None
        # add selection only if requested
        s = self._selection if addselection else None

        cutlist = [s]+cuts if isinstance(cuts,list) else [s,cuts]
        cutstr = ' && '.join( ['(%s)' % s for s in cutlist if (s and str(s) != '')])

        expr ='*'.join(['(%s)' % s for s in [w,cutstr] if (s and str(s) != '')])

        return expr

    #---
    @staticmethod
    def _projexpr( name, bins = None ):
        '''
        Prepares the target for plotting if the binning is standard (n,min,max)
        then return a string else, it's variable binning, make the htemp and
        return it
        '''
        if not bins:
            return 0,name,None
        elif not isinstance(bins, tuple):
            raise TypeError('bin must be an ntuple or an array')
        
        l = len(bins)
        # if the tuple is made of lists
        if l in [1,2] and all(map(lambda o: isinstance(o,list),bins)):
            dirsentry = utils.TH1AddDirSentry()
            sumsentry = utils.TH1Sumw2Sentry()

            # get the hshape
            hdim,hclass,hargs = _bins2hclass( bins )

            # make the histogram
            htemp = hclass(name, name, *hargs)

            return hdim,name,htemp

        else:
            # standard approach, the string goes into the expression
            if l in [1,3]:
                # nx,xmin,xmax
                ndim=1
            elif l in [4,6]:
                # nx,xmin,xmax,ny,ymin,ymax
                ndim=2
            else:
                # only 1d or 2 d hist
                raise RuntimeError('What a mess!!! bin malformed!')

            hdef = '('+','.join([ str(x) for x in bins])+')' if bins else ''
            return ndim,name+hdef,None



    #---
    def _plot(self,varexp, cut, options='', *args, **kwargs):
        '''
        Primitive method to produce histograms and projections
        '''
        dirsentry = utils.TH1AddDirSentry()
        sumsentry = utils.TH1Sumw2Sentry()
        options = 'goff '+options
        self._log.debug('varexp:  \'%s\'', varexp)
        self._log.debug('cut:     \'%s\'', cut)
        self._log.debug('options: \'%s\'', options)

        n = self._chain.Draw(varexp , cut, options, *args, **kwargs)
        h = self._chain.GetHistogram()
        if h.__nonzero__():
#             print h.GetDirectory()
            self._log.debug('entries  %d integral %f', h.GetEntries(), h.Integral())
            h.Scale(self._scale)
            self._log.debug('scale:   %f integral %f', self._scale, h.Integral())
            return h
        else:
            self._log.debug('entries  %d', n)
            return None
    
    
    #---
    def yields(self, cut='', options='', *args, **kwargs):
        cut = self._cutexpr(cut)
        h = self._plot('0 >> counter(1,0.,1.)', cut, options, *args, **kwargs)

        xax = h.GetXaxis()
        err = ctypes.c_double(0.)
        int = h.IntegralAndError(xax.GetFirst(), xax.GetLast(), err)
        
        return Yield(int,err.value)

    #---
    def plot(self, name, varexp, cut='', options='', bins=None, *args, **kwargs):
    
        # check the name doesn't contain project infos
        m = re.match(r'.*(\([^\)]*\))',name)
        if m: raise ValueError('Use bins argument to specify the binning %s' % m.group(1))

        ndim,hstr,htemp = self._projexpr(name,bins)

        cut = self._cutexpr(cut)

        if htemp:
            # do a projection with a target
            # make an unique name (juust in case)
            tname = '%s_%s' % (htemp.GetName(),uuid.uuid1())
            htemp.SetName( tname )
            htemp.SetDirectory( ROOT.gDirectory.func()) 
            hstr = hstr.replace(name,tname)

            varexp = '%s >> %s' % (varexp,hstr)
            h = self._plot( varexp, cut, options, *args, **kwargs)

            # reset the directory 
            h.SetDirectory(0x0)
            h.SetName(name)
        else:
            # let TTree::Draw to create the temporary histogram
            varexp = '%s >> %s' % (varexp,hstr)
            h = self._plot( varexp, cut, options, *args, **kwargs)

        return h

#V0     def _yieldsfromentries(self, elists, options='', extra=None):
#V0         '''Calculates the yields using eventlists instead of cuts'''
#V0         yields = odict.OrderedDict()

#V0         cut = extra if extra else ''
#V0         for c,l in elists.iteritems():
#V0             self._log.debug('yield for %s',c)
#V0             self._chain.SetEntryList(l)
#V0             yields[c] = self.yields( cut, options )

#V0         # restore the preselection
#V0         self._chain.SetEntryList(self._elist if self._elist else 0x0)

#V0         return yields

    #---
    def yieldsflow(self, cuts, options=''):
        '''Does it make sense to have a double step?
        In a way yes, because otherwise one would have to loop over all the events for each step
        '''

#V0         # make the entries
#V0         elists = self._makeentrylists(cuts)
#V0         
#V0         # add the weight and get the yields
#V0         yields = self._yieldsfromentries(elists,options)

#V0         # delete the lists
#V0         self._delroots(elists)

        elists = self.views(cuts)
        return odict.OrderedDict([( n,v.yields(options=options) ) for n,v in elists.iteritems()])
    


#V0     #---
#V0     def _plotsfromentries(self,name, varexp, elists, options='', bins=None, extra=None, *args, **kwargs):
#V0         '''plot the plots using eventlists instead of cuts'''
#V0         plots = odict.OrderedDict()

#V0         cut = extra if extra else ''
#V0         for c,l in elists.iteritems():
#V0             self._chain.SetEntryList(l)
#V0             plots[c] = self.plot('%s_%s' % (name,c),varexp,cut,options,bins,*args, **kwargs) 

#V0         # restore the preselection
#V0         self._chain.SetEntryList(self._elist if self._elist else 0x0)

#V0         return plots

    #---
    def plotsflow(self, name, varexp, cuts, options='', bins=None, *args, **kwargs):

#V0         # make the entries
#V0         elists = self._makeentrylists(cuts)
#V0         
#V0         # add the weight and get the yields
#V0         plots = self._plotsfromentries(name,varexp,elists,options,bins,*args, **kwargs)

#V0         # delete the lists
#V0         self._delroots(elists)

#V0         return plots
        elists = self.views(cuts)
        return odict.OrderedDict([( n,v.plot('%s_%s' % (name,n),varexp,cuts,options,bins) ) for n,v in elists.iteritems()])

    #--- 
    def fill(self, h, varexp, cut='', options='', *args, **kwargs):
       
        # check where we are
        here = ROOT.gDirectory.func()
        hdir = h.GetDirectory()
        tmp = None

        # and if h is connected to a dir
        if not hdir.__nonzero__():
            # null directory: make a temp one to lat TTree::Draw find it
            ROOT.gROOT.cd()
            tmp = 'treeworker_'+str(os.getpid())
            hdir = ROOT.gROOT.mkdir(tmp)
            h.SetDirectory(hdir)

        hdir.cd()

        varexp = '%s >> %s' % (varexp,h.GetName())
        cut = self._cutexpr(cut)

        hout = self._plot( varexp, cut, options, *args, **kwargs)
        
        if hout != h: raise ValueError('What happened to my histogram?!?!')

        # go back home
        here.cd()

        if tmp: 
            h.SetDirectory(0x0)
            ROOT.gROOT.rmdir(tmp)

        return h


# _____________________________________________________________________________
#   ______             _    ___             
#  /_  __/_______  ___| |  / (_)__ _      __
#   / / / ___/ _ \/ _ \ | / / / _ \ | /| / /
#  / / / /  /  __/  __/ |/ / /  __/ |/ |/ / 
# /_/ /_/   \___/\___/|___/_/\___/|__/|__/  
#                                           

class TreeView:
    '''
    A Class to create iews (via TEntryList) on a TreeWorker
    '''
    class Sentry:
        '''
        '''
        def __init__(self,worker,list):
            self._worker = worker

            current = self._worker.GetEntryList()

            self._oldlist = current if current.__nonzero__() else 0x0
            if list: self._worker.SetEntryList(list)

        def __del__(self):
            # reset the old configuration
            self._worker.SetEntryList(self._oldlist)

    _log = logging.getLogger('TreeView')
    # ---
    def __init__(self, worker, cut='', name=None):
        self._worker = worker
        self._cut    = cut
        self._expcut = cut
        self._elist = None

        # don't build the list if no worker (used by copy)  
        if not worker: return

        # make myself a name if I don't have one
        name = name if name else str(uuid.uuid1())
        if cut:
            self._elist = self._worker._makeentrylist(name,cut)
        elif self._worker._elist:
            self._elist = self._worker._elist.Clone()

    #---
    def __copy__(self):
        other             = TreeView()
        other._cut        = copy.deepcopy(self._cut)
        other._extcut     = copy.deepcopy(self._extcut)
        other._worker     = self._worker
        other._elist      = self._elist.Clone() if self._elist else None

    # ---
    def __repr__(self):
        return '%s(w=%r,c=%r,%d)' % (self.__class__.__name__,self._worker, self._expcut, self.entries())


    # ---
    @property
    def name():
        return self._elist.GetName()

    @property
    def cut(self):
        return self._cut

    # ---
    def _sentry(self):
        # make a sentry which sets the current entrlylist in the worker and removes it when going out of scope
        return TreeView.Sentry(self._worker,self._elist)
    
    # ---
    def entries(self,extracut=None):
        # get the entries from worker after setting the entrylist
        sentry = self._sentry()
        return self._worker.entries(extracut)

    # ---
    def yields(self, extracut='', options='', *args, **kwargs):
        # set temporarily my entrlylist
        sentry = self._sentry()
        return self._worker.yields(extracut, options, *args, **kwargs)

    # ---
    def plot(self, name, varexp, extracut='', options='', bins=None, *args, **kwargs):
        # set temporarily my entrlylist
        sentry = self._sentry()
        return self._worker.plot(name, varexp, extracut, options, bins, *args, **kwargs)
    
    # ---
    def spawn(self,cut,name=None):
        # make myself a name if I don't have one
        name = name if name else str(uuid.uuid1())
        # set temporarily my entrlylist
        sentry = self._sentry()
        # create my spawn
        v = TreeView(self._worker, cut, name=name)

        v._expcut = '(%s) && (%s)' % (self._expcut,cut) if self._expcut else cut
        return v





# helper class 
# class sample:
#     def __init__(self, **kwargs):
#         self.tree      = ''
#         self.files     = []
#         self.selection = ''
#         self.weight    = ''
#         self.title     = ''

#         for k,v in kwargs.iteritems():
#             if not hasattr(self,k): continue
#             setattr(self,k,v)

   


