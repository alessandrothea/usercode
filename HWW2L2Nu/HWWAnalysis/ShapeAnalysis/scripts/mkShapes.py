#!/usr/bin/env python


import sys
import ROOT
import optparse
import hwwinfo
import hwwsamples
import hwwtools
import os.path
import string
import logging
from HWWAnalysis.Misc.odict import OrderedDict
# import traceback


class ShapeFactory:
    _logger = logging.getLogger('ShapeFactory')
 
    # _____________________________________________________________________________
    def __init__(self):
        self._baseWgt = 'baseW*puWobs*effW*triggW'

        ranges = {}
        ranges['bdtl']       = (400  , -1. , 1.)
        ranges['bdts']       = (400  , -1. , 1.)
        ranges['mth']        = (400  , 0.  , 200)
        ranges['dphill']     = (400  , 0.  , 3.15)
        ranges['detajj']     = (240  , 0.  , 6.)
        ranges['mll']        = self._getmllrange
        ranges['mllsplit']   = self._getmllsplitrange
        ranges['gammaMRStar'] = self._getGMstarrange
        self._ranges = ranges
        
        self._dataTag = '2012A'
        self._masses = []
        self._categories = []
        self._flavors = []
        self._channels = {}
        # paths (to move out)
        self._outFileFmt  = ''
        self._paths = {}
        self._range = None
        self._split = None

    # _____________________________________________________________________________
    def __del__(self):
        pass
    
    # _____________________________________________________________________________
    def getrange(self,var,mass,cat):
        

        theRange = self._ranges[var]
        if isinstance(theRange,tuple):
            return theRange
        elif isinstance(theRange,dict):
            return theRange[mass][cat]
        elif callable(theRange):
            return theRange(mass,cat)
            
    # _____________________________________________________________________________
    def _getmllrange(self,mass,cat):
        
        if cat not in ['0j','1j']:
            raise RuntimeError('mll range for '+str(cat)+' not defined. Can be 0 or 1')
        # TODO: cleanup

        # xmin
        xmin   = 0. if mass<300 else 0.2*mass-20      #;--> changed "(mH<300)" and "0.2*float(mH) - 20"
        # xmax
        if mass < 200.:
            xmax = 200.
        elif mass < 400.:
            xmax = mass
        else:
            xmax = mass-50.
        # bins
        if mass < 300.:
            bins = 400 if cat == '0j' else 200
        else:
            bins = 300 if cat == '0j' else 150
        return (bins,xmin,xmax)

    # _____________________________________________________________________________
    def _getmllsplitrange(self,mass,cat):
        if cat not in ['0j','1j']:
            raise RuntimeError('mll range for '+str(cat)+' not defined. Can be 0 or 1')
        # xmax
        xmax = hwwinfo.massDependantCutsbyVar['mllmax_bdt'][mass]  
        # xmin
        xmin = -1.*xmax
        # bins
        if mass < 300.:
            bins = 400 if cat == 0 else 200
        else:
            bins = 300 if cat == 0 else 150
        return (bins,xmin,xmax)
    
    # _____________________________________________________________________________
    def _getGMstarrange(self,mass,cat):
        if cat not in [0,1]:
            raise RuntimeError('GMstar range '+str(cat)+' not defined. Can be 0 or 1')
        # lower alwyas 50
        # upper 100+(mH-100)*0.5
        xmin=40
        xmax=90.+(mass-100.)*0.6

        if cat == '1j': xmax += 20

        if mass < 300.:
            bins = 200 if cat == '0j' else 200
        else:
            bins = 150 if cat == '0j' else 150
        return (bins,xmin,xmax)

    # _____________________________________________________________________________
    def makeNominals(self, var, sel, inputDir, outPath, **kwargs):
        
        ROOT.TH1.SetDefaultSumw2(True)
        shapeFiles = []

        # mass dependent sample list, can be in the mass loop
        for mass in self._masses:
            samples = hwwsamples.samples(mass, self._dataTag)
            # mass and variable selection
            allCuts = hwwinfo.massSelections( mass )

            alias = var if not self._split else var+'*(-1+2*('+allCuts[self._split+'-selection']+') )'
            try:
                varSelection = allCuts[sel+'-selection']
            except KeyError as ke:
                raise RuntimeError('Config error: '+str(ke))
                
            
            #inner  jet and flavor loops
            for chan,(category,flavor) in self._channels.iteritems():
                cat = hwwinfo.categories[category]
                flavors = hwwinfo.flavors[flavor]
                for flavor in flavors:
                    pars = dict([
                        ('mass',mass),
                        ('category',cat.name),
                        ('flavor',flavor)
                    ])
                    print '-'*80
                    print ' Processing channel '+chan+': mass',mass,'category',cat.nick,'flavor',flavor
                    print '-'*80
                    
                    # - define the source paths 
                    activeInputPaths = ['base']
                    # - if the current var is listes among the known paths,
                    #   add it to the actives
                    if var in self._paths: activeInputPaths.append(var)

                    # - apply the pars of the current sample 
                    dirmap = {}
                    for path in activeInputPaths:
                        dirmap[path]=(self._paths[path]+'/'+inputDir).format( **pars )

                    print 'Input dir:',dirmap.values()

                    inputs = self._connectInputs(var,samples, dirmap)
                    
                    # and the output path (might be par dependent as well)
                    output = outPath.format(**pars)
                    outdir = os.path.dirname(output)
                    if outdir:
                        self._ensuredir(outdir)

                    print '.'*80
                    print 'Output file:',output

                    # - now build the selection
                    catSel = cat.cut;
                    selection = varSelection+' && '+catSel+' && '+hwwinfo.flavorCuts[flavor]
                    selections = dict(zip(samples.keys(),[selection]*len(samples)))

                    self._addweights(mass,var,selections)

                    print '.'*80
                    # - extract the histogram range
                    rng = self.getrange(opt.range,mass,cat.name) 

                    # - to finally fill it
                    self._draw(alias, rng, selections ,output,inputs)
                    # - then disconnect the files
                    self._disconnectInputs(inputs)

                    shapeFiles.append(output)
        return shapeFiles

    # _____________________________________________________________________________
    def makeSystematics(self,var,sel,syst,mask,inputDir,outPath,**kwargs):

        ROOT.TH1.SetDefaultSumw2(True)
        shapeFiles = []

        nicks = kwargs['nicks'] if 'nicks' in kwargs else None
        # mass dependent sample list, can be in the mass loop
        for mass in self._masses:
            samples = hwwsamples.samples(mass, self._dataTag)
            
            # remove the dirname
            for tag,files in samples.iteritems():
                samples[tag] = map(os.path.basename,files)

            # mass and variable selection
            allCuts = hwwinfo.massSelections( mass )
            varSelection = allCuts[sel+'-selection']

            alias = var if not self._split else var+'*(-1+2*('+allCuts[self._split+'-selection']+') )'
            
            #inner  jet and flavor loops
            for chan,(category,flavor) in self._channels.iteritems():
                cat = hwwinfo.categories[category]
                flavors = hwwinfo.flavors[flavor]
                for flavor in flavors:
                    print '-'*80
                    print ' Processing channel '+chan+': mass',mass,'category',cat.nick,'flavor',flavor
                    print '-'*80

                    pars = dict([
                        ('mass',mass),
                        ('category',cat.name),
                        ('flavor',flavor),
                        ('syst',syst),
                    ])
                    pars['nick'] = nicks[syst] if nicks else syst

                    # - define the source paths 
                    activeInputPaths = ['base']
                    # - if the current var is listes among the known paths,
                    #   add it to the actives
                    if var in self._paths: activeInputPaths.append(var)

                    # - apply the pars of the current sample 
                    dirmap = {}
                    for path in activeInputPaths:
                        dirmap[path]=(self._paths[path]+'/'+inputDir).format( **pars )

                    inputs = self._connectInputs(var,samples, dirmap, mask)
                    # ---

                    # - and the output path (might be par dependent as well)
                    output = outPath.format(**pars)
                    outdir = os.path.dirname(output)
                    if output:
                        self._ensuredir(outdir)
                    print '.'*80
                    print 'Output file: ',output

                    # - now build the selection
                    catSel = cat.cut;
                    selection = varSelection+' && '+catSel+' && '+hwwinfo.flavorCuts[flavor]
                    selections = dict(zip(samples.keys(),[selection]*len(samples)))
                    self._addweights(mass,var,selections)

                    print '.'*80
                    # - extract the histogram range
                    rng = self.getrange(opt.range,mass,cat.name) 
                    # - to finally fill it
                    self._draw(alias, rng, selections ,output,inputs)
                    # - then disconnect the files
                    self._disconnectInputs(inputs)
                shapeFiles.append(output)
        return shapeFiles
    
    # _____________________________________________________________________________
    def _draw(self, var, rng, selections, output, inputs):
        '''
        var :       the variable to plot
        selection : the selction to draw
        output :    the output file path
        inputs :    the process-input files map
        '''
        self._logger.info('Yields by process')
        outFile = ROOT.TFile.Open(output,'recreate')
        for process,tree  in inputs.iteritems():
#             print ' '*3,process.ljust(20),':',tree.GetEntries(),
            print '    {0:<20} : {1:^9}'.format(process,tree.GetEntries()),
            # new histogram
            shapeName = 'histo_'+process
            shape = ROOT.TH1D(shapeName,process+';'+var,
                              rng[0],
                              rng[1],
                              rng[2]
                             )
            outFile.cd()

            cut = selections[process]

            self._logger.debug('Formula: '+var)
            self._logger.debug('Cut:     '+cut)
            self._logger.debug('ROOTFiles:'+'\n'.join([f.GetTitle() for f in tree.GetListOfFiles()]))
            entries = tree.Draw( var+'>>'+shapeName, cut, 'goff')
#             print ' >> ',entries,':',shape.Integral()
            print '>> {0:>9} : {1:>9.2f}'.format(entries,shape.Integral())
            shape.Write()
        outFile.Close()
        del outFile

    # _____________________________________________________________________________
    # add the weights to the selection
    def _addweights(self,mass,var,selections):
        sampleWgts =  self._sampleWeights(mass,var)
        print '--',selections.keys()
        for process,cut in selections.iteritems():
            wgt = self._baseWgt
            if process in sampleWgts:
                wgt += '*'+sampleWgts[process]

            selections[process] = wgt+'*('+cut+')'

    # _____________________________________________________________________________
    # this is too convoluted
    # define here the mass-dependent weights
    def _sampleWeights(self,mass,var):
        weights = {}
        weights['WJet']             = 'fake2W'
        weights['WJetFakeRate']     = 'fake2W'
        weights['Data']             = '1'
        weights['DYLL']             = '(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))'
        weights['DYLLtemplate']     = '(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))'
        weights['DYLLtemplatesyst'] = '(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))'
        
#         stupidmasses = [118, 122, 124, 126, 128, 135]
#         if var in ['bdts','bdtl'] and mass in stupidmasses:
#             weights['ggH']+='*2*(event%2==0)'
#             weights['vbfH']='2*(event%2==0)'
#             weights['wzttH']='2*(event%2==0)'
#             # TODO Signal injection weights, if available
#             weights['ggH-SI']+='*2*(event%2==0)'
#             weights['vbfH-SI']='2*(event%2==0)'
#             weights['wzttH-SI']='2*(event%2==0)'
        if var in ['bdts','bdtl']:
            
            weights['WW']    = '*2*(event%2 == 0)'
            weights['ggH']   = '*2*(event%2 == 0)'
            weights['vbfH']  = '2*(event%2  == 0)'
            weights['wzttH'] = '2*(event%2  == 0)'
            # TODO Signal injection weights, if available
            weights['ggH-SI']   = '*2*(event%2 == 0)'
            weights['vbfH-SI']  = '2*(event%2  == 0)'
            weights['wzttH-SI'] = '2*(event%2  == 0)'
            
        return weights

    # _____________________________________________________________________________
    def _ensuredir(self,directory):
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno == 17:
                    pass
                else:
                    raise e

    # _____________________________________________________________________________
    def _connectInputs(self, var, samples, dirmap, mask=None):
        inputs = {}
        treeName = 'latino'
        for process,filenames in samples.iteritems():
            if mask and process not in mask:
                continue
            tree = self._buildchain(treeName,[ (dirmap['base']+'/'+f) for f in filenames])
            if 'bdt' in var:
                bdttreeName = 'latinobdt'
                bdtdir = self._paths[var]
                bdttree = self._buildchain(bdttreeName,[ (dirmap[var]+'/'+f) for f in filenames])
                
                if tree.GetEntries() != bdttree.GetEntries():
                    raise RuntimeError('Mismatching number of entries: '
                                       +tree.GetName()+'('+str(tree.GetEntries())+'), '
                                       +bdttree.GetName()+'('+str(bdttree.GetEntries())+')')
                logging.debug('{0:<20} - master: {1:<20} friend {2:<20}'.format(process,tree.GetEntries(), bdttree.GetEntries()))
                tree.AddFriend(bdttree)

            inputs[process] = tree

        return inputs

    # _____________________________________________________________________________
    def _disconnectInputs(self,inputs):
        for n in inputs.keys():
            friends = inputs[n].GetListOfFriends()
            if friends.__nonzero__():
                for fe in friends:
                    friend = fe.GetTree()
                    inputs[n].RemoveFriend(friend)
                    ROOT.SetOwnership(friend,True)
                    del friend
            del inputs[n]
    
    # _____________________________________________________________________________
    def _buildchain(self,treeName,files):
        tree = ROOT.TChain(treeName)
        for path in files:
            self._logger.debug('     '+str(os.path.exists(path))+' '+path)
            if not os.path.exists(path):
                raise RuntimeError('File '+path+' doesn\'t exists')
            tree.Add(path) 

        return tree

    

if __name__ == '__main__':
    print '''
--------------------------------------------------------------------------------------------------
  .-')    ('-. .-.   ('-.      _ (`-.    ('-.  _   .-')      ('-.    .-. .-')     ('-.  _  .-')   
 ( OO ). ( OO )  /  ( OO ).-. ( (OO  ) _(  OO)( '.( OO )_   ( OO ).-.\  ( OO )  _(  OO)( \( -O )  
(_)---\_),--. ,--.  / . --. /_.`     \(,------.,--.   ,--.) / . --. /,--. ,--. (,------.,------.  
/    _ | |  | |  |  | \-.  \(__...--'' |  .---'|   `.'   |  | \-.  \ |  .'   /  |  .---'|   /`. ' 
\  :` `. |   .|  |.-'-'  |  ||  /  | | |  |    |         |.-'-'  |  ||      /,  |  |    |  /  | | 
 '..`''.)|       | \| |_.'  ||  |_.' |(|  '--. |  |'.'|  | \| |_.'  ||     ' _)(|  '--. |  |_.' | 
.-._)   \|  .-.  |  |  .-.  ||  .___.' |  .--' |  |   |  |  |  .-.  ||  .   \   |  .--' |  .  '.' 
\       /|  | |  |  |  | |  ||  |      |  `---.|  |   |  |  |  | |  ||  |\   \  |  `---.|  |\  \  
 `-----' `--' `--'  `--' `--'`--'      `------'`--'   `--'  `--' `--'`--' '--'  `------'`--' '--' 
--------------------------------------------------------------------------------------------------
'''    
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--selection'      , dest='selection'      , help='selection cut'                              , default=None)
    parser.add_option('--dataset'        , dest='dataset'        , help='dataset to process'                         , default=None)
    parser.add_option('--path_latino'    , dest='path_latino'    , help='Root of the master trees'                   , default=None)
    parser.add_option('--path_bdt'       , dest='path_bdt'       , help='Root of the friendly bdt trees'             , default=None)
    parser.add_option('--path_shape_raw' , dest='path_shape_raw' , help='destination directory of nominals'          , default=None)
    parser.add_option('--range'          , dest="range"          , help='range (optional default is var)'            , default=None)
    parser.add_option('--split'          , dest="split"          , help='split in channels using a second selection' , default=None)

    parser.add_option('--no-noms',       dest='makeNoms',    help='Do not produce the nominal',            action='store_false',   default=True)
    parser.add_option('--no-syst',       dest='makeSyst',    help='Do not produce the systematics',        action='store_false',   default=True)
    parser.add_option('--do-syst',       dest='doSyst',      help='Do only one systematic',                default=None)
    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)
    (opt, args) = parser.parse_args()

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()

    if opt.debug and opt.debug > 0:
        logging.basicConfig(level=logging.DEBUG)

#     try:
    if True:
        if not opt.dataset:
            parser.print_help()
            parser.error('Dataset not defined')

        if not opt.sel:
            parser.print_help()
            parser.error('Selection not defined')

        if not opt.path_latino:
            parser.print_help()
            parser.error('Master tree path not defined')

        if not opt.path_shape_raw: 
            parser.print_help()
            parser.error('Where shall I put the shapes?')

        if not opt.range:
            opt.range = opt.variable


        variable = opt.variable
        selection = opt.selection

        latinoDir           = opt.path_latino
        bdtDir              = opt.path_bdt
        nomOutDir           = os.path.join(opt.path_shape_raw,'nominals/')
        systOutDir          = os.path.join(opt.path_shape_raw,'systematics/')
        
        nomInputDir         = ''
        systInputDir        = '{syst}/'

        nominalOutFile      = 'shape_Mh{mass}_{category}_'+variable+'_shapePreSel_{flavor}.root'
        systematicsOutFile  = 'shape_Mh{mass}_{category}_'+variable+'_shapePreSel_{flavor}_{nick}.root'
        
        factory = ShapeFactory()
        factory._outFileFmt  = nominalOutFile

        masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]
        factory._masses   = masses
        # update here: from cats and flavs to out_chans
#         factory._categories = [ hwwinfo.categories[c] for c in opt.cats ]
#         factory._flavors = hwwinfo.flavors[:]

        # go through final channels
        factory._channels = dict([ (k,v) for k,v in hwwinfo.channels.iteritems() if k in opt.chans])
        print factory._channels

        factory._paths['base']  = latinoDir
        factory._paths['bdtl']  = bdtDir
        factory._paths['bdts']  = bdtDir

        factory._dataTag = opt.dataset
        factory._range = opt.range
        factory._split = opt.split


        if opt.makeNoms:
            # nominal shapes
            print factory.makeNominals(variable,selection,nomInputDir,nomOutDir+nominalOutFile)

        if opt.makeSyst:
            # systematic shapes
            systematics = OrderedDict([
                ('electronResolution'    , 'p_res_e'),
                ('electronScale_down'    , 'p_scale_eDown'),
                ('electronScale_up'      , 'p_scale_eUp'),
                ('jetEnergyScale_down'   , 'p_scale_jDown'),
                ('jetEnergyScale_up'     , 'p_scale_jUp'),
                ('leptonEfficiency_down' , 'eff_lDown'),
                ('leptonEfficiency_up'   , 'eff_lUp'),
                ('metResolution'         , 'met'),
                ('muonScale_down'        , 'p_scale_mDown'),
                ('muonScale_up'          , 'p_scale_mUp'),
            ])

            mask = ['ggH', 'vbfH', 'ggWW', 'Top', 'WW', 'VV']
            systMasks = dict([(s,mask[:]) for s in systematics])

            for s,m in systMasks.iteritems():
                if opt.doSyst and opt.doSyst != s:
                    continue
                print '-'*80
                print ' Processing',s,'for samples',' '.join(mask)
                print '-'*80
                files = factory.makeSystematics(variable,selection,s,m,systInputDir,systOutDir+systematicsOutFile, nicks=systematics)
#     except Exception as e:
#         print 'Fatal exception: '+str(e)
#         exc_type, exc_value, exc_traceback = sys.exc_info()
#         traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
#     finally:
#         print 'Used options'
#         print ', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()])
