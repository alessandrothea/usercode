// -*- C++ -*-
//
// Package:    EventViewFiller
// Class:      EventViewFiller
// 
/**\class EventViewFiller EventViewFiller.cc HWWAnalysis/EventViewFiller/src/EventViewFiller.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Sat Jul  9 16:39:20 CEST 2011
// $Id: EventViewFiller.cc,v 1.1 2011/07/16 22:57:06 thea Exp $
//
//

#include "HWWAnalysis/DileptonSelector/interface/EventViewFiller.h"

namespace hww {
namespace helper {

reco::MET makeSmurfMet( const hww::DileptonPtr& pair , const edm::PtrVector<reco::Candidate>& cands );
//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
EventViewFiller::EventViewFiller(const edm::ParameterSet& iConfig)
{
    //now do what ever other initialization is needed

    hltSummarySrc_ = iConfig.getParameter<edm::InputTag>("hltSummarySrc");
    dileptonSrc_   = iConfig.getParameter<edm::InputTag>("dileptonSrc");

    jetSrc_        = iConfig.getParameter<edm::InputTag>("jetSrc");
    softMuonSrc_   = iConfig.getParameter<edm::InputTag>("softMuonSrc");

    pfMetSrc_      = iConfig.getParameter<edm::InputTag>("pfMetSrc");
    tcMetSrc_      = iConfig.getParameter<edm::InputTag>("tcMetSrc");
    chargedMetSrc_ = iConfig.getParameter<edm::InputTag>("chargedMetSrc");
    vertexSrc_     = iConfig.getParameter<edm::InputTag>("vertexSrc");
    pfChCandSrc_   = iConfig.getParameter<edm::InputTag>("pfChCandSrc");
}


EventViewFiller::~EventViewFiller()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
uint
EventViewFiller::count( const edm::Event& iEvent ) const {
    using namespace edm;

    Handle<edm::View<hww::DileptonView> > dileptons;
    iEvent.getByLabel(dileptonSrc_,dileptons);

	return dileptons->size();
}

void
EventViewFiller::doFill(std::vector<hww::EventView*> views, const edm::Event& iEvent)
{
	//TODO:
	//the argument is a vector of views
	//of course it doesn't work with a vector of child classes.
	//
	//to be implemented:
	//
	// vec = auto_ptr<vector<class> >( new vector<class> )
	// filler.init(iEvent) // prepare the handles
	// theVec->resize( filler.size() )
	//
    using namespace edm;

    Handle<edm::View<hww::DileptonView> > dileptons;
    iEvent.getByLabel(dileptonSrc_,dileptons);

    Handle<pat::strbitset> hltBits;
    iEvent.getByLabel(hltSummarySrc_,hltBits);

    Handle<edm::View<reco::Vertex> > vertexes;
    iEvent.getByLabel(vertexSrc_, vertexes);

    Handle<edm::View<pat::Jet> > jets;
    iEvent.getByLabel(jetSrc_, jets);

    Handle<edm::View<pat::Muon> > softMuons;
    iEvent.getByLabel(softMuonSrc_, softMuons);

    edm::Handle<edm::View<reco::MET> > tcMet;
    iEvent.getByLabel(tcMetSrc_, tcMet);

    Handle<edm::View<reco::PFMET> > pfMet;
    iEvent.getByLabel(pfMetSrc_, pfMet);

    Handle<edm::ValueMap<reco::PFMET> > chargedMet;
    iEvent.getByLabel(chargedMetSrc_, chargedMet);
    
    // reduced charged pf candidates
    edm::Handle<edm::View<reco::Candidate> > reducedPfCandidates;
    iEvent.getByLabel(pfChCandSrc_,reducedPfCandidates);

//     views.resize( dileptons->size() );
    for( uint k(0); k < dileptons->size() ; ++k ) {
        // the new EventViews have the same sorting as dileptonViews (by ptSum)
//         hww::EventView& view = views.at(k);
		hww::EventView& view = *(views.at(k));
        edm::Ptr< hww::DileptonView > dilepton = dileptons->ptrAt(k);

        //... hlt info...
        view.setHltBits( *hltBits );

        view.setDilepton( dilepton );

		const std::vector<edm::Ptr<reco::RecoCandidate> >& muons = dilepton->muons();

		// add vertexes
		for( uint i(0); i<vertexes->size(); ++i)
			view.addVrtx(vertexes->ptrAt(i));

        // add jets
        for ( uint i(0); i<jets->size(); ++i )
            view.addJet(jets->ptrAt(i));

        // add muons
        for( uint i(0); i<softMuons->size(); ++i ) {
            bool overlap=false;
            for( uint j(0); j<muons.size(); ++j ) {
                // one could use ptr1 == ptr2, but it must be sure they come from the same collection
                overlap = ( softMuons->at(i).p4().pt() == muons[j]->p4().pt() ); 
                if ( overlap ) break;
            }
            if ( overlap ) continue;
            view.addSoftMuon(softMuons->ptrAt(i));
        }

        // add mets
        view.setTcMet(tcMet->at(0));
        view.setPFMet(pfMet->at(0));
        view.setChargedMet(chargedMet->get(0));
        // and here calculate the smurfmet
        view.setChargedMetSmurf( makeSmurfMet( dileptons->ptrAt(k), reducedPfCandidates->ptrVector() ) );
    }

}

reco::MET makeSmurfMet( const hww::DileptonPtr& pair , const edm::PtrVector<reco::Candidate>& cands ) {
    math::XYZTLorentzVector pfP4;
    for( uint k(0); k < cands.size(); ++k ) {
        if ( TMath::Abs(ROOT::Math::VectorUtil::DeltaR(cands[k]->p4(), pair->leading()->p4() ) ) <= 0.1 )
            continue;
        if ( TMath::Abs(ROOT::Math::VectorUtil::DeltaR(cands[k]->p4(), pair->trailing()->p4() ) ) <= 0.1 )
            continue;
        pfP4 += cands[k]->p4();
    }

    pfP4 += pair->leading()->p4();
    pfP4 += pair->trailing()->p4();
    
    reco::MET met(-pfP4,reco::Candidate::Point(0,0,0));
    return met;
}

}
}
