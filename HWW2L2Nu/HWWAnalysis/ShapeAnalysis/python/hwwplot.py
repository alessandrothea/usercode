
import os
import ROOT
import HWWAnalysis.Misc.odict as odict
import logging
import hwwtools
import pdb

_defaults  = odict.OrderedDict([ 
    ('ggH',  { 'color':ROOT.kRed+1, 'label':'ggH', }),
    ('vbfH', { 'color':ROOT.kRed+2, 'label':'qqH', }),
    ('wzttH',{ 'color':ROOT.kRed+3, 'label':'VH' , }),
    ('VH',   { 'color':ROOT.kRed+3, 'label':'VH' , }),
    ('zH',   { 'color':ROOT.kRed-3, 'label':'zH' , }),
    ('wH',   { 'color':ROOT.kRed-4, 'label':'wH' , }),

    ('VV',   { 'color':858, 'label':'WZ/ZZ' , }),  
    ('DYTT', { 'color':418, 'label':'DY+jets' , }),
    ('DYLL', { 'color':419, 'label':'DY+jets' , }),
    ('Vg',   { 'color':617, 'label':'V+#gamma' , }),
    ('VgS',  { 'color':618, 'label':'V+#gamma*' , }),
    ('WJet', { 'color':921, 'label':'W+jets' , }),
    ('Top',  { 'color':400, 'label':'top' , }),
    ('WW',   { 'color':851, 'label':'WW' , }),
    ('ggWW', { 'color':853, 'label':'WW' , }),
])


if not ROOT.gROOT.GetListOfClasses().FindObject('PlotVHqqHggH'):
    shape_path = os.path.join(os.getenv('CMSSW_BASE'),'src/HWWAnalysis/ShapeAnalysis')
    print 'Shape directory is',shape_path

    print 'Loading PlotVHqqHggH.C'
    hwwtools.loadAndCompile(shape_path+'/macros/PlotVHqqHggH.C')

class HWWPlot(ROOT.PlotVHqqHggH):
    _log = logging.getLogger('HWWPlot') 
    
    _properties = ['label','color','scale','norm']

    #---
    def __init__(self, properties=_defaults):
        super(HWWPlot,self).__init__()

        self._properties = properties
        self._sortbydef = False

        self._data = None
        self._sigs = odict.OrderedDict()
        self._bkgs = odict.OrderedDict()
        self._errors = None

    @property
    def properties(self):
        return self._properties

    def _add(self, name, coll, h, **kwargs):
        coll[name] = (h,kwargs) 

    def setautosort(self, auto=True):
        self._sortbydef = auto

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
        

        itproc = coll.iterkeys() if not self._sortbydef else self._properties.iterkeys()
            
        # and fill them
        for name in itproc:
            try:
                (h,props) = coll[name]
            except KeyError:
                # some of the processes might not be there
                continue
            # 
            dummy = self._properties[name].copy()
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
