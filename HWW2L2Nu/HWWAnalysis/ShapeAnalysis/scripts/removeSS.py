#!/usr/bin/env python

import glob
import os.path

datacardDir    = 'datacards/'
noSSDir = 'datacards_noss/'  

ls = glob.glob(datacardDir+'*.txt')

# print ls
os.system('mkdir -p '+noSSDir)

for file in ls:
    filename = os.path.basename(file)
    cmd = 'head -n -6 '+file+' >& '+noSSDir+filename
    print cmd
    os.system(cmd)
