// -*- C++ -*-
//
// Package:    DileptonSelector
// Class:      HltObjMatcher
// 
/**

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Thu Apr 14 12:29:55 CEST 2011
// $Id: HltObjMatcher.h,v 1.1 2011/05/07 08:56:43 thea Exp $
//
//
// system include files

#ifndef HWWAnalysisDileptonSelector_HltObjMatcher_h
#define HWWAnalysisDileptonSelector_HltObjMatcher_h

#include <DataFormats/Candidate/interface/Candidate.h>
#include <HWWAnalysis/DileptonSelector/interface/HWWCandidates.h>
#include <FWCore/Common/interface/EventBase.h>
#include <FWCore/Common/interface/TriggerNames.h>
#include <DataFormats/Common/interface/TriggerResults.h>

class HltObjMatcher {
    public:
    HltObjMatcher( const std::string& dataType );
    ~HltObjMatcher() {}

    enum {
        kUndefined,
        kMC,
        kSingleMu,
        kDoubleMu,
        kElMu,
        kDoubleEl
    };

    bool isData() { return _dataType != kMC; }
    std::vector<unsigned int> findIndexes( const std::string& path );

    bool passSingleMu( const reco::Candidate* );
    bool passDoubleMu( const reco::Candidate* );
    bool passSingleEl( const reco::Candidate* );
    bool passDoubleEl( const reco::Candidate* );
    bool passElMu( const reco::Candidate* );

    bool matchesBits( LepPair& );
    bool matchesObject( LepPair& );

    void setTriggerResults( const edm::EventBase& );
    int dataType() { return _dataType; }
    std::string dataLabel() { return dataEnumToStr( _dataType ); }

    protected:
    std::vector<std::string> search(const std::string& name,const std::vector< std::string >& nameVec );
    std::string dataEnumToStr( int );
    int dataStrToEnum( const std::string& );

    private:
    
    const edm::TriggerResults* _hltTrgResults;
    edm::TriggerNames _hltTriggerNames;
    int _dataType;
    static const char wildcard_;// = '*';
};
#endif // HWWAnalysisDileptonSelector_HltObjMatcher_h 
