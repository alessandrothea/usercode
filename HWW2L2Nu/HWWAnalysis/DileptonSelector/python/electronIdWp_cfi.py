import FWCore.ParameterSet.Config as cms

def makeVBTFEntry( partition, eff, see, dphi, deta, hoe, combIso, hits, dist, cot):
    entry = cms.PSet(
        partition = cms.string(partition),
        eff       = cms.int32(eff),
        see       = cms.double(see),
        dphi      = cms.double(dphi), 
        deta      = cms.double(deta),
        hoe       = cms.double(hoe),
        combIso   = cms.double(combIso), 
        hits      = cms.double(hits), 
        dist      = cms.double(dist), 
        cot       = cms.double(cot),
    )
    return entry

def makeLHEntry( partition, eff, likelihood0, likelihood1, combIso, hits, dist, cot ):
    entry = cms.PSet(
        partition   = cms.string(partition),
        eff         = cms.int32(eff),
        likelihood0 = cms.double(likelihood0),
        likelihood1 = cms.double(likelihood1),
        combIso     = cms.double(combIso), 
        hits        = cms.double(hits), 
        dist        = cms.double(dist), 
        cot         = cms.double(cot),
    )
    return entry


#  _   _______ ___________ _____  _____  __  _____ 
# | | | | ___ \_   _|  ___/ __  \|  _  |/  ||  _  |
# | | | | |_/ / | | | |_  `' / /'| |/' |`| || |/' |
# | | | | ___ \ | | |  _|   / /  |  /| | | ||  /| |
# \ \_/ / |_/ / | | | |   ./ /___\ |_/ /_| |\ |_/ /
#  \___/\____/  \_/ \_|   \_____/ \___/ \___/\___/ 


#               p   eff   see     dphi     deta     hoe      combIso  hits  dist    cot
elVBTF2010 = cms.VPSet(
    makeVBTFEntry( 'B', 95,  0.01,    0.8,      0.007,  0.50,    0.15,    1,   0.00,    0.00 ), 
    makeVBTFEntry( 'B', 90,  0.01,    0.8 ,     0.007,  0.12,    0.10,    1,   0.02,    0.02 ),
    makeVBTFEntry( 'B', 85,  0.01,    0.06,     0.006,  0.04,    0.09,    1,   0.02,    0.02 ),
    makeVBTFEntry( 'B', 80,  0.01,    0.06,     0.004 , 0.04 ,   0.07,    0,   0.02,    0.02 ), 
    makeVBTFEntry( 'B', 70,  0.01,    0.03,     0.003 , 0.025,   0.05,    0,   0.02,    0.02 ),
    makeVBTFEntry( 'B', 60,  0.01,    0.02,     0.0025, 0.025,   0.04,    0,   0.02,    0.02 ),

    makeVBTFEntry( 'E', 95,  0.03,    0.7 ,     0.01 ,  0.07 ,   0.10,    1,   0.00,    0.00 ),
    makeVBTFEntry( 'E', 90,  0.03,    0.7 ,     0.009,  0.05 ,   0.07,    1,   0.02,    0.00 ),
    makeVBTFEntry( 'E', 85,  0.03,    0.04,     0.007,  0.025,   0.06,    1,   0.02,    0.00 ),
    makeVBTFEntry( 'E', 80,  0.03,    0.03,     0.007,  0.025,   0.06,    0,   0.02,    0.02 ),
    makeVBTFEntry( 'E', 70,  0.03,    0.02,     0.005,  0.012,   0.04,    0,   0.02,    0.02 ),
    makeVBTFEntry( 'E', 60,  0.03,    0.02,     0.005,  0.009,   0.03,    0,   0.02,    0.03 ),
)

#  _   _______ ___________ _____  _____  __   __  
# | | | | ___ \_   _|  ___/ __  \|  _  |/  | /  | 
# | | | | |_/ / | | | |_  `' / /'| |/' |`| | `| | 
# | | | | ___ \ | | |  _|   / /  |  /| | | |  | | 
# \ \_/ / |_/ / | | | |   ./ /___\ |_/ /_| |__| |_
#  \___/\____/  \_/ \_|   \_____/ \___/ \___/\___/
#                                                 

elVBTF2011 = cms.VPSet(
    makeVBTFEntry( 'B', 95,  0.012,   0.8,      0.007,  0.50,    0.15,    0,   0.00,    0.00 ), 
    makeVBTFEntry( 'B', 90,  0.01,    0.071,    0.007,  0.12,    0.085,   0,   0.00,    0.00 ),
    makeVBTFEntry( 'B', 85,  0.01,    0.039,    0.005,  0.04,    0.053,   0,   0.02,    0.02 ),
    makeVBTFEntry( 'B', 80,  0.01,    0.027,    0.005,  0.04 ,   0.04,    0,   0.02,    0.02 ), 
    makeVBTFEntry( 'B', 70,  0.01,    0.02,     0.004,  0.025,   0.03,    0,   0.02,    0.02 ),
    makeVBTFEntry( 'B', 60,  0.01,    0.02,     0.004,  0.025,   0.016,   0,   0.02,    0.02 ),

    makeVBTFEntry( 'E', 95,  0.031,   0.70,     0.011,  0.07 ,   0.10,    0,   0.00,    0.00 ),
    makeVBTFEntry( 'E', 90,  0.031,   0.047,    0.011,  0.05 ,   0.051,   0,   0.00,    0.00 ),
    makeVBTFEntry( 'E', 85,  0.031,   0.028,    0.007,  0.025,   0.042,   0,   0.02,    0.02 ),
    makeVBTFEntry( 'E', 80,  0.031,   0.021,    0.006,  0.025,   0.033,   0,   0.02,    0.02 ),
    makeVBTFEntry( 'E', 70,  0.031,   0.021,    0.005,  0.012,   0.016,   0,   0.02,    0.02 ),
    makeVBTFEntry( 'E', 60,  0.031,   0.021,    0.004,  0.009,   0.008,   0,   0.02,    0.03 ),
)

elWpTableSync2011 = cms.VPSet(
    makeVBTFEntry( 'B', 80,  0.01,    0.06,     0.004 , 0.04 ,   0.10,    0,   0.02,    0.02 ), 
    makeVBTFEntry( 'E', 80,  0.03,    0.03,     0.007,  0.025,   0.10,    0,   0.02,    0.02 ),
)

#  _      _   _  _____  _____  __   __  
# | |    | | | |/ __  \|  _  |/  | /  | 
# | |    | |_| |`' / /'| |/' |`| | `| | 
# | |    |  _  |  / /  |  /| | | |  | | 
# | |____| | | |./ /___\ |_/ /_| |__| |_
# \_____/\_| |_/\_____/ \___/ \___/\___/

#               par, eff,  lh0,      lh1,     combIso, hits, dist, cot 
elLH2011 = cms.VPSet(
    makeLHEntry( 'B', 95, -4.274,   -3.773,   0.113,   0,   0.02,    0.02 ),
    makeLHEntry( 'B', 90, -1.497,   -1.521,   0.070,   0,   0.02,    0.02 ),
    makeLHEntry( 'B', 85,  0.163,    0.065,   0.046,   0,   0.02,    0.02 ),
    makeLHEntry( 'B', 80,  1.193,    1.345,   0.033,   0,   0.02,    0.02 ),
    makeLHEntry( 'B', 70,  1.781,    2.397,   0.026,   0,   0.02,    0.02 ),

    makeLHEntry( 'E', 95, -5.092,   -2.796,   0.109,   0,   0.02,    0.02 ),
    makeLHEntry( 'E', 90, -2.571,   -0.657,   0.069,   0,   0.02,    0.02 ),
    makeLHEntry( 'E', 85, -0.683,    1.564,   0.046,   0,   0.02,    0.02 ),
    makeLHEntry( 'E', 80,  0.810,    3.021,   0.039,   0,   0.02,    0.02 ),
    makeLHEntry( 'E', 70,  2.361,    4.052,   0.037,   0,   0.02,    0.02 ),
)

