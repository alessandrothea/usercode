import FWCore.ParameterSet.Config as cms

# def makeElWorkingPoint( partition, eff, see, dphi, deta, hoe, tkIso, ecalIso, hcalIso, combIso, hits, dist, cot):
def makeElWorkingPoint( partition, eff, see, dphi, deta, hoe, combIso, hits, dist, cot):
    wp = cms.PSet(partition = cms.string(partition),
                  eff       = cms.double(eff),
                  see       = cms.double(see),
                  dphi      = cms.double(dphi), 
                  deta      = cms.double(deta),
                  hoe       = cms.double(hoe),
                  combIso   = cms.double(combIso), 
                  hits      = cms.double(hits), 
                  dist      = cms.double(dist), 
                  cot       = cms.double(cot),
                 )
    return wp

#                    p   eff   see     dphi     deta     hoe      combIso  hits  dist    cot
elWpTable2010 = cms.VPSet(
makeElWorkingPoint( 'B', 95,  0.01,    0.8,      0.007,  0.50,    0.15,    1,   0.00,    0.00 ), 
makeElWorkingPoint( 'B', 90,  0.01,    0.8 ,     0.007,  0.12,    0.10,    1,   0.02,    0.02 ),
makeElWorkingPoint( 'B', 85,  0.01,    0.06,     0.006,  0.04,    0.09,    1,   0.02,    0.02 ),
makeElWorkingPoint( 'B', 80,  0.01,    0.06,     0.004 , 0.04 ,   0.07,    0,   0.02,    0.02 ), 
makeElWorkingPoint( 'B', 70,  0.01,    0.03,     0.003 , 0.025,   0.05,    0,   0.02,    0.02 ),
makeElWorkingPoint( 'B', 60,  0.01,    0.02,     0.0025, 0.025,   0.04,    0,   0.02,    0.02 ),

makeElWorkingPoint( 'E', 95,  0.03,    0.7 ,     0.01 ,  0.07 ,   0.10,    1,   0.00,    0.00 ),
makeElWorkingPoint( 'E', 90,  0.03,    0.7 ,     0.009,  0.05 ,   0.07,    1,   0.02,    0.00 ),
makeElWorkingPoint( 'E', 85,  0.03,    0.04,     0.007,  0.025,   0.06,    1,   0.02,    0.00 ),
makeElWorkingPoint( 'E', 80,  0.03,    0.03,     0.007,  0.025,   0.06,    0,   0.02,    0.02 ),
makeElWorkingPoint( 'E', 70,  0.03,    0.02,     0.005,  0.012,   0.04,    0,   0.02,    0.02 ),
makeElWorkingPoint( 'E', 60,  0.03,    0.02,     0.005,  0.009,   0.03,    0,   0.02,    0.03 ),
)

elWpTable2011 = cms.VPSet(
makeElWorkingPoint( 'B', 95,  0.012,   0.8,      0.007,  0.50,    0.15,    0,   0.00,    0.00 ), 
makeElWorkingPoint( 'B', 90,  0.01,    0.071,    0.007,  0.12,    0.085,   0,   0.00,    0.00 ),
makeElWorkingPoint( 'B', 85,  0.01,    0.039,    0.005,  0.04,    0.053,   0,   0.02,    0.02 ),
makeElWorkingPoint( 'B', 80,  0.01,    0.027,    0.005,  0.04 ,   0.04,    0,   0.02,    0.02 ), 
makeElWorkingPoint( 'B', 70,  0.01,    0.02,     0.004,  0.025,   0.03,    0,   0.02,    0.02 ),
makeElWorkingPoint( 'B', 60,  0.01,    0.02,     0.004,  0.025,   0.016,   0,   0.02,    0.02 ),

makeElWorkingPoint( 'E', 95,  0.031,   0.70,     0.011,  0.07 ,   0.10,    0,   0.00,    0.00 ),
makeElWorkingPoint( 'E', 90,  0.031,   0.047,    0.011,  0.05 ,   0.051,   0,   0.00,    0.00 ),
makeElWorkingPoint( 'E', 85,  0.031,   0.028,    0.007,  0.025,   0.042,   0,   0.02,    0.02 ),
makeElWorkingPoint( 'E', 80,  0.031,   0.021,    0.006,  0.025,   0.033,   0,   0.02,    0.02 ),
makeElWorkingPoint( 'E', 70,  0.031,   0.021,    0.005,  0.012,   0.016,   0,   0.02,    0.02 ),
makeElWorkingPoint( 'E', 60,  0.031,   0.021,    0.004,  0.009,   0.008,   0,   0.02,    0.03 ),
)

elWpTableSync2011 = cms.VPSet(
makeElWorkingPoint( 'B', 80,  0.01,    0.06,     0.004 , 0.04 ,   0.10,    0,   0.02,    0.02 ), 
makeElWorkingPoint( 'E', 80,  0.03,    0.03,     0.007,  0.025,   0.10,    0,   0.02,    0.02 ),
)

elWpTable = elWpTableSync2011
