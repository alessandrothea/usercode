// -*- C++ -*-
//
// Package:    HltSummaryProducer
// Class:      HltSummaryProducer
// 
/**\class HltSummaryProducer HltSummaryProducer.cc HWWAnalysis/HltSummaryProducer/src/HltSummaryProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Thu Jun 23 15:18:30 CEST 2011
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
#include "HWWAnalysis/DileptonSelector/interface/HltBitChecker.h"
//
// class declaration
//

class HltSummaryProducer : public edm::EDProducer {
   public:
      explicit HltSummaryProducer(const edm::ParameterSet&);
      ~HltSummaryProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      // ----------member data ---------------------------
      edm::InputTag triggerSrc_;
      std::vector<std::pair<std::string, HltBitChecker> > checkers_;

};

//
// constants, enums and typedefs
//


//
// static data member definitions
//


#include "PhysicsTools/SelectorUtils/interface/strbitset.h"
using namespace std;
//
// constructors and destructor
//
HltSummaryProducer::HltSummaryProducer(const edm::ParameterSet& iConfig)
{
    //register your products
    produces<pat::strbitset>();

    //now do what ever other initialization is needed
    triggerSrc_ = iConfig.getParameter<edm::InputTag>("triggerSrc");

    std::vector< std::string > pathNames = iConfig.getParameterNamesForType<std::vector<std::string> >();
    std::vector<std::string>::iterator iName, bp = pathNames.begin(), ep = pathNames.end();
    for( iName = bp; iName != ep; ++iName) {
        // printout
//         cout << *iName << endl;
        vector<string> ranges = iConfig.getParameter<std::vector<std::string> >(*iName);
        // printout
        HltBitChecker path( ranges );
        checkers_.push_back( make_pair(*iName, path) );
    }
}


HltSummaryProducer::~HltSummaryProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
    void
HltSummaryProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    std::auto_ptr<pat::strbitset> pBits(new pat::strbitset);

    Handle<edm::TriggerResults> results; 
    iEvent.getByLabel(triggerSrc_,results);

    std::vector<std::pair<std::string, HltBitChecker> >::const_iterator iChk, bc = checkers_.begin(), ec = checkers_.end();
    for ( iChk = bc; iChk != ec; ++iChk ){
        pBits->push_back(iChk->first);
        pBits->set(iChk->first, iChk->second.check(iEvent,*results));
    }

//     pBits->print(cout);
    iEvent.put(pBits);

}

// ------------ method called once each job just before starting event loop  ------------
void 
HltSummaryProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
HltSummaryProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
HltSummaryProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
HltSummaryProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
HltSummaryProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
HltSummaryProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
HltSummaryProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(HltSummaryProducer);
