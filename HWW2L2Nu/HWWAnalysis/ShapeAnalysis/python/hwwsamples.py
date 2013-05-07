import hwwtools
import re


signals = ['ggH','vbfH','wzttH','ggH_ALT','wH','zH','ttH']

#--------------
# mcsets,
# list of samples and compact dictionary
#
# filter the list of samples
# and create association     label          -> label                  -> vector of root files
#                       used by mkShapes      just for association       blabla.root
#

mcsets = {
    '0j1j-JHU' : [
        #signals
        'ggH','ggH_ALT','jhu_NORM','jhu_NLO',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown',
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template', 'Vg-template',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    '0j1j-JHUOthers' : [
        #signals
        'ggH','ggH_ALT','jhu_NORM','jhu_NLO','vbfH','wzttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown',
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    '0j1j' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown',
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    '0j1j-mH125' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown',
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j') ,         #    mkmerged vuole "-template"
        # mH125 as background
        'ggH125', 'vbfH125', 'wzttH125', 
    ],
     '0j1j-ss' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'Other','VgS','Vg','WJet',
        #'WW',
        #'ggWW','VgS','Vg','WJet',
        #'Top',
        #'VV','DYTT','DYLL',
        #'WWnlo','WWnloUp','WWnloDown','TopTW','TopCtrl',
        #,'WJetSS',
        # systematics
        #'WJetFakeRate-eUp', 'WJetFakeRate-eDn','WJetFakeRate-mUp', 'WJetFakeRate-mDn'
        # templates
        #'VgS-template','Vg-template','Top-template',
        # 0j1j specific
        #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        #('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    'cutbased' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW', 'VgS','Vg','WJet','Top','VV','DYTT',
        # templates
        'VgS-template','Vg-template',
        # replce ggWW and DYLL
        ('ggWW',    'WW'),
        ('DYLL',    'WW'),
    ],
    'vbf_sf' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        #'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT','DYLL',
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT',
        # dummy
        ('DYee', 'WW'),
        ('DYmm', 'WW'),
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        # templates
        'VgS-template','Vg-template',
    ],
   'vbf_of' : [
        #signals
        'ggH','vbfH','wzttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT',
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        # top shape ---> to be checked if needed
        #('TopTW',   'Top'),
        #('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 2j specific
        ('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        ('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
    ],
    'vh_sf' : [
        #signals
        'ggH','vbfH','wH','zH','ttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV',
        'VVV',
         # dummy
        ('DYee', 'WW'),
        ('DYmm', 'WW'),
        # templates
        'VgS-template','Vg-template',
    ],
   'vh_of' : [
        #signals
        'ggH','vbfH','wH','zH','ttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT',
        'VVV',
        # templates
        'VgS-template','Vg-template',
        # 2j specific
        #('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        #('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
        #('WJetFakeRate-nominal', 'WJetFakeRate-vh-template-nominal'),
        #('WJetFakeRate-eUp',     'WJetFakeRate-vh-template-nominal'),
        #('WJetFakeRate-eDn',     'WJetFakeRate-vh-template-nominal'),
        #('WJetFakeRate-mUp',     'WJetFakeRate-vh-template-nominal'),
        #('WJetFakeRate-mDn',     'WJetFakeRate-vh-template-nominal'),
        ('WJetFakeRate-2j-template', 'WJetFakeRate-nominal'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal'),
    ],

    'zh4j_mm' : [
        #signals
        'ggH','vbfH','wH','zH','ttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV',
        'VVV',
         # dummy
        ('DYee', 'WW'),
        ('DYmm', 'WW'),
        # templates
        'VgS-template','Vg-template',
    ],
   'zh4j_ee' : [
        #signals
        'ggH','vbfH','wH','zH','ttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV',
        'VVV',
         # dummy
        ('DYee', 'WW'),
        ('DYmm', 'WW'),
        # templates
        'VgS-template','Vg-template',
    ],

}

#--------------
def samples(mass, energytag, datatag='Data2012', sigtag='SM', mctag='all'):
    '''
    mass: mass for the higgs samples'
    datatag: tag for the dataset to be included
    sigtag: kind of signal (SM or Graviton)
    mctag: tag for the set of mc to be included
    '''

    
    if energytag == '8TeV':
        import samples.samples8TeV as sampledb
    elif energytag == '7TeV':
        import samples.samples7TeV as sampledb
    else:
        raise ValueError('Energy misdefined: '+energytag)

    signals = sampledb.signalSamples(sigtag,mass)

    mcsamples = {}
    mcsamples.update(signals)

    mcsamples.update(sampledb.backgrounds)
    if 'mH' in mctag:
        print mctag
        # get the background-higgs mass from the tag
        mHbkg = int(re.match('0j1j-mH(\d+)', mctag).group(1))
        print 'signal as background', mHbkg
        signalbkg = sampledb.signalSamples(sigtag, mHbkg, str(mHbkg))
        mcsamples.update(signalbkg)

    if isinstance(mctag,list):
        mclabels = mctag
    else:
        if mctag not in mcsets:
            raise ValueError('MCtag '+mctag+' not supported')
        mclabels = mcsets[mctag]

    selectedMc = hwwtools.filterSamples( mcsamples, mclabels )

    # add data
    selectedData = {}
    if datatag == 'NoData':
        pass
    elif 'Data' in datatag:
        selectedData['Data'] = sampledb.data[datatag]
    elif 'SI' in datatag:
        # add the signal samples of the given mass
        m = re.match('SI(\d+)',datatag)
        print 'SI with mH =', int(m.group(1))
        if not m:
            raise ValueError('Signal injection must have the format SImmm where mmm is the mass')
        simass = int(m.group(1))
        siSamples = sampledb.signalSamples(sigtag, simass,suffix='-SI')
        selectedData.update(siSamples)
    else:
        raise ValueError('Data tag '+datatag+' not supported')

    samples = {}
    samples.update(selectedMc)
    samples.update(selectedData)

    return samples



