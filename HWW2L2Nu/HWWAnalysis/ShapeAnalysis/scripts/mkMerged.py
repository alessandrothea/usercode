#!/usr/bin/env python

import sys
import ROOT
import os
import re
import glob
import optparse
import hwwinfo
import hwwtools
import numpy
import array
import bisect
import datadriven
import logging

#  __  __                      
# |  \/  |___ _ _ __ _ ___ _ _ 
# | |\/| / -_) '_/ _` / -_) '_|
# |_|  |_\___|_| \__, \___|_|  
#                |___/         


class ShapeMerger:
    _logger = logging.getLogger('ShapeMerger')
    def __init__(self):
        self.sets = []
        self.histograms = {}

    def add(self,s):
        # add a collection to be summed
        self.sets.append(s)

    def sum(self):
        # sum the collections together
        if len(self.sets) == 0:
            print 'No sets defined'
            return
        signals = ['ggH', 'vbfH', 'wzttH']
        
        # build an histogram template
        shapes = {}
        
        # loop over all the sets
        for s in self.sets:
            for n,h in s.histograms.iteritems():
                if n in shapes:
                    continue
                # ->> ninja
                dummy = h.Clone()

                dummy.Reset()
                shapes[n] = dummy

        for n,h in shapes.iteritems():
            for s in self.sets:
                if n not in s.histograms:
                    self._logger.info('Warning: '+n+' is not available in set '+s.label)
                    continue
#                 h.Add(s.histograms[n])
                dummy = s.histograms[n]
                h2add = dummy.Clone()
                h.Add(h2add)

            # remove the negative bins before storing it
            self._removeNegativeBins(h)
            self.histograms[n] = h


    def injectSignal(self):
        signals = ['ggH', 'vbfH', 'wzttH']
        if 'Data' in self.histograms:
            return

        print ' '*4+' - injecting signal!'
        nomRegex = re.compile('^([^ ]+)$')

        injected = [ n for n in self.histograms if '-SI' in n and nomRegex.match(n) ]
        backgrounds = [ n for n in self.histograms if n not in injected and n not in signals and nomRegex.match(n) ]

#         if not len(injected):
#             raise RuntimeError('No injected histograms. And now?')

        pseudo = self.histograms[backgrounds[0]].Clone('histo_PseudoData')
        pseudo.SetTitle('Data')
        pseudo.Reset()
        inputs = []
        inputs.extend(injected)
        inputs.extend(backgrounds)

        print injected
        print backgrounds

        for n in inputs:
#             self.histograms[n].Print()
            pseudo.Add(self.histograms[n])

        for n in injected:
            self.histograms.pop(n)

        nBins = pseudo.GetNbinsX()
        xax = pseudo.GetXaxis()

        data = pseudo.Clone('histo_Data')
        data.SetTitle('Data')
        data.Reset()

        for i in xrange(1,nBins+1):
            entries = ROOT.TMath.Nint(pseudo.GetAt(i)) 
            for j in xrange(entries):
                data.Fill(xax.GetBinCenter(i))

        self.histograms['Data'] = data


    def _removeNegativeBins(self,h):
        # move it in the merger as last step
        # TODO

        integral = h.Integral() if h.Integral() >=0 else 0.001 
        for i in xrange(1,h.GetNbinsX()+1):
            c = h.GetBinContent(i)
            if c < 0.:
                h.SetAt(0.,i)
        if 'WJet' in h.GetName():
            self._logger.debug('/'*50)
            self._logger.debug('{0:<50} {1} {2}'.format(h.GetName().ljust(50),integral,h.Integral()))
            self._logger.debug('/'*50)

        if h.Integral() > 0:
            h.Scale(integral/h.Integral())
#         print 'Integral', integral, h.Integral()

    def applyDataDriven(self, estimates):
        ''' rescale to the data driven estimates if available'''
        for p,e in estimates.iteritems():
            nominal = self.histograms[p]
#             if nominal.Integral() == 0:
#                 print 'Empty histogram',p,': Data driven rescaling skipped'
#                 continue
            proRegex = re.compile('^'+p+' .+')
            shapes = [ h for n,h in self.histograms.iteritems() if proRegex.match(n) ]
#             if p == 'DYLL':
#                 print '+'*20
#                 print p,' Nsig', e.Nsig(),'  Nctrl', e.Nctr,' alpha', e.alpha,'dalpha',e.delta
#                 print p,nominal.Integral()
#                 print '+'*20
#             factor = e.Nsig()/nominal.Integral()
            shapes.append(nominal)

            for shape in shapes:
                if shape.Integral() == 0.: 
                    self._logger.warning('Empty histogram: '+p)
                    continue
                shape.Scale(e.Nsig()/shape.Integral())

    def applyDataDrivenRelative(self, estimates):
        ''' rescale to the data driven estimates if available'''
        for p,e in estimates.iteritems():
            print 'DEBUG ---> DD',p
            nominal = self.histograms[p]
            if nominal.Integral() == 0:
                print 'Empty histogram',p,': Data driven rescaling skipped'
                continue
            proRegex = re.compile('^'+p+' .+')
            shapes = [ h for n,h in self.histograms.iteritems() if proRegex.match(n) ]
            if p == 'DYLL':
                print '+'*20
                print p,' Nsig', e.Nsig(),'  Nctrl', e.Nctr,' alpha', e.alpha,'dalpha',e.delta
                print p,nominal.Integral()
                print '+'*20
            factor = e.Nsig()/nominal.Integral()
            shapes.append(nominal)

            for shape in shapes:
                shape.Scale(factor)

    def save(self, path):
        # save the final output file
        outFile = ROOT.TFile.Open(path,'recreate')
        for n,h in self.histograms.iteritems():
            if 'DYLL' in n:
               self._logger.debug('{0} {1}'.format(n,h.Integral()))
            h.Write()
        outFile.Close()



#  __  __ _             
# |  \/  (_)_ _____ _ _ 
# | |\/| | \ \ / -_) '_|
# |_|  |_|_/_\_\___|_|  


class ShapeMixer:
    _logger = logging.getLogger('ShapeMixer')
    def __init__(self, label):
        self.label = label
        self.rebin = 1
        self.nominalsPath = None
        self.systSearchPath = None
        self.histograms = {}

        self.nominals = {}
        self.statistical = {}
        self.experimental = {}
        self.generators = {}
        self.fakerate = {}
        self.templates = {}
        
        self.factors = {}
        self.indent = 4
        self.nameMap = {}
        self.lumiMask = []
        self.lumi = 1.

    def __del__(self):
        self._disconnect()
    
    def _connect(self):
        self._logger.debug('Opening '+self.nominalsPath)
        if not os.path.exists(self.nominalsPath):
            raise IOError('Root file '+self.nominalsPath+' doesn\'t exists.')
        self.shapeFile = ROOT.TFile.Open(self.nominalsPath)
        self.systFiles = {}
#         print self.systSearchPath
        for file in glob.glob(self.systSearchPath):
            m = re.search('_(e|m)(e|m)_(.*).root',file)
            if m is None:
                raise NameError('something went wrong, this \''+file+'\' doesn\'t look like a experimental file')
            self.systFiles[m.group(3)] = ROOT.TFile.Open(file)
#             print 'TFile',file,'opened'

    def _remodel(self,h):
        nBins = h.GetNbinsX()
        entries = h.GetEntries()
        underFlow = h.GetBinContent(0)
        overFlow  = h.GetBinContent(nBins+1)
        bin1      = h.GetBinContent(1)
        binN      = h.GetBinContent(nBins)

        h.SetAt(0.,0)
        h.SetAt(underFlow+bin1,1)
        h.SetAt(overFlow+binN, nBins)
        h.SetAt(0.,nBins+1,)
        h.Rebin(self.rebin)


    def _mirror(self,process, nom, shift, systName, scale2Nom = False):
        up = shift.Clone('histo_'+process+'_'+systName+'Up')
        up.SetTitle(process+' '+systName+' Up')
        # rescale before mirroring, if necessary
        if scale2Nom:
            up.Scale(nom.Integral()/up.Integral())

        down = nom.Clone('histo_'+process+'_'+systName+'Down')
        down.SetTitle(process+' '+systName+' Down')
        down.Scale(2.)
        down.Add(up,-1)
        # rescale if necessary
        if scale2Nom:
            down.Scale(nom.Integral()/down.Integral())

        return (up, down)



#     def mix(self, cat, flavor):
    def mix(self, chan):
        # mixing histograms

        self._connect()


        # -----------------------------------------------------------------
        # Nominal shapes
        #
        for k in self.shapeFile.GetListOfKeys():
            h = k.ReadObj()
            self._remodel(h)
            self.nominals[h.GetTitle()] = h

        # -----------------------------------------------------------------
        # WJet shape syst
        #
        #   add the WJets shape systematics derived from miscalculated weights
        #   down is mirrored
        wJet = self.nominals['WJet']
        if 'WJetFakeRate' in self.nominals: 
            wJetEff = self.nominals.pop('WJetFakeRate')
            wJetSystName = 'CMS_hww_WJet_FakeRate_jet_shape'
            wJetShapeUp = wJetEff.Clone('histo_WJet_'+wJetSystName+'Up')
            wJetShapeUp.SetTitle('WJet '+wJetSystName+' Up')
            wJetShapeUp.Scale(wJet.Integral()/wJetShapeUp.Integral())
            self.fakerate[wJetShapeUp.GetTitle()] = wJetShapeUp

            wJetShapeDown = wJet.Clone('histo_WJet_'+wJetSystName+'Down')
            wJetShapeDown.SetTitle('WJet '+wJetSystName+' Down')
            wJetShapeDown.Scale(2)
            wJetShapeDown.Add(wJetShapeUp,-1)
            wJetShapeDown.Scale(wJet.Integral()/wJetShapeDown.Integral())
            self.fakerate[wJetShapeDown.GetTitle()] = wJetShapeDown

        # -----------------------------------------------------------------
        # DY shape syst
        #
        #   take the shape from the pfmet loosened sample
        #   down is mirrored
        if 'DYLLtemplate' in self.nominals:
            dyLLmc = self.nominals.pop('DYLL')
            dyLLShape = self.nominals.pop('DYLLtemplate')
            dyLLShapeSyst = self.nominals.pop('DYLLtemplatesyst')
            dyLLSystName = 'CMS_hww_DYLL_template_shape'

            dyLLnom = dyLLShape.Clone('histo_DYLL')
            dyLLnom.SetTitle('DYLL')
            if dyLLnom.Integral() == 0.:
                # no entries in the reference shape
                # so what?
                if dyLLmc.Integral() != 0.:
    #                 raise ValueError('DYLL shape template has 0. integral, but the standard mc is not ('+str(dyLLmc.Integral())+')')
                    self._logger.warn('DYLL shape template has 0. integral, but the standard mc is not ('+str(dyLLmc.Integral())+')')
                    self.nominals['DYLL'] = dyLLmc
                else:
                    self.nominals['DYLL'] = dyLLnom
            else:
                dyLLnom.Scale( (dyLLmc.Integral() if dyLLmc.Integral() != 0. else 0.001)/dyLLnom.Integral() )
                self.nominals['DYLL'] = dyLLnom
                
                # no shape systematic
                if dyLLShapeSyst.Integral() != 0.:
                    dyLLShapeUp, dyLLShapeDown = self._mirror('DYLL',dyLLnom,dyLLShapeSyst, dyLLSystName,True)

                    self.templates[dyLLShapeUp.GetTitle()] = dyLLShapeUp
                    self.templates[dyLLShapeDown.GetTitle()] = dyLLShapeDown

        # anyway put some nominal back


        # -----------------------------------------------------------------
        # DYLL shape systematics
        #
        #
        #
        if False and 'DYLL' in self.nominals and 'DYLLctrZ' in self.nominals:
            print ' '*self.indent+'  + Replacing DY wil DYctrZ'
            dy = self.nominals['DYLL']
            dyCtrZ = self.nominals['DYLLctrZ']
            print '*'*20
            print 'DYLL',dy.Integral() == 0.,dy.Integral()
            print 'DYLLctrZ',dyCtrZ.Integral()==0,dyCtrZ.Integral()
            print '*'*20

            if dyCtrZ.Integral() == 0.:
                print ' '*self.indent+'  WARNING: DYctrZ is 0, MC is the reference now'
            else:
                self.nominals.pop('DYLL')
                if dy.Integral() == 0. :
                    print ' '*self.indent+'  WARNING: empty DY, the rescaling will be done by the DD estimates. Rescaling to 0.001'
                    dyCtrZ.Scale(0.001/dyCtrZ.Integral())
                else:
                    dyCtrZ.Scale(dy.Integral()/dyCtrZ.Integral())

                dyCtrZ.SetNameTitle(dy.GetName(), dy.GetTitle())
                self.nominals['DYLL'] = dyCtrZ
#             elif dyCtrZ.Integral() != 0:   
#                 self.nominals.pop('DYLL')
#                 self.nominals['DYLL'] = dyCtrZ
            self.nominals.pop('DYLLctrZ')
            print '*'*20
            print 'DYLL',dy.Integral() == 0.,dy.Integral()
            print 'DYLLctrZ',dyCtrZ.Integral()==0,dyCtrZ.Integral()
            print self.nominals.keys()
            print '*'*20


        #
        # WW generator shapes
        #
        mcAtNLO = {} 
        madWW = self.nominals['WW']
        wwNLOs = ['WWnlo','WWnloUp','WWnloDown',]

        if set(wwNLOs).issubset(self.nominals):
            for t in wwNLOs:
                mcAtNLO[t] = self.nominals[t]
                del self.nominals[t]

            wwGenUp = mcAtNLO['WWnlo'].Clone('histo_WW_Gen_nlo_WWUp')
            wwGenUp.SetTitle('WW Gen_nlo_WW Up')
            wwGenUp.Scale(madWW.Integral()/wwGenUp.Integral())
            self.generators[wwGenUp.GetTitle()] = wwGenUp

            #copy the nominal
            wwGenDown = madWW.Clone('histo_WW_Gen_nlo_WWDown')
            wwGenDown.SetTitle('WW Gen_nlo_WW Down')
            wwGenDown.Scale(2.)
            wwGenDown.Add(wwGenUp, -1)
            wwGenDown.Scale(madWW.Integral()/wwGenDown.Integral())
            self.generators[wwGenDown.GetTitle()] = wwGenDown


            # MC@NLO scale
            wwScaleUp = mcAtNLO['WWnloUp'].Clone('histo_WW_Gen_scale_WWUp')
            wwScaleUp.SetTitle('WW Gen_scale_WW Up')
            wwScaleUp.Divide(mcAtNLO['WWnlo'])
            wwScaleUp.Multiply(madWW)
            wwScaleUp.Scale(madWW.Integral()/wwScaleUp.Integral())
            self.generators[wwScaleUp.GetTitle()] = wwScaleUp

            wwScaleDown = mcAtNLO['WWnloDown'].Clone('histo_WW_Gen_scale_WWDown')
            wwScaleDown.SetTitle('WW Gen_scale_WW Down')
            wwScaleDown.Divide(mcAtNLO['WWnlo'])
            wwScaleDown.Multiply(madWW)
            wwScaleDown.Scale(madWW.Integral()/wwScaleDown.Integral())
            self.generators[wwScaleDown.GetTitle()] = wwScaleDown

        #
        # Statistical
        #
        for n,h in self.nominals.iteritems():
            # skip data or injected sample
            if n in ['Data'] or '-SI' in n:
                continue
            if h.GetEntries() == 0. and h.Integral() == 0.0:
                self._logger.info('Warning: nominal shape '+n+' is empty. The stat histograms won\'t be produced')
                continue
#             if n in ['DYTT']:
#                 print n,h.GetEntries(),h.Integral()
#             effName = 'CMS_hww_{0}_{1}_{2}_stat_shape'.format(n,flavor,cat)
            effName = 'CMS_hww_{0}_{1}_stat_shape'.format(n,chan)

            statName  = h.GetName()+'_'+effName
            statTitle = h.GetTitle()+' '+effName
            # clone the nominal twice
            statUp = h.Clone(statName+'Up')
            statUp.SetTitle(statTitle+' Up')
            for i in xrange(1,statUp.GetNbinsX()+1):
                c = statUp.GetBinContent(i)
                e = statUp.GetBinError(i)
                statUp.SetAt(c+e if c+e > 0. else c*0.001,i)
            # rescale to the original, shape only
            if statUp.Integral() != 0.:
                statUp.Scale(h.Integral()/statUp.Integral())
            self.statistical[statUp.GetTitle()] = statUp

            # clone the nominal twice
            statDown = h.Clone(statName+'Down')
            statDown.SetTitle(statTitle+' Down')
            for i in xrange(1,statDown.GetNbinsX()+1):
                c = statDown.GetBinContent(i)
                e = statDown.GetBinError(i)
                statDown.SetAt(c-e if c-e > 0.0 else c*0.001,i)
            # rescale to the original, shape only
            if statDown.Integral() != 0.:
                statDown.Scale(h.Integral()/statDown.Integral())
            self.statistical[statDown.GetTitle()] = statDown
        #
        # Experimental
       #
        udRegex = re.compile("(.+)(Up|Down)$")
#         print self.histograms
        allSysts = {}
        for n,syst in self.systFiles.iteritems():
            histograms = []
            for k in syst.GetListOfKeys():
                h = k.ReadObj()
                self._remodel(h)
                histograms.append(h)

            m = udRegex.match(n)
            if m is not None:
                systName = 'CMS_'+m.group(1)
                systShift = m.group(2)
                # x-check on the regex match
                if not( n.endswith('Up') or n.endswith('Down') ):
                    raise RuntimeError(n+' doesn\'t end with Up or Down!')

                for h in histograms:
                    
                    if not h.GetTitle() in self.nominals:
                        raise RuntimeError('Systematic '+h.GetTitle()+' found, but no nominal shape')
                    h.SetName(h.GetName()+'_'+systName+systShift)
                    h.SetTitle(h.GetTitle()+' '+systName+' '+systShift)
                    self.experimental[h.GetTitle()] = h
            else:
                systName = 'CMS_'+n

                for h in histograms:
                    if not h.GetTitle() in self.nominals:
                        raise RuntimeError('Systematic '+h.GetTitle()+' found, but no nominal shape')
                    # we call up the shape taken from the experimental file
                    systUp = h.Clone(h.GetName()+'_'+systName+'Up')
                    systUp.SetTitle(h.GetTitle()+' '+systName+' Up')
                    self.experimental[systUp.GetTitle()] = systUp

                    # copy the nominal histogram
                    systDown = self.nominals[h.GetTitle()].Clone(h.GetName()+'_'+systName+'Down')
                    systDown.SetTitle(h.GetTitle()+' '+systName+' Down')
                    systDown.Scale(2)
                    systDown.Add(systUp,-1)
                    self.experimental[systDown.GetTitle()] = systDown

#             print 'systName:',systName,n
#         print 'Systematics',',\n'.join([ n+';'+h.GetName() for n,h in self.experimental.iteritems()])
#         print 'Nominals','\n'.join([ n+';'+h.GetName()+';'+h.GetTitle() for n,h in self.nominals.iteritems()])

        # add the nominals and the experimental to 1 container
        self.histograms.update(self.nominals)
        self.histograms.update(self.fakerate)
        self.histograms.update(self.templates)
        self.histograms.update(self.generators)
        self.histograms.update(self.statistical)
        self.histograms.update(self.experimental)

#         sys.exit(0)

    def scale2Nominals(self, list ):
        if not list:
            return

        print '   - Scaling systematic shapes to nominal:',
        sanityCheck = dict([(ss,0) for ss in list])

        for name,hSys in self.experimental.iteritems():
            tokens = name.split()
            sample = tokens[0]
            syst   = tokens[1]
            for iSample,iSyst in list:
                if not ( (iSample == '*' or iSample == sample) and (iSyst == '*' or iSyst == syst) ):
                    continue
                sanityCheck[(iSample,iSyst)] += 1
                if sample not in self.nominals:
                    raise RuntimeError('Nominal histogram '+sample+' not found')
                hNom = self.nominals[sample]
                hSys.Scale(hNom.Integral()/hSys.Integral())
        
        for ss,k in sanityCheck.iteritems():
            if k == 0:
                raise NameError('sample,systematic pair not found '+ss[0]+':'+ss[1])

        
    def _rename(self):
        print '   - Renaming'
        histograms2 = {}
        for (n,h) in self.histograms.iteritems():
            if n in self.nameMap:
                nn = self.nameMap[n]
                h.SetName('histo_'+nn)
                h.SetTitle(nn)
                histograms2[nn] = h
            else:
                histograms2[n] = h

        self.histograms = histograms2


    def applyScaleFactors(self, factors):
        print '    - Applying scaling factors'
        for n,h in self.histograms.iteritems():
            # get the identification token
            type = n.split()[0]
            if type in factors:
#                 print n,factors[type]
                h.Scale(factors[type])

            if not type in self.lumiMask:
                h.Scale(self.lumi)

    def close(self):
        self._disconnect()

    def _disconnect(self):
        if hasattr(self,'shapeFile'):
            self.shapeFile.Close()

        if hasattr(self,'systFiles'):
            for n,f in self.systFiles.iteritems():
                f.Close()





if __name__ == '__main__':
    print '''
-------------------------------------------------------------------------------
  ______     _ _  _____ _                      __  __                          
 |  ____|   (_) |/ ____| |                    |  \/  |                         
 | |____   ___| | (___ | |__   __ _ _ __   ___| \  / | ___ _ __ __ _  ___ _ __ 
 |  __\ \ / / | |\___ \| '_ \ / _` | '_ \ / _ \ |\/| |/ _ \ '__/ _` |/ _ \ '__|
 | |___\ V /| | |____) | | | | (_| | |_) |  __/ |  | |  __/ | | (_| |  __/ |   
 |______\_/ |_|_|_____/|_| |_|\__,_| .__/ \___|_|  |_|\___|_|  \__, |\___|_|   
                                   | |                          __/ |          
                                   |_|                         |___/           
-------------------------------------------------------------------------------
'''
#     logging.basicConfig(level=logging.DEBUG)
    mypath = os.path.dirname(os.path.abspath(__file__))
    #  ___       __           _ _      
    # |   \ ___ / _|__ _ _  _| | |_ ___
    # | |) / -_)  _/ _` | || | |  _(_-<
    # |___/\___|_| \__,_|\_,_|_|\__/__/
#     scaleFactorPath   = '/shome/thea/HWW/ShapeAnalysis/data/datamcsf.txt'

    usage = 'usage: %prog -s sample1:syst1,sample2:* [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-n', '--dry', dest='dry', help='Dry run', action='store_true' )
    parser.add_option('-r', '--rebin', dest='rebin', help='Rebin by', default='1')
    parser.add_option('-s', '--scale',help='Scale sample by an additional factor (overwrides previously defined factors)', action='append',default=[])

    parser.add_option('--path_dd'           , dest='path_dd'           , help='Data driven path'                 , default=None)
    parser.add_option('--path_scale'        , dest='path_scale'        , help='Scale factors'                    , default=None)
    parser.add_option('--path_shape_raw'    , dest='path_shape_raw'    , help='Input directory of raw shapes'    , default=None)
    parser.add_option('--path_shape_merged' , dest='path_shape_merged' , help='Destination directory for merged' , default=None)

# discontined
#     parser.add_option('--scale2nominal', dest='scale2nom', help='Systematics to normalize to nominal ', default='')
#     parser.add_option('--ninja', dest='ninja', help='Ninja', action='store_true', default=False )

    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)


    (opt, args) = parser.parse_args()


    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()

    if not opt.debug:
        pass
    elif opt.debug > 0:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug('Used options')
    logging.debug(', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()]))
    #  ___                         _              
    # | _ \__ _ _ _ __ _ _ __  ___| |_ ___ _ _ ___
    # |  _/ _` | '_/ _` | '  \/ -_)  _/ -_) '_(_-<
    # |_| \__,_|_| \__,_|_|_|_\___|\__\___|_| /__/
    #                                             

    nomPath   = opt.path_shape_raw+'/nominals/' 
    systPath  = opt.path_shape_raw+'/systematics/' 
    mergedDir = opt.path_shape_merged
    rebin     = int(opt.rebin)

    masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]

    if not opt.var or not opt.lumi:
        parser.error('The variable and the luminosty must be defined')
    lumi = opt.lumi
    var = opt.var
    lumiMask = ['Data','WJet']
    nameTmpl  = 'shape_Mh{0}_{1}_'+var+'_shapePreSel_{2}'
    os.system('mkdir -p '+mergedDir)

   
    # read the scale factors from the scale factors file 

    if opt.path_scale:
        scaleFactors = {}
        for cat in hwwinfo.categories:
            factors = {}
            scaleFactors[cat] = factors
            scalepath = opt.path_scale.format(category=cat)
            try:
                f = open(scalepath)
                for l in f.readlines():
                    tokens = l.split()
                    factors[tokens[0]] = float(tokens[1])
                logging.defined('Scale factor file '+scalepath+' loaded')
            except IOError as ioe:
                logging.debug('File '+scalepath+' not found')

            # cmd line override
            for o in opt.scale:
                tokens = o.split('=')
                if len(tokens) != 2:
                    parser.print_help()
                    parser.error('Scale option syntax is -s <sample>=<value>')
            
                print cat,'Scale override:',tokens[0],tokens[1]
                factors[tokens[0]] = float(tokens[1])
    else:
        scaleFactors = dict([ (cat,{}) for cat in hwwinfo.categories])




    logging.debug('Scale Factors: '+str(scaleFactors))


    ROOT.TH1.SetDefaultSumw2(True)

#     scale2NomList = []
#     for entry in opt.scale2nom.split(','):
#         if entry == '':
#             continue
#         tokens = entry.split(':')
#         if len(tokens) != 2:
#             parser.error('scale2nom: syntax error in token '+entry)
#         scale2NomList.append( (tokens[0], tokens[1]) )
#     print scale2NomList

#     channels = {}
#     channels['of_0j'] = ('0j',['em','me'])
#     channels['of_1j'] = ('1j',['em','me'])
#     channels['sf_0j'] = ('0j',['mm','ee'])
#     channels['sf_1j'] = ('1j',['mm','ee'])
#     channels['of_0j'] = ('0j',['em','me'])
#     channels['vbf']   = ('vbf',['mm','ee','em','me'])



#  _                  
# | |   ___  ___ _ __ 
# | |__/ _ \/ _ \ '_ \
# |____\___/\___/ .__/
#               |_|   
#     
    reader = datadriven.DDCardReader( opt.path_dd )

    channels =  dict([ (k,v) for k,v in hwwinfo.channels.iteritems() if k in opt.chans])

    for mass in masses:
        for chan,(cat,fl) in channels.iteritems():
            flavors = hwwinfo.flavors[fl]
            print chan,cat,fl,flavors
            # open output file
            m = ShapeMerger()
            print '-'*100
            print 'ooo Processing',mass, chan
            print '-'*100


            for fl in flavors:
                print '  o Channel:',fl
                # configure
                label = 'mH{0} {1} {2}'.format(mass,cat,fl)
                ss = ShapeMixer(label)
                ss.nominalsPath   = os.path.join(nomPath,nameTmpl.format(mass, cat, fl)+'.root')
                ss.systSearchPath = os.path.join(systPath,nameTmpl.format(mass, cat, fl)+'_*.root')
                ss.lumiMask = lumiMask
                ss.lumi = lumi
                ss.rebin = rebin

                # run
                print '     - mixing histograms'
                ss.mix(chan)

                ss.applyScaleFactors( scaleFactors[cat] )

                m.add(ss)
            print '  - summing sets'
            m.sum()

            
            if not reader.iszombie:
                print '  - data driven'
                (estimates,dummy) = reader.get(mass,chan)
                m.applyDataDriven( estimates )

            m.injectSignal()
            if not opt.dry:
                output = 'hww-{lumi:.2f}fb.mH{mass}.{channel}_shape.root'.format(lumi=lumi,mass=mass,channel=chan)
                path = os.path.join(mergedDir,output)
                print '  - writing to',path
                m.save(path)

    print 'Used options'
    print ', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()])
