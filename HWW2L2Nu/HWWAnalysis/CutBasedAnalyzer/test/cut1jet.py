from HWWAnalysis.CutBasedAnalyzer.treeCutter import *

from HWWAnalysis.CutBasedAnalyzer.cuts import channels,cuts0j,variables

process.channels  = channels.copy()
process.cuts      = cuts0j.copy()
process.variables = variables.copy()

# find the jet veto
for c in process.cuts:
    if c.name.value() == 'jetVeto':
        c.name.setValue('njet == 1')
