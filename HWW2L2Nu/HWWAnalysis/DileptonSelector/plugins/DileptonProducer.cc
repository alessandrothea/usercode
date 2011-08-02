// -*- C++ -*-
//
// Package:    DileptonProducer
// Class:      DileptonProducer
// 
/**\class DileptonProducer DileptonProducer.cc HWWAnalysis/DileptonProducer/src/DileptonProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Fri Jun 24 16:27:01 CEST 2011
// $Id: DileptonProducer.cc,v 1.2 2011/07/16 22:57:06 thea Exp $
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
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "HWWAnalysis/DataFormats/interface/DileptonView.h"
#include "HWWAnalysis/Misc/interface/Tools.h"
#include "Math/VectorUtil.h"

//
// class declaration
//

class DileptonProducer : public edm::EDProducer {
   public:
      explicit DileptonProducer(const edm::ParameterSet&);
      ~DileptonProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      // ----------member data ---------------------------
      std::string   cut_;
      edm::InputTag electronSrc_;
      edm::InputTag muonSrc_;

      StringCutObjectSelector<hww::DileptonView, true> selector_;
      StringCutObjectSelector<reco::RecoCandidate, true > extraSelector_;

};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
DileptonProducer::DileptonProducer(const edm::ParameterSet& iConfig) :
    selector_( iConfig.getParameter<std::string>("cut") ),
	extraSelector_( (iConfig.existsAs<std::string>("extraCut") ? iConfig.getParameter<std::string>("extraCut") : "" ) ) 
{
    //register your products
    produces<std::vector<hww::DileptonView> >();

    electronSrc_ = iConfig.getParameter<edm::InputTag>("electronSrc");
    muonSrc_     = iConfig.getParameter<edm::InputTag>("muonSrc");

}


DileptonProducer::~DileptonProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
    void
DileptonProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    using namespace std;
	using namespace ROOT::Math;

    std::auto_ptr<hww::DileptonViewVec > pairs(new std::vector<hww::DileptonView> );

    edm::Handle<edm::View<reco::RecoCandidate> > electrons;
    iEvent.getByLabel(electronSrc_,electrons);
    edm::Handle<edm::View<reco::RecoCandidate> > muons;
    iEvent.getByLabel(muonSrc_,muons);

    vector<edm::Ptr<reco::RecoCandidate> > leptons;
    for( uint i(0); i<electrons->size(); ++i) 
        leptons.push_back(electrons->ptrAt(i));

    for( uint i(0); i<muons->size(); ++i)
        leptons.push_back(muons->ptrAt(i));

    for( uint i(0); i<leptons.size(); ++i)
        for( uint j(i+1); j<leptons.size(); ++j) {
            hww::DileptonView p( leptons[i], leptons[j]);
            if ( i == j ) THROW_RUNTIME("Warning!!! i == j")
            if ( !selector_(p) ) continue;

            for( uint k(0); k < leptons.size(); ++k ) {
                // no double counting
                if ( k == i || k == j ) continue;
                // and overlap removal
                double dRi = VectorUtil::DeltaR(leptons[i]->p4(),leptons[k]->p4());
                double dRj = VectorUtil::DeltaR(leptons[j]->p4(),leptons[k]->p4());
                if ( dRi < 0.1 || dRj < 0.1 ) continue;
				if ( !extraSelector_(*leptons[k]) ) continue;
                p.addExtra(leptons[k]);
            }
            pairs->push_back(p);

//             cout << "all " << leptons.size() << " | " << p.getLeptons().size() << " | " << p.getExtra().size() << " | " << endl;
        }

    sort(pairs->begin(), pairs->end(), hww::helper::greaterByPtSum() );
    iEvent.put(pairs);
    
}

// ------------ method called once each job just before starting event loop  ------------
void 
DileptonProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
DileptonProducer::endJob() {
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
DileptonProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(DileptonProducer);
