#!/usr/bin/env python


import sys
import ROOT
import optparse
import hwwinfo
import os.path
import string
import logging
from HWWAnalysis.Misc.odict import OrderedDict

def makeHistograms():
    pass

class ShapeFactory:
    def __init__(self):
        self._baseWgt = 'baseW*puW*effW*triggW' # TODO check what to to with the triggerW
        weights = {}
        weights['ggH']   = 'kfW'
        weights['vbf']   = 'kfW'
        weights['WJet']  = 'fake2W'
        weights['Data']  = '1'
        self._sampleWgt = weights
        ranges = {}
        ranges['bdtl']       = (400  , -1. , 1.)
        ranges['bdts']       = (400  , -1. , 1.)
#         ranges["mll"]        = (1200 , 0   , 600)
        ranges["mth"]        = (400  , 0   , 200)
        ranges["dphill"]     = (400  , 0   , 3.15)
#         ranges["gammaMRStar"]= (1200 , 0   , 600)
        self._ranges = ranges
        
        self._dataTag = '2011A'
        self._masses = []
        self._jets = []
        self._channels = []
        # paths (to move out)
        self._outFileFmt  = ''
        self._paths = {}

    def __del__(self):
        pass
    
    def getrange(self,var,mass,njet):
        
        if var in ['mll','gammaMRStar']:
            return self._getmllrange(mass,njet)

        varRange = self._ranges[var]
        if isinstance(varRange,tuple):
            return varRange
        elif isinstance(varRange,dict):
            return varRange[mass][njet]
            
    def _getmllrange(self,mass,njet):

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
#         bins = 400 if njet == 0 else 200

        if mass < 300.:
            bins = 400 if njet == 0 else 200
        else:
            bins = 300 if njet == 0 else 150
        return (bins,xmin,xmax)

    def makeNominals(self, var, inputDir, outPath, **kwargs):
        
        ROOT.TH1.SetDefaultSumw2(True)

#         inputDirTmpl = string.Template(inputDir)
#         outDirTmpl = string.Template(outDir)
#         outFileTmpl = string.Template(self._outFileFmt)

        shapeFiles = []
        # mass dependent sample list, can be in the mass loop
        for mass in self._masses:
            samples = hwwinfo.samples(mass, self._dataTag)
            # mass and variable selection
            allCuts = hwwinfo.massSelections( mass )
            varSelection = allCuts[var+'sel']
            varCtrlZ     = allCuts[var+'ctrZ']
            
            #inner  jet and channel loops
            for njet in self._jets:
                for channel in self._channels:
                    print '-'*80
                    pars = dict([
                        ('mass',mass),
                        ('jets',njet),
                        ('channel',channel)
                    ])
                    
                    # ----
                    activeInputPaths = ['base']
                    if var in self._paths: activeInputPaths.append(var)

                    dirmap = {}
                    for path in activeInputPaths:
                        dirmap[path]=(self._paths[path]+'/'+inputDir).format( **pars )

                    print 'Input dir:',dirmap.values()

                    inputs = self._connectInputs(var,samples, dirmap)
                    
                    # and the output path (might be par dependent as well)
                    output = outPath.format(**pars)
                    outdir = os.path.dirname(output)
                    if outdir:
                        os.system('mkdir -p '+outdir)
                    print 'Output file:',output
                    print '-'*80

                    # now build the selection
                    jetSel = 'njet == {0}'.format(njet) #'njet>%.1f && njet<%.1f' % (njet-0.5,njet+0.5)
                    selection = varSelection+' && '+jetSel+' && '+hwwinfo.channelCuts[channel]
                    selections = dict(zip(samples.keys(),[selection]*len(samples)))
                    if 'DYLL' in selections:
                        selections['DYLLctrZ'] = varCtrlZ+' && '+jetSel+' && '+hwwinfo.channelCuts[channel]
                        logging.debug(str(inputs))
#                         inputs['DYLLctrZ'] = inputs['DYLL']
                        inputs['DYLLctrZ'] = inputs['Data']

#                     print 'Selection:',selections
                    print '-'*80
                    rng = self.getrange(var,mass,njet) 
                    self._draw(var, rng, selections ,output,inputs)
                    shapeFiles.append(output)
        return shapeFiles

    def makeSystematics(self,var,syst,mask,inputDir,outPath,**kwargs):
        ROOT.TH1.SetDefaultSumw2(True)
        shapeFiles = []
        nicks = kwargs['nicks'] if 'nicks' in kwargs else None
        # mass dependent sample list, can be in the mass loop
        for mass in self._masses:
            samples = hwwinfo.samples(mass, self._dataTag)
            # mass and variable selection
            allCuts = hwwinfo.massSelections( mass )
            varSelection = allCuts[var+'sel']
            
            #inner  jet and channel loops
            for njet in self._jets:
                for channel in self._channels:
                    print '-'*80
                    print ' Mass',mass,'jets',njet,'channel',channel
                    print '-'*80

                    pars = dict([
                        ('mass',mass),
                        ('jets',njet),
                        ('channel',channel),
                        ('syst',syst),
                    ])
                    pars['nick'] = nicks[syst] if nicks else syst

                    # ----
                    activeInputPaths = ['base']
                    if var in self._paths: activeInputPaths.append(var)

                    dirmap = {}
                    for path in activeInputPaths:
                        dirmap[path]=(self._paths[path]+'/'+inputDir).format( **pars )

                    inputs = self._connectInputs(var,samples, dirmap, mask)

                    # ---

                    # and the output path (might be par dependent as well)
                    output = outPath.format(**pars)
                    outdir = os.path.dirname(output)
                    if output:
                        os.system('mkdir -p '+outdir)
                    print 'Output file',output
                    print '-'*80

                    # now build the selection
                    jetSel = 'njet == {0}'.format(njet) #njet>%.1f && njet<%.1f' % (njet-0.5,njet+0.5)
                    selection = varSelection+' && '+jetSel+' && '+hwwinfo.channelCuts[channel]
                    selections = dict(zip(samples.keys(),[selection]*len(samples)))
#                     print selections
                    #-- hack for 
#                     sys.exit(0)
                    rng = self.getrange(var,mass,njet) 
                    self._draw(var, rng, selections ,output,inputs)
                shapeFiles.append(output)
        return shapeFiles
    
    def _draw(self, var, rng, selections, output, inputs):
        '''
        var :       the variable to plot
        selection : the selction to draw
        output :    the output file path
        inputs :    the process-input files map
        '''
        outFile = ROOT.TFile.Open(output,'recreate')
        for process,tree  in inputs.iteritems():
            print '     ',process.ljust(20),':',tree.GetEntries(),
            # new histogram
            shapeName = 'histo_'+process
            shape = ROOT.TH1D(shapeName,process+';'+var,
                              rng[0],
                              rng[1],
                              rng[2]
                             )
            outFile.cd()
            wgt = self._baseWgt[:]
            # correct the selection with sample depented weights
            if process in self._sampleWgt:
                wgt += '*'+self._sampleWgt[process]
            cut = wgt+'*('+selections[process]+')'

            logging.debug('Applied cut: '+cut)
            entries = tree.Draw( var+'>>'+shapeName, cut, 'goff')
            print ' >> ',entries
            shape.Write()
        outFile.Close()
        del outFile

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
                    raise RuntimeError('Mismatching number of entries: '+tree.GetName()+'('+str(tree.GetEntries())+'), '+bdttree.GetName()+'('+str(bdttree.GetEntries())+')')
                print '   master: ',tree.GetEntries(), ' friend ', bdttree.GetEntries()
                tree.AddFriend(bdttree)

            inputs[process] = tree

        return inputs


    
    def _buildchain(self,treeName,files):
        tree = ROOT.TChain(treeName)
        for path in files:
            print '     ',os.path.exists(path),path
            if not os.path.exists(path):
                raise RuntimeError('File '+path+' doesn\'t exists')
            tree.Add(path) 

        return tree

    

if __name__ == '__main__':
    
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--noNoms', dest='makeNoms',help='Do not produce the nominal', action='store_false',default=True)
    parser.add_option('--noSyst', dest='makeSyst',help='Do not produce the systematics', action='store_false',default=True)
    parser.add_option('--doSyst', dest='doSyst',help='Do only one systematic',default=None)
    hwwinfo.addOptions(parser)
    hwwinfo.loadOptDefaults(parser)
    (opt, args) = parser.parse_args()

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()

    variable = opt.var

    # var replacememnt
    # mass = mass
    # jets = jets
    # channel = channel
    # syst = systematics label
    # nick = systematics short name (if defined)
    # /scratch/thea/shapes/MVA/syst_electronResolution/ntupleMVA_MH600_njet1/

    latinoDir           = '/shome/thea/HWW/ShapeAnalysis/trees/latino_skim'
    bdtDir              = '/shome/thea/HWW/ShapeAnalysis/trees/bdt_skim/ntupleMVA_MH{mass}_njet{jets}'
    nominalDir          = 'all/'
    systematicsDir      = '{syst}/'
    nominalOutFile      = 'histo_H{mass}_{jets}jet_'+variable+'shapePreSel_{channel}.root'
    systematicsOutFile  = 'histo_H{mass}_{jets}jet_'+variable+'shapePreSel_{channel}_{nick}.root'
    
    factory = ShapeFactory()
    factory._outFileFmt  = nominalOutFile
#     factory._nominalDir  = '/scratch/maiko/postLP/MVA/ntupleMVA/ntupleMVA_MH{mass}_njet{jets}/'
#     factory._systematicsDir = '/scratch/maiko/postLP/MVA/' 

    masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]
    factory._masses   = masses
    factory._jets     = hwwinfo.jets[:]
    factory._channels = hwwinfo.channels[:]
    factory._paths['base'] = latinoDir
    factory._paths['bdtl']  = bdtDir
    factory._paths['bdts']  = bdtDir

#     print factory._masses
#     sys.exit(0) 

    factory._dataTag = '2011'
    
    if opt.makeNoms:
        # nominal shapes
        print factory.makeNominals(variable,nominalDir,'Nominal/'+nominalOutFile)

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
            files = factory.makeSystematics(variable,s,m,systematicsDir,'SystMC/'+systematicsOutFile, nicks=systematics)
    #         for old in files:
    #             new = old.replace(s,systematics[s])
    #             print 'Renaming',old,'->',new
    #             os.rename(old,new)
            
