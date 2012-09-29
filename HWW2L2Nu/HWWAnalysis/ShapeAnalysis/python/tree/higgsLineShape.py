from tree.gardening import TreeCloner
import ctypes
import optparse
import os
import ROOT

from ctypes import c_int,c_double,c_float,cdll,byref

class HiggsLineshapeWeightAdder(TreeCloner):
    
    _topMass = 172.5
    _widths = {
        250  : 4.04e+00,
        300  : 8.43e+00,
        350  : 1.52e+01,
        400  : 2.92e+01,
        450  : 4.69e+01,
        500  : 6.80e+01,
        550  : 9.31e+01,
        600  : 1.23e+02,
        700  : 1.99E+02,
        800  : 3.04E+02,
        900  : 4.49E+02,
        1000 : 6.47E+02,
    }
    _scales = {
        'ggH':  {
            250  : 10.,
            300  : 10.,
            350  : 10.,
            400  : 10.,
            450  : 10.,
            500  : 10.,
            550  : 10.,
            600  : 10.,
            700  : 10.,
            800  : 10.,
            900  : 10.,
            1000 : 10.,
        },
        'qqH':  {
            250  : 10.,
            300  : 10.,
            350  : 10.,
            400  : 10.,
            450  : 10.,
            500  : 10.,
            550  : 10.,
            600  : 10.,
            700  : 10.,
            800  : 10.,
            900  : 10.,
            1000 : 10.,
        },
    }


    #---
    def __init__(self):
        self._mass = None

    #---
    def help(self):
        return 'Add the lineshape weight to higgs sample'

    #---
    def addOptions(self, parser):
        description=self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        group.add_option('-b', '--branch',    dest='branch',  help='Name of the higgs lineshape weight branch (default = %default)', default='kfW')
        group.add_option('-p', '--process',   dest='process', help='Scale factor to add to the weight (default = %default)', default='ggH')
        group.add_option('-m', '--mass',      dest='mass',    type='int', help='Higgs Mass to reweight to')
        group.add_option('-n', '--noscale',   dest='scale', action='store_false', help='don\'t apply sample specific scale factor', default=True)
        parser.add_option_group(group)
        return group

    #---
    def checkOptions(self,opts):
        if not hasattr(opts,'mass'):
            raise RuntimeError('Higgs Mass must be defined!')

        masses = sorted(HiggsLineshapeWeightAdder._widths.keys())
        if opts.mass not in masses:
            raise ValueError('Supported mass values are %s (found %d)' % (','.join([str(m) for m in masses]), opts.mass) )

        if opts.process not in ['ggH','qqH']:
            raise ValueError('Process mus be ggH or qqH (found %d)' % opts.process)

        self._mass    = opts.mass
        self._branch  = opts.branch
        self._process = opts.process
        self._scale   = opts.scale
        print opts.scale

    #---
    def process(self, **kwargs):

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        self.clone(output,[self._branch])


        weight = c_float(5.)
        self.otree.Branch(self._branch, weight, '%s/F' % self._branch )

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree

        lib = cdll.LoadLibrary('libMMozerpowhegweight.so')
        
        cl = self.__class__
        width = cl._widths[self._mass]
        scale = cl._scales[self._process][self._mass] if self._scale else 1.

        # prepare the vars to feed to the function
        mh = c_double(self._mass)
        gh = c_double(cl._widths[self._mass])
        mt = c_double(cl._topMass)
        BWflag = c_int(0)
        m  = c_double(0.)
        w  = c_double(0.)

        step = 5000
        for i in xrange(nentries):
            if i > 0 and i%step == 0:
                print i,' events processed.'

            itree.GetEntry(i)
#             m.value  = getattr(itree,'mll') 
            m.value  = getattr(itree,'MHiggs') 
            
            #   void pwhg_cphto_reweight_(double *mh, double *gh, double *mt, int *BWflag, double *m, double *w);
            lib.pwhg_cphto_reweight_(byref(mh),byref(gh),byref(mt),byref(BWflag),byref(m),byref(w))
#             print mh,gh,mt,BWflag,m,w

            weight.value = w.value*scale

            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'


