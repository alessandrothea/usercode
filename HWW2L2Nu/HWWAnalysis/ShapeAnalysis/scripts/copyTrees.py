#!/usr/bin/env python

import glob
import os.path
import hwwinfo

nominalDir          = '/scratch/maiko/postLP/MVA/ntupleMVA/ntupleMVA_MH{mass}_njet{jets}/'
systematicsDir      = '/scratch/maiko/postLP/MVA/mvaapp_syst_{type}_{syst}/ntupleMVA_MH{mass}_njet{jets}/' 
nominalOutFile      = 'histo_H{mass}_{jets}jet_mllmtPreSel_{channel}.root'
systematicsOutFile  = 'histo_H{mass}_{jets}jet_mllmtPreSel_{channel}_{syst}.root'
    
types = ['testing','bckgd']
systs = [
'electronResolution',
'electronScale_down',
'electronScale_up',
'jetEnergyScale_down',
'jetEnergyScale_up',
'leptonEfficiency_down',
'leptonEfficiency_up',
'metResolution',
'muonScale_down',
'muonScale_up',
]

systDestDir = '/scratch/thea/shapes/MVA/syst_{syst}/ntupleMVA_MH{mass}_njet{jets}/'
nomDestDir  = '/scratch/thea/shapes/MVA/nominal/ntupleMVA_MH{mass}_njet{jets}/'
for syst in systs:
    for mass in hwwinfo.masses:
        for j in hwwinfo.jets:
            print mass,j
            dirs = [ systematicsDir.format(mass=mass,jets=j,syst=syst,type=t) for t in types]
            for d in dirs:
                if not os.path.exists(d):
                    raise RuntimeError('Directory not found '+d)
                dest = systDestDir.format(mass=mass,jets=j,syst=syst)
                os.system('mkdir -p '+dest)
                files = glob.glob(d+'/*') 
                for f in files:
#                     cmd = 'ln -s {src} {dest}'.format(src=f,dest=dest)
#                     print cmd
#                     os.system(cmd)
                    basename = os.path.basename(f)
                    target = dest+'/'+basename
                    if os.path.exists(target):
                        os.unlink(target)
                    os.symlink(f,target)


# for mass in hwwinfo.masses:
#     for j in hwwinfo.jets:
#             print mass,j
#             dirs = [ nominalDir.format(mass=mass,jets=j) ]
#             for d in dirs:
#                 if not os.path.exists(d):
#                     raise RuntimeError('Directory not found '+d)
#                 dest = nomDestDir.format(mass=mass,jets=j)
#                 os.system('mkdir -p '+dest)
#                 cmd = 'cp {src}/* {dest}'.format(src=d,dest=dest)
#                 print cmd
#                 os.system(cmd)
