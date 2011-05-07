// -*- C++ -*-
//
// Package:    HltObjMatcher
// Class:      HltObjMatcher
// 
// FIXME a _lot_ of stuff hardcoded here. All the trigger names

#include <HWWAnalysis/DileptonSelector/interface/HltObjMatcher.h>
#include <HWWAnalysis/DileptonSelector/interface/Tools.h>
#include <DataFormats/PatCandidates/interface/Electron.h>
#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h>
#include <algorithm>

//______________________________________________________________________________
HltObjMatcher::HltObjMatcher( const std::string& dataType ) {

    //match the dataType string with a known type
    _dataType = dataStrToEnum( dataType );

    if ( _dataType == kUndefined ) {
        THROW_RUNTIME("DataType "<< dataType << " not known");
    }

}


//______________________________________________________________________________
std::string HltObjMatcher::dataEnumToStr( int type ) {
    std::string dataTypeName(""); 
   
    switch (type) {
        case kMC:
            dataTypeName = "MC";
            break;
        case kSingleMu:
            dataTypeName = "SingleMu";
            break;
        case kDoubleMu:
            dataTypeName = "DoubleMu";
            break;
        case kElMu:
            dataTypeName = "EgMu";
            break;
        case kDoubleEl:
            dataTypeName = "DoubleEl";
    }

    return dataTypeName;
            
}

//______________________________________________________________________________
int HltObjMatcher::dataStrToEnum( const std::string& name ) {

    // not found
    int dataTypeEnum(kUndefined);

    std::string lowName = name;
    std::transform(lowName.begin(), lowName.end(), lowName.begin(), ::tolower);

    if ( lowName=="mc" ) {
        dataTypeEnum = kMC;
    } else if ( lowName == "singlemu" ) {
        dataTypeEnum = kSingleMu;
    } else if ( lowName == "doublemu" ) {
        dataTypeEnum = kDoubleMu;
    } else if ( lowName == "mueg" ) {
        dataTypeEnum = kElMu;
    } else if ( lowName == "doubleel" ) {
        dataTypeEnum = kDoubleEl;
    }
    
    return dataTypeEnum;
}

//______________________________________________________________________________
void HltObjMatcher::setTriggerResults( const edm::EventBase& event ) {
    edm::Handle< edm::TriggerResults > hltTriggerResults;
    if( _dataType == kMC )
        event.getByLabel( edm::InputTag("TriggerResults","","REDIGI311X"), hltTriggerResults);
    else
        event.getByLabel( edm::InputTag("TriggerResults","","HLT"), hltTriggerResults);
    
    _hltTrgResults = hltTriggerResults.product();
    _hltTriggerNames = event.triggerNames( *hltTriggerResults );
    
}

//______________________________________________________________________________
bool HltObjMatcher::matchesBits( LepPair& pair ) {
    // useful for mc only
    // the trigger names in the data are different

    bool matched = false;

    if ( isData() ) return true;


    // get all the indexes
    unsigned int iSingleMu  = _hltTriggerNames.triggerIndex("HLT_Mu21_v1");
    unsigned int iDoubleMu  = _hltTriggerNames.triggerIndex("HLT_DoubleMu5_v");
    unsigned int iDoubleEl  = _hltTriggerNames.triggerIndex("HLT_Ele17_SW_TightCaloEleId_Ele8HE_L1R_v2");
    unsigned int iCrossElMu = _hltTriggerNames.triggerIndex("HLT_Mu5_Ele17_v2");
    unsigned int iCrossMuEl = _hltTriggerNames.triggerIndex("HLT_Mu11_Ele8_v1");

    // check the bits
    bool bSingleMu  = (iSingleMu  != _hltTriggerNames.size()) && _hltTrgResults->accept( iSingleMu);
    bool bDoubleMu  = (iDoubleMu  != _hltTriggerNames.size()) && _hltTrgResults->accept( iDoubleMu);
    bool bDoubleEl  = (iDoubleEl  != _hltTriggerNames.size()) && _hltTrgResults->accept( iDoubleEl);
    bool bCrossMuEl = (iCrossMuEl != _hltTriggerNames.size()) && _hltTrgResults->accept( iCrossMuEl);
    bool bCrossElMu = (iCrossElMu != _hltTriggerNames.size()) && _hltTrgResults->accept( iCrossElMu);

    switch( pair.finalState() ) {
        case LepPair::kMM_t: 
            matched = bSingleMu || bDoubleMu;
            break;
        case LepPair::kME_t: 
        case LepPair::kEM_t: 
            matched = bCrossElMu || bCrossMuEl || bSingleMu;
            break;
        case LepPair::kEE_t: 
            matched = bDoubleEl;
            break;
        default:
            THROW_RUNTIME( "Pair what?!?! " << pair.finalState());
    }
    
    return matched;
}

//______________________________________________________________________________
bool HltObjMatcher::matchesObject( LepPair& pair ) {
    // working on data only so far
    //
    bool matched = false;

    // no filtering on mc. Done at the trg bits level so far
    if ( _dataType == kMC ) return true;

    // get the pat objects
    const reco::Candidate* lA = pair.leading()->candidate;
    const reco::Candidate* lB = pair.trailing()->candidate;

    switch ( pair.finalState() ) {
        case LepPair::kMM_t:
            // MuMu pairs
            switch( _dataType ) {
                case kDoubleMu:
                    // DoubleMu dataset
                    // 2x doubles
                    matched = ( passDoubleMu(lA) && passDoubleMu(lB) );

                    break;
                case kSingleMu:
                    // SingleMu dataset
                    // 1+1 single && !2x doubles
                    matched = ( ( passSingleMu(lA) || passSingleMu(lB))
                        && !( passDoubleMu(lA) && passDoubleMu(lB) ) );

                    break;
                case kMC:
                    // MonteCarlo
                    // 2x doubles || 1+1 singles
                    matched = ( ( passDoubleMu(lA) && passDoubleMu(lB) ) 
                        || ( passSingleMu(lA) || passSingleMu(lB) ));
                    break;
//                 default:
//                     THROW_RUNTIME("Dataset type " << _dataType << " not recognized for pair " << pair.finalState() );
            }

            break; // LepPair::kMM_t

        case LepPair::kME_t:
        case LepPair::kEM_t:
            // mixed pairs
            switch( _dataType ) {
                case kElMu:
                    // ElMu dataset
                    // 2x elmu
                    matched = ( passElMu(lA) && passElMu(lB) ) 
                        && !( passSingleMu(lA) || passSingleMu(lB) ) ; 
                    break;
                case kSingleMu:
                    // SingleMu dataset
                    // 1+1 singlemu
                    matched = ( passSingleMu(lA) || passSingleMu(lB) );
//                         && !( passElMu(lA) && passElMu(lB) );
                    break;
                case kMC:
                    // MonteCarlo
                    // 2x elmu || 1+1 singles
                    matched = ( passElMu(lA) && passElMu(lB) )
                        || ( passSingleMu(lA) || passSingleMu(lB) );
                        break;
//                 default:
//                     THROW_RUNTIME("Dataset type " << _dataType << " not recognized for pair " << pair.finalState() );
            }
            break; // LepPair::kEM_t,kME_t

        case LepPair::kEE_t:
            // ElEl pairs
            switch( _dataType ) {
                case kDoubleEl:
                    // DoubleMu dataset
                    // 2x doubles
                    matched = ( passDoubleEl(lA) && passDoubleEl(lB) );
                    break;
                case kMC:
                    // MonteCarlo
                    // 2x doubles 
                    matched = ( passDoubleEl(lA) && passDoubleEl(lB) );
                    break;
//                 default:
//                     THROW_RUNTIME("Dataset type " << _dataType << " not recognized for pair " << pair.finalState() );

            }
            break;
    }

    return matched;
}

//______________________________________________________________________________
bool HltObjMatcher::passSingleMu( const reco::Candidate* lep ) {
    bool ismatch = false;
    // is muon?
    if ( TMath::Abs( lep->pdgId() ) != 13 ) return false;

//     std::cout << " - SingleMuon" << std::endl;
    const pat::Muon *mu = static_cast<const pat::Muon*>(lep); 
    const pat::TriggerObjectStandAlone *hltObj;
    hltObj = mu->triggerObjectMatchByCollection("hltL3MuonCandidates");

//     std::cout << "   pt: " << mu->pt() << "  " << hltObj << std::endl;
    if ( !hltObj ) return false; 
//     std::cout << "   hltObj->pt: " << hltObj->pt() << std::endl;

//     std::vector<std::string> names = hltObj->pathNames();
//     std::copy(names.begin(), names.end(), std::ostream_iterator<std::string>(std::cout, " "));
    // muon 24
    if ( isData() ) {
        ismatch = hltObj->hasPathName("HLT_Mu24_v*",false); 
    } else {
        ismatch = (hltObj->hasPathName("HLT_Mu21_v*",false) && hltObj->pt()>24.0);
    }
    return ismatch;
}


//______________________________________________________________________________
bool HltObjMatcher::passDoubleMu( const reco::Candidate* lep ) {
    bool ismatch = false;
    // is muon?
    if ( TMath::Abs( lep->pdgId() ) != 13 ) return false;

//     std::cout << "-- DoubleMuon -------------------------------------" << std::endl;
    const pat::Muon* mu = static_cast<const pat::Muon*>(lep); 
    const pat::TriggerObjectStandAlone* hltObj = mu->triggerObjectMatchByCollection("hltL3MuonCandidates");
    
//     std::cout << "   pt: " << mu->pt() << "  " << hltObj << std::endl;
    if ( !hltObj ) return false; 
//     std::cout << "   hltObj->pt: " << hltObj->pt() << std::endl;

//     std::cout << "   ";
//     std::vector<std::string> names = hltObj->pathNames();
//     std::copy(names.begin(), names.end(), std::ostream_iterator<std::string>(std::cout, " "));
//     std::cout << std::endl;
    //double mu 7
    if ( isData() ) {
        ismatch = hltObj->hasPathName("HLT_DoubleMu7_v*",false);
    } else {
        ismatch = (hltObj->hasPathName("HLT_DoubleMu5_v*",false) && hltObj->pt()>7.0);  
    }
//     std::cout << " - DoubleMu match " << ismatch << "-------------------------" << std::endl;
    return ismatch;
}

//______________________________________________________________________________
bool HltObjMatcher::passSingleEl( const reco::Candidate* lep ) {
    bool ismatch = false;
    return ismatch;
}

//______________________________________________________________________________
bool HltObjMatcher::passDoubleEl( const reco::Candidate* lep ) {
    bool ismatch = false;

    if ( TMath::Abs( lep->pdgId() ) != 11 ) return false;
    const pat::Electron* el = static_cast<const pat::Electron*>(lep);

    if ( isData() ) {
        ismatch = (el->triggerObjectMatchesByPath("HLT_Ele17_CaloIdL_CaloIsoVL_Ele8_CaloIdL_CaloIsoVL_v*").size() != 0 ||
                el->triggerObjectMatchesByPath("HLT_Ele17_CaloIdT_TrkIdVL_CaloIsoVL_TrkIsoVL_Ele8_CaloIdT_TrkIdVL_CaloIsoVL_TrkIsoVL_v*").size() != 0 ); 
    } else {
        ismatch = (el->triggerObjectMatchesByPath("HLT_Ele17_SW_TightCaloEleId_Ele8HE_L1R_v*").size() != 0);
    }

    return ismatch;
}

//______________________________________________________________________________
bool HltObjMatcher::passElMu( const reco::Candidate* lep ) {
    bool ismatch = false;

    if ( TMath::Abs( lep->pdgId() ) == 13 ) {
        // muon
//         std::cout << "-- ElMu - mu --------------------------------------" << std::endl;
        const pat::Muon* mu = static_cast<const pat::Muon*>(lep); 
        const pat::TriggerObjectStandAlone* hltObj = mu->triggerObjectMatchByCollection("hltL3MuonCandidates");

//         std::cout << "   pt: " << mu->pt() << "  " << hltObj << std::endl;
        if ( !hltObj ) return false;
//         std::cout << "   hltObj->pt: " << hltObj->pt() << std::endl;

//         std::cout << "   ";
//         std::vector<std::string> names = hltObj->pathNames();
//         std::copy(names.begin(), names.end(), std::ostream_iterator<std::string>(std::cout, " "));
//         std::cout << std::endl;
        if ( isData() ) {
            ismatch = ( hltObj->hasPathName("HLT_Mu8_Ele17_CaloIdL_v*",false) 
                    || hltObj->hasPathName("HLT_Mu17_Ele8_CaloIdL_v*",false) );
        } else {
            ismatch = ( hltObj->hasPathName("HLT_Mu5_Ele17_v*",false) && hltObj->pt()>8.0)
                || ( hltObj->hasPathName("HLT_Mu11_Ele8_v*",false) && hltObj->pt()>17.0); 
        }
//         std::cout << " - ElMu mu match " << ismatch << "-------------------------" << std::endl;
    } else if ( TMath::Abs( lep->pdgId() ) == 11 ) {
        // electron
//         std::cout << "-- ElMu - el --------------------------------------" << std::endl;
        const pat::Electron* el = static_cast<const pat::Electron*>(lep);
//         std::cout << "   pt: " << el->pt() << std::endl;
        if ( isData() ) {
            ismatch = ( el->triggerObjectMatchesByPath("HLT_Mu8_Ele17_CaloIdL*").size() != 0
                    ||  el->triggerObjectMatchesByPath("HLT_Mu17_Ele8_CaloIdL*").size() != 0 );
        } else {

//             const pat::TriggerObjectStandAloneCollection& coll = el->triggerObjectMatches();
//             std::cout << " ++ ElMatches Size " << coll.size() << std::endl;
//             for ( size_t i(0); i < coll.size(); ++i) {
//                 std::cout << " + " << i << std::endl;
//                 std::cout << " ++  ";
//                 std::vector<std::string> names = coll[i].pathNames();
//                 std::copy(names.begin(), names.end(), std::ostream_iterator<std::string>(std::cout, " "));
//                 std::cout << std::endl;

//             }

//             const pat::TriggerObjectStandAlone* matchesA = el->triggerObjectMatchByPath("HLT_Mu5_Ele17_v*",true);
//             const pat::TriggerObjectStandAlone* matchesB = el->triggerObjectMatchByPath("HLT_Mu11_Ele8_v*",true);
//             std::cout << "   matchesA " << matchesA<< std::endl;
//             std::cout << "   matchesB " << matchesB<< std::endl;
            ismatch = ( el->triggerObjectMatchByPath("HLT_Mu5_Ele17_v*",true) != 0 
                    || el->triggerObjectMatchByPath("HLT_Mu11_Ele8_v*",true) !=0 );
        }
//         std::cout << " - ElMu el match " << ismatch << "-------------------------" << std::endl;

    } else {
        return false;
    }

    return ismatch;
}
