#!/usr/bin/env python



##
## ./compareNormalization.py of_1j -i tmp/tmpESYbMR_pack_newrange2/datacards/ -o test_directory/
##






import sys
import os
import glob
import optparse

import ROOT

from subprocess import Popen, PIPE, STDOUT
import HWWAnalysis.Misc.odict as odict



allowedtags = ['sf_0j','sf_1j','of_0j','of_1j','allcomb','comb_0j','comb_1j','comb_0j1j','comb_of']


bindict_of_0j = {
    'of_0j_DYTT':12,
    'of_0j_ggWW':11,
    'of_0j_VgS':10,
    'of_0j_Vg':9,
    'of_0j_WJet':8,
    'of_0j_Top':7,
    'of_0j_WW':6,
    'of_0j_DYLL':5,
    'of_0j_VV':4,
    'of_0j_ggH':3,
    'of_0j_vbfH':2,
    'of_0j_wzttH':1,
}
bindict_of_1j = {
    'of_1j_DYTT':12,
    'of_1j_ggWW':11,
    'of_1j_VgS':10,
    'of_1j_Vg':9,
    'of_1j_WJet':8,
    'of_1j_Top':7,
    'of_1j_WW':6,
    'of_1j_DYLL':5,
    'of_1j_VV':4,
    'of_1j_ggH':3,
    'of_1j_vbfH':2,
    'of_1j_wzttH':1,

}
bindict_sf_0j = {
    'sf_0j_DYTT':12,
    'sf_0j_ggWW':11,
    'sf_0j_VgS':10,
    'sf_0j_Vg':9,
    'sf_0j_WJet':8,
    'sf_0j_Top':7,
    'sf_0j_WW':6,
    'sf_0j_DYLL':5,
    'sf_0j_VV':4,
    'sf_0j_ggH':3,
    'sf_0j_vbfH':2,
    'sf_0j_wzttH':1,

}
bindict_sf_1j = {
    'sf_1j_DYTT':12,
    'sf_1j_ggWW':11,
    'sf_1j_VgS':10,
    'sf_1j_Vg':9,
    'sf_1j_WJet':8,
    'sf_1j_Top':7,
    'sf_1j_WW':6,
    'sf_1j_DYLL':5,
    'sf_1j_VV':4,
    'sf_1j_ggH':3,
    'sf_1j_vbfH':2,
    'sf_1j_wzttH':1,
}

bindict_0j = {

    'of_0j_DYTT':12,
    'of_0j_ggWW':11,
    'of_0j_VgS':10,
    'of_0j_Vg':9,
    'of_0j_WJet':8,
    'of_0j_Top':7,
    'of_0j_WW':6,
    'of_0j_DYLL':5,
    'of_0j_VV':4,
    'of_0j_ggH':3,
    'of_0j_vbfH':2,
    'of_0j_wzttH':1,

    'sf_0j_DYTT' :12,
    'sf_0j_ggWW' :11,
    'sf_0j_VgS'  :10,
    'sf_0j_Vg'   :9,
    'sf_0j_WJet' :8,
    'sf_0j_Top'  :7,
    'sf_0j_WW'   :6,
    'sf_0j_DYLL' :5,
    'sf_0j_VV'   :4,
    'sf_0j_ggH'  :3,
    'sf_0j_vbfH' :2,
    'sf_0j_wzttH':1,

##     'of_0j_DYTT':22,
##     'of_0j_ggWW':21,
##     'of_0j_Vg':20,
##     'of_0j_WJet':19,
##     'of_0j_Top':18,
##     'of_0j_WW':17,
##     'of_0j_DYLL':16,
##     'of_0j_VV':15,
##     'of_0j_ggH':14,
##     'of_0j_vbfH':13,
##     'of_0j_wzttH':12,

##     'sf_0j_DYTT':11,
##     'sf_0j_ggWW':10,
##     'sf_0j_Vg':9,
##     'sf_0j_WJet':8,
##     'sf_0j_Top':7,
##     'sf_0j_WW':6,
##     'sf_0j_DYLL':5,
##     'sf_0j_VV':4,
##     'sf_0j_ggH':3,
##     'sf_0j_vbfH':2,
##     'sf_0j_wzttH':1,
    }

bindict_1j = {

    'sf_1j_DYTT' :12,
    'sf_1j_ggWW' :11,
    'sf_1j_VgS'  :10,
    'sf_1j_Vg'   :9,
    'sf_1j_WJet' :8,
    'sf_1j_Top'  :7,
    'sf_1j_WW'   :6,
    'sf_1j_DYLL' :5,
    'sf_1j_VV'   :4,
    'sf_1j_ggH'  :3,
    'sf_1j_vbfH' :2,
    'sf_1j_wzttH':1,

    'of_1j_DYTT' :12,
    'of_1j_ggWW' :11,
    'of_1j_VgS'  :10,
    'of_1j_Vg'   :9,
    'of_1j_WJet' :8,
    'of_1j_Top'  :7,
    'of_1j_WW'   :6,
    'of_1j_DYLL' :5,
    'of_1j_VV'   :4,
    'of_1j_ggH'  :3,
    'of_1j_vbfH' :2,
    'of_1j_wzttH':1,

    
##     'of_1j_DYTT':22,
##     'of_1j_ggWW':21,
##     'of_1j_Vg':20,
##     'of_1j_WJet':19,
##     'of_1j_Top':18,
##     'of_1j_WW':17,
##     'of_1j_DYLL':16,
##     'of_1j_VV':15,
##     'of_1j_ggH':14,
##     'of_1j_vbfH':13,
##     'of_1j_wzttH':12,
##     'sf_1j_DYTT':11,
##     'sf_1j_ggWW':10,
##     'sf_1j_Vg':9,
##     'sf_1j_WJet':8,
##     'sf_1j_Top':7,
##     'sf_1j_WW':6,
##     'sf_1j_DYLL':5,
##     'sf_1j_VV':4,
##     'sf_1j_ggH':3,
##     'sf_1j_vbfH':2,
##     'sf_1j_wzttH':1,
    }
bindict_comb_0j1j = {

    'sf_0j_DYTT' :12,
    'sf_0j_ggWW' :11,
    'sf_0j_VgS'  :10,
    'sf_0j_Vg'   :9,
    'sf_0j_WJet' :8,
    'sf_0j_Top'  :7,
    'sf_0j_WW'   :6,
    'sf_0j_DYLL' :5,
    'sf_0j_VV'   :4,
    'sf_0j_ggH'  :3,
    'sf_0j_vbfH' :2,
    'sf_0j_wzttH':1,

    'of_0j_DYTT' :12,
    'of_0j_ggWW' :11,
    'of_0j_VgS'  :10,
    'of_0j_Vg'   :9,
    'of_0j_WJet' :8,
    'of_0j_Top'  :7,
    'of_0j_WW'   :6,
    'of_0j_DYLL' :5,
    'of_0j_VV'   :4,
    'of_0j_ggH'  :3,
    'of_0j_vbfH' :2,
    'of_0j_wzttH':1,

    'sf_1j_DYTT' :12,
    'sf_1j_ggWW' :11,
    'sf_1j_VgS'  :10,
    'sf_1j_Vg'   :9,
    'sf_1j_WJet' :8,
    'sf_1j_Top'  :7,
    'sf_1j_WW'   :6,
    'sf_1j_DYLL' :5,
    'sf_1j_VV'   :4,
    'sf_1j_ggH'  :3,
    'sf_1j_vbfH' :2,
    'sf_1j_wzttH':1,

    'of_1j_DYTT' :12,
    'of_1j_ggWW' :11,
    'of_1j_VgS'  :10,
    'of_1j_Vg'   :9,
    'of_1j_WJet' :8,
    'of_1j_Top'  :7,
    'of_1j_WW'   :6,
    'of_1j_DYLL' :5,
    'of_1j_VV'   :4,
    'of_1j_ggH'  :3,
    'of_1j_vbfH' :2,
    'of_1j_wzttH':1,

}

bindict_comb_of = {

    'of_0j_DYTT' :12,
    'of_0j_ggWW' :11,
    'of_0j_VgS'  :10,
    'of_0j_Vg'   :9,
    'of_0j_WJet' :8,
    'of_0j_Top'  :7,
    'of_0j_WW'   :6,
    'of_0j_DYLL' :5,
    'of_0j_VV'   :4,
    'of_0j_ggH'  :3,
    'of_0j_vbfH' :2,
    'of_0j_wzttH':1,

    'of_1j_DYTT' :12,
    'of_1j_ggWW' :11,
    'of_1j_VgS'  :10,
    'of_1j_Vg'   :9,
    'of_1j_WJet' :8,
    'of_1j_Top'  :7,
    'of_1j_WW'   :6,
    'of_1j_DYLL' :5,
    'of_1j_VV'   :4,
    'of_1j_ggH'  :3,
    'of_1j_vbfH' :2,
    'of_1j_wzttH':1,

}


bindict_all = { 
    'HWW_2j_DYTT':55,
    'HWW_2j_ggWW':54,
    'HWW_2j_Vg':53,
    'HWW_2j_WJet':52,
    'HWW_2j_Top':51,
    'HWW_2j_WW':50,
    'HWW_2j_DYLL':49,
    'HWW_2j_VV':48,
    'HWW_2j_ggH':47,
    'HWW_2j_vbfH':46,
    'HWW_2j_wzttH':45,

    'HWW_0j_of_0j_DYTT':44,
    'HWW_0j_of_0j_ggWW':43,
    'HWW_0j_of_0j_Vg':42,
    'HWW_0j_of_0j_WJet':41,
    'HWW_0j_of_0j_Top':40,
    'HWW_0j_of_0j_WW':39,
    'HWW_0j_of_0j_DYLL':38,
    'HWW_0j_of_0j_VV':37,
    'HWW_0j_of_0j_ggH':36,
    'HWW_0j_of_0j_vbfH':35,
    'HWW_0j_of_0j_wzttH':34,

    'HWW_1j_of_1j_DYTT':33,
    'HWW_1j_of_1j_ggWW':32,
    'HWW_1j_of_1j_Vg':31,
    'HWW_1j_of_1j_WJet':30,
    'HWW_1j_of_1j_Top':29,
    'HWW_1j_of_1j_WW':28,
    'HWW_1j_of_1j_DYLL':27,
    'HWW_1j_of_1j_VV':26,
    'HWW_1j_of_1j_ggH':5,
    'HWW_1j_of_1j_vbfH':24,
    'HWW_1j_of_1j_wzttH':23,

    'HWW_0j_sf_0j_DYTT':22,
    'HWW_0j_sf_0j_ggWW':21,
    'HWW_0j_sf_0j_Vg':20,
    'HWW_0j_sf_0j_WJet':19,
    'HWW_0j_sf_0j_Top':18,
    'HWW_0j_sf_0j_WW':17,
    'HWW_0j_sf_0j_DYLL':16,
    'HWW_0j_sf_0j_VV':15,
    'HWW_0j_sf_0j_ggH':14,
    'HWW_0j_sf_0j_vbfH':13,
    'HWW_0j_sf_0j_wzttH':12,

    'HWW_1j_sf_1j_DYTT':11,
    'HWW_1j_sf_1j_ggWW':10,
    'HWW_1j_sf_1j_Vg':9,
    'HWW_1j_sf_1j_WJet':8,
    'HWW_1j_sf_1j_Top':7,
    'HWW_1j_sf_1j_WW':6,
    'HWW_1j_sf_1j_DYLL':5,
    'HWW_1j_sf_1j_VV':4,
    'HWW_1j_sf_1j_ggH':3,
    'HWW_1j_sf_1j_vbfH':2,
    'HWW_1j_sf_1j_wzttH':1,
}  

tagdict = {
    'allcomb':'HWW',

    'comb_0j':'0j',
    'comb_1j':'1j',

    'sf_0j':'sf_0j',
    'sf_1j':'sf_1j',
    'of_0j':'of_0j',
    'of_1j':'of_1j',


    'comb_0j1j':'_',

    'comb_of':'_',
    }

plottag_sf_0j = ['sf_0j']
plottag_sf_1j = ['sf_1j']
plottag_of_0j = ['of_0j']
plottag_of_1j = ['of_1j']
plottag_0j = ['sf_0j','of_0j']
plottag_1j = ['sf_1j','of_1j']
plottag_all = []
plottag_comb_0j1j = [
    'of_0j','of_1j',
    'sf_0j','sf_1j'
    ]
plottag_comb_of = ['of_0j','of_1j']

procDict = {
    'sf_0j_DYTT' :'Z #rightarrow #tau #tau',
    'sf_0j_ggWW' :'gg #rightarrow WW',
    'sf_0j_VgS'  :'V #gamma*',
    'sf_0j_Vg'   :'V #gamma',
    'sf_0j_WJet' :'W+jets',
    'sf_0j_Top'  :'top',
    'sf_0j_WW'   :'qq #rightarrow WW',
    'sf_0j_DYLL' :'Z #rightarrow ll',
    'sf_0j_VV'   :'VV',
    'sf_0j_ggH'  :'gg #rightarrow H',
    'sf_0j_vbfH' :'VBF',
    'sf_0j_wzttH':'VH',                        

    'of_0j_DYTT' :'Z #rightarrow #tau #tau',   
    'of_0j_ggWW' :'gg #rightarrow WW',
    'of_0j_VgS'  :'V #gamma*',
    'of_0j_Vg'   :'V #gamma',                  
    'of_0j_WJet' :'W+jets',                    
    'of_0j_Top'  :'top',                       
    'of_0j_WW'   :'qq #rightarrow WW',         
    'of_0j_DYLL' :'Z #rightarrow ll',          
    'of_0j_VV'   :'VV',                        
    'of_0j_ggH'  :'gg #rightarrow H',          
    'of_0j_vbfH' :'VBF',                       
    'of_0j_wzttH':'VH',                        

    'sf_1j_DYTT' :'Z #rightarrow #tau #tau',   
    'sf_1j_ggWW' :'gg #rightarrow WW',
    'sf_1j_VgS'  :'V #gamma*',
    'sf_1j_Vg'   :'V #gamma',                  
    'sf_1j_WJet' :'W+jets',                    
    'sf_1j_Top'  :'top',                       
    'sf_1j_WW'   :'qq #rightarrow WW',         
    'sf_1j_DYLL' :'Z #rightarrow ll',          
    'sf_1j_VV'   :'VV',                        
    'sf_1j_ggH'  :'gg #rightarrow H',          
    'sf_1j_vbfH' :'VBF',                       
    'sf_1j_wzttH':'VH',                        

    'of_1j_DYTT' :'Z #rightarrow #tau #tau',   
    'of_1j_ggWW' :'gg #rightarrow WW',
    'of_1j_VgS'  :'V #gamma*',
    'of_1j_Vg'   :'V #gamma',                  
    'of_1j_WJet' :'W+jets',                    
    'of_1j_Top'  :'top',                       
    'of_1j_WW'   :'qq #rightarrow WW',         
    'of_1j_DYLL' :'Z #rightarrow ll',          
    'of_1j_VV'   :'VV',                        
    'of_1j_ggH'  :'gg #rightarrow H',          
    'of_1j_vbfH' :'VBF',                       
    'of_1j_wzttH':'VH',                        

    }

def index_containing_substring(the_list, substring, start):
    for i, s in enumerate(the_list):
        if i <= start:
            continue
        if substring in s:
              return i
    return -1


def maxlikelihoodfit(file,out):
    print('combine -M MaxLikelihoodFit '+file+' --out='+out+' --saveNormalization')
    os.system('combine -M MaxLikelihoodFit '+file+' --out='+out+' --saveNormalization')
    os.system('mv '+out+'mlfit.root '+out+file.split('/')[-1].replace('.txt','_mlfit.root'))

def mlfitnormstotext(file,out,tag):
    cmd = 'mlfitNormsToText.py '+out+file
##    print(cmd)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    print '----------------------'
    print output


    pyt = '''
    I am python
    + Executing global rootlogon.C
    '''
#    ll = output.lstrip(pyt)
    ll = output.replace('I am python','').replace('+ Executing global rootlogon.C','')
    print ll
    l = ll.split()

    norm = {}
    normalization = {}
    i = -2
    try:
        while i<len(l)-4:
            #i = l.index(tag, i+1)
            
#            print tag,i


            
            i = index_containing_substring(l, tagdict[tag],i+1)
            ## FIXME: here I have to change the process for the combined datacards...

            process = l[i]+'_'+l[i+1]
            
#            print i, process
            fit_sb = l[i+2]
            fit_b  = l[i+3]
            normalization[process] = [fit_sb,fit_b]
    except ValueError:
        pass

##     mass = file.split('.')[-3].replace('mH','')
##     norm[mass] = normalization
    return normalization


def readdatacard(file):
##    a_values = odict.OrderedDict()
    dict_values = {}

    f = open(file)
            
    process = []
    rate = []
    bin = []
    for line in f:
        if not line.startswith('process') and not line.startswith('rate') and not line.startswith('bin'):
            continue
        elif line.startswith('process') and line.split()[1]=='0'  or line.split()[1].startswith('-'):
            continue
        elif line.startswith('process'):
            process = line.split()
        elif line.startswith('rate'):
            rate = line.split()
        elif line.startswith('bin'):
            bin = line.split()
                    
    process.remove('process')
    rate.remove('rate')
    bin.remove('bin')
    
##             print process
##             print rate
                    
    if len(process) != len(rate):
        sys.exit('Something is wrong reading the lines... exiting!')

    values = {}
    for p in range(len(process)):
        values[bin[p]+'_'+process[p]] = rate[p]

##     mass = file.split('.')[-3].replace('mH','')
##     dict_values[mass] = values
    print 'datacard', values
    return values

def main():

    usage = 'usage: %prog tag -i dir -o dir'
    parser = optparse.OptionParser(usage)
    
    parser.add_option('-i','--input', dest='inputdir', help='Input directory')   
    parser.add_option('-o','--output',dest='outputdir',help='Output directory')   

    (opt, args) = parser.parse_args()
    
    if opt.inputdir is None:
        parser.error('No input directory defined')
    if not args:
        parser.error('No tag defined: '+' '.join(allowedtags))

    tag = args[0]
    dir = opt.inputdir
    outdir = opt.outputdir

    if outdir:
        if outdir[:-1]!='/':
            outdir += '/'
        os.system('mkdir -p '+outdir)


    filenames = glob.glob(dir+'/hww*'+'*'+tag+'*.txt')
    filenames.sort()

    if tag == 'sf_0j':
        bindict = bindict_sf_0j
        plottag = plottag_sf_0j
    if tag == 'sf_1j':
        bindict = bindict_sf_1j
        plottag = plottag_sf_1j
    if tag == 'of_0j':
        bindict = bindict_of_0j
        plottag = plottag_of_0j
    if tag == 'of_1j':
        bindict = bindict_of_1j
        plottag = plottag_of_1j
    if tag == 'comb_0j':
        bindict = bindict_0j
        plottag = plottag_0j
    if tag == 'comb_1j':
        bindict = bindict_1j
        plottag = plottag_1j
    if tag == 'allcomb':
        bindict = bindict_all
        plottag = plottag_all
    if tag == 'comb_0j1j':
        bindict = bindict_comb_0j1j
        plottag = plottag_comb_0j1j
    if tag == 'comb_of':
        bindict = bindict_comb_of
        plottag = plottag_comb_of


    # run the maxlikelihood thing
    for file in filenames:
        maxlikelihoodfit(file,outdir)

    fits = odict.OrderedDict()
    norms = odict.OrderedDict()

    for file in filenames:
        if not 'comb' in tag and '0j1j' in file:
            continue
##         if '0j1j' in file:
##             continue
        if '0j1j2j' in file:
            continue
        mass = file.split('.')[-3].replace('mH','')
        print mass

        # run the normalization to txt macro
        f = file.split('/')[-1].replace('.txt','_mlfit.root')
        print f
        fit = mlfitnormstotext(f,outdir,tag)


        print 'kkk fit'
        print fit
        
        # read the datacards
        norm = readdatacard(file)

        fits[mass] = fit
        norms[mass] = norm

        print norm


#    print norms


    text = open(tag+'_normalization.txt','w')

    print '========================================================='
    print 'channel: '+tag

    for mass in norms:
        print '-------------------------------------------------------'
        print '***'+mass+'***'
        print 'process'.ljust(15)+'nominal'.ljust(15)+'fit: s+b (ratio)'.ljust(20)+'fit: b (ratio)'.ljust(20)
##        for proc in norms[mass]:
        for proc in fits[mass]:
##             if proc == 'DYTT':
##                 continue
##             if proc == 'wzttH':
##                 continue
            n  = norms[mass][proc]
            sb = fits[mass][proc][0]
            b  = fits[mass][proc][1]
            if not float(n) == 0.:
                r_sb = float(sb)/float(n)
                r_b  = float(b)/float(n)
            else:
                r_sb = 0
                r_b  = 0

##             print proc.ljust(15)+norms[mass][proc].ljust(15)+(fits[mass][proc][0]+' '+str(float(fits[mass][proc][0])/float(norms[mass][proc])).ljust(15)+fits[mass][proc][1].ljust(15)
##             print proc.ljust(15)+n.ljust(15)+(sb+' ('+str('%.2f' % r_sb)+')').ljust(20)+(b+' ('+str('%.2f' % r_b)+')').ljust(20)


    print >> text, '========================================================='
    print >> text, 'channel: '+tag

    for mass in norms:
        print >> text, '-------------------------------------------------------'
        print >> text, '***'+mass+'***'
        print >> text, 'process'.ljust(15)+'nominal'.ljust(15)+'fit: s+b (ratio)'.ljust(20)+'fit: b (ratio)'.ljust(20)
##        for proc in norms[mass]:
        for proc in fits[mass]:
##             if proc == 'DYTT':
##                 continue
##             if proc == 'wzttH':
##                 continue
            n  = norms[mass][proc]
            sb = fits[mass][proc][0]
            b  = fits[mass][proc][1]
            if not float(n) == 0.:    
                r_sb = float(sb)/float(n)
                r_b  = float(b)/float(n)
            else:
                r_sb = 0
                r_b  = 0
         
            
            #            print >> text, proc.ljust(15)+norms[mass][proc].ljust(15)+(fits[mass][proc][0]+' '+str(float(fits[mass][proc][0])/float(norms[mass][proc])).ljust(15)+fits[mass][proc][1].ljust(15)
            print >> text, proc.ljust(15)+n.ljust(15)+(sb+' ('+str('%.2f' % r_sb)+')').ljust(20)+(b+' ('+str('%.2f' % r_b)+')').ljust(20)


    for ptag in plottag:

        print 'ptag',ptag

## make 2-dim histograms
        c_sb = ROOT.TCanvas()
        c_b = ROOT.TCanvas()


        c_sb.SetLeftMargin(0.15)
        c_b.SetLeftMargin(0.15)
        n_mass = len(norms)
        n_proc = 12
##     n_proc = len(bindict)

        h_sb = ROOT.TH2D('h','h',n_mass,0.,n_mass,n_proc,0.,n_proc)
        h_sb.GetXaxis().SetTitle('mass')
##    h_sb.GetYaxis().SetTitle('process')
        h_sb.SetMaximum(1.5)
        h_sb.SetMinimum(-0.00001)
        title_sb = 'N_{fit_{S+B}} / N_{nominal} - '+tag
        h_sb.SetTitle(title_sb)

        h_b = ROOT.TH2D('h_b','h_b',n_mass,0.,n_mass,n_proc,0.,n_proc)
        h_b.GetXaxis().SetTitle('mass')
##    h_b.GetYaxis().SetTitle('process')
        h_b.SetMaximum(1.5)
        h_b.SetMinimum(-0.00001)
        title_b = 'N_{fit_{B}} / N_{nominal} - '+tag
        h_b.SetTitle(title_b)


    
        i = 1
        for mass in norms:

            print '++++++++++++++++'
            print mass
            print norms[mass]
            print fits[mass]
            
            h_sb.GetXaxis().SetBinLabel(i,mass)
            h_b.GetXaxis().SetBinLabel(i,mass)
            for proc in fits[mass]:

                if ptag not in proc:
                    continue

                n  = norms[mass][proc]
                sb = fits[mass][proc][0]
                b  = fits[mass][proc][1]
                r_sb = float(sb)/float(n)
                r_b  = float(b)/float(n)
                j = bindict[proc]
##             h_sb.GetYaxis().SetBinLabel(j,proc)
##             h_b.GetYaxis().SetBinLabel(j,proc)
                print proc,j,mass,r_sb
                h_sb.SetBinContent(i,j,r_sb)
                h_b.SetBinContent(i,j,r_b)
            i += 1

            for proc in bindict:

                if ptag not in proc:
                    continue

                j = bindict[proc]
                h_sb.GetYaxis().SetBinLabel(j,procDict[proc])
                h_b.GetYaxis().SetBinLabel(j,procDict[proc])
                ## h_sb.GetYaxis().SetBinLabel(j,proc)
                ## h_b.GetYaxis().SetBinLabel(j,proc)


        ROOT.gROOT.SetBatch(True)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetPaintTextFormat('3.3g')
        c_sb.cd()
        h_sb.Draw('COLZ TEXT')
        c_sb.Print(tag+'_normalization_sbFit_'+ptag+'.pdf')
        c_b.cd()
        h_b.Draw('COLZ TEXT')
        c_b.Print(tag+'_normalization_bFit_'+ptag+'.pdf')
        
        
        rf = ROOT.TFile(tag+'_normalization_'+ptag+'.root','RECREATE')
        rf.cd()
        c_sb.Write()
        c_b.Write()
        ROOT.gStyle.Write('theStyle')
        rf.Write()
        rf.Close()


    
if __name__ == '__main__':
    main()












