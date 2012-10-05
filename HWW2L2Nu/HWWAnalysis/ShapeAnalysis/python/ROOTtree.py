#!/usr/bin/env python


import ctypes
import os.path
import HWWAnalysis.Misc.ROOTAndUtils as utils
import HWWAnalysis.Misc.odict as odict

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
class TreeWorker:
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
        self._scale     = ''
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
        for fchain in self._friends:
            self._chain.RemoveFriend(fchain)
            ROOT.SetOwnership(fchain,True)
            del fchain

    #---
    def setweight(self,w):
        self._weight = str(w)

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

        self._chain.Draw('>> '+name, self._selection, 'entrylist')

        elist = ROOT.gDirectory.Get(name)
        elist.SetDirectory(0x0)
        self._chain.SetEntryList(elist)

        ROOT.SetOwnership(elist,True)
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
        return self._chain.Draw(*args, **kwargs)

    def _cutexpr(self,cuts):
        if isinstance(cuts,list):
            cuts = [self._scale,self._weight]+cuts
#         elif isinstance(cuts,CutFlow):
#             cuts = [self._scale,self._weight]+cuts.list()
        else:
            cuts = [self._scale,self._weight,cuts]
        expr = '*'.join( ['(%s)' % s for s in cuts if s ] )
        return expr


    #---
    def _plot(self,varexp, cut, options, *args, **kwargs):
        sentry = utils.TH1AddDirSentry()
        options = 'goff '+options
        self._chain.Draw(varexp , cut, options, *args, **kwargs)
        return self._chain.GetHistogram()
    
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
        return h.Integral()

    #--
    def yieldsflow(self, cuts, options=''):
        yields = odict.OrderedDict()

        flow = []
        elists = []
        for i,(name,acut) in enumerate(cuts.iteritems()):
            flow += [acut]
            cut = self._cutexpr(flow)
            elabel = 'elist%d' % i
            self._chain.Draw('>>'+elabel,cut,'goff entrylist')
            

            l = ROOT.gDirectory.Get(elabel)
            elists.append(l)
            self._chain.SetEntryList(l)
            yields[name] = self.yields( '', options )

        self._chain.SetEntryList(0)

        for l in elists:
            l.IsA().Destructor(l)
            del l
        
        return yields
    
    #---
    def plot(self, name, varexp, cut='', options='', bins=None, *args, **kwargs):
        
        hstr,ndim = self._projexpr(name,bins)
        
        varexp = '%s >> %s' % (varexp,hstr)
        cut = self._cutexpr(cut)

        return self._plot( varexp, cut, options, *args, **kwargs)

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

   


