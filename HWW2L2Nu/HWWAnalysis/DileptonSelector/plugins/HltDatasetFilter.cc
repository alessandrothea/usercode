// -*- C++ -*-
//
// Package:    HltDatasetFilter
// Class:      HltDatasetFilter
// 
/**\class HltDatasetFilter HltDatasetFilter.cc HWWAnalysis/HltDatasetFilter/src/HltDatasetFilter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Tue Jun 21 18:38:37 CEST 2011
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

//
// class declaration
//

class HltDatasetFilter : public edm::EDFilter {
   public:
      explicit HltDatasetFilter(const edm::ParameterSet&);
      ~HltDatasetFilter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual bool filter(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual bool beginRun(edm::Run&, edm::EventSetup const&);
      virtual bool endRun(edm::Run&, edm::EventSetup const&);
      virtual bool beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual bool endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      // ----------member data ---------------------------
      edm::InputTag hltSummarySrc_;
      std::string mode_;

      std::vector<std::string> accept_;
      std::vector<std::string> reject_;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

#include "PhysicsTools/SelectorUtils/interface/strbitset.h"
//
// constructors and destructor
//
HltDatasetFilter::HltDatasetFilter(const edm::ParameterSet& iConfig)
{
   //now do what ever initialization is needed

    hltSummarySrc_  = iConfig.getParameter<edm::InputTag>("hltSummarySrc");
    mode_           = iConfig.getParameter<std::string>("mode");

//     std::vector< std::string > pathNames = iConfig.getParameterNamesForType<std::vector<std::string> >();
//     std::vector<std::string>::iterator iName, bp = pathNames.begin(), ep = pathNames.end();
//     for( iName = bp; iName != ep; ++iName) {
//     }
    edm::ParameterSet pset = iConfig.getParameter<edm::ParameterSet>(mode_);
    accept_ = pset.getParameter< std::vector<std::string> >("accept");
    reject_ = pset.getParameter< std::vector<std::string> >("reject");

}


HltDatasetFilter::~HltDatasetFilter()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called on each new Event  ------------
bool
HltDatasetFilter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   Handle<pat::strbitset> hltBits;
   iEvent.getByLabel(hltSummarySrc_,hltBits);

//    hltBits->print(std::cout);
   std::vector<std::string>::iterator iPath,
       bAcc = accept_.begin(), eAcc = accept_.end(),
       bRej = reject_.begin(), eRej = reject_.end();

   bool accept(false), reject(false);
   for ( iPath = bAcc; iPath != eAcc; ++iPath )
       accept |= hltBits->test(*iPath);

   for ( iPath = bRej; iPath != eRej; ++iPath )
       reject |= hltBits->test(*iPath);
   

   return (accept && !reject);
}

// ------------ method called once each job just before starting event loop  ------------
void 
HltDatasetFilter::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
HltDatasetFilter::endJob() {
}

// ------------ method called when starting to processes a run  ------------
bool 
HltDatasetFilter::beginRun(edm::Run&, edm::EventSetup const&)
{ 
  return true;
}

// ------------ method called when ending the processing of a run  ------------
bool 
HltDatasetFilter::endRun(edm::Run&, edm::EventSetup const&)
{
  return true;
}

// ------------ method called when starting to processes a luminosity block  ------------
bool 
HltDatasetFilter::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
  return true;
}

// ------------ method called when ending the processing of a luminosity block  ------------
bool 
HltDatasetFilter::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
  return true;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
HltDatasetFilter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
//define this as a plug-in
DEFINE_FWK_MODULE(HltDatasetFilter);
