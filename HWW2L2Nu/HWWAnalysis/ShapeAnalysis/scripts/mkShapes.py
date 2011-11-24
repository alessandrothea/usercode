#!/usr/bin/env python


import sys
import ROOT
import optparse
import hwwinfo
import os.path
import string
from HWWAnalysis.Misc.odict import OrderedDict

def makeHistograms():
    pass

class ShapeFactory:
    def __init__(self):
        self._baseWgt = 'baseW*puW*effW' # TODO check what to to with the triggerW
        weights = {}
        weights['ggH']   = 'kfW'
        weights['vbf']   = 'kfW'
        weights['WJet']  = 'fake2W'
        weights['Data']  = '1'
        self._sampleWgt = weights
        ranges = {}
        ranges['bdtl']       = [400,-1.,1.]
        ranges['bdts']       = [400,-1.,1.]
        ranges["mll"]        = [500, 0, 200]
        ranges["mth"]        = [500, 0, 200]
        ranges["dphill"]     = [500, 0, 3.15]
        ranges["gammaMRStar"]= [500, 0, 200]
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
            
            #inner  jet and channel loops
            for j in self._jets:
                for channel in self._channels:
                    print '-'*80
                    pars = dict([
                        ('mass',mass),
                        ('jets',j),
                        ('channel',channel)
                    ])
                    
#                     indir = (self._paths['base']+'/'+inputDir).format( **pars )
                    activeInputPaths = ['base']
                    if var in self._paths: activeInputPaths.append(var)

                    indirs = {}
                    for path in activeInputPaths:
                        indirs[path]=(self._paths[path]+'/'+inputDir).format( **pars )

#                     indir = inputDirTmpl.safe_substitute(pars)
                    print 'Input dir:',indirs.values()
                    
                    inputs = {}
                    for process,filenames in samples.iteritems():
                        inputs[process] = {}
                        for path,d in indirs.iteritems():
                            filepaths = [ (d+'/'+f) for f in filenames]
                            #             print ' ',process
                            inputs[process][path] = filepaths

                    # and the output path (might be par dependent as well)
                    output = outPath.format(**pars)
#                     outdir = outDirTmpl.safe_substitute(pars)
                    outdir = os.path.dirname(output)
                    if outdir:
                        os.system('mkdir -p '+outdir)
                    print 'Output file:',output
                    print '-'*80

                    # now build the selection
                    jetSel = 'njet == {0}'.format(j) #'njet>%.1f && njet<%.1f' % (j-0.5,j+0.5)
                    selection = varSelection+' && '+jetSel+' && '+hwwinfo.channelCuts[channel]
                    print 'Selection:',selection
                    print '-'*80
                    self._draw(var, selection ,output,inputs)
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
            for j in self._jets:
                for channel in self._channels:
                    print '-'*80
                    pars = dict([
                        ('mass',mass),
                        ('jets',j),
                        ('channel',channel),
                        ('syst',syst),
                    ])
                    pars['nick'] = nicks[syst] if nicks else syst

                    # ----
                    activeInputPaths = ['base']
                    if var in self._paths: activeInputPaths.append(var)
#                     print activeInputPaths

                    indirs = {}
                    for path in activeInputPaths:
                        indirs[path]=(self._paths[path]+'/'+inputDir).format( **pars )

                    inputs = {}
                    for process,filenames in samples.iteritems():
                        if process not in mask:
                            continue
                        inputs[process] = {}
                        for t,d in indirs.iteritems():
                            filepaths = [ (d+'/'+f) for f in filenames]
                            inputs[process][t] = filepaths

                    # ---

                    # and the output path (might be par dependent as well)
                    output = outPath.format(**pars)
                    outdir = os.path.dirname(output)
                    if output:
                        os.system('mkdir -p '+outdir)
                    print 'Output file',output
                    print '-'*80

                    # now build the selection
                    jetSel = 'njet == {0}'.format(j) #njet>%.1f && njet<%.1f' % (j-0.5,j+0.5)
                    selection = varSelection+' && '+jetSel+' && '+hwwinfo.channelCuts[channel]

                    self._draw(var, selection ,output,inputs)
                shapeFiles.append(output)
        return shapeFiles

    def _draw(self, var, selection, output, inputs):
        '''
        var :       the variable to plot
        selection : the selction to draw
        output :    the output file path
        inputs :    the process-input files map
        '''
        outFile = ROOT.TFile.Open(output,'recreate')
        for process,paths  in inputs.iteritems():
            # new histogram
            shapeName = 'histo_'+process
            shape = ROOT.TH1D(shapeName,process+';'+var,
                              self._ranges[var][0],
                              self._ranges[var][1],
                              self._ranges[var][2]
                             )
            # build the chain
            treeName = 'latino'
            tree = self._buildchain(treeName,paths['base'])
            if 'bdt' in var:
                bdttreeName = 'latinobdt'
                bdttree = self._buildchain(bdttreeName,paths[var])
                
                if tree.GetEntries() != bdttree.GetEntries():
                    raise RuntimeError('Mismatching number of entries: '+tree.GetName()+'('+str(tree.GetEntries())+'), '+bdttree.GetName()+'('+str(bdttree.GetEntries())+')')
                tree.AddFriend(bdttree)
                print ' '*8,'+','treecheck master: ',tree.GetEntries(), ' friend ', bdttree.GetEntries()
            
            print ' '*5,'+',process.ljust(10),':',tree.GetEntriesFast(),
            outFile.cd()
            wgt = self._baseWgt[:]
            # correct the selection with sample depented weights
            if process in self._sampleWgt:
                wgt += '*'+self._sampleWgt[process]
            cut = wgt+'*('+selection+')'

            entries = tree.Draw( var+'>>'+shapeName, cut, 'goff')
            print ' >> ',entries
            shape.Write()
        outFile.Close()
        del outFile

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
#     nominalDir          = '/scratch/maiko/postLP/MVA/ntupleMVA/ntupleMVA_MH{mass}_njet{jets}/'
#     systematicsDir      = '/scratch/maiko/postLP/MVA/mvaapp_syst_{type}_{syst}/ntupleMVA_MH{mass}_njet{jets}/' 
#     systematicsDir      = '/scratch/thea/shapes/MVA/syst_{syst}/ntupleMVA_MH{mass}_njet{jets}/'
#     nominalDir          = '/scratch/thea/latino_skim/all'
#     systematicsDir      = '/scratch/thea/latino_skim/'


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
            
