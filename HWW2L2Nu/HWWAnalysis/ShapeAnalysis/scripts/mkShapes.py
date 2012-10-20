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
from HWWAnalysis.Misc.ROOTAndUtils import TH1AddDirSentry
import traceback


class ShapeFactory:
    _logger = logging.getLogger('ShapeFactory')
 
    # _____________________________________________________________________________
    def __init__(self):
        self._stdWgt = 'baseW*puW60ABC*effW*triggW'
        self._systByWeight = {}

        ranges = {}
        ranges['counting']         = (1   , 0.  , 2.)
        ranges['bdtl']             = (400 , -1. , 1.)
        ranges['bdts']             = (400 , -1. , 1.)
        ranges['mth']              = (400 , 0.  , 200)
        ranges['dphill']           = (400 , 0.  , 3.15)
        ranges['detajj']           = (240 , 0.  , 6.)
        ranges['mll-vbf']          = (60  , 12  , 135)
        ranges['mll']              = self._getmllrange
        ranges['mllsplit']         = self._getmllsplitrange
        ranges['gammaMRStar']      = self._getGMstarrange
        ranges['vbf2D']            = self._getVBF2Drange
        ranges['mth-mll-hilomass'] = self._getMllMth2Drange
        self._ranges = ranges
        
        self._dataTag         = '2012A'
        self._mcTag           = '0j1j'
        self._masses          = []
        self._channels        = {}
        # paths (to move out)
        self._outFileFmt      = ''
        self._paths           = {}
        self._range           = None
        self._splitmode       = None
        self._lumi            = 1

    # _____________________________________________________________________________
    def __del__(self):
        pass
    
    # _____________________________________________________________________________
    def getrange(self,tag,mass,cat):
        
        if isinstance(tag,tuple):
            theRange = tag
        else:
            try:
                theRange = self._ranges[tag]
            except KeyError as ke:
                self._logger.error('Range '+tag+' not available. Possible values: '+', '.join(self._ranges.iterkeys()) )
                raise ke

        if isinstance(theRange,tuple):
            return theRange
        elif isinstance(theRange,dict):
            return theRange[mass][cat]
        elif callable(theRange):
            return theRange(mass,cat)

    # _____________________________________________________________________________
    def _getMllMth2Drange(self,mass,cat):

        if cat not in ['0j','1j']:
            raise RuntimeError('mll range for '+str(cat)+' not defined. Can be 0 or 1')

        if mass < 300.:
            return (10,80,280,8,0,200) 
        else:
            return (10,80,380,8,0,450) 

    # _____________________________________________________________________________
    def _getVBF2Drange(self,mass,cat):

        if cat not in ['2j']:
            raise RuntimeError('mth:mll range for '+str(cat)+' not defined. Can be 2')

        if mass<300 :
          return (4, 30, 280, 4, 0, 200)
        else :
          return (2, 30, 330, 3, 0, 450)

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
        if cat not in ['0j','1j']:
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
            samples = hwwsamples.samples(mass, self._dataTag, self._mcTag)
            # mass and variable selection
            allCuts = hwwinfo.massSelections( mass )

            alias = var if not self._splitmode else var+'*(-1+2*('+allCuts[self._splitmode+'-selection']+') )'
            try:
                varSelection = allCuts[sel+'-selection']
            except KeyError as ke:
                raise RuntimeError('Config error: '+str(ke))
                
            
            #inner  jet and flavor loops
            for chan,(category,flavor) in self._channels.iteritems():
#                 cat = hwwinfo.categories[category]
                flavors = hwwinfo.flavors[flavor]
                for flavor in flavors:
                    pars = dict([
                        ('mass',mass),
                        ('category',category),
                        ('flavor',flavor)
                    ])
                    print '-'*80
                    print ' Processing channel '+chan+': mass',mass,'category',category,'flavor',flavor
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
                    # - make a separate function to cotain the exceptions
                    catSel = hwwinfo.categoryCuts[category]
                    selection = varSelection+' && '+catSel+' && '+hwwinfo.flavorCuts[flavor]
                    selections = dict(zip(samples.keys(),[selection]*len(samples)))

                    self._addweights(mass,var,'nominals',selections,category)

                    print '.'*80
                    # - extract the histogram range
                    rng = self.getrange(opt.range,mass,category) 

                    # - to finally fill it
                    self._draw(alias, rng, selections, output, inputs)
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
            samples = hwwsamples.samples(mass, self._dataTag, self._mcTag)
            
            # remove the dirname
            for tag,files in samples.iteritems():
                samples[tag] = map(os.path.basename,files)

            # mass and variable selection
            allCuts = hwwinfo.massSelections( mass )
            varSelection = allCuts[sel+'-selection']

            alias = var if not self._splitmode else var+'*(-1+2*('+allCuts[self._splitmode+'-selection']+') )'
            
            #inner  jet and flavor loops
            for chan,(category,flavor) in self._channels.iteritems():
#                 cat = hwwinfo.categories[category]
                flavors = hwwinfo.flavors[flavor]
                for flavor in flavors:
                    print '-'*80
                    print ' Processing channel '+chan+': mass',mass,'category',category,'flavor',flavor
                    print '-'*80

                    pars = dict([
                        ('mass',mass),
                        ('category',category),
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
                    catSel = hwwinfo.categoryCuts[category]
                    selection = varSelection+' && '+catSel+' && '+hwwinfo.flavorCuts[flavor]
                    selections = dict(zip(samples.keys(),[selection]*len(samples)))
                    self._addweights(mass,var,syst,selections, category)

                    print '.'*80
                    # - extract the histogram range
                    rng = self.getrange(opt.range,mass,category) 
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
        vdim = var.count(':')+1
#         hproto,hdim = ShapeFactory._projexpr(rng)
        # 3 items per dimention
        hdim = self._bins2dim( rng )

        if vdim != hdim:
            raise ValueError('The variable\'s and range number of dimensions are mismatching')

        for process,tree  in inputs.iteritems():
#             print ' '*3,process.ljust(20),':',tree.GetEntries(),
            print '    {0:<20} : {1:^9}'.format(process,tree.GetEntries()),
            # new histogram
            shapeName = 'histo_'+process
#             hstr = shapeName+hproto
            
            outFile.cd()

            # prepare a dummy to fill
            shape = self._makeshape(shapeName,rng)
            cut = selections[process]

            self._logger.debug('---'+process+'---')
            self._logger.debug('Formula: '+var+'>>'+shapeName)
            self._logger.debug('Cut:     '+cut)
            self._logger.debug('ROOTFiles:'+'\n'.join([f.GetTitle() for f in tree.GetListOfFiles()]))
            entries = tree.Draw( var+'>>'+shapeName, cut, 'goff')
#             print ' >> ',entries,':',shape.Integral()
            shape = outFile.Get(shapeName)
            shape.SetTitle(process+';'+var)


            if isinstance(shape,ROOT.TH2):
                shape2d = shape
                # puts the over/under flows in
                self._reshape( shape )
                # go 1d
                shape = self._h2toh1(shape2d)
                # rename the old
                shape2d.SetName(shape2d.GetName()+'_2d')
                shape2d.Write()
                shape.SetDirectory(outFile)

            print '>> {0:>9} : {1:>9.2f}'.format(entries,shape.Integral())
            shape.Write()
        outFile.Close()
        del outFile

    # _____________________________________________________________________________
    @staticmethod
    def _moveAddBin(h, fromBin, toBin ):
        if not isinstance(fromBin,tuple) or not isinstance(toBin,tuple):
            raise ValueError('Arguments must be tuples')

        dims = [h.GetDimension(), len(fromBin), len(toBin) ]

        if dims.count(dims[0]) != len(dims):
            raise ValueError('histogram and the 2 bins don\'t have the same dimension')
        
        # get bins
        b1 = h.GetBin( *fromBin )
        b2 = h.GetBin( *toBin )

        # move contents
        c1 = h.At( b1 )
        c2 = h.At( b2 )

        h.SetAt(0, b1)
        h.SetAt(c1+c2, b2)

        # move weights as well
        sumw2 = h.GetSumw2()

        w1 = sumw2.At( b1 )
        w2 = sumw2.At( b2 )

        sumw2.SetAt(0, b1)
        sumw2.SetAt(w1+w2, b2)


    def _reshape(self,h):
        if h.GetDimension() == 1:
            # nx = h.GetNbinsX()
            # ShapeFactory._moveAddBin(h, (0,),(1,) )
            # ShapeFactory._moveAddBin(h, (nx+1,),(nx,) )
            return
        elif h.GetDimension() == 2:
            nx = h.GetNbinsX()
            ny = h.GetNbinsY()

            for i in xrange(1,nx+1):
                ShapeFactory._moveAddBin(h,(i,0   ),(i, 1 ) )
                ShapeFactory._moveAddBin(h,(i,ny+1),(i, ny) )

            for j in xrange(1,ny+1):
                ShapeFactory._moveAddBin(h,(0,    j),(1, j) )
                ShapeFactory._moveAddBin(h,(nx+1, j),(nx,j) )

            # 0,0 -> 1,1
            # 0,ny+1 -> 1,ny
            # nx+1,0 -> nx,1
            # nx+1,ny+1 ->nx,ny

            ShapeFactory._moveAddBin(h, (0,0),(1,1) )
            ShapeFactory._moveAddBin(h, (0,ny+1),(1,ny) )
            ShapeFactory._moveAddBin(h, (nx+1,0),(nx,1) )
            ShapeFactory._moveAddBin(h, (nx+1,ny+1),(nx,ny) )

    @staticmethod
    def _h2toh1(h):
        import array
        
        if not isinstance(h,ROOT.TH2):
            raise ValueError('Can flatten only 2d hists')

        sentry = TH1AddDirSentry()

#         H1class = getattr(ROOT,h.__class__.__name__.replace('2','1'))

        nx = h.GetNbinsX()
        ny = h.GetNbinsY()

        h_flat = ROOT.TH1D(h.GetName(),h.GetTitle(),nx*ny,0,nx*ny)

        
        sumw2 = h.GetSumw2()
        sumw2_flat = h_flat.GetSumw2()

        for i in xrange(1,nx+1):
            for j in xrange(1,ny+1):
                # i,j must be mapped in 
                b2d = h.GetBin( i,j )
#                 b2d = h.GetBin( j,i )
#                 b1d = ((i-1)+(j-1)*nx)+1
                b1d = ((j-1)+(i-1)*ny)+1

                h_flat.SetAt( h.At(b2d), b1d )
                sumw2_flat.SetAt( sumw2.At(b2d), b1d ) 

        h_flat.SetEntries(h.GetEntries())
        
        stats2d = array.array('d',[0]*7)
        h.GetStats(stats2d)

        stats1d = array.array('d',[0]*4)
        stats1d[0] = stats2d[0]
        stats1d[1] = stats2d[1]
        stats1d[2] = stats2d[2]+stats2d[4]
        stats1d[3] = stats2d[3]+stats2d[5]

        h_flat.PutStats(stats1d)

        xtitle = h.GetXaxis().GetTitle()
        v1,v2 = xtitle.split(':') # we know it's a 2d filled by an expr like y:x
        xtitle = '%s #times %s bin' % (v1,v2)

        h_flat.GetXaxis().SetTitle(xtitle)

        return h_flat


    # _____________________________________________________________________________
    # add the weights to the selection
    def _addweights(self,mass,var,syst,selections,cat=''):
        sampleWgts =  self._sampleWeights(mass,var,cat)
        print '--',selections.keys()
        for process,cut in selections.iteritems():
            wgt = self._stdWgt
            if process in sampleWgts:
                wgt = sampleWgts[process]
            
            if syst in self._systByWeight:
                wgt = wgt+'*'+self._systByWeight[syst]
   

            selections[process] = wgt+'*('+cut+')'

    # _____________________________________________________________________________
    # this is too convoluted
    # define here the mass-dependent weights
    def _sampleWeights(self,mass,var,cat):
        weights = {}
        # tocheck
        weights['WJet']              = 'baseW*fakeW'
        weights['WJetFakeRate']      = 'baseW*fakeWUp'
        weights['Data']              = '1'
        # problem with DYTT using embedded for em/me + MC for ee/mm
        # puWobs doesn't exist for embedded sample and lumi normalisation only applies for MC
        # select the dy -> tt mc events decaying only in ee/mm, in other words:
        # remove the mc (ds==37) events which are not tau decays (truth !=2) or are em/me (ch > 1.5)
        weights['DYTT']              = self._stdWgt+'*(!( dataset == 36 || dataset == 37 ) || (mctruth == 2 && channel<1.5))'
        weights['DYLL']              = self._stdWgt+'*(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))*(channel<1.5)'
        weights['DYee']              = self._stdWgt+'*(channel<1.5)'
        weights['DYmm']              = self._stdWgt+'*(channel<1.5)'
        weights['DYLL-template']     = self._stdWgt+'* dyW *(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))'
        weights['DYLL-templatesyst'] = self._stdWgt+'*dyWUp*(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))'
        #filter for buggy events in dataset==082
        weights['Vg']                = self._stdWgt+'*(dataset!=082 || (chmet<(0.75*pt1+100) && chmet<(0.75*jetpt1+100)))'
        weights['ggH']               = self._stdWgt+'*kfW'
        weights['vbfH']              = self._stdWgt+'*kfW'


        if cat in ['2j']:
            weights['WW']                = self._stdWgt+'*2'


        if var in ['bdts','bdtl']:
            weights['WW']       = self._stdWgt+'*2*(event%2 == 0)'
            weights['ggH']      = self._stdWgt+'*2*kfW*(event%2 == 0)'
            weights['vbfH']     = self._stdWgt+'*2*kfW*(event%2 == 0)'
            weights['wzttH']    = self._stdWgt+'*2*(event%2 == 0)'
            # TODO Signal injection weights, if available
            weights['ggH-SI']   = self._stdWgt+'*2*kfW*(event%2 == 0)'
            weights['vbfH-SI']  = self._stdWgt+'*2*kfW*(event%2 == 0)'
            weights['wzttH-SI'] = self._stdWgt+'*2*(event%2 == 0)'

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


    # _____________________________________________________________________________
    @staticmethod
    def _bins2hclass( bins ):
        '''
        Fixed bin width
        bins = (nx,xmin,xmax)
        bins = (nx,xmin,xmax, ny,ymin,ymax)
        Variable bin width
        bins = ([x0,...,xn])
        bins = ([x0,...,xn],[y0,...,ym])
        
        '''

        from array import array
        if not bins:
            return name,0
        elif not ( isinstance(bins, tuple) or isinstance(bins,list)):
            raise RuntimeError('bin must be an ntuple or an arryas')

        l = len(bins)
        # 1D variable binning
        if l == 1 and isinstance(bins[0],list):
            ndim=1
            hclass = ROOT.TH1D
            xbins = bins[0]
            hargs = (len(xbins)-1, array('d',xbins))
        elif l == 2 and  isinstance(bins[0],list) and  isinstance(bins[1],list):
            ndim=2
            hclass = ROOT.TH2D
            xbins = bins[0]
            ybins = bins[1]
            hargs = (len(xbins)-1, array('d',xbins),
                    len(ybins)-1, array('d',ybins))
        elif l == 3:
            # nx,xmin,xmax
            ndim=1
            hclass = ROOT.TH1D
            hargs = bins
        elif l == 6:
            # nx,xmin,xmax,ny,ymin,ymax
            ndim=2
            hclass = ROOT.TH2D
            hargs = bins
        else:
            # only 1d or 2 d hist
            raise RuntimeError('What a mess!!! bin malformed!')
        
        return hclass,hargs,ndim

    @staticmethod
    def _bins2dim(bins):
        hclass,hargs,ndim = ShapeFactory._bins2hclass( bins )
        return ndim

    @staticmethod
    def _makeshape( name, bins ):
        hclass,hargs,ndim = ShapeFactory._bins2hclass( bins )
        return hclass(name, name, *hargs)


    
    # _____________________________________________________________________________
    @staticmethod
    def _projexpr( bins = None ):
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
        return hdef,ndim

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

    parser.add_option('--tag'            , dest='tag'            , help='Tag used for the shape file name'           , default=None)
    parser.add_option('--selection'      , dest='selection'      , help='Selection cut'                              , default=None)
    parser.add_option('--dataset'        , dest='dataset'        , help='Dataset to process'                         , default=None)
    parser.add_option('--mcset'          , dest='mcset'          , help='Mcset to process'                           , default=None)
    parser.add_option('--path_latino'    , dest='path_latino'    , help='Root of the master trees'                   , default=None)
    parser.add_option('--path_bdt'       , dest='path_bdt'       , help='Root of the friendly bdt trees'             , default=None)
    parser.add_option('--path_shape_raw' , dest='path_shape_raw' , help='Destination directory of nominals'          , default=None)
    parser.add_option('--range'          , dest='range'          , help='Range (optional default is var)'            , default=None)
    parser.add_option('--splitmode'      , dest='splitmode'      , help='Split in channels using a second selection' , default=None)

    parser.add_option('--keep2d',        dest='keep2d',     help='Keep 2d histograms (no unrolling)',     action='store_true',    default=False)
    parser.add_option('--no-noms',       dest='makeNoms',   help='Do not produce the nominal',            action='store_false',   default=True)
    parser.add_option('--no-syst',       dest='makeSyst',   help='Do not produce the systematics',        action='store_false',   default=True)
    parser.add_option('--do-syst',       dest='doSyst',     help='Do only one systematic',                default=None)
    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)
    (opt, args) = parser.parse_args()

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()

    if not opt.debug:
        pass
    elif opt.debug == 2:
        print 'Logging level set to DEBUG (%d)' % opt.debug
        logging.basicConfig(level=logging.DEBUG)
    elif opt.debug == 1:
        print 'Logging level set to INFO (%d)' % opt.debug
        logging.basicConfig(level=logging.INFO)

    try:
#    if True:
        checks = [
            ('mcset','MonteCarlo not defined'),
            ('dataset','Dataset not defined'),
            ('selection','Selection not defined'),
            ('path_latino','Master tree path not defined'),
            ('path_shape_raw','Where shall I put the shapes?'),
        ]
        
        for dest,msg in checks:
            if not getattr(opt,dest):
                parser.print_help()
                parser.error(msg)

        if not opt.range:
            opt.range = opt.variable

        tag       = opt.tag if opt.tag else opt.variable
        variable  = opt.variable
        selection = opt.selection

        latinoDir           = opt.path_latino
        bdtDir              = opt.path_bdt
        nomOutDir           = os.path.join(opt.path_shape_raw,'nominals/')
        systOutDir          = os.path.join(opt.path_shape_raw,'systematics/')
        
        nomInputDir         = ''
        systInputDir        = '{syst}/'

        nominalOutFile      = 'shape_Mh{mass}_{category}_'+tag+'_shapePreSel_{flavor}.root'
        systematicsOutFile  = 'shape_Mh{mass}_{category}_'+tag+'_shapePreSel_{flavor}_{nick}.root'
        
        factory = ShapeFactory()
        factory._outFileFmt  = nominalOutFile

        masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]
        factory._masses   = masses

        # go through final channels
        factory._channels = dict([ (k,v) for k,v in hwwinfo.channels.iteritems() if k in opt.chans])
        print factory._channels

        factory._paths['base']  = latinoDir
        factory._paths['bdtl']  = bdtDir
        factory._paths['bdts']  = bdtDir

        factory._dataTag   = opt.dataset
        factory._mcTag     = opt.mcset
        factory._range     = opt.range
        factory._splitmode = opt.splitmode
        factory._lumi      = opt.lumi


        if opt.makeNoms:
            # nominal shapes
            print factory.makeNominals(variable,selection,nomInputDir,nomOutDir+nominalOutFile)

        if opt.makeSyst:
            class Systematics:
                def __init__(self,name,nick,indir,mask):
                    pass
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

            systByWeight = {}
            systByWeight['leptonEfficiency_down'] = 'effWDown/effW'
            systByWeight['leptonEfficiency_up']   = 'effWUp/effW'

            factory._systByWeight = systByWeight

            processMask = ['ggH', 'vbfH', 'ggWW', 'Top', 'WW', 'VV']
            systMasks = dict([(s,processMask[:]) for s in systematics])
            systDirs  = dict([(s,systInputDir if s not in systByWeight else 'nominals/' ) for s in systematics])

            print systDirs

            for syst,mask in systMasks.iteritems():
                if opt.doSyst and opt.doSyst != syst:
                    continue
                print '-'*80
                print ' Processing',syst,'for samples',' '.join(mask)
                print '-'*80
                files = factory.makeSystematics(variable,selection,syst,mask,systDirs[syst],systOutDir+systematicsOutFile, nicks=systematics)

    except Exception as e:
        print '*'*80
        print 'Fatal exception '+type(e).__name__+': '+str(e)
        print '*'*80
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=sys.stdout)
#         traceback.print_tb(exc_traceback, limit=3, file=sys.stdout)
        print '*'*80
    finally:
        print 'Used options'
        print ', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()])
