#!/usr/bin/env python
import optparse
import os.path
import subprocess
import hwwinfo

mypath = os.path.dirname(os.path.abspath(__file__))

plot_tmpl = '''
    makeLimitTable.py {option}
    root -b -l -q '{mypath}/PlotLimit.C+("limits/{option}_shape.summary","{tag}_{name}_{option}", 1,1)'
    mkdir -p tables
    pdflatex --output-directory tables limits/{option}_shape.tex
    rename {option} {tag}_{name}_{option} tables/{option}_shape*
    pdfcrop tables/{tag}_{name}_{option}_shape.pdf
    convert -density 200x200 tables/{tag}_{name}_{option}_shape-crop.pdf tables/{tag}_{name}_{option}_shape-crop.png
    rm -r `dir -1 tables/* | grep -v crop`
'''


def runTheShape():
    usage = 'usage: %prog -t tag -p prefix channel'
    parser = optparse.OptionParser(usage)
    parser.add_option('-t','--tag',dest='tag')
    parser.add_option('--prefix','-p',dest='prefix',help='prefix',default=None)
    hwwtools.loadOptDefaults(parser)
    (opt, args) = parser.parse_args()

    tag = opt.tag.replace(' ','_')

    if not args:
        raise 'Desired channels missing: check the usage'

    datacards = {}
    datacards['split'] = ['of_0j', 'of_1j', 'sf_0j', 'sf_1j']
    datacards['shape'] = ['comb_0j1j','comb_0j','comb_1j']
    datacards['full']  = ['comb_0j1j2j']

    datacards['all'] = datacards['split']+datacards['shape']+datacards['full']
    datacards['0j1j'] = datacards['split']+datacards['shape']


    if args[0] in datacards:
        plots = datacards[args[0]]
#     if args[0] == 'all':
#         plots = ['of_0j','of_1j','sf_0j','sf_1j','comb_0j','comb_1j','comb_0j1j','comb_0j1j2j']
#     elif args[0] == 'shape':
#         plots = ['comb_0j','comb_1j','comb_0j1j']
#     elif args[0] == 'split':
#         plots = ['of_0j','of_1j','sf_0j','sf_1j']
    else:
        plots = args[:]
        
    if opt.prefix:
        os.chdir(opt.prefix)

    name=opt.prefix if opt.prefix[-1] != '/' else opt.prefix[:-1] 

    for plot in plots:
        print plot
        command = plot_tmpl.format(tag=tag,option=plot,mypath=mypath,name=name)

        print command
        p = subprocess.call(command,shell=True)
#     p.communicate()
#     os.system('; '.join(commands))
    
    
if __name__ == '__main__':
    runTheShape()

