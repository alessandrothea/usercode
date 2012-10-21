#!/usr/bin/env python

import optparse
import ROOT
import sys
import re
import os.path
import logging
import pdb
import fnmatch

import hwwinfo
import hwwtools
import datadriven
from HWWAnalysis.Misc.odict import OrderedDict
from systematicUncertainties import getCommonSysts,addFakeBackgroundSysts

# da http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/Mangano/WWAnalysis/AnalysisStep/python/systematicUncertainties.py


# class AutoVivification(dict):
#     """Implementation of perl's autovivification feature."""
#     def __getitem__(self, item):
#         try:
#             return dict.__getitem__(self, item)
#         except KeyError:
#             value = self[item] = type(self)()
#             return value

class ShapeDatacardWriter:
    _logger = logging.getLogger('ShapeDatacardWriter')

    '''Dump a crappy datacard to file'''
    
    def __init__(self, mass, bin, shape=True):
        self._mass = mass
        self._bin = bin
        self._shape = shape

    def __del__(self):
        pass

    def write(self, yields, nuisances, path, fileFmt, signals = ['ggH', 'vbfH', 'wzttH']):

        cardPath = path.format(mass = self._mass, bin = self._bin)
        print 'Writing to '+cardPath 
        card = open( cardPath ,"w")
        card.write('## Shape input card for H->WW analysis\n')
        
        card.write('imax 1 number of channels\n')
        card.write('jmax * number of background\n')
        card.write('kmax * number of nuisance parameters\n') 

        card.write('-'*100+'\n')
        card.write('bin         %s' % self._bin+'\n')
        if 'Data' not in yields:
            self._logger.warning( 'Yields: '+','.join(yields.keys()) )
            raise RuntimeError('No Data found!')
        card.write('observation %.0f\n' % yields['Data']._N)
        # replace the second * with the bin?

        if self._shape:
            card.write('shapes  *           * '+
                       fileFmt.format(mass=self._mass, bin=self._bin)+
                       '     histo_$PROCESS histo_$PROCESS_$SYSTEMATIC'+'\n')
            card.write('shapes  data_obs    * '+
                       fileFmt.format(mass=self._mass, bin=self._bin)+
                       '     histo_Data'+'\n')

        card.write('-'*100+'\n')
        
        bkgs = [ name for name in yields if name not in signals and name != 'Data']
        sigs = [ name for name in yields if name in signals ]
        keyline = []
        keyline.extend([ (-i,s,yields[s]._N) for i,s in enumerate(sigs) ])
        keyline.extend([ (i+1,b,yields[b]._N) for i,b in enumerate(bkgs) ])

        coldef = 10

        card.write('bin'.ljust(48)+''.join([self._bin.ljust(coldef)*len(keyline)])+'\n')
        card.write('process'.ljust(48)+''.join([n.ljust(coldef) for (i,n,N) in keyline])+'\n' )
        card.write('process'.ljust(48)+''.join([('%d' % i).ljust(coldef) for (i,n,N) in keyline])+'\n' )
        card.write('rate'.ljust(48)+''.join([('%-.3f' % N).ljust(coldef) for (i,n,N) in keyline])+'\n' )
        card.write('-'*100+'\n')

        for name in nuisances:
            (pdf,effect) = nuisances[name]
            if len(pdf) == 1: card.write('{0:<31} {1:<7}         '.format(name,pdf[0]))
            else:             card.write('{0:<31} {1:<7} {2:<7} '.format(name,pdf[0],pdf[1]))
            for i,p,y in keyline:
                if p in effect: 
                    if pdf[0]=='gmN':   card.write('%-10.5f' % effect[p])
                    elif (pdf[0]=='shape' or pdf[0]=='shapeN2'): card.write('%-10d' % effect[p])
                    else:               card.write('%-10.3f' % effect[p] )
                else: card.write('-'.ljust(coldef))
            card.write('\n')

        card.close()

class Yield:
    def __init__(self,*args,**kwargs):
        if not args:
            raise RuntimeError('Specify number of entries')
        self._N = args[0]
        if 'name' in kwargs:
            self._name = kwargs['name']
        if 'entries' in kwargs:
            self._entries = kwargs['entries']


class ShapeLoader:
    '''Load the histogram data from the shape file
    + Yields
    + Nuisance shapes and parameters'''
    _logger = logging.getLogger('ShapeLoader')

    def __init__(self, path):
        self._systRegex = re.compile('^histo_([^_]+)_(.+)(Up|Down)$')
        self._nomRegex  = re.compile('^histo_([^_]+)$')
        self._src = ROOT.TFile.Open(path)
        self._yields = OrderedDict()

    def __del__(self):
        del self._src

    def yields(self):
        return self._yields.copy()

    def effects(self):
        return self._effects.copy()

    def load(self):
        # load the histograms and calculate the yields
        names = [ k.GetName() for k in self._src.GetListOfKeys()]
        self._nominals = sorted([ name for name in names if self._nomRegex.match(name) ]) 
#         print self._nominals
        self._systematics = sorted([ name for name in names if self._systRegex.match(name) ])
#         print '\n'.join(self._nominals)
#         print '\n'.join(self._systematics)
        for name in self._nominals:
            process = self._nomRegex.match(name).group(1)
            h = self._src.Get(name)
            N =  h.Integral(0,h.GetNbinsX())
            entries = h.GetEntries()

            # TODO: DYTT cleanup
#             if entries < 5: continue

            self._yields[process] = Yield( N, name=process, entries=entries ) 
#             self._yields[process] = Yield( N, name=process, entries=entries, shape=h ) 
        
        ups = {}
        downs = {}
        for name in self._systematics:
            # check for Up/Down
            (process,effect,var) = self._systRegex.match(name).group(1,2,3)
            if var == 'Up': 
                if effect not in ups: ups[effect]= []
                ups[effect].append(process)
            elif var == 'Down':
                if effect not in downs: downs[effect]= []
                downs[effect].append(process)

        # check 
        for effect in ups:
            if set(ups[effect]) != set(downs[effect]):
                sUp = set(ups[effect])
                sDown = set(downs[effect])
                raise RuntimeError('Some systematics shapes for '+effect+' not found in up and down variation: \n '+', '.join( (sUp | sDown) - ( sUp & sDown ) ))
        
        # all checks out, save only one
        self._effects = ups

class NuisanceMapBuilder:
    _logger = logging.getLogger('NuisanceMapBuilder')

    def __init__(self, ddPath, noWWddAbove, shape=True):
        self._common       = OrderedDict()
        self._0jetOnly     = OrderedDict()
        self._1jetOnly     = OrderedDict()
        self._ddEstimates  = OrderedDict()
        self._shape        = shape
        # to options
        self.statShapeVeto = []

        # data driven reader and filter for the ww
        self._ddreader      = datadriven.DDCardReader(ddPath)
        self._wwddfilter    = datadriven.DDWWFilter(self._ddreader, noWWddAbove)

        self._build()
 
    def _build(self):
        # common 0/1 jet systematics
        #pureMC = [ 'Vg', 'VV', 'DYTT', 'ggH', 'vbfH', 'wzttH'] 
        pureMC = [ 'Vg', 'VV', 'ggH', 'vbfH', 'wzttH'] 
        dummy = {}
        dummy['CMS_fake_e']    = (1.50, ['WJet']) # take the average of ee/me 
#         dummy['CMS_fake_m']    = (1.42, ['WJet']) # take the average of mm/em
        dummy['CMS_eff_l']     = (1.04, pureMC)
        dummy['CMS_p_scale_e'] = (1.02, pureMC)
#         dummy['CMS_p_scale_m'] = (1.01, pureMC)
        dummy['CMS_p_scale_j'] = (1.02, pureMC)
        dummy['CMS_met']       = (1.02, pureMC)
        dummy['lumi']          = (1.04, pureMC)

        for k,v in dummy.iteritems():
            self._common[k] = (['lnN'], dict([( process, v[0]) for process in v[1] ]) )

        self._common['pdf_gg']    = (['lnN'],dict([('ggWW',1.04),('ggH',1.08)]) )
        self._common['pdf_qqbar'] = (['lnN'],dict([('WW',1.04),('VV',1.04),('vbfH',1.02)]) )
        self._common['pdf_assoc'] = (['lnN'],dict([('WW',1.04)]) )

        dummy = {} 
        # both 0/1 jets but different
        dummy['CMS_QCDscale_WW_EXTRAP'] = ([0.95, 1.21], ['WW'])
        dummy['QCDscale_VV']            = ([1.03, 1.03], ['VV'])
        dummy['QCDscale_ggH1in']        = ([0.89, 1.39], ['ggH'])
        dummy['QCDscale_ggH_ACEPT']     = ([1.02, 1.02], ['ggH'])
        dummy['QCDscale_ggVV']          = ([1.30, 1.30], ['ggWW'])
        dummy['QCDscale_qqH']           = ([1.01, 1.01], ['vbfH'])
        dummy['QCDscale_qqH_ACEPT']     = ([1.02, 1.02], ['vbfH'])
        dummy['QCDscale_wzttH_ACEPT']   = ([1.02, 1.02], ['wzttH'])
        dummy['QCDscale_wzttH']         = ([1.01, 1.01], ['wzttH'])
        dummy['UEPS']                   = ([0.94, 1.11], ['ggH'])

        for k,v in dummy.iteritems():
            self._0jetOnly[k] = (['lnN'], dict([( process, v[0][0]) for process in v[1] ]) )
            self._1jetOnly[k] = (['lnN'], dict([( process, v[0][1]) for process in v[1] ]) )

        # 0 jets only
        dummy = {}
        
        dummy['CMS_fake_Vg']  = (2.00,['Vg']) # Vg, 0jet 
        dummy['QCDscale_Vg']  = (1.50,['Vg']) 
        dummy['QCDscale_ggH'] = (1.16,['ggH']) # 0 jets only
        for k,v in dummy.iteritems():
            self._0jetOnly[k] = (['lnN'], dict([( process, v[0]) for process in v[1] ]) )

        # 1 jet only
        dummy = {}
        dummy['QCDscale_ggH2in'] = (0.95,['ggH']) # 1 jey only
        for k,v in dummy.iteritems():
            self._1jetOnly[k] = (['lnN'], dict([( process, v[0]) for process in v[1] ]) )

    
    def _addDataDrivenNuisances(self, nuisances, yields, mass, channel, jetcat):
        
        if self._ddreader.iszombie: return
        (estimates,dummy) = self._wwddfilter.get(mass, channel)

        pdf = 'lnN'

        # this mapping specifies the context of the systematics (i.e. jet category, channel) and how the dds must be combined between channels.
        mapping = {
            'WW'   : ( jetcat,  ['WW','ggWW'] ),
            'Top'  : ( jetcat,  ['Top']       ),
            'DYLL' : ( jetcat,  ['DYLL']      ),
            'DYee' : ( channel, ['DYee']      ),
            'DYmm' : ( channel, ['DYmm']      ),
        }

        eff_bin1_tmpl = 'CMS_hww_{0}_{1}_stat_bin1'
        for tag,(context, processes) in mapping.iteritems(): 
            extr_uncorr_entries = {}
            extr_corr_entries = {}
            extr_entries = {}
            stat_entries = {}

            if (tag=="WW" and (jetcat=="0j" or jetcat=="1j")) :
                eff_extr    = 'CMS_hww_{0}_extr'.format(tag)
            else :
                eff_extr    = 'CMS_hww_{0}_{1}_extr'.format(tag,context)
            eff_stat        = 'CMS_hww_{0}_{1}_stat'.format(tag,context)
            eff_extr_corr   = 'CMS_hww_{0}_{1}_extr_corr'.format(tag,context)
            eff_extr_uncorr = 'CMS_hww_{0}_{1}_extr_uncorr'.format(tag,channel)

            available = [ p for p in processes if p in estimates ]
            if not available: continue

            # check the dd to have the same events in the ctr region before associating them
            listNctr = [ estimates[p].Nctr for p in available ]
            
            if len(available) != listNctr.count(estimates[available[0]].Nctr):
                raise RuntimeError('Mismatch between Nctr in the same systematic: '+', '.join([ '{0}{1}'.format(n[0],n[1]) for n in zip(available, listNctr) ]) )

            flagdoextracorr = 0
            flagdoextrauncorr = 0

            for process in available:
                e = estimates[process]
                extrUnc = 1+e.delta/e.alpha if pdf != 'gmM' else e.delta/e.alpha

                if e.deltaUnCorr != 0:
                    extr_uncorr_entries[process] = 1. + e.deltaUnCorr/e.alpha
                if e.deltaCorr != 0: 
                    extr_corr_entries[process] = 1. + e.deltaCorr/e.alpha
#                 if jetcat == '2j' and tag == 'Top' :
#                      if e.deltaCorr != 0: 
#                          extr_corr_entries[process] = 1. + e.deltaCorr/e.alpha
#                          flagdoextracorr = 1
                extr_entries[process] = extrUnc
                stat_entries[process] = e.alpha
                eff_bin1 = eff_bin1_tmpl.format(process,channel)
                if eff_bin1 in nuisances:
                    del nuisances[eff_bin1]


            nuisances[eff_extr] = ([pdf], extr_entries )
            nuisances[eff_stat] = (['gmN',e.Nctr], stat_entries)

#             if jetcat == '2j' and tag == 'Top' :
#                 if flagdoextracorr == 1 :
#                     nuisances[eff_extr_corr] = ([pdf], extr_corr_entries )

            if len(extr_corr_entries) > 0:
                nuisances[eff_extr_corr] = ([pdf], extr_corr_entries )
                
            if len(extr_uncorr_entries) > 0:
                nuisances[eff_extr_uncorr] = ([pdf], extr_uncorr_entries )





    def _addStatisticalNuisances(self,nuisances, yields,channel):
        for p,y in yields.iteritems():
            if p == 'Data':
                continue
            name  = 'CMS_hww_{0}_{1}_stat_bin1'.format(p,channel)
            if y._entries == 0.:
                continue
            value = 1+(1./ROOT.TMath.Sqrt(y._entries) if y._entries > 0 else 0.)
            nuisances[name] = ( ['lnN'], dict({p:value}) )

    def _addWWShapeNuisances(self,nuisances, effects):
        '''Generator relates shape nuisances'''
        wwRegex  = re.compile('Gen_(.+)$')
        for eff,processes in effects.iteritems():
            # select the experimental effects only (starting with gen)
            if not wwRegex.match(eff):
                continue
            tag = eff
            if tag in nuisances: del nuisances[tag]
            nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in processes]) )


    def _addExperimentalShapeNuisances(self, nuisances, effects):
        '''Experimental Shape-based nuisances'''
        # expr for CMS nuisances
        expRegex  = re.compile('CMS_(.+)')
        # expr for statistical nuisances
        statRegex = re.compile('CMS_hww_([^_]+)_.+_stat_shape')

#         mask = ['Vg','DYLL','DYTT']#'WJet',]#'Vg','DYLL','DYTT',]#]#,'Top',]#'WW','ggWW','VV',]#'ggH','vbfH']
        for eff in sorted(effects):
            # select the experimental effects only (starting with CMS)
            if not expRegex.match(eff):
                continue

            m = statRegex.match(eff)
#             if m:
#                 print m.group(1), self.statShapeVeto
            if m and m.group(1) in self.statShapeVeto:
                self._logger.info( 'Skipping %s (vetoed, data driven)', eff )
                continue
            tag = eff
            if tag in nuisances: del nuisances[tag]
            nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in effects[eff] ]) )

    def _addShapeNuisances(self, nuisances, effects, opts):
        # local copy
        shapeNu = OrderedDict()

        self._addWWShapeNuisances(shapeNu, effects)
        self._addExperimentalShapeNuisances(shapeNu, effects)

        if 'shapeFlags' not in opts:
            sys.exit(-1)
        flags = opts['shapeFlags']

        nus = set(shapeNu.keys())
        dummy = nus.copy()
        for exp,flag in flags:
            subset = set(fnmatch.filter(nus,exp))
            if flag:
                dummy |= subset
            else:
                dummy -= subset

        for eff in shapeNu:
            if eff not in dummy: continue
            if eff in nuisances: del nuisances[eff]
            nuisances[eff] = shapeNu[eff]

    #  _  _      _                          
    # | \| |_  _(_)___ __ _ _ _  __ ___ ___
    # | .` | || | (_-</ _` | ' \/ _/ -_|_-<
    # |_|\_|\_,_|_/__/\__,_|_||_\__\___/__/
    #                                      
    def nuisances(self, yields, effects, mass, channel, jetcat, flavor, opts):
        '''Add the nuisances according to the options'''
        allNus = OrderedDict()

        optMatt = mattOpts()
        optMatt.WJadd = 0.36
        optMatt.WJsub = 0.0

        qqWWfromData = self._wwddfilter.haswwdd(mass, channel)

        if jetcat not in ['0j','1j','2j']: raise ValueError('Unsupported jet category found: %s')
        CutBased = getCommonSysts(int(mass),flavor,int(jetcat[0]),qqWWfromData, optMatt)
        common = OrderedDict()
        for k in sorted(CutBased):
            common[k] = CutBased[k]
        allNus.update( common )

        self._addStatisticalNuisances(allNus, yields, channel)
        self._addDataDrivenNuisances(allNus, yields, mass, channel, jetcat)

        if self._shape: self._addShapeNuisances(allNus,effects, opts)

        if 'nuisFlags' not in opts:
            raise RuntimeError('nuisFlags not found among the allNus options')

        flags = opts['nuisFlags']

        finalNuisances = OrderedDict()
        nus = set(allNus.keys())
        dummy = nus.copy()
        for exp,flag in flags:
            subset = set(fnmatch.filter(nus,exp))
            if flag:
                dummy |= subset
            else:
                dummy -= subset

        nuisances = OrderedDict()
        for eff in allNus:
            if eff not in dummy: continue
            nuisances[eff] = allNus[eff]

        return nuisances

def incexc(option, opt_str, value, parser):
    if not hasattr(parser.values,'shapeFlags'):
        setattr(parser.values,'shapeFlags',[])

    optarray = str(option).split('/')
    print optarray
    if '--Ish' in optarray:
        parser.values.shapeFlags.append((value,True))
    elif '--Xsh' in optarray:
        parser.values.shapeFlags.append((value,False))
    elif '-I' in optarray:
        parser.values.nuisFlags.append((value,True))
    elif '-X' in optarray:
        parser.values.nuisFlags.append((value,False))
    
class mattOpts: pass

if __name__ == '__main__':
    print '''
.------..------..------.       .------..------..------.       .------..------..------.
|B.--. ||E.--. ||T.--. | .-.   |T.--. ||H.--. ||E.--. | .-.   |P.--. ||O.--. ||T.--. |
| :(): || (\/) || :/\: |((5))  | :/\: || :/\: || (\/) |((5))  | :/\: || :/\: || :/\: |
| ()() || :\/: || (__) | '-.-. | (__) || (__) || :\/: | '-.-. | (__) || :\/: || (__) |
| '--'B|| '--'E|| '--'T|  ((1))| '--'T|| '--'H|| '--'E|  ((1))| '--'P|| '--'O|| '--'T|
`------'`------'`------'   '-' `------'`------'`------'   '-' `------'`------'`------'
'''

    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-p', '--prefix'  , dest='prefix'      , help='Datacard directory prefix'           , default=None)
    parser.add_option('--cutbased'      , dest='shape'       , help='Make cutbased datacards (no shapes)' , default=True , action='store_false' )
    parser.add_option('--no_wwdd_above' , dest='noWWddAbove' , help='No WW dd above this mass'            , default=None   , type='int'     )
    parser.set_defaults(shapeFlags=[])
    parser.set_defaults(nuisFlags=[])
    parser.add_option('--Xsh','--excludeShape', dest='shapeFlags'        , help='exclude shapes nuisances matching the expression', action='callback', type='string', callback=incexc)
    parser.add_option('--Ish','--includeShape', dest='shapeFlags'        , help='include shapes nuisances matching the expression', action='callback', type='string', callback=incexc)
    parser.add_option('-X','--exclude',         dest='shapeFlags'        , help='exclude nuisances matching the expression',        action='callback', type='string', callback=incexc)
    parser.add_option('-I','--include',         dest='shapeFlags'        , help='include nuisances matching the expression',        action='callback', type='string', callback=incexc)
    parser.add_option('--path_dd'           ,   dest='path_dd'           , help='Data driven path'                 , default=None)
    parser.add_option('--path_shape_merged' ,   dest='path_shape_merged' , help='Destination directory for merged' , default=None)
    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)

    (opt, args) = parser.parse_args()
    print 'ShapeFlags: ',opt.shapeFlags
    print 'NuisFlags:  ',opt.nuisFlags
    print 'noWWddAbove:',opt.noWWddAbove


    # checks
    if not opt.variable or not opt.lumi:
        parser.error('The variable and the luminosty must be defined')
    var = opt.variable

    if not opt.debug:
        pass
    elif opt.debug > 0:
        logging.basicConfig(level=logging.DEBUG)

    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()

    masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]
    channels =  dict([ (k,v) for k,v in hwwinfo.channels.iteritems() if k in opt.chans])

    print channels

    mergedPath = opt.path_shape_merged
    outPath    = 'datacards/'
    if opt.prefix:
        if opt.prefix[0] == '/':
            raise NameError('prefix: Only subdirectories are supported')
        outPath = (opt.prefix if opt.prefix[-1] == '/' else opt.prefix+'/')+outPath
    shapeSubDir = 'shapes/'

    shapeDir = os.path.join(outPath,shapeSubDir[:-1])

    os.system('mkdir -p '+outPath)
    if os.path.exists(shapeDir):
        os.unlink(shapeDir)
    os.symlink(os.path.abspath(mergedPath), shapeDir)

    optsNuis = {}
    optsNuis['shapeFlags'] = opt.shapeFlags
    optsNuis['nuisFlags'] = opt.nuisFlags
    lumistr = '{0:.2f}'.format(opt.lumi)
    shapeTmpl = os.path.join(mergedPath,'hww-'+lumistr+'fb.mH{mass}.{channel}_shape.root')
    #mask = ['Vg','DYLL','DYTT']
    mask = ['Vg','DYLL']

    builder = NuisanceMapBuilder( opt.path_dd, opt.noWWddAbove, opt.shape )
    builder.statShapeVeto = mask
    for mass in masses:
        for ch,(jcat,fl) in channels.iteritems():

#         for jets in jetBins:
#             for flavor in flavors:
            print '- Processing',mass, ch
            loader = ShapeLoader(shapeTmpl.format(mass = mass, channel=ch) ) 
            loader.load()

            writer = ShapeDatacardWriter( mass, ch, opt.shape )
            print '   + loading yields'
            yields = loader.yields()

            # reshuffle the order
            #order = [ 'vbfH', 'ggH', 'wzttH', 'ggWW', 'Vg', 'WJet', 'Top', 'WW', 'DYLL', 'VV', 'DYTT', 'Data']
            order = [ 'vbfH', 'ggH', 'wzttH', 'ggWW', 'Vg', 'WJet', 'Top', 'WW', 'DYLL', 'VV', 'DYTT', 'DYee', 'DYmm', 'Data']
            oldYields = yields.copy()
            yields = OrderedDict([ (k,oldYields[k]) for k in order if k in oldYields])
            
            # lista systematiche sperimentali (dal file. root)
            effects = loader.effects()

            print '   + making nuisance map'
            nuisances = builder.nuisances( yields, effects , mass, ch, jcat, fl, optsNuis)

            #basename = 'hww-'+lumistr+'fb.mH{mass}.{bin}_shape'
            basename = 'hww-'+lumistr+'fb.mH{mass}.{bin}'
            if opt.shape :
                 basename  = basename + '_shape'
            print '   + dumping all to file'
            writer.write(yields,nuisances,outPath+basename+'.txt',shapeSubDir+basename+'.root')

