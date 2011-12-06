#!/usr/bin/env python

import sys
import ROOT
import os
import re
import glob
import optparse
import hwwinfo
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
    def __init__(self):
        self.sets = []
        self.histograms = {}

    def add(self,s):
        # add a collection to be summed
        self.sets.append(s)

    def sum(self, ninja=False):
        # sum the collections together
        if len(self.sets) == 0:
            print 'No sets defined'
            return
        
        # build an histogram template
        shapes = {}

        if ninja:
            print 'Ninja mode ON'
            # take the nominals
            signals = ['ggH', 'vbfH', 'wzttH']

            # check hte nominals are the same everywhere
            all_nominals = set()
            for s in self.sets:
                all_nominals.update(set(s.nominals))

    #         print all_nominals
            
            for s in self.sets:
                missing = all_nominals-set(s.nominals)
                if len(missing) != 0:
                    print 'Missing histograms',
                    print '   ',', '.join(missing)


            backgrouns = [ n for n in all_nominals if n not in signals ]
    #         print backgrouns
            allbkgs = None
            for s in self.sets:
                for n,h in s.nominals.iteritems():
                    if n in signals or n == 'Data': continue
                    if not allbkgs:
                        allbkgs = h.Clone('allbkgs')
                        allbkgs.Reset()
                    allbkgs.Add(h)

            integral = numpy.ndarray( (allbkgs.GetNbinsX(),),dtype=numpy.double, buffer=allbkgs.GetIntegral() )
            nBins = 20

            xax = allbkgs.GetXaxis()
            xmin= xax.GetXmin()
            xmax= xax.GetXmax()

            lowEdges = array.array('d',[0.]*(nBins+1))
            for k in xrange(1,nBins):
                x = k*1./nBins
                i = bisect.bisect(integral,x)
                lowEdges[k] =  xax.GetBinLowEdge(i)
    #             print k,x,i, xax.GetBinLowEdge(i)
            lowEdges[0] = xmin
            lowEdges[nBins] = xmax 
        
        # loop over all the sets
        for s in self.sets:
            for n,h in s.histograms.iteritems():
                if n in shapes:
                    continue
#                 h_tmp = h.Clone()
#                 h_tmp = h.Rebin(nBins,h.GetName(),lowEdges)
                # ->> ninja
                dummy = h.Rebin(nBins,h.GetName(),lowEdges) if ninja else h.Clone()

                dummy.Reset()
                shapes[n] = dummy

#         names = self.sets[0].histograms.keys()
#         print ', '.join(shapes)
        for n,h in shapes.iteritems():
            for s in self.sets:
                if n not in s.histograms:
                    logging.info('Warning: '+n+' is not available in set '+s.label)
                    continue
#                 h.Add(s.histograms[n])
                dummy = s.histograms[n]
                h2add = dummy.Rebin(nBins,h.GetName(),lowEdges) if ninja else dummy.Clone()
                h.Add(h2add)
#                 h.Add(s.histograms[n].Rebin(nBins,h.GetName(),lowEdges))

            # remove the negative bins before storing it
            self._removeNegativeBins(h)
            self.histograms[n] = h

    def _removeNegativeBins(self,h):
        # move it in the merger as last step
        # TODO

        integral = h.Integral() if h.Integral() >=0 else 0.001 
        for i in xrange(1,h.GetNbinsX()+1):
            c = h.GetBinContent(i)
            if c < 0.:
                h.SetAt(0.,i)
        if 'WJet' in h.GetName():
            logging.debug('/'*50)
            logging.debug('{0:<50} {1} {2}'.format(h.GetName().ljust(50),integral,h.Integral()))
            logging.debug('/'*50)

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
                    logging.warning('Empty histogram: '+p)
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
               logging.debug('{0} {1}'.format(n,h.Integral()))
            h.Write()
        outFile.Close()



#  __  __ _             
# |  \/  (_)_ _____ _ _ 
# | |\/| | \ \ / -_) '_|
# |_|  |_|_/_\_\___|_|  


class ShapeMixer:
    def __init__(self, label):
        self.label = label
        self.rebin = 10
        self.shapePath      = None
        self.dyYieldPath      = None
        self.dyShapePath    = None
        self.systSearchPath = None
        self.histograms = {}

        self.nominals = {}
        self.statistical = {}
        self.experimental = {}
        self.generators = {}
        self.fakerate = {}
        self.templates = {}
        
        self.factors = {}
#         TODO clean up
#         self.replaceDrellYan = True
        self.indent = 4
        self.nameMap = {}
        self.lumiMask = []
        self.lumi = 1.

    def __del__(self):
        self._disconnect()
    
    def _connect(self):
        self.shapeFile = ROOT.TFile.Open(self.shapePath)
#         TODO clean up
#         if self.replaceDrellYan:
#             self.dyYieldFile   = ROOT.TFile.Open(self.dyYieldPath)
#             self.dyShapeFile = ROOT.TFile.Open(self.dyShapePath)
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



    def mix(self, jets, flavor):
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
        wJetEff = self.nominals.pop('WJetFakeRate')
        wJetSystName = 'CMS_hww_WJet_FakeRate_jet_shape'
        wJetShapeUp = wJetEff.Clone('histo_WJet_'+wJetSystName+'Up')
        wJetShapeUp.SetTitle('WJet '+wJetSystName+' Up')
        wJetShapeUp.Scale(wJet.Integral()/wJetShapeUp.Integral())
        self.fakerate[wJetShapeUp.GetTitle()] = wJetShapeUp

        wJetShapeDown = wJetEff.Clone('histo_WJet_'+wJetSystName+'Down')
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
        dyLLmc = self.nominals.pop('DYLL')
        dyLLShape = self.nominals.pop('DYLLtemplate')
        dyLLShapeSyst = self.nominals.pop('DYLLtemplatesyst')
        dyLLSystName = 'CMS_hww_DYLL_template_shape'

#         dyLLmc.Print()
#         dyLLShape.Print()
#         dyLLShapeSyst.Print()

        dyLLnom = dyLLShape.Clone('histo_DYLL')
        dyLLnom.SetTitle('DYLL')
        if dyLLnom.Integral() == 0.:
            # no entries in the reference shape
            # so what?
            if dyLLmc.Integral() != 0.:
#                 raise ValueError('DYLL shape template has 0. integral, but the standard mc is not ('+str(dyLLmc.Integral())+')')
                logging.warn('DYLL shape template has 0. integral, but the standard mc is not ('+str(dyLLmc.Integral())+')')
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


#         TODO cleanup
# outdated
#         if self.replaceDrellYan:
#             print ' '*self.indent+'  + Replacing DY'
#             self.nominals.pop('DYLL')
#             self.nominals.pop('DYTT')

#             # take the DY yields
#             dyYield    = self.dyYieldFile.Get('histo_DY')
#             dyTauYield = self.dyYieldFile.Get('histo_DYtau') 
#             self._remodel(dyYield)
#             self._remodel(dyTauYield)

#             dyShape    = self.dyShapeFile.Get('histo_DY')
#             dyTauShape = self.dyShapeFile.Get('histo_DYtau')
#             self._remodel(dyShape)
#             self._remodel(dyTauShape)

# #         print 'dyYield :',dyYield.Integral()

#             dyShape.Scale(dyYield.Integral()/dyShape.Integral())
#             self.nominals['DYLL'] = dyShape
# #         print 'dyShape rescaled :',dyShape.Integral()

#             dyTauShape.Scale(dyTauYield.Integral()/dyTauShape.Integral())
#             self.nominals['DYTT'] = dyTauShape

        # apply a 

        #
        # WW generator shapes
        #
        mcAtNLO = {} 
        madWW = self.nominals['WW']
        for t in ['WWnlo','WWnloUp','WWnloDown',]:
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
            if n in ['Data']:
                continue
            if h.GetEntries() == 0. and h.Integral() == 0.0:
                logging.info('Warning: nominal shape '+n+' is empty. The stat histograms won\'t be produced')
                continue
#             if n in ['DYTT']:
#                 print n,h.GetEntries(),h.Integral()
            effName = 'CMS_hww_{0}_{1}_{2}j_stat_shape'.format(n,flavor,jets)

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
#             print sample, syst
            for iSample,iSyst in list:
#                 print '-',iSample,iSyst,tokens[2]
                if not ( (iSample == '*' or iSample == sample) and (iSyst == '*' or iSyst == syst) ):
                    continue
#                     print 'rescaling ',sample, syst 
                sanityCheck[(iSample,iSyst)] += 1
#                     print '!!!!here'
                if sample not in self.nominals:
                    raise RuntimeError('Nominal histogram '+sample+' not found')
                hNom = self.nominals[sample]
#                 print 'rescale',hSys.GetName(),':',hSys.Integral(),hNom.Integral(),
                hSys.Scale(hNom.Integral()/hSys.Integral())
#                 print hSys.Integral()
#                 print name+', ',
#         print ''
        
        for ss,k in sanityCheck.iteritems():
            if k == 0:
                raise NameError('sample,systematic pair not found '+ss[0]+':'+ss[1])
#         print sanityCheck

        
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
        self.shapeFile.Close()
#         TODO clean up
#         if self.replaceDrellYan:
#             self.dyYieldFile.Close()
#             self.dyShapeFile.Close()

        for n,f in self.systFiles.iteritems():
            f.Close()





if __name__ == '__main__':
    print '-- MegaShapeMerger --'

#     logging.basicConfig(level=logging.DEBUG)
    mypath = os.path.dirname(os.path.abspath(__file__))
    #  ___       __           _ _      
    # |   \ ___ / _|__ _ _  _| | |_ ___
    # | |) / -_)  _/ _` | || | |  _(_-<
    # |___/\___|_| \__,_|\_,_|_|\__/__/
    #
    # dyYieldsPath contains the corect DY and DYTau yields
    # dyShapePath contains the proper DY/DYTau shape
    # 
    # use symbolic lynks only
    # Nominal, Syst, DYYield, DYShape
                                 
    defaultOutputPath = 'merged/'
    defaultNominalPath  = 'Nominal/'
    dyYieldsPath      = '/shome/mtakahashi/HWW/Limits/Oct21/inputhisto/DYWjets_WWsel/'
    dyShapePath       = '/shome/mtakahashi/HWW/Limits/Oct21/inputhisto/DYWjets_WWselL/'
    systPath          = 'SystMC/'
    scaleFactorPath   = '/shome/thea/HWW/ShapeAnalysis/data/datamcsf.txt'
#     dataDrivenPath    = '/shome/thea/HWW/ShapeAnalysis/data/AnalFull2011_BDT'


    usage = 'usage: %prog -s sample1:syst1,sample2:* [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('-n', '--dry', dest='dry', help='Dry run', action='store_true' )
    parser.add_option('-o', '--outdir', dest='output', help='Output directory', default=defaultOutputPath )
    parser.add_option('--replaceDY', dest='replaceDY', help=' Don\'t replace drell-yan shapes', action='store_true', default=False )
    parser.add_option('--scale2nominal', dest='scale2nom', help='Systematics to normalize to nominal ', default='')
    parser.add_option('-i', '--indir', dest='input', help='Input directory', default=defaultNominalPath)
    parser.add_option('-r', '--rebin', dest='rebin', help='Rebin by', default='1')
    parser.add_option('--ddpath', dest='ddpath', help='Data driven path', default=None)
    parser.add_option('--ninja', dest='ninja', help='Ninja', action='store_true', default=False )


    hwwinfo.addOptions(parser)
    hwwinfo.loadOptDefaults(parser)


    (opt, args) = parser.parse_args()

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()
    #     ROOT.gSystem.Load('libFWCoreFWLite')
    #     ROOT.AutoLibraryLoader.enable()

    #  ___                         _              
    # | _ \__ _ _ _ __ _ _ __  ___| |_ ___ _ _ ___
    # |  _/ _` | '_/ _` | '  \/ -_)  _/ -_) '_(_-<
    # |_| \__,_|_| \__,_|_|_|_\___|\__\___|_| /__/
    #                                             

    inputDir        = opt.input+'/' 
    outPath         = opt.output
    rebin           = int(opt.rebin)


    jets       = ['0','1']
    masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]

    if not opt.var or not opt.lumi:
        parser.error('The variable and the luminosty must be defined')
    lumi = opt.lumi
    var = opt.var
    lumiMask = ['Data','WJet']
    flavors = dict([('sf',['ee','mm']),('of',['em','me'])])
    nameTemplateXavier = 'R42X_R42X_Sc1_mtCut_H{0}_{1}jet_mllmtPreSel_{2}__MVAShape'
    nameTemplateMaiko  = 'histo_H{0}_{1}jet_'+var+'shapePreSel_{2}'
    os.system('mkdir -p '+outPath)

    # insert some printout HERE
    
    scaleFactors = [{},{}]
    f = open(scaleFactorPath)
    for l in f.readlines():
        tokens = l.split()
        scaleFactors[0][tokens[0]] = float(tokens[1])
        scaleFactors[1][tokens[0]] = float(tokens[2])


    ROOT.TH1.SetDefaultSumw2(True)

    scale2NomList = []
    for entry in opt.scale2nom.split(','):
        if entry == '':
            continue
        tokens = entry.split(':')
        if len(tokens) != 2:
            parser.error('scale2nom: syntax error in token '+entry)
        scale2NomList.append( (tokens[0], tokens[1]) )
#     print scale2NomList


#  _                  
# | |   ___  ___ _ __ 
# | |__/ _ \/ _ \ '_ \
# |____\___/\___/ .__/
#               |_|   
#     
    reader = datadriven.DDCardReader( opt.ddpath )

    for mass in masses:
        for njet in [0,1]:
            for fl,chans in flavors.iteritems():
                # open output file
#                 reader = DDCardReader(opt.ddpath, mass,njet,fl)
                m = ShapeMerger()
                print '-'*100
                print 'ooo Processing',mass, str(njet), fl
                print '-'*100
                for ch in chans:
                    print '  o Channel:',ch
                    # configure
                    label = 'mH{0} {1}njet {2}'.format(mass,njet,ch)
                    ss = ShapeMixer(label)
                    ss.shapePath      = inputDir+nameTemplateMaiko.format(mass, str(njet), ch)+'.root'
#                     ss.dyYieldPath    = dyYieldsPath+nameTemplateMaiko.format(mass, str(njet), ch)+'.root'
#                     ss.dyShapePath    = dyShapePath+nameTemplateMaiko.format(mass, str(njet), ch)+'.root'
                    ss.systSearchPath = systPath+nameTemplateMaiko.format(mass, str(njet), ch)+'_*.root'
                    ss.lumiMask = lumiMask
                    ss.lumi = lumi
                    ss.rebin = rebin

#         TODO clean up
#                     ss.replaceDrellYan = opt.replaceDY
                    # run
                    print '     - mixing histograms'
                    ss.mix(njet,fl)
                    ss.scale2Nominals( scale2NomList )
                    ss.applyScaleFactors( scaleFactors[njet] )

                    m.add(ss)

                print '  - summing sets'
                m.sum(opt.ninja)
                
                (estimates,dummy) = reader.get(mass,njet,fl)
#                 print estimates

                m.applyDataDriven( estimates )
                if not opt.dry:
                    output = 'hww-{lumi:.2f}fb.mH{mass}.{flav}_{jets}j_shape.root'.format(lumi=lumi,mass=mass,flav=fl,jets=njet)
                    path = os.path.join(outPath,output)
                    print '  - writing to',path
                    m.save(path)

    print 'Used options'
    print ', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()])
