#!/bin/env python

import sys
import os.path
import hwwtools
import logging
import array
import re
import math
import numpy as np

from HiggsAnalysis.CombinedLimit.DatacardParser import *
from HWWAnalysis.Misc.ROOTAndUtils import TH1AddDirSentry

import ROOT

#---
class roofiter:
    def __init__(self,iter):
        self._iter = iter

    def __iter__(self):
        return self

    def next(self):
        o = self._iter.next()
        if not o: raise StopIteration
        return o

mlfdir = '.'

def RooList2Set( alist ):

    next =  alist.createIterator()
    aset = ROOT.RooArgSet()
    while True: 
        p = next.Next()
        if not p: break
        aset.add( p )
    return aset

class ShapeGluer:
    _logger = logging.getLogger('ShapeGluer')
    def __init__(self, bin, DC, ws, fit=None): 
        self._DC = DC
        self._bin = bin
        self._ws = ws
        self._fit = fit
        
        self._build()

    #---
    def _build(self):
        
        if self._bin in self._DC.shapeMap:  bintag = self._bin
        elif '*' in self._DC.shapeMap:      bintag = '*'
        else:
            raise ValueError('Couldn\'t find '+bin+' or * in shapeMap')

        try:
            hpath, hname =  self._DC.shapeMap[bintag]['data_obs']
        except KeyError as e:
            raise KeyError('Shape for '+str(e) +'not found!') 

        sentry = TH1AddDirSentry()
        hpath = os.path.join(os.path.dirname(dcpath),hpath)
        hfile = ROOT.TFile.Open(os.path.join(hpath))
        if not hfile.__nonzero__():
            raise IOError('Could not open '+wspath)

        hdata = hfile.Get(hname)

        # the Xaxis label has to be cheked
        self._template = hdata.Clone('shape_template')
        self._template.SetTitle('shape_template')
        self._template.Reset()

        self._dummy = hdata.Clone('dummy')

    
    #---
    def glue(self):
        exp = self._DC.exp[self._bin]
        errs = self._glueerrors()
        shapes = dict([ (p,self._glueprocess(p)) for p in self._DC.processes if exp[p] != 0])
        shapes['Data'] = self._gluedata()

        return shapes,errs,self._dummy

    #---
    def _makeHisto(self, name, title):

        sentry = TH1AddDirSentry()
        h = self._template.Clone(name)
        h.SetTitle(title)

        return h
        
    #---
    def _gluedata(self):
        from math import sqrt
        h = self._makeHisto('histo_Data','Data')

        data = self._ws.data('data_obs')
        for i in xrange(data.numEntries()):
            data.get(i)
            h.SetBinContent(i+1,data.weight())
            h.SetBinError(i+1,sqrt(data.weight()))
        
        return h

    #---
    def _glueprocess(self, process):

        self._logger.debug('Glueing %s', process)
        data = self._ws.data('data_obs')
        tag = 'Sig' if process in self._DC.signals else 'Bkg'

        mname  = 'shape{0}_{1}_{2}_morph'.format(tag,self._bin,process)
        sname  = 'shape{0}_{2}_{1}Pdf'.format(tag,self._bin,process)
        morph  = self._ws.pdf('shape{0}_{1}_{2}_morph'.format(tag,self._bin,process))
        static = self._ws.pdf('shape{0}_{2}_{1}Pdf'.format(tag,self._bin,process))
        # errs   = self._ws.pdf('shape{0}_{2}_{1}_CMS_hww_{2}_{1}_stat_shapeUpPdf'.format(tag,self._bin,process))
        # 'shape{0}_{2}_{1}.format(tag,self.bin,process)
        # 'shape{0}_{2}_{1}_CMS_hww_{2}_{1}_stat_shapeUpPdf'.format(tag,self.bin,process)

        if morph.__nonzero__():
            shape = morph
        elif static.__nonzero__():
            shape = static
        else:
            self._ws.allPdfs().Print('V')
            print morph.__nonzero__(),morph, mname
            print static.__nonzero__(),static, sname
            raise ValueError('Can\'t find the nether the morph nor the shape!!! '+process)

        h = self._makeHisto('histo_'+process, process)

        if self._fit:
            self._logger.debug('Using fitted shapes %s', self._fit)
            norms, res, model = self._fit
            norm = norms.find('n_exp_bin{0}_proc_{1}'.format(self._bin, process))
            if not norm:
                norm = norms.find('n_exp_final_bin{0}_proc_{1}'.format(self._bin, process))

            self._rooPdf2TH1(h,shape,data, norm, self._fit[1].floatParsFinal())

        else:
            self._logger.debug('Using expected shapes')
            self._rooPdf2TH1(h,shape,data, self._DC.exp[self._bin][process])

        
        syst = self._syst(process)
        return h

    #---
    def _glueerrors(self):

        shapere = re.compile('_shape$')
        if not self._fit: 
            self._ws.loadSnapshot('clean')
            # here we can use w.set('nuisances') :D
            nuisances = self._ws.set('nuisances')
            POI = self._ws.set('POI')

            pars = ROOT.RooArgList()
            pars.add(nuisances)
            pars.add(POI)

            pars = pars.snapshot()

            return None

        (norm,res,model) = self._fit
        # take ebin centers
        ax      = self._template.GetXaxis()
        nbins   = ax.GetNbins()
        xs      = np.array( [ ax.GetBinCenter(i) for i in xrange(1,nbins+1) ], np.float32)
        wu      = np.array( [ ax.GetBinUpEdge(i)-ax.GetBinCenter(i)  for i in xrange(1,nbins+1) ], np.float32)
        wd      = np.array( [ ax.GetBinCenter(i)-ax.GetBinLowEdge(i) for i in xrange(1,nbins+1) ], np.float32)
        
        # now the real thing
        pars = res.floatParsFinal().snapshot()

        # sort the nuisances
        shapes = [ arg.GetName() for arg in roofiter(pars.fwdIterator()) if shapere.search(arg.GetName())]
        norms  = [ arg.GetName() for arg in roofiter(pars.fwdIterator()) if not shapere.search(arg.GetName())]

        # groups the nuis to float: all norms together, shapes 1 by 1
        grouping = [norms] + [ [arg] for arg in shapes ]

        # nominal valuse from the best fit values
        data = self._ws.data('data_obs')
        nmarray = self._roo2array(model, data, pars)
        # and the errors to be filled
        uperrs = np.zeros(nbins, np.float32)
        dwerrs = np.zeros(nbins, np.float32)
        for g in grouping:
            upfloat,dwfloat = self._variate(model,pars,g)
            uperrs += np.square(upfloat)
            dwerrs += np.square(dwfloat)
#             for i in xrange(nbins):
#                 uperrs[i] += upfloat[i]*upfloat[i]
#                 dwerrs[i] += dwfloat[i]*dwfloat[i]

#         for i in xrange(nbins):
#             uperrs[i] = math.sqrt(uperrs[i])
#             dwerrs[i] = math.sqrt(dwerrs[i])

        uperrs = np.sqrt(uperrs)
        dwerrs = np.sqrt(dwerrs)

        # normalize to data
        A = data.sum(False)

#         for i in xrange(nbins):
#             nmarray[i] = nmarray[i] * A
#             uperrs[i] = uperrs[i] * A
#             dwerrs[i] = dwerrs[i] * A

        nmarray *= A
        uperrs  *= A
        dwerrs  *= A

        errs = ROOT.TGraphAsymmErrors(len(xs),xs,nmarray,wd,wu,dwerrs,uperrs)
        errs.SetNameTitle('model_errs','model_errs')
        return errs

    #---
    def _variate(self,model,pars,tofloat):
        '''variates a subgroup of nuisances by their error and calculate the fluctuation from the nominal value'''
        ups = pars.snapshot()
        dws = pars.snapshot()

        print tofloat

        for var in tofloat:
            up = ups.find(var) 
            up.setVal(up.getVal()+up.getError())
            dw = dws.find(var) 
            dw.setVal(dw.getVal()-dw.getError())

        data = self._ws.data('data_obs')

        # convert the modified parameters to a model
        nmarray = self._roo2array(model, data, pars)
        uparray = self._roo2array(model, data, ups)
        dwarray = self._roo2array(model, data, dws)
        
        upfloat = np.zeros(data.numEntries(), np.float32)
        dwfloat = np.zeros(data.numEntries(), np.float32)

        # and calculate the fluctuations in terms of the model
        for i in xrange(data.numEntries()):
            u =  max(uparray[i],dwarray[i])-nmarray[i]
            d = -min(uparray[i],dwarray[i])+nmarray[i]
            upfloat[i] = u if u > 0 else 0
            dwfloat[i] = d if d > 0 else 0

        return (upfloat,dwfloat)

    #---
    def _glueerrors2(self):

        shapere = re.compile('_shape$')
        if not self._fit: return None

#         h = self._makeHisto('what','what')
        nms = self._fit[1].floatParsFinal().snapshot()
        ups = self._fit[1].floatParsFinal().snapshot()
        dws = self._fit[1].floatParsFinal().snapshot()

        # shift up the non-shape nuisances
        for arg in roofiter(ups.fwdIterator()):
            if shapere.search(arg.GetName()): continue
            arg.setVal(arg.getVal()+arg.getError())

        # shift down the non-shape nuisances
        for arg in roofiter(dws.fwdIterator()):
            if shapere.search(arg.GetName()): continue
            arg.setVal(arg.getVal()-arg.getError())

#         t_1 = dict([ (arg.GetName(),arg.getVal()) for arg in roofiter(nms.fwdIterator()) ])
#         t_2 = dict([ (arg.GetName(),arg.getVal()) for arg in roofiter(ups.fwdIterator()) ])
#         t_3 = dict([ (arg.GetName(),arg.getVal()) for arg in roofiter(dws.fwdIterator()) ])

        model = self._fit[2]
        data = self._ws.data('data_obs')

        # tak ebin centers
        ax      = self._template.GetXaxis()
        nbins   = ax.GetNbins()
        xs      = np.array([ ax.GetBinCenter(i) for i in xrange(1,nbins+1) ], np.float32)
        wu      = np.array([ ax.GetBinUpEdge(i)-ax.GetBinCenter(i)  for i in xrange(1,nbins+1) ], np.float32)
        wd      = np.array([ ax.GetBinCenter(i)-ax.GetBinLowEdge(i) for i in xrange(1,nbins+1) ], np.float32)

        nmarray = self._roo2array(model, data, nms)
        uparray = self._roo2array(model, data, ups)
        dwarray = self._roo2array(model, data, dws)
        
        uperr   = np.zeros(nbins, np.float32)
        dwerr   = np.zeros(nbins, np.float32)

        for i in xrange(nbins):
            u =  max(uparray[i],dwarray[i])-nmarray[i]
            d = -min(uparray[i],dwarray[i])+nmarray[i]
            uperr[i] = u if u > 0 else 0
            dwerr[i] = d if d > 0 else 0

        A = data.sum(False)

        for i in xrange(nbins):
            nmarray[i] = nmarray[i] * A
            uperr[i] = uperr[i] * A
            dwerr[i] = dwerr[i] * A

#             print '[',dwerr[i],',',uperr[i],']'

        errs = ROOT.TGraphAsymmErrors(len(xs),xs,nmarray,wd,wu,dwerr,uperr)
        errs.SetNameTitle('model_errs','model_errs')
        return errs

    #---
    def _syst(self,process):
        '''sum all the uncertainties in quadrature for a given process'''
        import math
        sum2 = 0
        for (name, nofloat, pdf, args, errline) in self._DC.systs:
            if 'shape' in pdf: continue
            if pdf == 'gmN': continue
            
            try:
                x = errline[self._bin][process]
                if not x: continue 
                sum2 += (x-1)*(x-1)
            except:
                pass
        return math.sqrt(sum2)

    #---
    def _roo2array(self, pdf, data, pars=None):

        pdf_obs  = pdf.getObservables(data)
        pdf_pars = pdf.getParameters(data)

        # make 1 double (float32) array
        bins = np.zeros(data.numEntries(),dtype=np.float32)

        if pars:
            pdf_pars.__assign__(ROOT.RooArgSet(pars))

        for i in xrange(data.numEntries()):
            pdf_obs.__assign__(data.get(i))
            bins[i] = pdf.getVal(pdf_obs)

        return bins


        

#     @staticmethod
    def _rooPdf2TH1(self,h, pdf, data, norm=None, pars=None):

        pdf_obs  = pdf.getObservables(data)
        pdf_pars = pdf.getParameters(data)

        if h.GetNbinsX() != data.numEntries():
            raise ValueError('bins mismatch!')
        
        if pars:
            pdf_pars.__assign__(ROOT.RooArgSet(pars))

        for i in xrange(data.numEntries()):
            pdf_obs.__assign__(data.get(i))
            h.SetBinContent(i+1,pdf.getVal(pdf_obs))

        if norm:
            if isinstance(norm,ROOT.RooAbsReal):
                norm = norm.getVal()
            self._logger.debug('pdf %s, h %s, Normalization %f -> %f',pdf.GetName(), h.GetName(),h.Integral(), norm)
            h.Scale(norm/h.Integral())
        elif norm==0:
            # just in case we are normalizing a 0 integral to 0 (0/0 is bad)
            h.Scale(0)
        elif norm==None:
            print 'No norm'


def THSum( shapes, labels, name=None, title=None):

    labels = [ p for p in shapes.iterkeys() if p in labels ]
    if not labels: return None

    sentry = TH1AddDirSentry()
    h = shapes[labels[0]].Clone()

    for l in labels[1:]:
        h.Add(shapes[l])

    if name: h.SetName(name)
    if title: h.SetName(title)

    return h


def fitAndPlot( dcpath, opts ):
    '''
1. read the datacard
2. convert to ws
3. run combine
4. open get the mlfit rootfile

1-4 don't need to know the content of the card, only to check that there are shapes inside

'''

    remass = re.compile('mH(\d*)')
    m = remass.search(dcpath)
    if not m: raise ValueError('porcocazzo')

    print 'Mass',m.group(1)
    opt.mass = int(m.group(1))

    mypath = os.path.dirname(os.path.abspath(__file__))
    ROOT.gInterpreter.ExecuteMacro(mypath+'/LatinoStyle2.C')
    hwwtools.loadAndCompile(mypath+'/MWLPlot.C','g')


    # 1. load the datacard
    dcfile = open(dcpath,'r')
    class dummy: pass

    options = dummy()
    options.stat = False
    options.bin = True
    options.noJMax = False
    options.nuisancesToExclude = []
    options.nuisancesToRescale = []

    DC = parseCard(dcfile, options)

    if not DC.hasShapes:
        print 'This datacard has no shapes!'
        print dcpath
        sys.exit(-1)

    if len(DC.bins) != 1:
        raise ValueError('Only 1 bin datacards supported at the moment: '+', '.join(DC.bins))
        

    # 2. convert to ws
    wspath = os.path.splitext(dcpath)[0]+'.root'
    logging.debug('Working with workspace %s',wspath)
    if not os.path.exists(wspath):
        # workspace + parameters = shapes
        print 'Making the workspace...',
        sys.stdout.flush()
        os.system('text2workspace.py '+dcpath)
        print 'done.'

    ROOT.gSystem.Load('libHiggsAnalysisCombinedLimit')
    wsfile = ROOT.TFile.Open(wspath)
    if not wsfile.__nonzero__():
        raise IOError('Could not open '+wspath)
    
    w = wsfile.Get('w')
    w.saveSnapshot('clean',w.allVars())

    # 3. prepare the temp direcotry
    import tempfile
    mlfdir = opt.tmpdir if opt.tmpdir else tempfile.mkdtemp(prefix='mlfit_')
    hwwtools.ensuredir(mlfdir)
    # 3.1 go to the tmp dir 
    here = os.getcwd()
    os.chdir(mlfdir)
    # 3.2 
    mlcmd = 'combine -M MaxLikelihoodFit --saveNormalizations '+os.path.join(here,wspath)
    logging.debug(mlcmd)
    print 'Fitting the workspace...',
    sys.stdout.flush()
    os.system(mlcmd)
    os.chdir(here)
    print 'done.'

    # open the output and get the normalizations
    mlfpath = os.path.join(mlfdir,'mlfit.root')
    mlffile = ROOT.TFile.Open(mlfpath)
    if not mlffile.__nonzero__():
        raise IOError('Could not open '+wspath)

    sig_fit = ( mlffile.Get('norm_fit_s'),  mlffile.Get('fit_s'), w.pdf('model_s') )
    bkg_fit = ( mlffile.Get('norm_fit_b'),  mlffile.Get('fit_b'), w.pdf('model_b') )

    print DC.bins
    bin = DC.bins[0]

    modes = {
        'sig' :sig_fit,
        'bkg' :bkg_fit,
        'init':None, #(None, None, model_s)
    }

    allshapes = {}
    for mode,fit in modes.iteritems():
        allshapes[mode] = export(bin, DC, w, mode, fit, opts)
    
    if opts.dump:
        logging.debug('Dumping histograms to %s',opts.dump)
        dump = ROOT.TFile.Open(opts.dump,'recreate')
        here = ROOT.gDirectory.func()
        dump.cd()
        for mode,shapes in allshapes.iteritems():
            d = dump.mkdir(mode)
            d.cd()
            for s in shapes.itervalues(): s.Write()

        dump.Write()
        dump.Close()
        here.cd()

#---
def export( bin, DC, w, mode, fit, opts):

    logging.debug('Plotting %s', fit)

    gluer = ShapeGluer(bin, DC, w, fit)

    shapes,errs,dummy = gluer.glue()


    shapes2plot = shapes.copy()
    shapes2plot['Hsum']  = THSum(shapes2plot,['ggH','vbfH','wzttH'],'histo_higgs','higgs')
    shapes2plot['WWsum'] = THSum(shapes2plot,['WW','ggWW'],'histo_WWsum','WWsum')
    shapes2plot['VVsum'] = THSum(shapes2plot,['VV','Vg'],'histo_VVsum','VVsum')
    shapes2plot['DYsum'] = THSum(shapes2plot,['DYLL','DYTT'],'histo_DYsum','DYsum')

    plot = ROOT.MWLPlot()
    plot.setDataHist(shapes2plot['Data'])
    if mode != 'bkg':
        plot.setStackSignal(True)
        plot.setHWWHist(shapes2plot['Hsum'])

    plot.setWWHist(shapes2plot['WWsum'])  
    plot.setZJetsHist(shapes2plot['DYsum'])
    plot.setTopHist(shapes2plot['Top'])
    plot.setVVHist(shapes2plot['VVsum'])
    plot.setWJetsHist(shapes2plot['WJet'])

    cName = 'c_fitshapes_'+mode
    ratio = opts.ratio
    c = ROOT.TCanvas(cName,cName) if ratio else ROOT.TCanvas(cName,cName,1000,1000)
    plot.setMass(opts.mass)
    plot.setLumi(opts.lumi)
    plot.setLabel(opts.xlabel)
    plot.Draw(c,1,ratio)
    print 'Errs',errs
    if errs:
        plot.pad1().cd()
        errs.SetFillStyle(3153)
        errs.SetFillColor(1)
        errs.SetLineColor(3)
        errs.SetMarkerColor(3)
        errs.Draw('2')

#     if dummy:
#         plot.pad1().cd()
#         dummy.SetLineColor(6)
#         dummy.SetLineWidth(3)
#         dummy.Draw('same')

    ROOT.gPad.Modified()
    ROOT.gPad.Update()

    if opts.output:
        hwwtools.ensuredir(opts.output)

        outbasename = os.path.join(opts.output,'fitshapes_mH%d_%s_%s' % (opt.mass,bin,mode))
        c.Print(outbasename+'.pdf')
        c.Print(outbasename+'.png')
        c.Print(outbasename+'.root')

    del c
    all = {}
    all.update(shapes)
    if errs:
        all[errs] = errs
    return all


#---
def addOptions( parser ):
    
    parser.add_option('-o' , '--output' , dest='output' , help='Output directory (%default)' , default=None)
    parser.add_option('-x' , '--xlabel' , dest='xlabel' , help='X-axis label'                , default='')
    parser.add_option('-r' , '--ratio'  , dest='ratio'  , help='Plot the data/mc ration'     , default=True    , action='store_false')
#     parser.add_option('-M' , '--mode'   , dest='mode'   , help='Select the plot mode [input, sig, bkg]' , default='sig')
    parser.add_option('--dump'          , dest='dump'   , help='Dump the histograms to file' , default=None)
    parser.add_option('--tmpdir'        , dest='tmpdir' , help='Temporary directory'         , default=None)

    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)


if __name__ == '__main__':
    import optparse
    ## option parser
    usage = 'usage: %prog [options] datacard'
    parser = optparse.OptionParser(usage)

    addOptions(parser)
    
    (opt, args) = parser.parse_args()
    sys.argv.append('-b')

    if not opt.debug:
        pass
    elif opt.debug == 2:
        print 'Logging level set to DEBUG (%d)' % opt.debug
        logging.basicConfig(level=logging.DEBUG)
    elif opt.debug == 1:
        print 'Logging level set to INFO (%d)' % opt.debug
        logging.basicConfig(level=logging.INFO)

    try:
        dcpath = args[0]
    except IndexError:
        parser.print_usage()
    
    try:
        fitAndPlot(dcpath, opt)
    except SystemExit:
        pass
    except:
        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
#         print "*** print_tb:"
#         traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
#         print "*** print_exception:"
#         traceback.print_exception(exc_type, exc_value, exc_traceback,
#                                   limit=2, file=sys.stdout)
        print "*** print_exc:"
        traceback.print_exc()
        print "*** format_exc, first and last line:"
        formatted_lines = traceback.format_exc().splitlines()
        print formatted_lines[0]
        print formatted_lines[-1]
        print "*** format_exception:"
        print repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback))
#         print "*** extract_tb:"
#         print repr(traceback.extract_tb(exc_traceback))
#         print "*** format_tb:"
#         print repr(traceback.format_tb(exc_traceback))
#         print "*** tb_lineno:", exc_traceback.tb_lineno

