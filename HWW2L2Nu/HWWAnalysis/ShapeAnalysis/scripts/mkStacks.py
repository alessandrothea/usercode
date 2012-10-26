#!/usr/bin/env python

import os
import optparse
import sys
import re
import hwwinfo
import hwwtools
import fnmatch


import ROOT
import HWWAnalysis.Misc.ROOTAndUtils as utils

class H1UpDownPlotter:
    def __init__(self, **kwargs):
        self._ratio   = 0.7
        self._outer   = 0.1
        self._inner   = 0.02
        self._marg    = 0.1
        self._ltitle  = ''
        self._rtitle  = ''
        self._scale   = 1.4
        self._xtitle  = None
        self._ytitle  = None
        self._lumi    = None
        self._ytitle2 = 'ratio'
        self._legsize = (0.25,0.25)
        self._colors  = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue]
        self._lstyles = [1,1,2]
        self._lwidths = [3,3,3]
        self._h0      = None
        self._hists   = []
        self._pad0    = None
        self._pad1    = None
        self._legend  = None
        self._logx    = False
        self._logy    = False
        self._stack   = None
        self._dstack   = None

        for k,v in kwargs.iteritems():
            if not hasattr(self,'_'+k): continue
            setattr(self,'_'+k,v)

    def __del__(self):
        del self._h0
#         del self._h1

    @staticmethod
    def _resize(x,ratio):
        x.SetLabelSize(x.GetLabelSize()*ratio/(1-ratio))
        x.SetTitleSize(x.GetTitleSize()*ratio/(1-ratio))

    def set(self, h0, *hs ):
        if not hs:
            raise RuntimeError('cannot compare only 1 histogram')
        n = h0.GetDimension()
        if True in [ h.GetDimension() != n for h in hs ]:
            raise ValueError('Cannot compare histograms with different dimensions')
        sentry = utils.TH1AddDirSentry()
        self._h0 = h0.Clone()
        self._hists = [ h.Clone() for h in hs ]


    def draw(self, options='hist'):
        import ROOT
        if not ROOT.gPad.func():
            raise RuntimeError('No active pad defined')

        thePad = ROOT.gPad.func()
        thePad.cd()

        self._pad0 = ROOT.TPad('pad0','pad0',0.,(1-self._ratio),1.,1.)
        ROOT.SetOwnership(self._pad0,False)
        self._pad0.SetLogx( 1 if self._logx else 0 )
        self._pad0.SetLogy( 1 if self._logy else 0 )
        self._pad0.SetTopMargin(self._outer/self._ratio)
        self._pad0.SetBottomMargin(self._inner/self._ratio)
        self._pad0.SetTicks()
        self._pad0.Draw()

        self._pad0.cd()

        hists = [self._h0] + self._hists
        ndim = hists[0].GetDimension()

        marker = 24 if ndim == 1 else 1
        map(ROOT.TH1.SetLineWidth,hists, self._lwidths)
#         map(lambda h: ROOT.TH1.SetLineWidth(h,2),hists)
        map(lambda h: ROOT.TH1.SetMarkerStyle(h,marker),hists)

        for i,h in enumerate(hists):
            h.SetLineColor(self._colors[i])
            h.SetMarkerColor(self._colors[i])
            h.SetLineStyle(self._lstyles[i])

        
        self._stack = None

        stack = ROOT.THStack('overlap','')
        ROOT.SetOwnership(stack,True)

        stack.Add(hists[0],'e1')
        for h in hists[1:]: stack.Add(h,'hist') 

        stack.Draw('nostack')
        stack.SetMaximum(self._scale*max([h.GetMaximum() for h in hists]))
        stack.GetXaxis().SetLabelSize(0.00)
        stack.GetYaxis().SetTitle(self._ytitle if self._ytitle else self._h0.GetYaxis().GetTitle())

        anchor = [1-self._marg,1-self._outer/self._ratio]
        anchor[1] -= 0.05


        self._legend = None
        legend = ROOT.TLegend(anchor[0]-self._legsize[0],anchor[1]-self._legsize[1],anchor[0],anchor[1],'','NDC')
        legend.SetFillColor(ROOT.kWhite)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        # leg.SetNColumns(2)
        map(legend.AddEntry,hists,['Nominal','+1#sigma-shape','-1#sigma-shape'],['fl']*3)
#         for h in hists: legend.AddEntry(h,'','fl')
        legend.Draw()
        self._legend = legend


        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextAlign(12)
        l.DrawLatex(ROOT.gPad.GetLeftMargin(),1-(0.5*self._outer/self._ratio),self._ltitle)
        l.SetTextAlign(32)
        l.DrawLatex(1-ROOT.gPad.GetRightMargin(),1-(0.5*self._outer/self._ratio),self._rtitle)

        self._stack = stack

        l.SetTextAlign(22)

        anchorCMS = [0.25,0.09]
        l.SetTextSize(0.9*l.GetTextSize())
        l.DrawLatex(ROOT.gPad.GetLeftMargin()+anchorCMS[0],1-ROOT.gPad.GetTopMargin()-anchorCMS[1],'CMS Preliminary')

        if self._lumi:
            anchorCMS = [0.25,0.15]
            l.SetTextSize(0.9*l.GetTextSize())
            l.DrawLatex(ROOT.gPad.GetLeftMargin()+anchorCMS[0],1-ROOT.gPad.GetTopMargin()-anchorCMS[1],'L = %.1f fb^{-1}' % self._lumi)

        #- pad2 ---

        sentry = utils.TH1AddDirSentry()
#         print thePad
        thePad.cd()
        self._pad1 = ROOT.TPad('pad1','pad1',0.,0.0,1.,(1-self._ratio))
        ROOT.SetOwnership(self._pad1,False)
        self._pad1.SetTopMargin(self._inner/(1-self._ratio))
        self._pad1.SetBottomMargin(self._outer/(1-self._ratio))
        self._pad1.SetTicks()
        self._pad1.SetGridy()
        self._pad1.Draw()

        self._pad1.cd()

        hdiffs = []
        for i,h in enumerate(hists):
            hd = h.Clone('diff'+h.GetName())
            hd.Divide(self._h0)
            hd.SetMarkerStyle(20)
            hd.SetLineWidth(self._lwidths[i])
#             hd.SetLineColor(ROOT.kBlack)
#             hd.SetMarkerColor(ROOT.kBlack)
            hd.SetLineColor(self._colors[i])
            hd.SetMarkerColor(self._colors[i])
            hdiffs.append(hd)

        line = hdiffs[0]
        for i in xrange(line.GetNbinsX()+1):
            line.SetAt(1.,i)


        self._dstack = None

        dstack = ROOT.THStack('diffs','')
        ROOT.SetOwnership(dstack,False)

        map(dstack.Add,hdiffs,['hist']*len(hdiffs))
        dstack.Draw('nostack')
        dstack.SetMaximum(2.)

        ax = dstack.GetXaxis()
        ay = dstack.GetYaxis()
        ax.SetTitle( self._xtitle if self._xtitle else self._h0.GetXaxis().GetTitle() )
        ay.SetTitle(self._ytitle2)
        ay.SetTitleOffset(ay.GetTitleOffset()/self._ratio*(1-self._ratio) )
        self._resize(ax,self._ratio)
        self._resize(ay,self._ratio)

        self._dstack = dstack




#from ROOT import *

## legend title dictionary
legproc = {
    'ggWW':'gg #rightarrow WW',
    'WW':'qq #rightarrow WW',
    'ggH':'gg #rightarrow H',
    'Top':'Top',
    'wzttH':'ass. prod. H',
    'Vg':'V#gamma',
    'WJet':'W+Jets',
    'DYLL':'Z#rightarrow ll',
    'DYTT':'Z#rightarrow #tau #tau',
    'VV':'di-boson',
    'vbfH':'VBF H'
    }

legsyst = {
    'CMS_met':'#slashed{E}_{T}',
    ## '':'',
    ## '':'',
    ## '':'',
    ## '':'',
    ## '':'',
    ## '':'',
    ## '':'',
    }


def openTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f


def getHist(file, hist):
    h = file.Get(hist)
    if not h.__nonzero__():
        raise NameError('Histogram '+hist+' doesn\'t exist in '+str(file))
    return h

def getFiles(dir):
    list = os.listdir(dir)
    list.sort()
    ## remove non root files
    cleaned = [l for l in list if '.root' in l]
    return cleaned

def getNominals(file):
#     rootFile = ROOT.TFile.Open(file)
    finder = utils.ObjFinder("TH1D")
    names = finder.findRecursive(file)
    nomRegex  = re.compile('^histo_([^_]+)$')

    nominals = {}
    for name in names:
        if not nomRegex.match(name):
            continue
        h = getHist(file,name)
        nominals[name.replace('histo_','')] = h
                 
    return nominals

class variation:
    def __repr__(self):
        return str(self.__dict__)

def getNominalUpDown(file):
    finder = utils.ObjFinder("TH1D")
    names = finder.findRecursive(file)
    nomRegex  = re.compile('^histo_([^_]+)$')
    systRegex = re.compile('^histo_([^_]+)_(.+)(Up|Down)$')

    nominals = {}
    nomupdown = {}
    for name in names:
        if not nomRegex.match(name):
            continue
        h = getHist(file,name)
        nominals[name.replace('histo_','')] = h

    for name in names:
        m = systRegex.match(name)
        if not m: continue
        
        process,syst,var = m.group(1,2,3)

        if process not in nomupdown:
            nomupdown[process] = {}
        
        if not syst in nomupdown[process]:
            v =  variation()
            v.Nom = nominals[process]
            nomupdown[process][syst] = v

        hUpDown = getHist(file,name)
        setattr(nomupdown[process][syst],var,hUpDown)


    return nomupdown

    
def makeNominalPlots(file,outputdir, opt):

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    # open the file
    f = openTFile(file)

    # in one root file,there is one set of nominal
    # histograms to plot, so get those...

    reMass = re.compile('.+\.mH(\d+)\..+\.root')
    m = reMass.match(file)
    if not m: 
        raise RuntimeError('Mass label not found in '+file)
    mass = int(m.group(1))

    nominals = getNominals(f)

    histo = nominals['ggH']
    if 'vbfH' in nominals:
        histo.Add(nominals['vbfH'])
    nominals['HWW'] = histo

    histo = nominals['ggWW']
    histo.Add(nominals['WW'])
    nominals['WWsum'] = histo

    histo = nominals['Vg']
    histo.Add(nominals['VV'])
    nominals['VVsum'] = histo

    histo = nominals['DYLL'].Clone()
    if 'DYTT' in nominals:
        histo.Add(nominals['DYTT'])
    nominals['DYsum'] = histo

    plot = ROOT.MWLPlot()
    plot.setStackSignal(opt.stacksignal)
    if opt.showdata:
        plot.setDataHist(nominals['Data'])

    plot.setHWWHist(nominals['HWW'])
    plot.setWWHist(nominals['WWsum'])  
    plot.setZJetsHist(nominals['DYsum'])
    plot.setTopHist(nominals['Top'])
    plot.setVVHist(nominals['VVsum'])
    plot.setWJetsHist(nominals['WJet'])


#    plot.setWZHist(nominals[])
##     plot.setZZHist(nominals[])
##     plot.setFakesHist(nominals[])

    ratio = opt.ratio and opt.showdata


    cName = 'c_'+file.split('/')[-1].replace('.root','').replace('.','_')
    c = ROOT.TCanvas(cName,cName) if ratio else ROOT.TCanvas(cName,cName,1000,1000)
    if opt.logY: c.SetLogy()
    plot.setMass(mass)
    plot.setLumi(opt.lumi)
    plot.setLabel(opt.xlabel)
    plot.Draw(c,1,ratio)

#     c.ls()
    c.Print(outputdir+'/'+cName+'.pdf')
    c.Print(outputdir+'/'+cName+'.png')
#     c.Print(outputdir+'/'+cName+'.root')

#    c.Delete()

    f.Close()

def makeShapeUpDown(file,outputdir, opt):

    # open the file
    f = openTFile(file)

    # in one root file,there is one set of nominal
    # histograms to plot, so get those...

    reMass = re.compile('.+\.mH(\d+)\..+\.root')
    m = reMass.match(file)
    if not m: 
        raise RuntimeError('Mass label not found in '+file)

    mass = int(m.group(1))
    print 'Detected mass',mass
    odir = outputdir+'/'+m.group(1)
    os.system('mkdir -p '+odir)
    
    (root,ext) = os.path.splitext(os.path.basename(file))
#     print root,ext
    
    updown = getNominalUpDown(f)
    for process,systs in updown.iteritems():
        for syst,vars in systs.iteritems():
            if not fnmatch.fnmatch(syst, opt.filter):
                continue

            if vars.Nom.GetEntries() == 0: continue
            
            pName = ('%s_%s_%s' % (root,process,syst)).replace('.','_')
            cName = 'c_'+pName
            fName = odir+'/'+pName
            c = ROOT.TCanvas(cName,cName, 650, 794,)

            plotter = H1UpDownPlotter(xtitle=opt.xlabel, ytitle='entries', lumi=opt.lumi)
            plotter.set(vars.Nom, vars.Up, vars.Down)
            plotter.draw()

            legheader = legproc[process]+', m_{H} = '+str(mass)+', '+root.split('_')[0].split('.')[-1]+' '+root.split('_')[1]
            
            for ext in ['pdf','png']:
                c.SaveAs(fName+'.'+ext)

            del plotter
#             c = printUpDown(cName,fName,exts,syst,vars,xlabel,legheader)
            
            
def plotCMSText():
    lines = [ 'CMS Preliminary - #sqrt{s}=7 TeV']
    
    entries = [ ROOT.TLatex(0,0,line) for line in lines ]
    
    shrink = 0.7
    Dx = shrink * max([txt.GetXsize() for txt in entries])
    dy = shrink*entries[0].GetYsize()
    
    x0 = 0.1
    y0 = 0.9
    #         x0 = 0.115
    #         y1 = 0.885
    
    x1 = x0 + Dx
    y1 = y0+dy*len(lines)+0.01*(len(lines))
    
    pave = ROOT.TPaveText(x0,y0,x1,y1,'ndc')
    pave.SetFillColor(ROOT.kRed)
    pave.SetBorderSize(0)
    pave.SetMargin(0)
    pave.SetFillStyle(0)
    pave.SetTextAlign(11)
    
    pave.SetName('preliminary')
    
    for line in lines:
        pave.InsertText(line)
        
    return pave


def addOptions(parser):
    parser.add_option('-i' , '--input'       , dest='inputdir'    , help='Input dir')
    parser.add_option('-o' , '--output'      , dest='outputdir'   , help='Output dir'                          , default='.' )
    parser.add_option('-V' , '--variations'  , dest='variations'  , help='make the scale up/down stacks'       , default=False , action='store_true' )
    parser.add_option('-x' , '--xlabel'      , dest='xlabel'      , help='X-axis label'                        , default='' )
    parser.add_option('-r' , '--ratio'       , dest='ratio'       , help='Plot the data/mc ration'             , default=True  , action='store_false'  )
    parser.add_option('-s' , '--stacksignal' , dest='stacksignal' , help='Stack the signal on the backgrounds' , default=False , action='store_true' )
    parser.add_option('-n' , '--nodata'      , dest='showdata'    , help='Hide data histogram'                 , default=True  , action='store_false' )
    
    parser.add_option('-f' , '--filter'      , dest='filter'      , help='Filter on the variations'            , default='*')
    parser.add_option('-Y' , '--logY'        , dest='logY'        , help='Log Y axis'                          , default=False , action='store_true' )

def parseOptions(parser):
    # use
    # (opt, args) = parser.parse_args([])
    # with [] as arguments to have an opt object with the defaults

    (opt, args) = parser.parse_args()
    sys.argv.append('-b')

    if opt.inputdir is None:
        parser.error('No input file defined')

    return (opt, args)

def main():
    ## option parser
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)

    addOptions(parser)
    (opt, args) = parseOptions(parser)

    inputdir = opt.inputdir
    outputdir = opt.outputdir
    mass = opt.mass    

    # get MWLPlot.C
    shapepath = os.path.abspath(os.path.dirname(os.path.normpath(__file__))+'/..')
    print 'Shape main directory is',shapepath
    ROOT.gInterpreter.ExecuteMacro(shapepath+'/macros/LatinoStyle2.C')
    hwwtools.loadAndCompile(shapepath+'/macros/MWLPlot.C')
#     try:
#         ROOT.gROOT.LoadMacro(mypath+'/MWLPlot.C+g')
#     except RuntimeError:
#         ROOT.gROOT.LoadMacro(mypath+'/MWLPlot.C++g')

    filenames = getFiles(inputdir)
    # loop over all files
    for file in filenames:
        path = inputdir+'/'+file
        if str(mass) not in file and mass > 0:
            continue

        print 'Making',path
        if not opt.variations:
            makeNominalPlots(path, outputdir, opt)
        else:
            makeShapeUpDown(path,outputdir, opt)

    print 'Used options'
    print ', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()])

if __name__ == '__main__':

    main()

       
