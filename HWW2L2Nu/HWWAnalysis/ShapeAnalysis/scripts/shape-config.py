#!/usr/bin/env python

import hwwinfo
import hwwtools
import optparse

parser = optparse.OptionParser()
hwwtools.addOptions(parser)
hwwtools.loadOptDefaults(parser, quiet=True)
(opt,args) = parser.parse_args([])

# print opt

print '\n'
print 'export masses="'+' '.join([str(mass) for mass in hwwinfo.masses])+'";'
# print 'export jets="'+' '.join([str(njet) for njet in hwwinfo.jets])+'";'
print 'export flavors="'+' '.join(hwwinfo.flavors)+'";'
print 'export channels="'+' '.join(hwwinfo.channels)+'";'
print 'export lumi="%.2f"' % opt.lumi+';'


