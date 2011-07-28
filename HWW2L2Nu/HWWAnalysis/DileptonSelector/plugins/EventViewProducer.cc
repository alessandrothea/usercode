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
// $Id: EventViewProducer.cc,v 1.1 2011/07/16 22:57:06 thea Exp $
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
#include "HWWAnalysis/DileptonSelector/interface/EventViewFiller.h"

//
// class declaration
//

class EventViewProducer : public edm::EDProducer {
   public:
      explicit EventViewProducer(const edm::ParameterSet&);
      ~EventViewProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void produce(edm::Event&, const edm::EventSetup&);
      
      // ----------member data ---------------------------
	  hww::helper::EventViewFiller filler;


};

//
// constructors and destructor
//
EventViewProducer::EventViewProducer(const edm::ParameterSet& iConfig)
: filler( iConfig )
{
    //register your products
    produces< hww::EventViewVec >();

}

EventViewProducer::~EventViewProducer()
{
}

//
// member functions
//

// ------------ method called to produce the data  ------------
void
EventViewProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    std::auto_ptr<hww::EventViewVec> pEventViews( new hww::EventViewVec() );
	filler.fill(*pEventViews, iEvent);
    iEvent.put(pEventViews);

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
