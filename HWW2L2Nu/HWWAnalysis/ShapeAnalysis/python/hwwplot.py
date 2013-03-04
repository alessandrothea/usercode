
import os
import ROOT
import HWWAnalysis.Misc.odict as odict
import logging
import hwwtools
import pdb

_defaults  = {
    'ggH':  { 'color':ROOT.kRed+1, 'label':'ggH', },
    'vbfH': { 'color':ROOT.kRed+2, 'label':'qqH', },
    'VH':   { 'color':ROOT.kRed+3, 'label':'VH' , },
    'zH':   { 'color':ROOT.kRed-3, 'label':'zH' , },
    'wH':   { 'color':ROOT.kRed-4, 'label':'wH' , },

    'VV':   { 'color':858, 'label':'WZ/ZZ' , },  
    'WJet': { 'color':921, 'label':'W+jets' , },
    'Vg':   { 'color':617, 'label':'V+#gamma' , },
    'VgS':  { 'color':618, 'label':'V+#gamma*' , },
    'Top':  { 'color':400, 'label':'top' , },
    'DYTT': { 'color':418, 'label':'DY+jets' , },
    'DYLL': { 'color':419, 'label':'DY+jets' , },
    'WW':   { 'color':851, 'label':'WW' , },
    'ggWW': { 'color':853, 'label':'ggWW' , },

}


if not ROOT.gROOT.GetListOfClasses().FindObject('PlotVHqqHggH'):
    shape_path = os.path.join(os.getenv('CMSSW_BASE'),'src/HWWAnalysis/ShapeAnalysis')
    print 'Shape directory is',shape_path

    print 'Loading PlotVHqqHggH.C'
    hwwtools.loadAndCompile(shape_path+'/macros/PlotVHqqHggH.C')

class HWWPlot(ROOT.PlotVHqqHggH):
    _log = logging.getLogger('HWWPlot') 
    
    _properties = ['label','color','scale','norm']

    # enum
    SIG = 1
    BGK = 2

    # rename

    #---
    def __init__(self, defaults=_defaults):
        super(HWWPlot,self).__init__()

        self._defaults = defaults

        self._data = None
        self._sigs = odict.OrderedDict()
        self._bkgs = odict.OrderedDict()
        self._errors = None

    def _add(self, name, coll, h, **kwargs):
        coll[name] = (h,kwargs) 

    def seterror(self,eg):
        self._errors = eg

    def setdata(self, h):
        self._data = h

    def addsig(self, name, h, **kwargs):
        self._add( name, self._sigs, h, **kwargs) 

    def addbkg(self, name, h, **kwargs):
        self._add( name, self._bkgs, h, **kwargs) 

    def _fillvecs(self, coll ):

        # init the vectors
        vecs = {
            'color' : ROOT.vector('int')(),
#             'syst' : ROOT.vector('double')(),
            'scale' : ROOT.vector('double')(),
            'label' : ROOT.vector('std::string')(),
            'norm'  : ROOT.vector('double')(),
            'th1'   : ROOT.vector('TH1*')(),
        }

        # and fill them
        for name,(h,props) in coll.iteritems():
            # 
            dummy = self._defaults[name].copy()
            dummy.update(props)

            vecs['th1']  .push_back(h)
            vecs['label'].push_back( dummy.get('label',h.GetTitle() ) )
            vecs['color'].push_back( dummy.get('color',h.GetFillColor() ) )
            vecs['scale'].push_back( dummy.get('scale',1. ) )
            # negative normalisation is not applied
            vecs['norm'] .push_back( dummy.get('norm',-1. ) )

        return vecs

    #---
    def prepare(self):

        if self._data:   self.setDataHist(self._data)
        if self._errors: self.set_ErrorBand(self._errors)

        vecSig = self._fillvecs(self._sigs)
        vecBkg = self._fillvecs(self._bkgs)

        
        self.set_vectTHSig(vecSig['th1'])
        self.set_vectNameSig(vecSig['label'])
        self.set_vectColourSig(vecSig['color'])

        self.set_vectTHBkg(vecBkg['th1'])
        self.set_vectNameBkg(vecBkg['label'])
        self.set_vectColourBkg(vecBkg['color'])

        super(HWWPlot,self).prepare()

if __name__ == '__main__':
    # 
    pass
