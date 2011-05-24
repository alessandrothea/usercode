#!/usr/bin/env python

import optparse
import sys
import ROOT
import array
import os.path
import HWWAnalysis.Misc.ROOTAndUtils as utils

#---------------------------------------------------------
import locale
locale.setlocale(locale.LC_NUMERIC, "")
def format_num(num):
    """Format a number according to given places.
    Adds commas, etc. Will truncate floats into ints!"""

    if isinstance(num,int):
        return '%d' % num
    elif isinstance(num,float):
        return '%.2f' % num
    else:
        return str(num)

def get_max_width(table, index):
    """Get the maximum width of the given column index"""
    return max([len(format_num(row[index])) for row in table])

def pprint_table(out, table):
    """Prints out a table of data, padded for alignment
    @param out: Output stream (file-like object)
    @param table: The table to print. A list of lists.
    Each row must have the same number of columns. """
    col_paddings = []

    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))

    for row in table:
        # left col
#         print >> out, row[0].ljust(col_paddings[0] + 1),
        # rest of the cols
        for i in range(1, len(row)):
            col = format_num(row[i]).rjust(col_paddings[i] + 2)
            print >> out, col,
        print >> out
            
#---------------------------------------------------------

treeName='hwwAnalysis'

def dumpSelected( path ):
    f =  ROOT.TFile.Open(path)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    
    hwwTree = f.Get(treeName)
    if not hwwTree.__nonzero__():
        raise NameError('Tree '+treeName+' doesn\'t exist in '+path)
    
    types = {}
    types['ee'] = '00'
    types['em'] = '01'
    types['me'] = '10'
    types['mm'] = '11'

#     cut = types['ll']
    hwwTree.Draw('>>counters','nt.selected==1','entrylist')
    eList = ROOT.gDirectory.Get('counters')


    n = ROOT.HWWNtuple()
    hwwTree.SetBranchAddress('nt',ROOT.AddressOf(n))
    hwwTree.SetEntryList(eList)

    table = []
    for i in xrange(eList.GetN()):
        j = eList.GetEntry(i) 
        hwwTree.GetEntry(j)
        table.append([j,n.run,n.lumiSection,n.event,n.type,n.mll,n.pA.Pt(),n.pB.Pt(),n.dPhi])

    table = sorted(table, key=lambda nt: nt[1]) 
    table.insert(0,['entry','run','lumi','event','type','mll','ptLead','ptTrail','dphi'])
    pprint_table(sys.stdout,table)





if __name__ == '__main__':
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    (opt, args) = parser.parse_args()
    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()
    ROOT.gSystem.Load('libFWCoreFWLite')
    ROOT.AutoLibraryLoader.enable()


    dumpSelected( args[0])
