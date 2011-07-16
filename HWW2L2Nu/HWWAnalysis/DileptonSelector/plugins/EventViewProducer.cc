// -*- C++ -*-
//
// Package:    EventViewProducer
// Class:      EventViewProducer
// 
/**\class EventViewProducer EventViewProducer.cc HWWAnalysis/EventViewProducer/src/EventViewProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Sat Jul  9 16:39:20 CEST 2011
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "HWWAnalysis/DataFormats/interface/EventView.h"
#include "Math/VectorUtil.h"
#include "PhysicsTools/SelectorUtils/interface/strbitset.h"

//
// class declaration
//

class EventViewProducer : public edm::EDProducer {
   public:
      explicit EventViewProducer(const edm::ParameterSet&);
      ~EventViewProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      // ----------member data ---------------------------

      edm::InputTag hltSummarySrc_;
      edm::InputTag dileptonSrc_;
      edm::InputTag jetSrc_;
      edm::InputTag softMuonSrc_;
      edm::InputTag pfMetSrc_;
      edm::InputTag tcMetSrc_;
      edm::InputTag chargedMetSrc_;
      edm::InputTag vertexSrc_;
      edm::InputTag pfChCandSrc_;

};

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
EventViewProducer::EventViewProducer(const edm::ParameterSet& iConfig)
{
    //register your products
    produces< hww::EventViewVec >();
    /* Examples
       produces<ExampleData2>();

    //if do put with a label
    produces<ExampleData2>("label");

    //if you want to put into the Run
    produces<ExampleData2,InRun>();
     */
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


EventViewProducer::~EventViewProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
EventViewProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    Handle<pat::strbitset> hltBits;
    iEvent.getByLabel(hltSummarySrc_,hltBits);

    Handle<edm::View<hww::DileptonView> > dileptons;
    iEvent.getByLabel(dileptonSrc_,dileptons);

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


    std::auto_ptr<hww::EventViewVec> pEventViews( new hww::EventViewVec() );

    pEventViews->resize( dileptons->size() );
    for( uint k(0); k < dileptons->size() ; ++k ) {
        // the new EventViews have the same sorting as dileptonViews (by ptSum)
        hww::EventView& view = pEventViews->at(k);
        edm::Ptr< hww::DileptonView > dilepton = dileptons->ptrAt(k);

        //... hlt info...
        view.setHltBits( *hltBits );

        view.setDilepton( dilepton );

        // add muons
        //         for ( uint i(0); i<muons->size(); ++i )
        //             view.addMuon(muons->ptrAt(i));

        //         // electron-muon disambiguation
        //         // add electrons
        //         for ( uint i(0); i<electrons->size(); ++i ) {
        //             bool overlap = false;
        //             for ( uint j(0); j<muons->size(); ++j ) {
        //                 // config file? separated module?
        //                 overlap = ROOT::Math::VectorUtil::DeltaR( electrons->ptrAt(i)->p4(), muons->ptrAt(j)->p4() ) <= 0.1;
        //                 if (overlap) break;
        //             }
        //             if (overlap) continue;
        //             view.addElectron(electrons->ptrAt(i));
        //         }
        const std::vector<edm::Ptr<reco::RecoCandidate> >& muons = dilepton->muons();

        // add jets
        for ( uint i(0); i<jets->size(); ++i )
            view.addJets(jets->ptrAt(i));

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



    iEvent.put(pEventViews);

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


// ------------ method called once each job just before starting event loop  ------------
void 
EventViewProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
EventViewProducer::endJob() {
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
EventViewProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(EventViewProducer);
