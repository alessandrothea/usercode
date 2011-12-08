#!/usr/bin/env python

import hwwinfo

print 'export masses="'+' '.join([str(mass) for mass in hwwinfo.masses])+'"'
print 'export jets="'+' '.join([str(njet) for njet in hwwinfo.jets])+'"'
print 'export flavors="'+' '.join(hwwinfo.flavors)+'"'
print 'export channels="'+' '.join(hwwinfo.channels)+'"'

