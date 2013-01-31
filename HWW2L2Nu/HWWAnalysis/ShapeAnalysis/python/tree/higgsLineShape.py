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
            250  : 0.949871,
            300  : 0.950109,
            350  : 0.92256,
            400  : 0.863159,
            450  : 0.82215,
            500  : 0.79441,
            550  : 0.772816,
            600  : 0.756956,
            700  : 0.754791,
            800  : 0.775468,
            900  : 0.55175,
            1000 : 0.878601,
        },
        'qqH':  {
            250  : 0.954932,
            300  : 0.962449,
            350  : 0.957838,
            400  : 0.940355,
            450  : 0.948707,
            500  : 0.996891,
            550  : 1.05551,
            600  : 1.12096,
            700  : 1.28318,
            800  : 1.48592,
            900  : 1.13413,
            1000 : 2.0193,
        },
    }
    _interf = {
        'ggH':  {
            250  : 1.0,
            300  : 1.0,
            350  : 1.0,
            400  : 0.9979665200,
#            420  : 0.9973644000,
#            440  : 1.0163872112,
            450  : 1.0264436689,
#            460  : 1.0365001265,
#            480  : 1.0652680626,
            500  : 1.0932697009,
#            520  : 1.1217136719,
#            540  : 1.1457909461,
            550  : 1.1622655466,
#            560  : 1.1787401470,
#            580  : 1.2145965883,
            600  : 1.2697380560,
#            620  : 1.3130814036,
#            640  : 1.3592299637,
#            660  : 1.4082594910,
#            680  : 1.4603888461,
            700  : 1.5160605911,
#            720  : 1.5751212640,
#            740  : 1.6376827699,
#            760  : 1.7039012956,
#            780  : 1.7740012982,
            800  : 1.8482963461,
#            820  : 1.9258143934,
#            840  : 2.0067943194,
#            860  : 2.0921212543,
#            880  : 2.1819660879,
            900  : 2.2618724091,
            1000 : 2.3417787303,
        },
        'qqH':  {
            250  : 1.0, 
            300  : 1.0,
            350  : 1.0,
            400  : 1.0,
            450  : 1.0,
            500  : 1.0,
            550  : 1.0,
            600  : 1.0,
            700  : 1.0,
            800  : 1.0,
            900  : 1.0,
            1000 : 1.0,
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
        group.add_option('-m', '--mass',      dest='mass',    type='int', help='Higgs Mass to reweight to', default=0)
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
        width  = cl._widths[self._mass]
        scale  = cl._scales[self._process][self._mass] if self._scale else 1.
        interf = cl._interf[self._process][self._mass] if self._interf else 1.

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

            weight.value = w.value*scale*interf

            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'


