import ctypes
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


