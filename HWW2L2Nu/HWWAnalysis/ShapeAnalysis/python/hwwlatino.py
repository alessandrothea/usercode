import re
import hwwsamples
import HWWAnalysis.Misc.odict as odict
import ROOT
from ginger.analysis import TreeAnalyser,Latino

#_______________________________________________________________________
def makeanalysers(latinos,path,flow,lumi):

    analysers = odict.OrderedDict()

    for n in latinos.iterkeys():
        samples
        a = TreeAnalyser(latinos.latinos2samples(n,path),flow)
        a.lumi = lumi if n != 'Data' else 1
        analysers[n] = a

    return analysers

#_______________________________________________________________________
def printplots(plots,canv_name,**opts):

    import hwwplot
    plot = hwwplot.HWWPlot()
    plot.setautosort()

    plot.setdata(plots['Data'])


    for p in hwwplot._defaults:
        if p in plots:
            if p in hwwsamples.signals:
                plot.addsig(p,plots[p])
            else:
                plot.addbkg(p,plots[p])

    sentry = hwwplot.NullStdOutSentry()
    if 'order'  in opts: plot.setorder(opts['order'])
    if 'div'    in opts: plot.set_divide(opts['div'])
    if 'mass'   in opts: plot.setMass(opts['mass'])
    if 'lumi'   in opts: plot.setLumi(opts['lumi'])
    if 'xlabel' in opts: plot.setLabel(opts['xlabel'])
    if 'label'  in opts: plot.addLabel(opts['label'])
    if 'units'  in opts: plot.setUnits(opts['units'])
    del sentry

    plot.prepare()
    plot.mergeSamples() #---- merge trees with the same name! ---- to be called after "prepare"

    mass = 125
    stacksignal = False
    ratio=True

    c = ROOT.TCanvas(canv_name,canv_name) if ratio else ROOT.TCanvas(canv_name,canv_name,2)
    c.SetLogy( opts.get('logy',False) )
    plot.draw(c,1,ratio)


    for ext in opts.get('exts',['pdf']):
        c.Print(canv_name+'.'+ext)





#______________________________________________________________________________
class LatinoFastCollector(odict.OrderedDict):
    ''' this class is used to bridge between the current limited description of the samples to the new one.

    importraw is used to convert a list of files with a name into a Latino descriptor
    latinos2samples exports the list of Latino as List of Sample (to use with ChainWorker)
    '''

    #---
    def __init__(self, weights=() ):
        self._weights = weights
        odict.OrderedDict.__init__(self)

#     #---
#     def __setitem__(self,key,value):
#         if isinstance(value,Latino):
#             lsample = value
#         elif isinstance(value,list):
#             try:
#                 w = self._weights[key]
#             except KeyError:
#                 # what if there is no default?
#                 w = self._weights['default']
#             lsample = Latino(weight=w,files=value)
#
#         odict.OrderedDict.__setitem__(self,key,lsample)

    # ---
    def __setitem__(self,key,value):
        if isinstance(value,Latino):
            lsample = [ value ]
        elif isinstance(value,list) and all(isinstance(e,Latino) for e in value):
            lsample = value
        else:
            raise TypeError('only Latino and [Latino] can be added to the collector')

        odict.OrderedDict.__setitem__(self,key,lsample)

    # ---
    def importraw(self,key,value):
        if isinstance(value,list) and all(isinstance(s,str) for s in value):
            try:
                w = self._weights[key]
            except KeyError:
                # what if there is no default?
                w = self._weights['default']
            lsample = Latino(weight=w,files=value)
        else:
            raise TypeError('importraw wants list of files!')

        self.__setitem__(key,lsample)

    # ---
    def latinos2samples(self,key,masterpath):

        return [ l.makeSample(masterpath) for l in self[key] ]



    #---
#     def filter(self, collector, voc):

#         filtered = LatinoFastCollector(weight=self._weights.copy())
#         tome = dict([ e if isinstance(e,tuple) else (e,e) for e in voc])
#         for proc,label in tome.iteritems():
#             if label not in samples: continue

#             filtered[proc] = collector[label]

#         return filtered



weights = {
    'default'           : 'baseW*puW*effW*triggW',

    'WJet'              : 'baseW*fakeW*(run!=201191)',
    'WJetFakeRate-eUp'  : 'baseW*fakeWElUp*(run!=201191)',
    'WJetFakeRate-eDn'  : 'baseW*fakeWElDown*(run!=201191)',
    'WJetFakeRate-mUp'  : 'baseW*fakeWMuUp*(run!=201191)',
    'WJetFakeRate-mDn'  : 'baseW*fakeWMuDown*(run!=201191)',
    'WJetSS'            : 'baseW*fakeW*ssW*(run!=201191)',

    'WJet-template'              : 'baseW*fakeW',
    'WJetFakeRate-template'      : 'baseW*fakeWUp',
    'WJet-templatesyst'          : 'baseW*fakeWUp',

    'Data'              : '(run!=201191)',

    'DYTT'              : 'baseW*effW*triggW',
    'DYLL'              : 'baseW*puW*effW*triggW*(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))*(channel<1.5)',
    'DYee'              : 'baseW*puW*effW*triggW*(channel==1)',
    'DYmm'              : 'baseW*puW*effW*triggW*(channel==0)',
    'DYLL-template'     : 'baseW*puW*effW*triggW* dyW *(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))',
    'DYLL-templatesyst' : 'baseW*puW*effW*triggW*dyWUp*(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))',

#     'VgS'               : 'baseW*puW*effW*triggW*1.5',
    'Vg'                : 'baseW*puW*effW*triggW*kfW',
    'VgS'               : 'baseW*puW*effW*triggW*kfW',

    'ggH'               :'baseW*puW*effW*triggW*kfW',
    'qqH'               :'baseW*puW*effW*triggW*kfW',
    'vbfH'              :'baseW*puW*effW*triggW*kfW',

    'wH'                :'baseW*puW*effW*triggW*(mctruth == 26)',
    'zH'                :'baseW*puW*effW*triggW*(mctruth == 24)',
    'ttH'               :'baseW*puW*effW*triggW*(mctruth == 121)',


}


#         weights['Data']              = '(run!=201191)'
#         # problem with DYTT using embedded for em/me, for ee/mm it is inlcuded in DD DY estimate
#         weights['DYTT']              = self._stdWgt
#         weights['DYLL']              = self._stdWgt+'*(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))*(channel<1.5)'
#         weights['DYee']              = self._stdWgt+'*(channel<1.5)'
#         weights['DYmm']              = self._stdWgt+'*(channel<1.5)'
#         weights['DYLL-template']     = self._stdWgt+'* dyW *(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))'
#         weights['DYLL-templatesyst'] = self._stdWgt+'*dyWUp*(1-(( dataset == 36 || dataset == 37 ) && mctruth == 2 ))'
#         #systematics
#         weights['TopCtrl']           = self._stdWgt+'*bvetoW'
#         weights['Top-template']      = self._stdWgt+'*bvetoW'
#         #filter and k-factor on Vg* done by kfW
#         weights['VgS']               = self._stdWgt+'*kfW'
#         weights['Vg']                = self._stdWgt+'*kfW'
#         weights['ggH']               = self._stdWgt+'*kfW'
#         weights['vbfH']              = self._stdWgt+'*kfW'

#         weights['wH']                = self._stdWgt+'*(mctruth == 26)'
#         weights['zH']                = self._stdWgt+'*(mctruth == 24)'
#         weights['ttH']               = self._stdWgt+'*(mctruth == 121)'






#--------------
def samples(mass, energy='8TeV',datatag='Data2012', sigtag='SM', mctag='all'):
    samples = hwwsamples.samples(mass,energy,datatag,sigtag,mctag)
    latinos = LatinoFastCollector(weights)

    for s in sorted(samples):
        # we build a 1-d array to be used to create a ChainWorker later
#         latinos[s] = [ latinos.importraw(s,samples[s]) ]
        latinos.importraw(s,samples[s])

    return latinos



