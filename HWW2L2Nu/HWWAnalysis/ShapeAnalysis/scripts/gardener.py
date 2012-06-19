#!/bin/env python

import optparse
import sys
import ROOT
import numpy
import re
import warnings
import os.path
import math

# for trigger efficiency fits
from HWWAnalysis.ShapeAnalysis.triggerEffCombiner import TriggerEff


def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.
    
    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.
    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True
    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

class wwcuts:
    wwcommon = [
        'trigger==1.',
        'pfmet>20.',
        'mll>12',                       # ema7
        '(zveto==1||!sameflav)',
        'mpmet>20.',                    # ema9
        'bveto_mu==1',
        'nextra==0',
        '(bveto_ip==1 && (nbjettche==0 || njet>3)  )',
        'ptll>45.',                     # ema 14
    ]

    #dy cuts
    dylo   = '(njet==0 || njet==1 || (dphilljetjet<pi/180.*165. || !sameflav )  )'
    dyhi   = '((njet<=1 && dphiveto) || (njet>1 && dphilljetjet<pi/180.*165.) || !sameflav )'

    # met cuts lo: <=140 GeV, hi > 140 GeV
    metlo  = '( !sameflav || ( (njet!=0 || dymva1>0.60) && (njet!=1 || dymva1>0.30) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) )'
    methi  = ''+'( !sameflav || ( (njet!=0 || mpmet>45.0) && (njet!=1 || mpmet>45.0) && ( njet==0 || njet==1 || (pfmet > 45.0)) ) )'

    wwlo    = wwcommon+[dylo,metlo]
    wwhi    = wwcommon+[dyhi,methi]

    zerojet = 'njet == 0'
    onejet  = 'njet == 1'
    vbf     = '(njet >= 2 && njet <= 3 && (jetpt3 <= 30 || !(jetpt3 > 30 && (  (jeteta1-jeteta3 > 0 && jeteta2-jeteta3 < 0) || (jeteta2-jeteta3 > 0 && jeteta1-jeteta3 < 0))))) '


#   _______                 
#  / ___/ /__  ___  ___ ____
# / /__/ / _ \/ _ \/ -_) __/
# \___/_/\___/_//_/\__/_/   
#                           

class TreeCloner(object):
    def __init__(self):
        self.ifile = None
        self.itree = None
        self.ofile = None
        self.otree = None
    
    def _openRootFile(self,path, option=''):
        f =  ROOT.TFile.Open(path,option)
        if not f.__nonzero__() or not f.IsOpen():
            raise NameError('File '+path+' not open')
        return f

    def _getRootObj(self,d,name):
        o = d.Get(name)
        if not o.__nonzero__():
            raise NameError('Object '+name+' doesn\'t exist in '+d.GetName())
        return o

    def connect(self, tree, input):
        self.ifile = self._openRootFile(input)
        self.itree = self._getRootObj(self.ifile,tree)

    def clone(self,output,branches=[]):

        self.ofile = self._openRootFile(output, 'recreate')

        for b in self.itree.GetListOfBranches():
            if b.GetName() not in branches: continue
            b.SetStatus(0)

        self.otree = self.itree.CloneTree(0)

        ## BUT keep all branches "active" in the old tree
        self.itree.SetBranchStatus('*'  ,1)


    def disconnect(self):
        self.otree.Write()
        self.ofile.Close()
        self.ifile.Close()

        self.ifile = None
        self.itree = None
        self.ofile = None
        self.otree = None


#    ___                       
#   / _ \______ _____  ___ ____
#  / ___/ __/ // / _ \/ -_) __/
# /_/  /_/  \_,_/_//_/\__/_/   
#                              

class Pruner(TreeCloner):
    def __init__(self):
        self.filter = ''

    def help(self):
        print "Skim the tree according to the cut string"

    def addOptions(self,parser):
        parser.add_option('-f','--filter',dest='filter')

    def checkOptions(self, opts ):
        if not opts.filter:
            raise ValueError('No filter defined?!?')

        self.filter = getattr(opts,'filter')

    def process(self, **kwargs ):
        print 'Filtering \''+self.filter+'\''

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)

        print 'Initial entries:',self.itree.GetEntries()
        evlist = ROOT.TEventList('prunerlist')
        self.itree.Draw('>>prunerlist',self.filter)
        print 'Filtered Entries',evlist.GetN()

        ofile = ROOT.TFile.Open(output,'recreate')

        self.clone(output)

        itree = self.itree
        otree = self.otree
        step = 5000
        for i in xrange(evlist.GetN()):
            if i > 0 and i%step == 0:
                print i,' events processed.'

            itree.GetEntry(evlist.GetEntry(i))

            otree.Fill()

        self.disconnect()

#   _      ___      _____                       
#  | | /| / / | /| / / _ \______ _____  ___ ____
#  | |/ |/ /| |/ |/ / ___/ __/ // / _ \/ -_) __/
#  |__/|__/ |__/|__/_/  /_/  \_,_/_//_/\__/_/   
#                                               
class WWPruner(Pruner):
    levels = ['wwcommon','wwlo','wwhi']

    def help(self):
        print 'Skim with one predefined ww-selection lever'

    def addOptions(self,parser):
        parser.add_option('-f','--filter',dest='filter',help='Selection level. Can be '+str(self.levels))

    def checkOptions(self,opts):
        if not opts.filter:
            raise ValueError('No filter defined?!?')

        class options: pass
        wwopt = options()


        if opts.filter not in self.levels:
            raise NameError('Filter '+opt.filter+' not valid. Can be '+str(self.levels)+'.')

        wwopt.filter = ' && '.join(getattr(wwcuts,opts.filter))
#         if opts.filter in 

        super(WWPruner,self).checkOptions(wwopt)

    


#    ___                    __   _____         _____         
#   / _ )_______ ____  ____/ /  / ___/______ _/ _/ /____ ____
#  / _  / __/ _ `/ _ \/ __/ _ \/ (_ / __/ _ `/ _/ __/ -_) __/
# /____/_/  \_,_/_//_/\__/_//_/\___/_/  \_,_/_/ \__/\__/_/   
#                                                            
class Grafter(TreeCloner):
    '''Adds or replace variables to the tree'''

    def __init__(self):
        self.variables = {}
        self.regex = re.compile("([a-zA-Z0-9]*)/([FID])=(.*)")

    def help(self):
        print "Add or replace variables in the tree"

    def addOptions(self,parser):
        parser.add_option('-v','--var',dest='variables',action='append',default=[])

    def checkOptions(self,opts):
        if not opts.variables:
            raise ValueError('No variables defined?!?')

        for s in opts.variables:
            r = self.regex.match(s)
            if not r:
                raise RuntimeError('Malformed option '+s)
            name=r.group(1)
            type=r.group(2)
            formula=r.group(3)
            if type=='F':
                numtype = numpy.float32
            elif type=='D':
                numtype = numpy.float64
            elif type=='I':
                numtype = numpy.int32
            else:
                RuntimeError('Type '+type+' not supported')

            value=numpy.zeros(1, dtype = numtype)
            
            self.variables[name] = (value, type, formula)

    def process(self,**kwargs):

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)

        vars = [ ( value, type, ROOT.TTreeFormula(name,formula, self.itree)) for name, (value, type, formula) in self.variables.iteritems() ]


        print 'Adding/replacing the following branches'
        template=' {0:10} | {1:^3} | "{2}"'
        for name  in sorted(self.variables):
            (value, type, formula) = self.variables[name]
            print template.format(name,type,formula)
        print


        oldbranches = [ b.GetName() for b in self.itree.GetListOfBranches() ]
        hasMutation = False
        for bname in self.variables:
            # not there, continue
            if bname not in oldbranches: continue
            # found, check for consistency
            branch = self.itree.GetBranch(bname)
            btype = self.variables[bname][1]
            newtitle = bname+'/'+btype
            if ( branch.GetTitle() != newtitle ):
                print 'WARNING: Branch mutation detected: from',branch.GetTitle(),'to',newtitle
                hasMutation = True

        if hasMutation:
            confirm('Mutation detected. Do you _really_ want to continue?') or sys.exit(0)

        self.clone(output,self.variables.keys())

        for (val,type,formula) in vars:
            name = formula.GetName()
            title = name+'/'+type
            self.otree.Branch(name,val,title)

        nentries = self.itree.GetEntries()
        print 'Entries:',nentries

        # avoid dots in the loop
        itree = self.itree
        otree = self.otree

        step = 5000
        for i in xrange(0,nentries):
            itree.GetEntry(i)

            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for (val,type,formula) in vars:
                    val[0] = formula.EvalInstance()

            otree.Fill()
        
        self.disconnect()

#   _      ___      ________              _____         _____         
#  | | /| / / | /| / / __/ /__ ____ ____ / ___/______ _/ _/ /____ ____
#  | |/ |/ /| |/ |/ / _// / _ `/ _ `(_-</ (_ / __/ _ `/ _/ __/ -_) __/
#  |__/|__/ |__/|__/_/ /_/\_,_/\_, /___/\___/_/  \_,_/_/ \__/\__/_/   
#                             /___/                                   

class WWFlagsGrafter(Grafter):

    def help(self):
        print 'Add the flags at ww, ww+0j,ww+1j, ww+2j levels, hi and lo mass'

    def addOptions(self,parser):
        pass

    def checkOptions(self, opts):
        # create the options in 'adder style'
        class options: pass

        wwopt = options()

        wwopt.variables = [
            'wwsel/I='     +' && '.join(wwcuts.wwlo),
            'wwsel0j/I='   +' && '.join(wwcuts.wwlo+[wwcuts.zerojet]),
            'wwsel1j/I='   +' && '.join(wwcuts.wwlo+[wwcuts.onejet]),
            'wwsel2j/I='   +' && '.join(wwcuts.wwlo+[wwcuts.vbf]),

            'wwsel_hi/I='  +' && '.join(wwcuts.wwhi),
            'wwsel0j_hi/I='+' && '.join(wwcuts.wwhi+[wwcuts.zerojet]),
            'wwsel1j_hi/I='+' && '.join(wwcuts.wwhi+[wwcuts.onejet]),
            'wwsel2j_hi/I='+' && '.join(wwcuts.wwhi+[wwcuts.vbf]),
        ]


        super(WWFlagsGrafter,self).checkOptions(wwopt)
        

#    ___  __  __                 
#   / _ \/ / / /__  ___  ___ ____
#  / ___/ /_/ / _ \/ _ \/ -_) __/
# /_/   \____/ .__/ .__/\__/_/   
#           /_/  /_/             
class PUpper(TreeCloner):
    # ----
    def __init__(self):
        pass

    # ----
    def __del__(self):
        for f in ['datafile','mcfile']:
            if hasattr(self,f):
                getattr(self,f).Close()

    # ----
    def help(self):
        pass

    # ----
    def addOptions(self,parser):
        parser.add_option('-d', '--data'    , dest='datafile', help='Name of the input root file with pu histogram from data',)
        parser.add_option('-m', '--mc'      , dest='mcfile'  , help='Name of the input root file with pu histogram from mc',)
        parser.add_option('-H', '--HistName', dest='histname', help='Histogram name', default='pileup')
        parser.add_option('-k', '--kind'    , dest='kind'    , help='kind of PU reweighting: trpu (= true pu), itpu (= in time pu, that is observed!)',)
        parser.add_option('-n', '--name'    , dest='branch'  , help='Name of the branch of PU weight', default='puW')

    # ----
    def checkOptions(self,opts):
        if not (hasattr(opts,'datafile') and 
                hasattr(opts,'mcfile') and
                hasattr(opts,'kind') ):
            raise RuntimeError('Missing parameter')

        self.kind     = opts.kind
        self.branch   = opts.branch

        self.datafile   = self._openRootFile(opt.datafile)
        self.datadist   = self._getRootObj(self.datafile,opts.histname)
        self.mcfile     = self._openRootFile(opt.mcfile)
        self.mcdist     = self._getRootObj(self.mcfile, opts.histname)

    # ----
    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        self.clone(output,[self.branch])

        weight = numpy.ones(1, dtype=numpy.float32)
        self.otree.Branch(self.branch,weight,self.branch+'/F')


        data_nBin     = self.datadist.GetNbinsX()
        data_minValue = self.datadist.GetXaxis().GetXmin()
        data_maxValue = self.datadist.GetXaxis().GetXmax()
        data_dValue   = (data_maxValue - data_minValue) / data_nBin

        mc_nBin       = self.mcdist.GetNbinsX()
        mc_minValue   = self.mcdist.GetXaxis().GetXmin()
        mc_maxValue   = self.mcdist.GetXaxis().GetXmax()
        mc_dValue     = (mc_maxValue - mc_minValue) / mc_nBin
  
        ratio    = mc_dValue/data_dValue
        nBin     = data_nBin
#         minValue = data_minValue
#         maxValue = data_maxValue
        dValue   = data_dValue
 
        print "Data/MC bin Ratio:",ratio
 
        if (ratio - int(ratio)) != 0 :
            raise RuntimeError(" ERROR: incompatible intervals!")
 
        puScaleDATA   = numpy.ones(nBin, dtype=numpy.float32)
        puScaleMCtemp = numpy.ones(nBin, dtype=numpy.float32)
        puScaleMC     = numpy.ones(nBin, dtype=numpy.float32)

        for iBin in xrange(0, nBin):
            puScaleDATA[iBin] = self.datadist.GetBinContent(iBin+1)
            mcbin = int(math.floor(iBin / ratio))
            puScaleMCtemp[iBin] = self.mcdist.GetBinContent(mcbin+1)

 
        integralDATA = 0.
        integralMC   = 0.
 
        for iBin in range(0, nBin):
            integralDATA += puScaleDATA[iBin]
            integralMC   += puScaleMCtemp[iBin]

        print "Integrals: data = %.3f, mc = %3f" % (integralDATA,integralMC)
 
        for iBin in xrange(nBin):
            puScaleMC[iBin] =  puScaleMCtemp[iBin] * integralDATA / integralMC
 
        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries
        
        # this is for speed
        leaf = self.kind 
        itree = self.itree
        otree = self.otree
        
        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            weight[0] = 1.

            ## true pu reweighting 
            ibin = int(getattr(itree,leaf) / dValue)
            if ibin >= len(puScaleDATA) : ibin = len(puScaleDATA)-1

            if puScaleMC[ibin] != 0 :
                weight[0] = 1. * puScaleDATA[ibin] / puScaleMC[ibin]
            else:
                weight[0] = 1.

            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'


#    ____________            _____ ____       
#   / __/ _/ _/ /  ___ ___  / __(_) / /__ ____
#  / _// _/ _/ /__/ -_) _ \/ _// / / / -_) __/
# /___/_//_//____/\__/ .__/_/ /_/_/_/\__/_/   
#                   /_/                       
class EffLepFiller(TreeCloner):

    def __init__(self):
        pass

    def __del__(self):
        for f in ['elfile','mufile']:
            if hasattr(self,f):
                getattr(self,f).Close()

#     @staticmethod
    def _getBoundaries(self,h2):
        xlo = h2.GetXaxis().GetXmin()
        xhi = h2.GetXaxis().GetXmax()

        ylo = h2.GetYaxis().GetXmin()
        yhi = h2.GetYaxis().GetXmax()

        return (xlo,xhi,ylo,yhi,h2)

#     @staticmethod
    def _getWeight(self,eta,pt,bounds):

        eta_lo, eta_hi, pt_lo, pt_hi, hW = bounds
        
        eta = abs(eta) if abs(eta) < eta_hi else eta_hi-0.01
        pt = pt if pt < pt_hi else pt_hi-0.01
        pt = pt if pt > pt_lo else pt_lo+0.01

        effW = hW.GetBinContent(hW.FindBin(eta,pt))
        return effW

    def help(self):
        pass

    def addOptions(self,parser):
        parser.add_option('-e', '--elfile', dest='elfile', help='Name of the input root file with electron efficiencies',)
        parser.add_option('-m', '--mufile', dest='mufile', help='Name of the input root file with muon efficiencies',)
        parser.add_option('-E', '--elname', dest='elname', help='Electon\'s histogram name', default='newhwwWP_ratio')
        parser.add_option('-M', '--muname', dest='muname', help='Muon\'s histogram name', default='muonDATAMCratio')
        parser.add_option('-n', '--name',   dest='branch', help='Name of the lepton efficiency weight branch', default='effW')

    def checkOptions(self,opts):
        if not (hasattr(opts,'elfile') and 
                hasattr(opts,'mufile') ):
            raise RuntimeError('Missing parameter')

        self.elfile = self._openRootFile(opt.elfile)
        elhist = self._getRootObj(self.elfile,opts.elname)
        self.mufile = self._openRootFile(opt.mufile)
        muhist = self._getRootObj(self.mufile, opts.muname)

        self.branch = opts.branch

        self.elBounds = self._getBoundaries(elhist)
        self.muBounds = self._getBoundaries(muhist)

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        self.clone(output,[self.branch]) 

        weight = numpy.ones(1, dtype=numpy.float32)
        w1 = numpy.ones(1, dtype=numpy.float32)
        w2 = numpy.ones(1, dtype=numpy.float32)
        self.otree.Branch(self.branch,weight,self.branch+'/F')
        self.otree.Branch('w1',w1,'w1/F')
        self.otree.Branch('w2',w2,'w2/F')
        

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 
                
        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree
        elBounds  = self.elBounds
        muBounds  = self.muBounds
        getWeight = self._getWeight
        
        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            channel = itree.channel
            eta1 = itree.eta1
            pt1  = itree.pt1
            eta2 = itree.eta2
            pt2  = itree.pt2

            if channel == 0:
                b1 = muBounds
                b2 = muBounds
            elif channel == 1:
                b1 = elBounds
                b2 = elBounds
            elif channel == 2:
                b1 = elBounds
                b2 = muBounds
            elif channel == 3:
                b1 = muBounds
                b2 = elBounds
            else:
                raise ValueError('channel=={0} What is that?!?!'.format(channel))

            w1[0] = getWeight(eta1,pt1,b1)
            w2[0] = getWeight(eta2,pt2,b2)

            w1[0] = w1[0] if w1[0] >= 0.5 else 1.
            w2[0] = w2[0] if w2[0] >= 0.5 else 1.

            weight[0] = w1[0]*w2[0]
            
            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'

#    ________________         _____ ____       
#   / __/ _/ _/_  __/______ _/ __(_) / /__ ____
#  / _// _/ _/ / / / __/ _ `/ _// / / / -_) __/
# /___/_//_/  /_/ /_/  \_, /_/ /_/_/_/\__/_/   
#                     /___/                    

class EffTrgFiller(TreeCloner):

    def __init__(self):
        pass

    def help(self):
        pass

    def addOptions(self,parser):
        parser.add_option('-f', '--fitfile', dest='fitfile', help='path to the file containing the fit results',)
        parser.add_option('-n', '--name',   dest='branch', help='Name of the trigger efficiency weight branch', default='triggW')

    def checkOptions(self,opts):
        if not (hasattr(opts,'fitfile')):
            raise RuntimeError('Missing parameter')

        self.trgEff = TriggerEff(getattr(opts,'fitfile'))
        self.trgEEeff = self.trgEff.getEEeff()
        self.trgMMeff = self.trgEff.getMMeff()
        self.trgEMeff = self.trgEff.getEMeff()
        
        self.branch = opts.branch

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        self.clone(output,[self.branch]) 

        trgweight = numpy.ones(1, dtype=numpy.float32)
        self.otree.Branch(self.branch,trgweight,self.branch+'/F')

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 
                
        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree
        trgEff    = self.trgEff
        trgEEeff  = self.trgEEeff
        trgMMeff  = self.trgMMeff
        trgEMeff  = self.trgEMeff
        
        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            channel = itree.channel

            if channel == 0:
                e = trgEff.getTriggerEfficiency(trgMMeff, itree)
            elif channel == 1:
                e = trgEff.getTriggerEfficiency(trgEEeff, itree)
            elif channel == 2 or channel == 3:
                e = trgEff.getTriggerEfficiency(trgEMeff, itree)
            else:
                raise ValueError('channel=={0} What is that?!?!'.format(channel))

            if e > 1:
                print 'channel=={%d}, triggW: {%f} > 1 !!!' % (channel,e)
                
            trgweight[0] = e
            
            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



#    __  ___     _    
#   /  |/  /__ _(_)__ 
#  / /|_/ / _ `/ / _ \
# /_/  /_/\_,_/_/_//_/
#                     

modules = {}
modules['filter']     = Pruner()
modules['wwfilter']   = WWPruner()
modules['adder']      = Grafter()
modules['wwflagger']  = WWFlagsGrafter()
modules['puadder']    = PUpper()
modules['effwfiller'] = EffLepFiller()
modules['efftfiller'] = EffTrgFiller()


if __name__ == '__main__':
    usage =  'Usage: %prog <command> <options> filein.root fileout.root\n'
    usage += '  Commands: '+', '.join(modules.keys()+['help'])

    parser = optparse.OptionParser(usage)
    parser.add_option('-t','--tree',        dest='tree',                            default='latino')
    parser.add_option('-r','--recursive',   dest='recursive',action='store_true',   default=False)
    parser.add_option('-F','--force',       dest='force',action='store_true',       default=False)

    # some boring argument handling
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    modname = sys.argv[1]
    if modname.startswith('-'):
        parser.print_help()
        sys.exit(0)

    if modname == 'help':
        if len(sys.argv) == 2:
            parser.print_help()
            sys.exit(0)
        
        module = sys.argv[2]
        if module not in modules:
            print 'Help: command',module,'not known'
            print 'The available commands are',', '.join(modules.keys())
            sys.exit(0)
        
        print 'Help for module',module+':'
        modules[module].help()
        modules[module].addOptions(parser)
        parser.print_help()
        sys.exit(0)


    if modname not in modules:
        print 'Command',modname,'unknown'
        print 'The available commands are',modules.keys()
        sys.exit(0)

    module = modules[modname]
    module.addOptions(parser)

    sys.argv.remove(modname)

    (opt, args) = parser.parse_args()

    print opt,args

    sys.argv.append('-b')

    module.checkOptions(opt)

    tree = opt.tree
    input = args[0]
    output = args[1]

    # recursiveness here
    if os.path.isdir(input):
        if not opt.recursive:
            print input,'is a directory. Use -r to go recursive'
            sys.exit(0)

        if os.path.exists(output) and not os.path.isdir(output):
            print output,'exists and is not a directory!'
            sys.exit(0)

#         output = output if output[-1]=='/' else output+'/'
        fileList = []
        for root, subFolders, files in os.walk(input):
            for file in files:
                if not file.endswith('.root'): continue
                fileList.append(os.path.join(root,file))

        print 'The directory tree',input,'will be gardened and copied to',output
        print 'The following files will be copied:'
        print '\n'.join(fileList)
        print 'for a grand total of',len(fileList),'files'
        opt.force or ( confirm('Do you want to continue?') or sys.exit(0) )

        nfiles=len(fileList)
        for i,file in enumerate(fileList):
            print '-'*80
            print 'Entry {0}/{1} | {2}'.format(i+1,nfiles,file)
            print '-'*80
            output = output if output[-1]=='/' else output+'/'
            newfile = file.replace(input,output)
            newdir  = os.path.dirname(newfile)
            if newdir and not os.path.exists(newdir):
                os.system('mkdir -p '+newdir)
#             print file,newfile

            inputfile = file
            outputfile = newfile
            print 'Input: ',inputfile
            print 'Output:',outputfile
            print '-'*80
        
            module.process( input=inputfile, output=outputfile, tree=tree )

    else:
        if os.path.exists(output) and os.path.isdir(output):
            output = os.path.join( output , os.path.basename(input) )
        module.process( input=input, output=output, tree=tree )


