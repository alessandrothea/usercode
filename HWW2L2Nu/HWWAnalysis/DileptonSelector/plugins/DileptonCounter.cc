// -*- C++ -*-
//
// Package:    DileptonCounter
// Class:      DileptonCounter
// 
/**\class DileptonCounter DileptonCounter.cc tmp/DileptonCounter/src/DileptonCounter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Fri Jun 24 17:35:11 CEST 2011
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDFilter.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "HWWAnalysis/DataFormats/interface/DileptonView.h"

//
// class declaration
//

class DileptonCounter : public edm::EDFilter {
   public:
      explicit DileptonCounter(const edm::ParameterSet&);
      ~DileptonCounter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual bool filter(edm::Event&, const edm::EventSetup&);
      // ----------member data ---------------------------

      edm::InputTag src_;
      int min_;
      int max_;
};

DileptonCounter::DileptonCounter(const edm::ParameterSet& iConfig)
: src_(iConfig.getParameter<edm::InputTag>("src")), min_(-1), max_(-1)
{
   //now do what ever initialization is needed

    if ( iConfig.existsAs<int>("min") ) min_ = iConfig.getParameter<int>("min");
    if ( iConfig.existsAs<int>("max") ) max_ = iConfig.getParameter<int>("max");
}


DileptonCounter::~DileptonCounter()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called on each new Event  ------------
bool
DileptonCounter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   using namespace std;

   Handle<hww::DileptonViewVec> dileptons;
   iEvent.getByLabel(src_, dileptons);
   
   bool selected = true;
   if (min_ >= 0)  selected &= ( (int)dileptons->size() >= min_ );
   if (max_ >= 0)  selected &= ( (int)dileptons->size() <= max_ );

   return selected;
}
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
DileptonCounter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
//define this as a plug-in
DEFINE_FWK_MODULE(DileptonCounter);
