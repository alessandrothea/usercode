#!/bin/env python

import pdb

import sys
import os.path
import hwwtools
import logging
import array
import re
import math
import numpy as np

from HiggsAnalysis.CombinedLimit.DatacardParser import *
from HiggsAnalysis.CombinedLimit.ShapeTools import *
from HWWAnalysis.Misc.ROOTAndUtils import TH1AddDirSentry

import ROOT

#---
def getnorms(pdf, obs, norms = None ):
    '''helper function to exctact the normalisation factors'''

    out = norms if norms!=None else {}

    #if isinstance(pdf,ROOT.RooSimultaneous):
        #cat = sim.indexCat()
        #for i in xrange(cat.numBins(0)):
            #cat.setBin(i)
            #pdfi = sim.getPdf(cat.getLabel());
            #if pdfi.__nonzero__(): getnorms(pdfi, obs, out);
        #pass

    if isinstance(pdf,ROOT.RooProdPdf):
        pdfs = ROOT.RooArgList(pdf.pdfList())
        for pdfi in roofiter(pdfs):
            if pdfi.dependsOn(obs): getnorms(pdfi,obs,out)

    if isinstance(pdf,ROOT.RooAddPdf):
        coefs = ROOT.RooArgList(pdf.coefList())
        for c in roofiter(coefs):
            out[c.GetName()] =  c.getVal(obs)

    return out

#---
class roofiter:
    def __init__(self,collection):
        self._iter = collection.fwdIterator()

    def __iter__(self):
        return self

    def next(self):
        o = self._iter.next()
        if not o: raise StopIteration
        return o

mlfdir = '.'

# ---
class ShapeGluer:
    '''Class to recompose a histograms-base combined model into drawable objects'''
    _logger = logging.getLogger('ShapeGluer')
    def __init__(self, bin, DC, MB, ws, fit): 
        self._DC = DC
        self._MB = MB
        # todo: what is the role of the bin in the multibin case?
        self._bin = bin
        self._ws = ws
        # TODO, rearrange this fit information
        self._fit = fit
        self._model    = fit[0]  
        self._fitpars  = fit[1]
        self._fitnorms = fit[2]
        
        self._build()


    #---
    def _build(self):
        '''Fill up the objects'''
        
        hdata = self._MB.getShape(self._bin,'data_obs')

        # the Xaxis label has to be cheked
        self._template = hdata.Clone('shape_template')
        self._template.SetTitle('shape_template')
        self._template.Reset()

        self._dummy = hdata.Clone('dummy')

        # keep a pointer to the data object
        self._data  = self._ws.data('data_obs')

        # store the list of pdfs
        self._pdfs = self._getpdfs()

    #---
    def _getpdfs( self ):
        '''Extract the process pdfs from the ws.'''

        pdfs = {}
        for process in self._DC.processes:
            tag = 'Sig' if process in self._DC.signals else 'Bkg'

            mname  = 'shape{0}_{1}_{2}_morph'.format(tag,self._bin,process)
            sname  = 'shape{0}_{2}_{1}Pdf'.format(tag,self._bin,process)
            morph  = self._ws.pdf('shape{0}_{1}_{2}_morph'.format(tag,self._bin,process))
            static = self._ws.pdf('shape{0}_{2}_{1}Pdf'.format(tag,self._bin,process))

            if morph.__nonzero__():
                shape = morph
            elif static.__nonzero__():
                shape = static
            else:
                self._ws.allPdfs().Print('V')
                print morph.__nonzero__(),morph, mname
                print static.__nonzero__(),static, sname
                raise ValueError('Can\'t find the nether the morph nor the shape!!! '+process)

            pdfs[process] = shape
        return pdfs

    #---
    def _getnormalisations( self, pdf ):
        pdf_obs  = pdf.getObservables(self._data)
        roonorms = getnorms(pdf, pdf_obs)

        exp = self._DC.exp[self._bin]

#         print exp
#         print roonorms
#         print self._DC.processes
        
        norms = {}
        for process in self._DC.processes:

            n = roonorms.get( 'n_exp_bin%s_proc_%s' % (self._bin, process) )
            if not n: n = roonorms.get( 'n_exp_final_bin%s_proc_%s' % (self._bin, process) )

            # fill it up only if the process exists in the model
            if not n: continue

            norms[process] = n
            
        return norms

    #---
    def _makeHisto(self, name, title):
        sentry = TH1AddDirSentry()
        h = self._template.Clone(name)
        h.SetTitle(title)

        return h

    def _array2TH1(self, name, array, title=None ):
        if len(array) != self._template.GetNbinsX():
            raise ValueError('Mismatching bin array length and histogram bins')

        if title==None: title = name
        h = self._makeHisto( name, title )

        for i,c in enumerate(array):
            h.SetBinContent(i+1,c)

        return h
            

    #---
    def _roo2array(self, pdf, pars=None, norm=None):
        '''Converts a pdf into a numpy array
        The pdf is plotted against the data stored in the builder
        A custom set of parameters and normalisation can be applied'''

        data = self._data

        pdf_obs  = pdf.getObservables(data)
        pdf_pars = pdf.getParameters(data)

        # make 1 double (float32) array
        bins = np.zeros(data.numEntries(),dtype=np.float32)

        if pars:
            pdf_pars.__assign__(ROOT.RooArgSet(pars))

        for i in xrange(data.numEntries()):
            pdf_obs.__assign__(data.get(i))
            bins[i] = pdf.getVal(pdf_obs)

        # the pdf should have area equal 1
        if norm or norm == 0:
            bins *= norm
        elif norm==None:
            self._logger.debug('No normalisation')

        return bins

    #---
    def _rooPdf2TH1(self, name, pdf, pars=None, norm=None, title=None):
        ''' '''

        contents = self._roo2array(pdf,pars)

        h = self._array2TH1(name, contents, title)

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
        
        return h

#         for i,c in enumerate(contents):
#             h.SetBinContent(i+1,c)

    #---
    def _model2arrays(self,pars):
        '''Turns the array into '''

        data  = self._data
        model = self._model
        pdfs  = self._pdfs

        # convert the model to array (this applies the params)
        model_array = self._roo2array(model,pars)

        # then get the list of normalisations
        norms = self._getnormalisations( model )
        
        # normalise the arrary to the sum of the components
        model_array *= sum(norms.itervalues())

        #loop over the processes
        arrays = {}

        for p,s in self._pdfs.iteritems():
            if p not in norms: continue

            # here I can avoid pars, but it might not make any difference,
            # as the operation to copy the pars is quick. Maybe
            x = self._roo2array(s,pars)
            # normalise the process pdf to the yields
            x *= norms[p]
            arrays[p] = x

        arrays['model'] = model_array
        
        return arrays

    #---
    def _model2TH1(self,pars):
        
        arrays = self._model2arrays(pars)
        
        #convert the model array into the histogram
        hists = dict( [ ( p,self._array2TH1('hist_'+p, a, title=p) ) for p,a in arrays.iteritems() ] )

        return hists

    #---
    def glue(self):
        hists,errs = self._gluenew()
        hists['Data'] = self._gluedata()
        return hists,errs,self._dummy
#         sys.exit(0)

#         exp = self._DC.exp[self._bin]
#         errs = self._glueerrors()
#         shapes = dict([ (p,self._glueprocess(p)) for p in self._DC.processes if exp[p] != 0])
#         shapes['Data'] = self._gluedata()

#         return shapes,errs,self._dummy

        
    #---
    def _gluedata(self):
        from math import sqrt
        h = self._makeHisto('histo_Data','Data')

#         data = self._ws.data('data_obs')
        data = self._data
        for i in xrange(data.numEntries()):
            data.get(i)
            h.SetBinContent(i+1,data.weight())
            h.SetBinError(i+1,sqrt(data.weight()))
        
        return h

    #---
    def _glueprocess(self, process):

        self._logger.debug('Glueing %s', process)
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

#         h = self._makeHisto('histo_'+process, process)
        
        model, pars, norms = self._fit
        if norms:
            self._logger.debug('Using fitted shapes %s', self._fit)
#             norms, pars, model = self._fit
            norm = norms.find('n_exp_bin{0}_proc_{1}'.format(self._bin, process))
            if not norm:
                norm = norms.find('n_exp_final_bin{0}_proc_{1}'.format(self._bin, process))

#             self._rooPdf2TH1(h, shape, pars, norm)
#             h = self._rooPdf2TH1(name, shape, pars, norm, title=title)

        else:
            self._logger.debug('Using expected shapes')
#             self._rooPdf2TH1(h, shape, data, pars, self._DC.exp[self._bin][process])
#             self._rooPdf2TH1(h, shape, pars, self._DC.exp[self._bin][process])
#             h = self._rooPdf2TH1(name, shape, pars, self._DC.exp[self._bin][process], title=title)
            norm = self._DC.exp[self._bin][process]

        h = self._rooPdf2TH1('hist_'+process, shape, pars, norm, title=process)

        
#         syst = self._syst(process)
        return h

    #---
    def _chknorms(self, A, norms):
        pdf_obs  = self._model.getObservables(self._data)
        ns = getnorms(self._model,pdf_obs)
        I = J = 0

        print '-'*80
        print '%-10s %-10s %-10s %-10s' % ('Process','frompdf','fromfit','datacard')
        print '-'*80
        fn = {}
        if norms:
            for n in roofiter(norms):
                fn[n.GetName()] = n.getVal()
                J+=n.getVal()

        for p,v in sorted(self._DC.exp[self._bin].iteritems()):
            # associate the normalization to the process
            endswith = re.compile('_%s$' % p)
            matches = [ n for n in ns if endswith.search(n)]
            if not matches: continue
            if len(matches) > 1:
                raise RuntimeError('Can\'t match normalisation to process: %s,%s' % (p,matches))
            n = matches[0]

            print '%-10s %10.3f %10.3f %10.3f' % (p,ns[n],fn[n] if fn else 0,v)
            I += ns[n]


        print 'Integrals I,J,A,sum',I, J, A,sum(self._DC.exp[self._bin].itervalues())
        print '-'*80

    #---
    def _gluenew(self):
#         print 'gluenew'
        # clean the parameters
        self._ws.loadSnapshot('clean')
        model, pars, norms = self._fit
        
        # deal with the 2 cases. Fit 
        if norms: 
            # now the real thing
            pars = pars.snapshot()

            # normalize to data
            A = self._data.sum(False)
        else:
            # here we can use w.set('nuisances') :D
            pars = pars.snapshot()
            
            # set the errors to 1. sigma for the priors
            for arg in roofiter(pars):
                name = arg.GetName()
                # don't add errors to the signal strength
                if name == 'r': continue
                # find the functional form
                ptype = None
                for (n,nf,p,a,e) in self._DC.systs:
                    if n==name:
                        ptype = p
                        break
                
                # add errors
                if   ptype == 'lnN' or ptype == 'lnU' or 'shape' in ptype:
                    # +/- 1 for lnN (and shapes)
                    arg.setError(1.)
                elif ptype == 'gmN':
                    # +/- sqrt(N) for gmN
                    arg.setError(math.sqrt(arg.getVal()))
                else:
                    raise ValueError('Pdf type %s not known',ptype)

            # normalize to the expected from the DC
            A = sum(self._DC.exp[self._bin].itervalues())


        # take ebin centers
        ax      = self._template.GetXaxis()
        nbins   = ax.GetNbins()
        xs      = np.array( [ ax.GetBinCenter(i) for i in xrange(1,nbins+1) ], np.float32)
        wu      = np.array( [ ax.GetBinUpEdge(i)-ax.GetBinCenter(i)  for i in xrange(1,nbins+1) ], np.float32)
        wd      = np.array( [ ax.GetBinCenter(i)-ax.GetBinLowEdge(i) for i in xrange(1,nbins+1) ], np.float32)
        
        # sort the nuisances
        shapes = [n for (n,nf,p,a,e) in self._DC.systs if 'shape' in p]

        # split shape and normalisation nuisances
        nushapes = [ arg.GetName() for arg in roofiter(pars) if arg.GetName() in shapes]
        nunorms  = [ arg.GetName() for arg in roofiter(pars) if not arg.GetName() in shapes ]

        # groups the nuis to float: all norms together, shapes 1 by 1
        # grouping = dict([('norms',nunorms)] + [ (arg,[arg]) for arg in nushapes] )
        grouping = dict([ (arg,[arg]) for arg in (nushapes+nunorms)] )

        # print some stats
        self._chknorms(A, norms)

        # now produce the arrays for everything
        nmarrays =  self._model2arrays( pars )

        # convert the shapes into histograms
        hists = dict( [
            (p,self._array2TH1('hist_'+p, a, title=p)) for p,a in nmarrays.iteritems()
        ] )


        mega = {}
        
        # now the variations
        print 'Generating the variations'
        for nu,group in grouping.iteritems():
            self._logger.debug(' - %s',nu)
            nuvars = self._variatemodel(pars,group)
            # store the variation by process
            for p,v in nuvars.iteritems():
                if not p in mega: mega[p] = {}
                mega[p][nu] = v

        # loop over processes to calculate the square sum of the nuisamces
        print 'Calculating the nuisances square sum'
        for p,nus in mega.iteritems():
            self._logger.debug(' - %s',p)
            
            uperrs = np.zeros(nbins, np.float32)
            dwerrs = np.zeros(nbins, np.float32)

            for n,(ups,dws) in nus.iteritems():
                 
                uperrs += np.square(ups)
                dwerrs += np.square(dws)

            uperrs = np.sqrt(uperrs)
            dwerrs = np.sqrt(dwerrs)

            nus['all'] = (uperrs,dwerrs)


        # turn them into TGraphs
        print 'Converting the arrays into TGraphs'
        errs = {}

        for p,nus in mega.iteritems():
            self._logger.debug(' - %s',p)
            # ensure the sub-dictionary
            if not p in errs: errs[p] = {}

            # take the nominal
            nmarray = nmarrays[p]

            for n,(uperrs,dwerrs) in nus.iteritems():
                errgraph = ROOT.TGraphAsymmErrors(len(xs),xs,nmarray,wd,wu,dwerrs,uperrs)
                nametitle = '%s_errs_%s' % (p,n)
                errgraph.SetNameTitle(nametitle, nametitle)
                
                errs[p][n] = errgraph

        return hists,errs

    #---
    def _glueerrors(self):

        # clean the parameters
        self._ws.loadSnapshot('clean')
        model, pars, norms = self._fit

#         data = self._ws.data('data_obs')
#         data = self._data
        
        # deal with the 2 cases. Fit 
        if norms: 
            # now the real thing
            pars = pars.snapshot()

            # normalize to data
            A = self._data.sum(False)
        else:
            # here we can use w.set('nuisances') :D
            pars = pars.snapshot()
            
            # set the errors to 1. sigma for the priors
            for arg in roofiter(pars):
                name = arg.GetName()
                # don't add errors to the signal strength
                if name == 'r': continue
                # find the functional form
                ptype = None
                for (n,nf,p,a,e) in self._DC.systs:
                    if n==name:
                        ptype = p
                        break
                
                # add errors
                if   ptype == 'lnN' or ptype == 'lnU' or 'shape' in ptype:
                    # +/- 1 for lnN (and shapes)
                    arg.setError(1.)
                elif ptype == 'gmN':
                    # +/- sqrt(N) for gmN
                    arg.setError(math.sqrt(arg.getVal()))
                else:
                    raise ValueError('Pdf type %s not known',ptype)

            # normalize to the expected from the DC
            A = sum(self._DC.exp[self._bin].itervalues())


        # take ebin centers
        ax      = self._template.GetXaxis()
        nbins   = ax.GetNbins()
        xs      = np.array( [ ax.GetBinCenter(i) for i in xrange(1,nbins+1) ], np.float32)
        wu      = np.array( [ ax.GetBinUpEdge(i)-ax.GetBinCenter(i)  for i in xrange(1,nbins+1) ], np.float32)
        wd      = np.array( [ ax.GetBinCenter(i)-ax.GetBinLowEdge(i) for i in xrange(1,nbins+1) ], np.float32)
        
        # sort the nuisances
        shapes = [n for (n,nf,p,a,e) in self._DC.systs if 'shape' in p]

        nushapes = [ arg.GetName() for arg in roofiter(pars) if arg.GetName() in shapes]
        nunorms  = [ arg.GetName() for arg in roofiter(pars) if not arg.GetName() in shapes ]

        # groups the nuis to float: all norms together, shapes 1 by 1
        # grouping = dict([('norms',nunorms)] + [ (arg,[arg]) for arg in nushapes] )
        grouping = dict([ (arg,[arg]) for arg in (nushapes+nunorms)] )

        # nominal valuse from the best fit values
#         nmarray = self._roo2array(model, data, pars)
        nmarray = self._roo2array(model, pars)

        pdf_obs  = model.getObservables(self._data)
        ns = getnorms(model,pdf_obs)
#         print ns
        I = J = 0

        print '-'*80
        print '%-10s %-10s %-10s %-10s' % ('Process','frompdf','fromfit','datacard')
        print '-'*80
        fn = {}
        if norms:
            for n in roofiter(norms):
                fn[n.GetName()] = n.getVal()
                J+=n.getVal()

        for p,v in sorted(self._DC.exp[self._bin].iteritems()):
            # associate the normalization to the process
            endswith = re.compile('_%s$' % p)
            matches = [ n for n in ns if endswith.search(n)]
            if not matches: continue
            if len(matches) > 1:
                raise RuntimeError('Can\'t match normalisation to process: %s,%s' % (p,matches))
            n = matches[0]

            print '%-10s %10.3f %10.3f %10.3f' % (p,ns[n],fn[n] if fn else 0,v)
            I += ns[n]


        print 'Integrals I,J,A,sum',I, J, A,sum(self._DC.exp[self._bin].itervalues())
        print '-'*80

        m_a,p_a =  self._model2arrays( pars )

        print 'sum A',sum(m_a)

        # and the errors to be filled
        uperrs = np.zeros(nbins, np.float32)
        dwerrs = np.zeros(nbins, np.float32)

        allfloats = {}

        # how to normalise? curently I normlise to the data
        # Otherwise I could extract the normalisation from the coefficient,
        # both for the total and the single process.

        for n,g in grouping.iteritems():
            upfloat,dwfloat = self._variate(model,pars,g)

            upfloat *= A
            dwfloat *= A

            allfloats[n] = (upfloat,dwfloat)
            uperrs += np.square(upfloat)
            dwerrs += np.square(dwfloat)

        uperrs = np.sqrt(uperrs)
        dwerrs = np.sqrt(dwerrs)

        nmarray *= A

        allfloats['allnuisances'] = (uperrs,dwerrs)

        errs = {}

        for n in allfloats.iterkeys():
            uperrs,dwerrs = allfloats[n]
            errgraph = ROOT.TGraphAsymmErrors(len(xs),xs,nmarray,wd,wu,dwerrs,uperrs)
            nametitle = 'model_errs_%s' % n if n != 'allnuisances' else 'model_errs'
            errgraph.SetNameTitle(nametitle, nametitle)
            errs[n] = errgraph

#         print errs.keys()

        return errs


    #---
    def _dovariations(self,nmarray,uparray,dwarray):

        nentries = self._data.numEntries()

        upfloat = np.zeros(nentries, np.float32)
        dwfloat = np.zeros(nentries, np.float32)

        # and calculate the fluctuations in terms of the model
        for i in xrange(nentries):
            u =  max(uparray[i],dwarray[i])-nmarray[i]
            d = -min(uparray[i],dwarray[i])+nmarray[i]
            upfloat[i] = u if u > 0 else 0
            dwfloat[i] = d if d > 0 else 0

        return (upfloat,dwfloat)

    #---
    def _variatemodel(self,pars,tofloat):
        '''variates a subgroup of nuisances by their error and calculate the fluctuation from the nominal value'''
        ups = pars.snapshot()
        dws = pars.snapshot()

        for var in tofloat:
            up = ups.find(var) 
            up.setVal(up.getVal()+up.getError())
            dw = dws.find(var) 
            dw.setVal(dw.getVal()-dw.getError())


        # model+pars -> 
        nmarrays =  self._model2arrays( pars )
        uparrays =  self._model2arrays( ups )
        dwarrays =  self._model2arrays( dws )

#         variations = dict( [
#             (p,self._dovariations(nmarrays[p],uparrays[p],dwarrays[p])) for p in nmarrays.iterkeys()
#         ])

        # transform the fluctuations in differences
        # filter those which do not differ from the nominal
        vararrays = []
        for p in nmarrays.iterkeys():
            if (nmarrays[p] == uparrays[p]).all() and (nmarrays[p] == dwarrays[p]).all(): 
                self._logger.debug('   - skipping %s',p)
                #                 pdb.set_trace()
                continue
            vararrays.append( ( p, self._dovariations(nmarrays[p],uparrays[p],dwarrays[p])) )

        variations = dict(vararrays)

            



        return variations

    #---
    def _variate(self,model,pars,tofloat):
        '''variates a subgroup of nuisances by their error and calculate the fluctuation from the nominal value'''
        ups = pars.snapshot()
        dws = pars.snapshot()

        for var in tofloat:
            up = ups.find(var) 
            up.setVal(up.getVal()+up.getError())
            dw = dws.find(var) 
            dw.setVal(dw.getVal()-dw.getError())

        nentries = self._data.numEntries()

        # convert the modified parameters to a model
        nmarray = self._roo2array(model, pars)
        uparray = self._roo2array(model, ups)
        dwarray = self._roo2array(model, dws)
        
        upfloat = np.zeros(nentries, np.float32)
        dwfloat = np.zeros(nentries, np.float32)

        # and calculate the fluctuations in terms of the model
        for i in xrange(nentries):
            u =  max(uparray[i],dwarray[i])-nmarray[i]
            d = -min(uparray[i],dwarray[i])+nmarray[i]
            upfloat[i] = u if u > 0 else 0
            dwfloat[i] = d if d > 0 else 0

        return (upfloat,dwfloat)


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

    shapepath = os.path.abspath(os.path.dirname(os.path.normpath(__file__))+'/..')
    print 'Shape directory is',shapepath
    ROOT.gInterpreter.ExecuteMacro(shapepath+'/macros/LatinoStyle2.C')
    hwwtools.loadAndCompile(shapepath+'/macros/MWLPlot.C')

    # 1. load the datacard
    dcfile = open(dcpath,'r')
    
    class dummy: pass
    options = dummy()
    options.stat = False
    options.bin = True
    options.noJMax = False
    options.nuisancesToExclude = []
    options.nuisancesToRescale = []

    # get some default arguments
#     dummy = optparse.OptionParser()
#     addDatacardParserOptions(dummy)
#     options = dummy.parse_args([])
#     del dummy

    options.fileName = dcpath
    options.out = None
    options.cexpr = False
    options.fixpars = False
    options.libs = []
    options.verbose = 0
    options.poisson = 0
    options.mass = opt.mass

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

    mkws = (not os.path.exists(wspath) or
            os.path.getmtime(wspath) < os.path.getmtime(dcpath) or
            opts.clean)
    if mkws:
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
    if opts.fit: os.system(mlcmd)
    os.chdir(here)
    print 'done.'

    # open the output and get the normalizations
    mlfpath = os.path.join(mlfdir,'mlfit.root')
    mlffile = ROOT.TFile.Open(mlfpath)
    if not mlffile.__nonzero__():
        raise IOError('Could not open '+wspath)

    model_s = w.pdf('model_s')
    model_b = w.pdf('model_b')
    res_s   = mlffile.Get('fit_s')
    res_b   = mlffile.Get('fit_b')
    sig_fit = ( model_s, res_s.floatParsFinal(), mlffile.Get('norm_fit_s'), )
    bkg_fit = ( model_b, res_b.floatParsFinal(), mlffile.Get('norm_fit_b'), )

    print DC.bins
    bin = DC.bins[0]

    modes = {
        'sig' :sig_fit,
        'bkg' :bkg_fit,
        'init':(model_s,res_s.floatParsInit(),None), #(None, None, model_s)
    }

    # experimental
    MB = ShapeBuilder(DC, options)

    allshapes = {}
    for mode,fit in modes.iteritems():
        print 'mode',mode
#         allshapes[mode] = export(bin, DC, MB, w, mode, fit, opts)
        logging.debug('Plotting %s', fit)

        gluer = ShapeGluer(bin, DC, MB, w, fit)
        shapes,errs,dummy = gluer.glue()

        if opts.output:
            printshapes(shapes, errs, mode, opts, bin)

        allshapes[mode] = (shapes,errs)
    
    if opts.dump:
        logging.debug('Dumping histograms to %s',opts.dump)
        dump = ROOT.TFile.Open(opts.dump,'recreate')
        here = ROOT.gDirectory.func()
        dump.cd()
        for mode,(shapes,errs) in allshapes.iteritems():
            d = dump.mkdir(mode)
            d.cd()
            for s in shapes.itervalues(): s.Write()

            for p,nugs in errs.iteritems():
                dp = d.mkdir(p+'_errs')
                dp.cd()
                for g in nugs.itervalues(): g.Write()
                d.cd()
            
            modelall = errs['model']['all'].Clone('model_errs')
            modelall.SetTitle('model_errs')
            modelall.Write()



        dump.Write()
        dump.Close()
        here.cd()

#---
def printshapes( shapes, errs, mode, opts, bin ):
    # deep copy?
    shapes2plot = copy.deepcopy(shapes)

    import hwwsamples
    shapes2plot['Hsum']  = THSum(shapes2plot,hwwsamples.signals,'histo_higgs','higgs')
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

    if ratio: w = 1000; h = 1400
    else:     w = 1000; h = 1000

    if opts.stretch:
        plot.stretch(opts.stretch)
        w = int(w*opts.stretch)

    c = ROOT.TCanvas(cName,cName, w+4, h+28) #if ratio else ROOT.TCanvas(cName,cName,1000,1000)
#     print w,h, c.GetWw(), c.GetWh()

    plot.setMass(opts.mass)
    plot.setLumi(opts.lumi if opt.lumi else 0)
    plot.setLabel(opts.xlabel)
    plot.setRatioRange(0.,2.)

    def _print(c, p, e, l):

        if not e:
            e = 0x0

        plot.setNuisances(e)

        c.Clear()
    
        p.Draw(c,1,ratio)

        c.Modified()
        c.Update()
    
        hwwtools.ensuredir(opts.output)

        outbasename = os.path.join(opts.output,'fitshapes_mH%d_%s_%s' % (opt.mass,bin,mode))
        if l: 
            outbasename += '_' + l

        print 'outbasename:',outbasename
        c.Print(outbasename+'.pdf')
        c.Print(outbasename+'.png')


    if errs:
        for ename,eg in errs.iteritems():
            _print(c,plot,eg,ename) 

    del c



#---
def export( bin, DC, MB, w, mode, fit, opts):


    logging.debug('Plotting %s', fit)

    gluer = ShapeGluer(bin, DC, MB, w, fit)

    shapes,errs,dummy = gluer.glue()

    if opts.output:
        printshapes(shapes, errs, mode, opts, bin)

    return shapes,err
#     all = {}
#     all.update(shapes)
#     if errs:
# #         all[errs] = errs
#         all.update(errs)
#     return all


#---
def addOptions( parser ):
    
    parser.add_option('-o' , '--output' , dest='output' , help='Output directory (%default)' , default=None)
    parser.add_option('-x' , '--xlabel' , dest='xlabel' , help='X-axis label'                , default='')
    parser.add_option('-r' , '--ratio'  , dest='ratio'  , help='Plot the data/mc ration'     , default=True    , action='store_false')
    parser.add_option('--nofit'         , dest='fit'    , help='Don\'t fit'                  , default=True    , action='store_false')
    parser.add_option('--clean'         , dest='clean'  , help='Clean the ws (regenerate it' , default=False   , action='store_true')
    parser.add_option('--dump'          , dest='dump'   , help='Dump the histograms to file' , default=None)
    parser.add_option('--tmpdir'        , dest='tmpdir' , help='Temporary directory'         , default=None)
    parser.add_option('--stretch'       , dest='stretch', help='Stretch'                     , default=None, type='float')

    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)

#---
def parseOptions(parser):
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

    return (opt,args)


if __name__ == '__main__':
    import optparse
    ## option parser
    usage = 'usage: %prog [options] datacard'
    parser = optparse.OptionParser(usage)

    addOptions(parser)
    (opt, args) = parseOptions(parser)

    try:
        dcpath = args[0]
    except IndexError:
        parser.print_usage()
        sys.exit(0)
    
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




#---
#     def _syst(self,process):
#         '''sum all the uncertainties in quadrature for a given process'''
#         import math
#         sum2 = 0
#         for (name, nofloat, pdf, args, errline) in self._DC.systs:
#             if 'shape' in pdf: continue
#             if pdf == 'gmN': continue
#             
#             try:
#                 x = errline[self._bin][process]
#                 if not x: continue 
#                 sum2 += (x-1)*(x-1)
#             except:
#                 pass
#         return math.sqrt(sum2)


#     def _rooPdf2TH1(self,h, pdf, pars=None, norm=None):
#         # consider the othe option
#         # 
#         # Check upstream the dependencies:
#         # data = w.data('data_obs')
#         # model_s = w.pdf('model_s')
#         # obs = model_s.getObservables(data)
#         # if ( obs.getSize() != 1 ) raise ValueError('Only 1D shapes are supported')
#         # x = obs.first()
#         # h = model_s.createHistogram(name,x)

#         
#         '''Converts a pdf into a numpy array
#         The pdf is plotted against the data stored in the builder.
#         A custom set of parameters and normalisation can be applied'''
#         data = self._data

#         pdf_obs  = pdf.getObservables(data)
#         pdf_pars = pdf.getParameters(data)

#         if h.GetNbinsX() != data.numEntries():
#             raise ValueError('bins mismatch!')
#         
#         if pars:
#             pdf_pars.__assign__(ROOT.RooArgSet(pars))

#         for i in xrange(data.numEntries()):
#             pdf_obs.__assign__(data.get(i))
#             h.SetBinContent(i+1,pdf.getVal(pdf_obs))

#         if norm:
#             if isinstance(norm,ROOT.RooAbsReal):
#                 norm = norm.getVal()
#             self._logger.debug('pdf %s, h %s, Normalization %f -> %f',pdf.GetName(), h.GetName(),h.Integral(), norm)
#             h.Scale(norm/h.Integral())
#         elif norm==0:
#             # just in case we are normalizing a 0 integral to 0 (0/0 is bad)
#             h.Scale(0)
#         elif norm==None:
#             print 'No norm'
