
import FWCore.ParameterSet.Config as cms

ELE_NOCONV =("( (abs(userFloat('convValueMapProd:dist')) > 0.02   ||" +
             "   abs(userFloat('convValueMapProd:dcot')) > 0.02 ) &&"
             "   gsfTrack.trackerExpectedHitsInner.numberOfLostHits == 0 )")

ELE_IP =("( abs(userFloat('ip2')) < 0.03)")

BARREL_ISO = ("( ( dr03TkSumPt + max(0,dr03EcalRecHitSumEt - 1.0) + " +
              "  userFloat('hcalFull') - userFloat('rhoEl')*3.14159265*0.3*0.3 )/pt )" )
ENDCAP_ISO = ("( ( dr03TkSumPt +       dr03EcalRecHitSumEt        + " +
              "  userFloat('hcalFull') - userFloat('rhoEl')*3.14159265*0.3*0.3 )/pt )" )

PF_ISO = ("( ( userFloat('pfCharged') + userFloat('pfPhoton') + userFloat('pfNeutral') - userFloat('rhoElNoPU') ) / pt )")
SMURF_ISO = ("( ( userFloat('eleSmurfPF') ) / pt )")


# _      _    _  __      ______     ___  _____ 
#| |    | |  | | \ \    / /___ \   / _ \| ____|
#| |    | |__| |  \ \  / /  __) | | (_) | |__  
#| |    |  __  |   \ \/ /  |__ <   \__, |___ \ 
#| |____| |  | |    \  /   ___) |    / / ___) |
#|______|_|  |_|     \/   |____/    /_/ |____/ 
#                                              

ELE_ID_LH_95_2011=("( (  isEB  && numberOfBrems == 0 && electronID('egammaIDLikelihood') > -4.274 ) ||" +           
                   "  (  isEB  && numberOfBrems  > 0 && electronID('egammaIDLikelihood') > -3.773 ) ||" + 
                   "  ((!isEB) && numberOfBrems == 0 && electronID('egammaIDLikelihood') > -5.092 ) ||" + 
                   "  ((!isEB) && numberOfBrems  > 0 && electronID('egammaIDLikelihood') > -2.796 ) )" )

ELE_ISO_LH_95_2011=("(( isEB && " + BARREL_ISO + " < 0.113 ) || ( (!isEB) && " + ENDCAP_ISO + " < 0.109 ) )")

# _      _    _  __      ______     ___   ___  
#| |    | |  | | \ \    / /___ \   / _ \ / _ \ 
#| |    | |__| |  \ \  / /  __) | | (_) | | | |
#| |    |  __  |   \ \/ /  |__ <   \__, | | | |
#| |____| |  | |    \  /   ___) |    / /| |_| |
#|______|_|  |_|     \/   |____/    /_/  \___/ 
#                                              
#

ELE_ID_LH_90_2011=("( (  isEB  && numberOfBrems == 0 && electronID('egammaIDLikelihood') > -1.497 ) ||" +           
                   "  (  isEB  && numberOfBrems  > 0 && electronID('egammaIDLikelihood') > -1.521 ) ||" + 
                   "  ((!isEB) && numberOfBrems == 0 && electronID('egammaIDLikelihood') > -2.571 ) ||" + 
                   "  ((!isEB) && numberOfBrems  > 0 && electronID('egammaIDLikelihood') > -0.657 ) )" )

ELE_ISO_LH_90_2011=("(( isEB && " + BARREL_ISO + " < 0.070 ) || ( (!isEB) && " + ENDCAP_ISO + " < 0.069 ) )")
ELE_ISOPF_LH_90_2011=("(( isEB && " + PF_ISO + " < 0.11 ) || ( (!isEB) && " + PF_ISO + " < 0.15 ) )")


# _      _    _  __      ______     ___  _____ 
#| |    | |  | | \ \    / /___ \   / _ \| ____|
#| |    | |__| |  \ \  / /  __) | | (_) | |__  
#| |    |  __  |   \ \/ /  |__ <   > _ <|___ \ 
#| |____| |  | |    \  /   ___) | | (_) |___) |
#|______|_|  |_|     \/   |____/   \___/|____/ 
#                                              

ELE_ID_LH_85_2011=("( (  isEB  && numberOfBrems == 0 && electronID('egammaIDLikelihood') >  0.163 ) ||" +           
                   "  (  isEB  && numberOfBrems  > 0 && electronID('egammaIDLikelihood') >  0.065 ) ||" + 
                   "  ((!isEB) && numberOfBrems == 0 && electronID('egammaIDLikelihood') > -0.683 ) ||" + 
                   "  ((!isEB) && numberOfBrems  > 0 && electronID('egammaIDLikelihood') >  1.564 ) )" )

ELE_ISO_LH_85_2011=("(( isEB && " + BARREL_ISO + " < 0.046 ) || ( (!isEB) && " + ENDCAP_ISO + " < 0.046 ) )")


#  _      _    ___      ______     ___   ___  
# | |    | |  | \ \    / /___ \   / _ \ / _ \ 
# | |    | |__| |\ \  / /  __) | | (_) | | | |
# | |    |  __  | \ \/ /  |__ <   > _ <| | | |
# | |____| |  | |  \  /   ___) | | (_) | |_| |
# |______|_|  |_|   \/   |____/   \___/ \___/ 
                                            
ELE_ID_LH_80_2011=("( (  isEB  && numberOfBrems == 0 && electronID('egammaIDLikelihood') >  0.193 ) ||" +           
                   "  (  isEB  && numberOfBrems  > 0 && electronID('egammaIDLikelihood') >  1.345 ) ||" + 
                   "  ((!isEB) && numberOfBrems == 0 && electronID('egammaIDLikelihood') >  0.810 ) ||" + 
                   "  ((!isEB) && numberOfBrems  > 0 && electronID('egammaIDLikelihood') >  3.021 ) )" )



#__      ______ _______ ______ ___  _____   ___   ___  __ __ 
#\ \    / /  _ \__   __|  ____/ _ \| ____| |__ \ / _ \/_ /_ |
# \ \  / /| |_) | | |  | |__ | (_) | |__      ) | | | || || |
#  \ \/ / |  _ <  | |  |  __| \__, |___ \    / /| | | || || |
#   \  /  | |_) | | |  | |      / / ___) |  / /_| |_| || || |
#    \/   |____/  |_|  |_|     /_/ |____/  |____|\___/ |_||_|
#                                                            
                                                            
ELE_ID_CB_95_2011=("((isEB && sigmaIetaIeta < 0.012 &&" +           
                   " deltaPhiSuperClusterTrackAtVtx > -0.800 && deltaPhiSuperClusterTrackAtVtx < 0.800 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.007 && deltaEtaSuperClusterTrackAtVtx < 0.007) || " + 
                   " ( (!isEB) && sigmaIetaIeta < 0.031  &&  " +
                   " deltaPhiSuperClusterTrackAtVtx > -0.700 && deltaPhiSuperClusterTrackAtVtx < 0.700 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.011 && deltaEtaSuperClusterTrackAtVtx < 0.011 )) ")

ELE_ISO_CB_95_2011=("(( isEB && " + BARREL_ISO + " < 0.150 ) || ( (!isEB) && " + ENDCAP_ISO + " < 0.100 ) )")


#__      ______ _______ ______ ___   ___    ___   ___  __ __ 
#\ \    / /  _ \__   __|  ____/ _ \ / _ \  |__ \ / _ \/_ /_ |
# \ \  / /| |_) | | |  | |__ | (_) | | | |    ) | | | || || |
#  \ \/ / |  _ <  | |  |  __| \__, | | | |   / /| | | || || |
#   \  /  | |_) | | |  | |      / /| |_| |  / /_| |_| || || |
#    \/   |____/  |_|  |_|     /_/  \___/  |____|\___/ |_||_|
#

ELE_ID_CB_90_2011=("((isEB && sigmaIetaIeta < 0.01 &&" +           
                   " deltaPhiSuperClusterTrackAtVtx > -0.071 && deltaPhiSuperClusterTrackAtVtx < 0.071 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.007 && deltaEtaSuperClusterTrackAtVtx < 0.007) || " + 
                   " ( (!isEB) && sigmaIetaIeta < 0.031  &&  " +
                   " deltaPhiSuperClusterTrackAtVtx > -0.047 && deltaPhiSuperClusterTrackAtVtx < 0.047 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.011 && deltaEtaSuperClusterTrackAtVtx < 0.011 )) ")

ELE_ISO_CB_90_2011=("(( isEB && " + BARREL_ISO + " < 0.085 ) || ( (!isEB) && " + ENDCAP_ISO + " < 0.051 ) )")


#__      ______ _______ ______ ___  _____   ___   ___  __ __ 
#\ \    / /  _ \__   __|  ____/ _ \| ____| |__ \ / _ \/_ /_ |
# \ \  / /| |_) | | |  | |__ | (_) | |__      ) | | | || || |
#  \ \/ / |  _ <  | |  |  __| > _ <|___ \    / /| | | || || |
#   \  /  | |_) | | |  | |   | (_) |___) |  / /_| |_| || || |
#    \/   |____/  |_|  |_|    \___/|____/  |____|\___/ |_||_|
#                                                            

ELE_ID_CB_85_2011=("((isEB && sigmaIetaIeta < 0.01 &&" +           
                   " deltaPhiSuperClusterTrackAtVtx > -0.039 && deltaPhiSuperClusterTrackAtVtx < 0.039 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.005 && deltaEtaSuperClusterTrackAtVtx < 0.005) || " + 
                   " ( (!isEB) && sigmaIetaIeta < 0.031  &&  " +
                   " deltaPhiSuperClusterTrackAtVtx > -0.028 && deltaPhiSuperClusterTrackAtVtx < 0.028 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.007 && deltaEtaSuperClusterTrackAtVtx < 0.007 )) ")

ELE_ISO_CB_85_2011=("(( isEB && " + BARREL_ISO + " < 0.053 ) || ( (!isEB) && " + ENDCAP_ISO + " < 0.042 ) )")


#__      ______ _______ ______ ___   ___    ___   ___  __ __ 
#\ \    / /  _ \__   __|  ____/ _ \ / _ \  |__ \ / _ \/_ /_ |
# \ \  / /| |_) | | |  | |__ | (_) | | | |    ) | | | || || |
#  \ \/ / |  _ <  | |  |  __| > _ <| | | |   / /| | | || || |
#   \  /  | |_) | | |  | |   | (_) | |_| |  / /_| |_| || || |
#    \/   |____/  |_|  |_|    \___/ \___/  |____|\___/ |_||_|
#

ELE_ID_CB_80_2011=("((isEB && sigmaIetaIeta < 0.01 &&" +           
                   " deltaPhiSuperClusterTrackAtVtx > -0.027 && deltaPhiSuperClusterTrackAtVtx < 0.027 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.005 && deltaEtaSuperClusterTrackAtVtx < 0.005) || " + 
                   " ( (!isEB) && sigmaIetaIeta < 0.031  &&  " +
                   " deltaPhiSuperClusterTrackAtVtx > -0.021 && deltaPhiSuperClusterTrackAtVtx < 0.021 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.006 && deltaEtaSuperClusterTrackAtVtx < 0.006 )) ")



#  __  __ ______ _____   _____ ______    _____ _______ _    _ ______ ______ 
# |  \/  |  ____|  __ \ / ____|  ____|  / ____|__   __| |  | |  ____|  ____|
# | \  / | |__  | |__) | |  __| |__    | (___    | |  | |  | | |__  | |__   
# | |\/| |  __| |  _  /| | |_ |  __|    \___ \   | |  | |  | |  __| |  __|  
# | |  | | |____| | \ \| |__| | |____   ____) |  | |  | |__| | |    | |     
# |_|  |_|______|_|  \_\\_____|______| |_____/   |_|   \____/|_|    |_|     
                                                                          
ELE_MERGE_CONV =  " ( gsfTrack.trackerExpectedHitsInner.numberOfLostHits == 0 && userFloat('convValueMapProd:passVtxConvert') != 0 ) "
ELE_MERGE_ID   =  ("(( isEB && pt < 20 && sigmaIetaIeta < 0.01 &&" +           
                   " deltaPhiSuperClusterTrackAtVtx > -0.03 && deltaPhiSuperClusterTrackAtVtx < 0.03 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.004 && deltaEtaSuperClusterTrackAtVtx < 0.004 &&" +
                   " hadronicOverEm < 0.025 && (fbrem > 0.15 || ( abs(superCluster.eta) < 1. && eSuperClusterOverP > 0.95 )) ) ||" +
                   " ( (!isEB) && pt < 20 && sigmaIetaIeta < 0.03 &&" +           
                   " deltaPhiSuperClusterTrackAtVtx > -0.02 && deltaPhiSuperClusterTrackAtVtx < 0.02 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.005 && deltaEtaSuperClusterTrackAtVtx < 0.005 &&" +
                   " hadronicOverEm < 0.1 && fbrem > 0.15) ||" +
                   " ( isEB && pt > 20 && sigmaIetaIeta < 0.01 &&" +           
                   " deltaPhiSuperClusterTrackAtVtx > -0.06 && deltaPhiSuperClusterTrackAtVtx < 0.06 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.004 && deltaEtaSuperClusterTrackAtVtx < 0.004 &&" +
                   " hadronicOverEm < 0.04) ||" +
                   " ( (!isEB) && pt > 20 && sigmaIetaIeta < 0.03  &&  " +
                   " deltaPhiSuperClusterTrackAtVtx > -0.03 && deltaPhiSuperClusterTrackAtVtx < 0.03 &&" +
                   " deltaEtaSuperClusterTrackAtVtx > -0.007 && deltaEtaSuperClusterTrackAtVtx < 0.007 && " + 
                   " hadronicOverEm < 0.1 ) ) ")

ELE_MERGE_ID2   =  ("( (pt < 20 && " + ELE_ID_LH_80_2011 +") || (pt >= 20 && "+ ELE_ID_LH_90_2011 + ") )")

ELE_MERGE_IP   =   "( abs(userFloat('tip')) < 0.02 && abs(userFloat('dzPV')) < 0.1 )"
ELE_MERGE_ISO  =   "( (isEB && " + SMURF_ISO + " < 0.13) || ( !isEB && " + SMURF_ISO + " < 0.09 ) )"

