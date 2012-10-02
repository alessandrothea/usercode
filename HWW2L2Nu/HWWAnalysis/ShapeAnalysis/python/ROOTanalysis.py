import HWWAnalysis.Misc.odict as odict
# 
# Sample class to 
# 
# 
# 

#______________________________________________________________________________
class Sample:
    '''
    How do we define files?

    [('latino',['pippo/pluto.root','pippo/topolino.root']), ('latino_bdt',['bdt/pluto.root','bdt/topolino.root'])]

    Latino(weight='baseW*effW',selection='',files=['pippo/'])
'''

    #---
    def __init__(self, **kwargs):
        self.master       = (None,None)
        self.friends      = []
        self.preselection = ''
        self.weight       = ''
        self.title        = ''

        for k,v in kwargs.iteritems():
            if not hasattr(self,k): continue
            setattr(self,k,v)    

    #---
    def __repr__(self):
        repr = []
        repr += ['weight: \'%s\', preselection: \'%s\'' % (self.weight, self.preselection) ]
        repr += ['master: '+self.master[0]+'  files: '+str(self.master[1]) ]
        for friend in self.friends:
            repr += ['friend: '+friend[0]+'  files: '+str(friend[1]) ]

        return '\n'.join(repr)

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

    def __init__(self, init_val=(), strict=False):
        odict.OrderedDict.__init__(self,init_val, strict) 
    
    def __setitem__(self, key, val):
        if isinstance(val,str):
            val = Cut(val)    
        elif not isinstance(val,Cut):
            raise TypeError('CutFlow need CutSteps')
        
        val.name = key

        odict.OrderedDict.__setitem__(self,key,val)


    def __repr__(self):
        return '%s([%s])' % (self.__class__.__name__, ', '.join( 
            ['(%r, %r)' % (key, self[key].cut) for key in self._sequence]))
    
    __str__ = __repr__

    def rename(self, old_key, new_key):

        odict.OrderedDict.rename(self,old_key,new_key)

        self.__getitem__(new_key).name = new_key

    def string(self):
        return ' && '.join( [ '(%s)' % step.cut for step in self.itervalues() ] ) 

    def list(self):
        return [ step.cut for step in self.itervalues() ]


#______________________________________________________________________________
class Cut:
    def __init__(self, cut, latex=None, tlatex=None):
        self.name  = ''
        self._latex = latex
        self._tlatex = tlatex
        self.cut = cut

    def __str__(self):
        return self.cut

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,self.cut)


    def latex(self):
        return self._latex if self._latex else self.name

    def tlatex(self):
        return self._tlatex if self._tlatex else self.name

    def getTLatex(self):
        return ROOT.TLatex(0.,0.,self.tlatex())

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
        return 'sample(\'%s\', \'%s\', %s)' % (self.weight, self.preselection, str(self.files) )

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

class TreeAnalyser:

    def __init__(self, sample, cuts ):
        self._worker = self._makeworker(sample)

    def __repr__(self):
        pass

    @staticmethod
    def _makeworker(sample):
        if not isinstance( sample, Sample):
            raise ValueError('sample must inherit from Sample')
        t = TreeWorker( sample.trees() )
        t.setselection( sample.preselection )
        t.setweight( sample.weight )
        return t

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
    
    print a._worker._friends

    del a
    




