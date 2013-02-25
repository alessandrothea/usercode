#!/usr/bin/env python
import optparse
import os.path
import subprocess
import hwwinfo
import hwwtools
import hwwlimits

mypath = os.path.dirname(os.path.abspath(__file__))

plot_tmpl = '''
    makeLimitTable.py {option}
    [[ $? -ne 0 ]] && exit -1
#     mkdir -p plots
#     root -b -l -q '{mypath}/PlotLimit.C+g("limits/{option}_shape.summary","plots/{tag}_{name}_{option}","{lumi} fb^{{-1}}", 110, 160, 0, 0, "H #rightarrow WW #rightarrow 2l2#nu" , 0)'
    mkdir -p tables
    pdflatex --output-directory tables limits/{option}_shape.tex
    rename {option} {tag}_{name}_{option} tables/{option}_shape*
    pdfcrop tables/{tag}_{name}_{option}_shape.pdf
    convert -density 200x200 tables/{tag}_{name}_{option}_shape-crop.pdf tables/{tag}_{name}_{option}_shape-crop.png
    rm -r `dir -1 tables/* | grep -v crop`
'''

# void PlotLimit(string  limitFiles   = "inputs/ana_ICHEP_limits_nj_shape7teV_cut8TeV.txt",
#            string  outputPrefix = "combined",
#            string  luminosity   = "5.1 fb^{-1} (8 TeV) + 4.9 fb^{-1} (7 TeV)",
#            Float_t mhmin        = 110,
#            Float_t mhmax        = 160,
#            Int_t   setLogx      = 0,
#            Int_t   setLogy      = 1,
#            string  title        = "H #rightarrow WW #rightarrow 2l2#nu",
#            Bool_t  drawObserved = 1,
#            Int_t   ratio        = 0,
#            string  format       = "pdf")
# {


def runTheShape():
    usage = 'usage: %prog -t tag -p prefix channel'
    parser = optparse.OptionParser(usage)
    parser.add_option('--tag'   ,'-t', dest='tag'  , help='tag to identify the plots' , default=None)
    parser.add_option('--prefix','-p',dest='prefix', help='prefix', default='.')
    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)
    (opt, args) = parser.parse_args()

    tag = opt.tag.replace(' ','_')

    if not args:
        raise ValueError('Desired channels missing: check the usage')


    
    if args[0] in hwwlimits.dcnames:
        plots = hwwlimits.dcnames[args[0]]
    else:
        plots = args[:]
        
    if opt.prefix:
        os.chdir(opt.prefix)

    name = opt.prefix if opt.prefix[-1] != '/' else opt.prefix[:-1] 


    macropath = os.path.join(os.path.dirname(mypath),'macros')

    import ROOT
    hwwtools.loadAndCompile(macropath+'/tdrstyle.C')
    hwwtools.loadAndCompile(macropath+'/PlotLimit.C')

    pars = {
        'tag' : tag,
        'option' : '',
        'mypath' : mypath,
        'name' : name,
        'lumi' : opt.lumi
    }
    print pars
    os.system('mkdir -p plots')
    for plot in plots:
        print plot
        pars['option'] = plot
        command = plot_tmpl.format(tag=tag,option=plot,mypath=macropath,name=name,lumi=opt.lumi)

        print command
        p = os.system(command)

        ROOT.gROOT.SetBatch(True)
        ROOT.setTDRStyle()
        ROOT.PlotLimit("limits/{option}_shape.summary".format(**pars),
                       "plots/{tag}_{name}_{option}".format(**pars),
                       "{lumi} fb^{{-1}}".format(**pars), 
                       110, 600, 1, 1, 
                       "H #rightarrow WW #rightarrow 2l2#nu",
                       True, 0, 'pdf')
        ROOT.PlotLimit("limits/{option}_shape.summary".format(**pars),
                       "plots/{tag}_{name}_{option}".format(**pars),
                       "{lumi} fb^{{-1}}".format(**pars), 
                       110, 600, 1, 1, 
                       "H #rightarrow WW #rightarrow 2l2#nu",
                       True, 0, 'png')
        ROOT.PlotLimit("limits/{option}_shape.summary".format(**pars),
                       "plots/{tag}_{name}_{option}".format(**pars),
                       "{lumi} fb^{{-1}}".format(**pars),
                       110, 250, 0, 1,
                       "H #rightarrow WW #rightarrow 2l2#nu",
                       True, 0, 'pdf')
        ROOT.PlotLimit("limits/{option}_shape.summary".format(**pars),
                       "plots/{tag}_{name}_{option}".format(**pars),
                       "{lumi} fb^{{-1}}".format(**pars),
                       110, 250, 0, 1,
                       "H #rightarrow WW #rightarrow 2l2#nu",
                       True, 0, 'png')

#     p.communicate()
#     os.system('; '.join(commands))
    
    
if __name__ == '__main__':
    runTheShape()

