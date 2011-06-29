import FWCore.ParameterSet.Config as cms

MUON_ID_CUT=("(( (isGlobalMuon() && "
             "    globalTrack.normalizedChi2 <10 &&" +
             "    globalTrack.hitPattern.numberOfValidMuonHits > 0 && " + 
             "    numberOfMatches > 1 ) || " + 
             "   (isTrackerMuon() && muonID('TMLastStationTight')) ) && " + 
             " innerTrack.found >10 &&" +
             " innerTrack.hitPattern().numberOfValidPixelHits > 0 && " + 
             " abs(track.ptError / pt) < 0.10 )")

MUON_ID_CUT_OLD=("(isGlobalMuon && isTrackerMuon &&" +
                 " innerTrack.found >10 &&" +
                 " innerTrack.hitPattern().numberOfValidPixelHits > 0 && " + 
                 " globalTrack.normalizedChi2 <10 &&" +
                 " globalTrack.hitPattern.numberOfValidMuonHits > 0 && " + 
                 " numberOfMatches > 1 && " + 
                 " abs(track.ptError / pt) < 0.10 )")

#SMURF_ISO = ("( userFloat('smurfCharged') + userFloat('smurfPhoton') + userFloat('smurfNeutral') )/ pt")
SMURF_ISO = ("( userFloat('muSmurfPF') )/ pt")
MUON_MERGE_ISO  =   ("( (abs(eta) < 1.479 && pt >  20 && " + SMURF_ISO + " < 0.13) || ( abs(eta) >= 1.479 && pt >  20 && " + SMURF_ISO + " < 0.09 ) || " + 
                     "  (abs(eta) < 1.479 && pt <= 20 && " + SMURF_ISO + " < 0.06) || ( abs(eta) >= 1.479 && pt <= 20 && " + SMURF_ISO + " < 0.05 ) )  ")

MUON_MERGE_IP  = ("( ( (pt >= 20 && abs(userFloat('tip')) < 0.02) || (pt < 20 && abs(userFloat('tip')) < 0.01) ) && " +
                  "  abs(userFloat('dzPV'))  < 0.1 )" )
              
              


MUON_ISO_CUT = ("(isolationR03().emEt +" +
                " isolationR03().hadEt +" +
                " isolationR03().sumPt - userFloat('rhoMu')*3.14159265*0.3*0.3)/pt < 0.15 ");

MUON_ISO_CUT_TIGHT=("( ( pt > 20 && (isolationR03().emEt + isolationR03().hadEt + " +
                        " isolationR03().sumPt - userFloat('rhoMu')*3.14159265*0.3*0.3)/pt < 0.15 ) || " + 
                    "  ( pt <= 20 && (isolationR03().emEt + isolationR03().hadEt +" +
                        " isolationR03().sumPt - userFloat('rhoMu')*3.14159265*0.3*0.3)/pt < 0.12 ) )");

MUON_ISOPF_CUT = ("( (userFloat('pfCharged')+userFloat('pfPhoton')+userFloat('pfNeutral')-userFloat('rhoMuNoPU')*3.14159265*0.4*0.4) / pt < 0.20)")


MUON_IP_CUT=( "( abs(userFloat('tip2')) < 0.01 && " +
              "  abs(userFloat('dzPV'))  < 0.05    )" )


MUON_ID_CUT_4VETO=("(isTrackerMuon &&" +
                   " muonID('TMLastStationAngTight') &&" +
                   " innerTrack.found >10 && abs(userFloat('tip')) < 0.2 && abs(userFloat('dzPV')) < 0.1 &&" +
                   " ( (pt <= 20) || " +
                   "   (pt >  20  && (isolationR03().emEt+isolationR03().hadEt+isolationR03().sumPt" +
                   "                 )/pt > 0.10) ) )")

