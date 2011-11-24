#!/usr/bin/env python
import optparse
import os.path
import subprocess

mypath = os.path.dirname(os.path.abspath(__file__))

plot_tmpl = 
'''
    makeLimitTable.py {option}
    root -b -q \''+mypath+'/PlotLimit.C+("limits/{option}_shape.summary","{tag}", 1,1)\'
    mkdir -p tables
    pdflatex --output-directory tables limits/{option}_shape.tex
    rename {option} {tag}_{option} tables/{option}_shape*
    pdfcrop tables/{tag}_{option}_shape.pdf
    convert -density 200x200 tables/{tag}_{option}_shape-crop.pdf tables/{tag}_{option}_shape-crop.png
'''


allowedCommands = {
    'rename':[
        'cd merged/',
        'ls',
        'rename.sh ',
        'ls',
        'cd ..',
    ],
    # hardcoded
    'datacardsHC':[
        'makeDatacards.py --exnu=default',
    ],
    # mass dependent
    'datacardsMass':[
        'makeDatacards.py --exnu=mass',
    ],
    # shape base
    'datacardsShape':[
        'makeDatacards.py --exnu=shape',
    ],
    'combine':[
        'cd datacards/',
        'combine.sh' ,
        'cd ..',
    ],
    'run':[
        'runLimits.py comb',
    ],
    'plots':[
        'makeLimitTable.py comb',
        'root -b -q \''+mypath+'/PlotLimit.C+("limits/comb_shape.summary","{tag}", 1,1)\'',
        'mkdir -p tables',
        'pdflatex --output-directory tables limits/comb_shape.tex',
        'rename comb {tag}_comb tables/comb_shape*',
        'pdfcrop tables/{tag}_comb_shape.pdf',
        'convert -density 200x200 tables/{tag}_comb_shape-crop.pdf tables/{tag}_comb_shape-crop.png'
    ],
    'run0j':[
        'runLimits.py comb_0j',
    ],
    'plots0j':[
        'makeLimitTable.py comb_0j',
        'root -b -q \''+mypath+'/PlotLimit.C+("limits/comb_0j_shape.summary","{tag}_0j", 1,1)\'',
        'mkdir -p tables',
        'pdflatex --output-directory tables limits/comb_0j_shape.tex',
        'rename comb {tag}_comb tables/comb_0j_shape*',
        'pdfcrop tables/{tag}_comb_0j_shape.pdf',
        'convert -density 200x200 tables/{tag}_comb_0j_shape-crop.pdf tables/{tag}_comb_0j_shape-crop.png'
    ],
    'run1j':[
        'runLimits.py comb_1j',
    ],
    'plots1j':[
        'makeLimitTable.py comb_1j',
        'root -b -q \''+mypath+'/PlotLimit.C+("limits/comb_1j_shape.summary","{tag}_1j", 1,1)\'',
        'mkdir -p tables',
        'pdflatex --output-directory tables limits/comb_1j_shape.tex',
        'rename comb {tag}_comb tables/comb_1j_shape*',
        'pdfcrop tables/{tag}_comb_1j_shape.pdf',
        'convert -density 200x200 tables/{tag}_comb_1j_shape-crop.pdf tables/{tag}_comb_1j_shape-crop.png'
    ],
     'plotsof_0j':[
        'makeLimitTable.py of_0j',
        'root -b -q \''+mypath+'/PlotLimit.C+("limits/of_0j_shape.summary","{tag}_of_0j", 1,1)\'',
        'mkdir -p tables',
        'pdflatex --output-directory tables limits/of_0j_shape.tex',
        'rename of_0j {tag}_of_0j tables/of_0j_shape*',
        'pdfcrop tables/{tag}_of_0j_shape.pdf',
        'convert -density 200x200 tables/{tag}_of_0j_shape-crop.pdf tables/{tag}_of_0j_shape-crop.png'
    ],
     'plotssf_0j':[
        'makeLimitTable.py sf_0j',
        'root -b -q \''+mypath+'/PlotLimit.C+("limits/sf_0j_shape.summary","{tag}_sf_0j", 1,1)\'',
        'mkdir -p tables',
        'pdflatex --output-directory tables limits/sf_0j_shape.tex',
        'rename sf_0j {tag}_sf_0j tables/sf_0j_shape*',
        'pdfcrop tables/{tag}_sf_0j_shape.pdf',
        'convert -density 200x200 tables/{tag}_sf_0j_shape-crop.pdf tables/{tag}_sf_0j_shape-crop.png'
    ],
     'plotsof_1j':[
        'makeLimitTable.py of_1j',
        'root -b -q \''+mypath+'/PlotLimit.C+("limits/of_1j_shape.summary","{tag}_of_1j", 1,1)\'',
        'mkdir -p tables',
        'pdflatex --output-directory tables limits/of_1j_shape.tex',
        'rename of_1j {tag}_of_1j tables/of_1j_shape*',
        'pdfcrop tables/{tag}_of_1j_shape.pdf',
        'convert -density 200x200 tables/{tag}_of_1j_shape-crop.pdf tables/{tag}_of_1j_shape-crop.png'
    ],
     'plotssf_1j':[
        'makeLimitTable.py sf_1j',
        'root -b -q \''+mypath+'/PlotLimit.C+("limits/sf_1j_shape.summary","{tag}_sf_1j", 1,1)\'',
        'mkdir -p tables',
        'pdflatex --output-directory tables limits/sf_1j_shape.tex',
        'rename sf_1j {tag}_sf_1j tables/sf_1j_shape*',
        'pdfcrop tables/{tag}_sf_1j_shape.pdf',
        'convert -density 200x200 tables/{tag}_sf_1j_shape-crop.pdf tables/{tag}_sf_1j_shape-crop.png'
    ],
}

allowedCommands['limits'] = (
                allowedCommands['rename']+
                allowedCommands['datacardsShape']+
                allowedCommands['combine']+
                allowedCommands['run']
)

allowedCommands['allPlots'] = (
    allowedCommands['plots']+
    allowedCommands['plots0j']+
    allowedCommands['plots1j']
)

allowedCommands['bins'] = (
    allowedCommands[ 'plotsof_0j']+
    allowedCommands[ 'plotsof_1j']+
    allowedCommands[ 'plotssf_0j']+
    allowedCommands[ 'plotssf_1j']

)

def runTheShape():
    usage = 'usage: %prog [dir] [cmd]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-d',dest='dir')
    (opt, args) = parser.parse_args()

    if len(args) < 2:
        parser.error('No directory defined')
    
    tag = args[0] if args[0][-1] != '/' else args[0][:-1]
    basedir = os.path.abspath(tag)

    print basedir
    
    if not os.path.exists(basedir):
        parser.error('Directory not found: '+basedir)

    cmd = args[1]
    if cmd not in allowedCommands:
        parser.error('Command not found: '+cmd)

    commands = allowedCommands[cmd]


    cwd = os.getcwd()

    #format
    commands = [c.format(basedir=basedir, tag=tag) for c in commands]
#     print command
#     for cmd in commands:
    cmdline =  'cd '+basedir+'; '+'; '.join(commands)
    print cmdline
    p = subprocess.call(cmdline,shell=True)
#     p.communicate()
#     os.system('; '.join(commands))
    
    os.chdir(cwd)
    
if __name__ == '__main__':
    runTheShape()

