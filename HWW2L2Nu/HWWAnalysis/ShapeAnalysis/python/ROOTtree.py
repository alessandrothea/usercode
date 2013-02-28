#!/usr/bin/env python


import ctypes
import os.path
import HWWAnalysis.Misc.ROOTAndUtils as utils
import HWWAnalysis.Misc.odict as odict
import logging
import math
import re

#      ________      __  ______                 __ 
#     / ____/ /___ _/ /_/ ____/   _____  ____  / /_
#    / /_  / / __ `/ __/ __/ | | / / _ \/ __ \/ __/
#   / __/ / / /_/ / /_/ /___ | |/ /  __/ / / / /_  
#  /_/   /_/\__,_/\__/_____/ |___/\___/_/ /_/\__/  
#                                                  

class Leaves:
    types = [
        ctypes.c_char_p,
        ctypes.c_byte,
        ctypes.c_ubyte,
        ctypes.c_short,
        ctypes.c_ushort,
        ctypes.c_int,
        ctypes.c_uint,
        ctypes.c_float,
        ctypes.c_double,
        ctypes.c_long,
        ctypes.c_ulong,
        ctypes.c_bool,
    ]

    flags = [
        'C',
        'B',
        'b',
        'S',
        's',
        'I',
        'i',
        'F',
        'D',
        'L',
        'l',
        'O',
    ]

    flag2type = dict(zip(flags,types))
    type2flag = dict(zip(types,flags))

class Event(object):
    '''this is an alternative way to access the TTree leaves for a flat tree'''


    #---
    def __getattr__(self,name):
        try:
            print name
            return self._leaves[name].value
        except KeyError:
            raise AttributeError(name)
    #---
    def __setattr__(self,name, value):
        
        try:
            self._leaves[name].value = value
        except:
            self.__dict__[name] = value

    #---
    def __init__(self, tree):
        self.__dict__['_leaves'] = {}
        self._tree = tree

        self._linked = set()

        self._attach()


    def _attach(self):
        # do cleaning?
        import re
        expr = re.compile('([a-zA-Z0-9_]*)/([CBbSsIiFDLlO])')
        for b in self._tree.GetListOfBranches():
            title = b.GetTitle()
            # how do we check the branch is elemetary?
            m = expr.match(title)
            if not m:
                print 'NOT Matched',title
                continue
            else:
                name,t = m.groups()

            # - C : a character string terminated by the 0 character
            # - B : an 8 bit signed integer (Char_t)
            # - b : an 8 bit unsigned integer (UChar_t)
            # - S : a 16 bit signed integer (Short_t)
            # - s : a 16 bit unsigned integer (UShort_t)
            # - I : a 32 bit signed integer (Int_t)
            # - i : a 32 bit unsigned integer (UInt_t)
            # - F : a 32 bit floating point (Float_t)
            # - D : a 64 bit floating point (Double_t)
            # - L : a 64 bit signed integer (Long64_t)
            # - l : a 64 bit unsigned integer (ULong64_t)
            # - O : [the letter 'o', not a zero] a boolean (Bool_t)

            if t not in Leaves.flag2type:
                print 'Type',t,'not found'
                continue

            if name in self._leaves:
                print 'What?? twice the same branch?!?',name
                continue

            leaf = Leaves.flag2type[t]()
            self._leaves[name] = leaf
            self._tree.SetBranchAddress(name, leaf)

    #--- 
    def link(self,t):
        '''
Link another tree to this event:

Example: 
    When cloning trees
    t0 = TTree

    t1 = t0.CloneTree(0)

    e = Event(t1)  # the event is built on t1, but now t0 and t1 buffers are decoupled
    e.link(t0)     # now both trees are filling the same buggers i.e. e.leaves

'''
        if t == self._tree:
            raise ValueError('TTree '+str(t)+' is already attached to this event')

        for n,b in self._leaves.iteritems():
            t.SetBranchAddress(n,b)

        self._linked.add(t)


    #--- 
    def unlink(self,):
        self._linked.remove(t)

    #--- 
    def _addleaf(self,name,t):
            if t not in Leaves.flag2type:
                raise ValueError('Type '+t+' not found')

            if name in self._leaves:
                raise AttributeError( 'What?? twice the same branch name?!? '+name)

            leaf = Leaves.flag2type[t]()
            self._leaves[name] = leaf
            self._tree.Branch(name, leaf,'%s/%s' % (name,t) )

    #---
    def leafflag(self,name):
        ''' returns the type-flag of the variable '''
        try:
            return Leaves.type2flag(self._leaves[name].__class__)
        except KeyError as e:
            raise e

    #--- 
    def leaves(self):
        return self._leaves.keys()

    #--- 
    def add(self, branches ):
        if isinstance(branches,tuple):
            branches = [branches]
        elif isinstance(branches, list):
            pass
        else:
            raise TypeError('the argument must be either a tuple or a list')

        for n,t in branches: 
            self._addleaf(n,t)





import ROOT
#    ______             _       __           __            
#   /_  __/_______  ___| |     / /___  _____/ /_____  _____
#    / / / ___/ _ \/ _ \ | /| / / __ \/ ___/ //_/ _ \/ ___/
#   / / / /  /  __/  __/ |/ |/ / /_/ / /  / ,< /  __/ /    
#  /_/ /_/   \___/\___/|__/|__/\____/_/  /_/|_|\___/_/     
#                                                          

# _____________________________________________________________________________
def _buildchain(treeName,files):
    tree = ROOT.TChain(treeName)
    for path in files:
        if not os.path.exists(path):
            raise RuntimeError('File '+path+' doesn\'t exists')
        tree.Add(path) 

    return tree

# _____________________________________________________________________________
class Yield:
    def __init__(self, y, ey):
        self.value = y 
        self.error  = ey

    def __add__(self,other):
        
        value = self.value+other.value
        error = math.sqrt(self.error**2 +other.error**2)

        return Yield(value,error)

    def __sub__(self,other):
        
        value = self.value-other.value
        error = math.sqrt(self.error**2 +other.error**2)

        return Yield(value,error)

    def __rmul__(self,other):
        if isinstance(other,float) or isinstance(other,int):
            return Yield(other * self.value, other * self.error)
        else:
            raise ValueError('Right multiplication with type \'%s\' not supported' % other.__class__.__name__)

    def __repr__(self):
        return '(%.3f+/-%.3f)' % (self.value, self.error)

    def __str__(self):
        return '%f +/- %f' % (self.value, self.error)

# _____________________________________________________________________________
class TreeWorker:
    _logger = logging.getLogger('TreeWorker')
    #---
    def __init__(self, samples ):
    
        if not isinstance( samples, list ):
            raise TypeError('samples is not a list of tuples')

        if len(samples) == 0:
            raise ValueError('no entries found in the sample list')

        name, filenames = samples[0]

        self._chain = _buildchain(name, filenames)
        self._chain.GetEntries()
        self._elist     = None
        self._friends   = []
        self._weight    = ''
        self._scale     = 1.
        self._selection = ''
        self._link(samples[1:])



    #---
    def _link(self,friends):
        for ftree,ffilenames in friends:
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
    def _makeentrylists(self, cuts):
        '''make a list of entries from an ordered dict of strings'''
        elists = odict.OrderedDict()
        for i,(name,acut) in enumerate(cuts.iteritems()):
            cut = self._cutexpr(acut)
            elabel = 'elist%d' % i
            self._plot('>>'+elabel,cut,'entrylist')
            
            l = ROOT.gDirectory.Get(elabel)
            # detach the list
            l.SetDirectory(0x0)
            # ensure the ownership
            ROOT.SetOwnership(l,True)
            # store it
            elists[name] = l
            # activate it
            self._chain.SetEntryList(l)

            self._logger.debug('%s -> %d',l.GetName(),l.GetN())

        # restore the preselection
        self._chain.SetEntryList(self._elist if self._elist else 0x0)
        return elists

    #---
    def _updateentrylists(self, cuts, elists):
        '''merge it with _makeentrylists?'''
        
        # check the keys
        lentries = len(elists)

        # find the first mismatching cut
        for i, ( n,m ) in enumerate(zip(cuts.iterkeys(),elists.iterkeys())):
            if not ( ( n == m ) and ( self._cutexpr(cuts[n]) == elists[m].GetTitle() ) ): break
        elast = elists[n] 
        numok = i+1

        # purge the rest of elists
        if numok < lentries:
            for n in elists.keys()[numok:lentries]:
                self._logger.debug('Deleting %s',n)
                del elists[n]

        for i,(n,l) in enumerate(elists.iteritems()):
            self._logger.debug('- %d %s,%d', i,n,l.GetN())

        # setting the last common
        self._chain.SetEntryList(elast)

        newcuts = cuts[numok:]
        for i,(name,acut) in enumerate(newcuts.iteritems()):
            self._logger.debug('Adding cut %d %s', i+numok,name)
            cut = self._cutexpr(acut)
            elabel = 'elist%d' % (i+numok)
            self._plot('>>'+elabel,cut,'entrylist')

            l = ROOT.gDirectory.Get(elabel)
            # detach the list
            l.SetDirectory(0x0)
            # ensure the ownership
            ROOT.SetOwnership(l,True)
            # store it
            elists[name] = l
            # activate it
            self._chain.SetEntryList(l)

            self._logger.debug('%s -> %d',l.GetName(),l.GetN())

        # restore the preselection
        self._chain.SetEntryList(self._elist if self._elist else 0x0)
        return elists

#         minl = min(len(cuts),len(elist))
#         
#         self._logger.debug('min len (cuts,entries): %d %s',minl, [len(cuts),len(elist)]) 

#         broken = False
#         # process the 2 lists in parallel
#         for i, ( n,m ) in enumerate(zip(cuts.iterkeys(),elist.iterkeys())):
#             print i,n,m, self._cutexpr(cuts[n]) == elist[m].GetTitle()

#             broken = ( n == m ) and ( self._cutexpr(cuts[n]) == elist[m].GetTitle() )

#         print i

#         [ self._cutexpr(c) for c in cuts ]


#         etrash = odict.OrderedDict()
#         
#         for i,(name,acut) in enumerate(cuts.iteritems()):
#             cut = self._cutexpr(acut)
#             elabel = 'elist%d' % i
#             self._plot('>>'+elabel,cut,'entrylist')
#             
#             l = ROOT.gDirectory.Get(elabel)
#             # detach the list
#             l.SetDirectory(0x0)
#             # ensure the ownership
#             ROOT.SetOwnership(l,True)
#             # store it
#             elists[name] = l
#             # activate it
#             self._chain.SetEntryList(l)

#             self._logger.debug('%s -> %d',l.GetName(),l.GetN())

#         # restore the preselection
#         self._chain.SetEntryList(self._elist if self._elist else 0x0)
#         return elists

    #---
    def _delroots(self,roots):
        for l in roots.itervalues():
            self._logger.debug( 'obj before %s',l.__repr__())
            l.IsA().Destructor(l)
            self._logger.debug( 'obj after  %s', l.__repr__())
        

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
        name = 'sellist'
        
        self._chain.SetEntryList(0x0)

        if self._elist: del self._elist

        #no selection, stop here
        if not self._selection: return
        self._logger.debug( 'applying worker selection %s', self._selection )

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
    def entries(self,cut=''):
        return self._chain.GetEntries(cut)

    #---
    def draw(self, *args, **kwargs):
        '''Direct access to the chain Draw. Is it really necessary?'''
        return self._chain.Draw(*args, **kwargs)
    
    #--
    def _cutexpr(self,cuts,addweight=True,addselection=False):
        ''' makes a cut string or a list of cuts into the cutsrting to be used with the TTree, adding the weight '''

        # ignore unitary weights
        w = self._weight if addweight and self._weight != '1' else None
        # add selection only if requested
        s = self._selection if addselection else None

        
        cutlist = [s]+cuts if isinstance(cuts,list) else [s,cuts]
        cutstr = ' && '.join( ['(%s)' % s for s in cutlist if s])

        expr ='*'.join(['(%s)' % s for s in [w,cutstr] if s])
        return expr

        
#         if isinstance(cuts,list):
#             clist = [self._weight,]
#         else:
#             clist = [self._weight,cuts]
#         expr = '*'.join( ['(%s)' % s for s in clist if s and s != '1' ] )
        return expr


    #---
    def _plot(self,varexp, cut, options, *args, **kwargs):
        '''primitive method to produce histograms and projections'''
        sentry = utils.TH1AddDirSentry()
        options = 'goff '+options
        self._logger.debug('varexp:  %s', varexp)
        self._logger.debug('cut:     %s', cut)
        self._logger.debug('options: %s', options)

        n = self._chain.Draw(varexp , cut, options, *args, **kwargs)
        h = self._chain.GetHistogram()
        if h.__nonzero__():
            self._logger.debug('entries  %d integral %f', h.GetEntries(), h.Integral())
            h.Scale(self._scale)
            self._logger.debug('scale:   %f integral %f', self._scale, h.Integral())
            return h
        else:
            self._logger.debug('entries  %d', n)
            return None
    
    #---
    @staticmethod
    def _projexpr( name, bins = None ):
        if not bins:
            return name,0
        elif not ( isinstance(bins, tuple) or isinstance(bins,list)):
            raise RuntimeError('bin must be an ntuple or an arrya')
            
        l = len(bins)
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
        return name+hdef,ndim



    #---
    def yields(self, cut='', options='', *args, **kwargs):
        cut = self._cutexpr(cut)
        h = self._plot('0 >> counter(1,0.,1.)', cut, options, *args, **kwargs)

        xax = h.GetXaxis()
        err = ctypes.c_double(0.)
        int = h.IntegralAndError(xax.GetFirst(), xax.GetLast(), err)
        
        return Yield(int,err.value)


    def _yieldsfromentries(self, elists, options='', extra=None):
        '''Calculates the yields using eventlists instead of cuts'''
        yields = odict.OrderedDict()

        cut = extra if extra else ''
        for c,l in elists.iteritems():
            self._logger.debug('yield for %s',c)
            self._chain.SetEntryList(l)
            yields[c] = self.yields( cut, options )

        # restore the preselection
        self._chain.SetEntryList(self._elist if self._elist else 0x0)

        return yields

    #---
    def yieldsflow(self, cuts, options=''):
        '''Does it make sense to have a double step?
        In a way yes, because otherwise one would have to loop over all the events for each step
        '''

        # make the entries
        elists = self._makeentrylists(cuts)
        
        # add the weight and get the yields
        yields = self._yieldsfromentries(elists,options)

        # delete the lists
        self._delroots(elists)

        return yields
    
    #---
    def plot(self, name, varexp, cut='', options='', bins=None, *args, **kwargs):
    
        # check the name doesn't contain project infos
        m = re.match(r'.*(\([^\)]*\))',name)
        if m: raise ValueError('Use bins argument to specify the binning %s' % m.group(1))
                
        hstr,ndim = self._projexpr(name,bins)
        
        varexp = '%s >> %s' % (varexp,hstr)
        cut = self._cutexpr(cut)

        return self._plot( varexp, cut, options, *args, **kwargs)

    #---
    def _plotsfromentries(self,name, varexp, elists, options='', bins=None, extra=None, *args, **kwargs):
        '''plot the plots using eventlists instead of cuts'''
        plots = odict.OrderedDict()

        cut = extra if extra else ''
        for c,l in elists.iteritems():
            self._chain.SetEntryList(l)
            plots[c] = self.plot('%s_%s' % (name,c),varexp,cut,options,bins,*args, **kwargs) 

        # restore the preselection
        self._chain.SetEntryList(self._elist if self._elist else 0x0)

        return plots

    #---
    def plotsflow(self, name, varexp, cuts, options='', bins=None, *args, **kwargs):

        # make the entries
        elists = self._makeentrylists(cuts)
        
        # add the weight and get the yields
        plots = self._plotsfromentries(name,varexp,elists,options,bins,*args, **kwargs)

        # delete the lists
        self._delroots(elists)

        return plots

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

# helper class 
class sample:
    def __init__(self, **kwargs):
        self.tree      = ''
        self.files     = []
        self.selection = ''
        self.weight    = ''
        self.title     = ''

        for k,v in kwargs.iteritems():
            if not hasattr(self,k): continue
            setattr(self,k,v)

   


