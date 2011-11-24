#!/usr/bin/env python
  
import os
import re
import optparse
import ROOT
from ROOT import *


from HWWAnalysis.Misc.odict import OrderedDict


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class Yield:
    def __init__(self,*args,**kwargs):
#         print 'args=',args
#         print 'kwargs=',kwargs
        if not args:
            raise RuntimeError('Specify number of entries')
        self._N = args[0]
        if 'name' in kwargs:
            self._name = kwargs['name']
        if 'entries' in kwargs:
            self._entries = kwargs['entries']

#         print self.__dict__


class ShapeLoader:
    '''Load the histogram data from the shape file
    + Yields
    + Nuisance shapes and parameters'''

    def __init__(self, path):
#         self._systRegex = re.compile('^histo_([^_]+)_CMS_(.+)(Up|Down)$')
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
        self._systematics = sorted([ name for name in names if self._systRegex.match(name) ])
#         print '\n'.join(self._nominals)
#         print '\n'.join(self._systematics)
        for name in self._nominals:
            process = self._nomRegex.match(name).group(1)
            h = self._src.Get(name)
            N =  h.Integral(0,h.GetNbinsX())
            entries = h.GetEntries()

            self._yields[process] = Yield( N, name=process, entries=entries ) 
#             self._yields[process] = Yield( N, name=process, entries=entries, shape=h ) 
#             print process, '%.3f' % h.Integral(0,h.GetNbins())
        
#         print self._systematics
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

#         del ups['p_scale_j'][0]
#         del ups['p_scale_e'][1]
        # check 
        for effect in ups:
            if set(ups[effect]) != set(downs[effect]):
                sUp = set(ups[effect])
                sDown = set(downs[effect])
                raise RuntimeError('Some systematics shapes for '+effect+' not found in up and down variation: \n '+', '.join( (sUp | sDown) - ( sUp & sDown ) ))
        
        # all checks out, save only one
        self._effects = ups


def mergeHistos(histograms):
    ROOT.TH2F.AddDirectory( False )
    ## FIXME: make something automatic to check binning and histogram size
#     histo = ROOT.TH1D('h', 'h', 25, 0, 200)
    first = sorted(histograms)[0]
    histo = histograms[first].Clone()
    histo.Reset()
    #histo = histograms[1].Clone()
##     for i in range(histo.GetNbinsX()):
##         histo.SetBinContent(bin+1, 0.)
    for h in histograms:
        histo.Add(histograms[h])
    return histo

def getZerobins(hist):
    zerobins = []
    for i in range(hist.GetNbinsX()):
        bin = i+1
        content = hist.GetBinContent(bin)
        if content != 0.:
            continue
        else:
            zerobins.append(bin)
    return zerobins




#masses = [130]

masses  = ['110','115','120','130','140','150','160','170','180','190',
           '200','250','300','350','400','450','500', 
           '550','600'] 


flavours = ['sf', 'of']
jetbins = [0,1]


def main():

    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    
    parser.add_option('-i','--input',dest='inputdir',help='Input directory', default='syst')

    (opt, args) = parser.parse_args()
    if opt.inputdir is None:
        parser.error('No input directory defined')


    inputdir = opt.inputdir

    problematic = OrderedDict()
    for mass in masses:
        for flav in flavours:
            for jetbin in jetbins:
            
                print '- Processing',mass, jetbin, flav
            
                shapeTmpl = inputdir+'hww-4.63fb.mH{mass}.{flavor}_{jets}j_shape.root'
                loader = ShapeLoader(shapeTmpl.format(mass = mass, jets=jetbin, flavor=flav) )

                loader.load()

                data = OrderedDict()
                signal = OrderedDict()
                background = OrderedDict()
                
                for name in loader._nominals:
                    process = loader._nomRegex.match(name).group(1)
                    h = loader._src.Get(name)
                    if process == 'Data':
                        data[process] = h
                    elif process == 'ggH' or process == 'vbfH':
                        signal[process] = h
                    else:
                        background[process] = h

                h_data = mergeHistos(data)
                h_signal = mergeHistos(signal)
                h_background = mergeHistos(background)


                ## get the bins with no entries in background
                background_zerobins = getZerobins(h_background)
                data_zerobins = getZerobins(h_data)
                signal_zerobins = getZerobins(h_signal)

                ## check the content in these bins for data and signal
                for bin in background_zerobins:
                    if h_data.GetBinContent(bin) != 0.:
                        print shapeTmpl.format(mass = mass, jets=jetbin, flavor=flav)
                        problematic[shapeTmpl.format(mass = mass, jets=jetbin, flavor=flav)] = bin
                    if h_signal.GetBinContent(bin)  != 0.:
                        print shapeTmpl.format(mass = mass, jets=jetbin, flavor=flav)
                        problematic[shapeTmpl.format(mass = mass, jets=jetbin, flavor=flav)] = bin



##                 processes = []
##                 effects = []
##                 vars = []
                histos = {}
                for name in loader._systematics:
                    h = loader._src.Get(name)
                    (process,effect,var) = loader._systRegex.match(name).group(1,2,3)

                    if process not in histos:
                        histos[process] = []
                    histos[process].append(h)

                for name in loader._nominals:
                    process = loader._nomRegex.match(name).group(1)
                    h = loader._src.Get(name)
                    if h.Integral() == 0. or process == 'Data':
                        continue
                    n_zeros = getZerobins(h)
                    for hist in histos[process]:
                        s_zeros = getZerobins(hist)

                    if s_zeros != n_zeros:
                        #print 'Bin migration between nominal and  syst obserevd!!'
                        print 'Process '+name+' in '+shapeTmpl.format(mass = mass, jets=jetbin, flavor=flav)
                        #print s_zeros, n_zeros
                        print [item for item in s_zeros if not item in n_zeros], [item for item in n_zeros if not item in s_zeros]
                        #print '----------------------------------------------'



    print 'Summary for nominal histograms:'
    for file in problematic:
        print file, problematic[file]

                    
if __name__ == '__main__':
    main()

    
