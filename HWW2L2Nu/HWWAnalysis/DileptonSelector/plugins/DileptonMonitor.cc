// -*- C++ -*-
//
// Package:    DileptonMonitor
// Class:      DileptonMonitor
// 
/**\class DileptonMonitor DileptonMonitor.cc HWWAnalysis/DileptonMonitor/src/DileptonMonitor.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Fri Jun 24 16:27:01 CEST 2011
// $Id: DileptonMonitor.cc,v 1.1 2011/06/29 22:16:06 thea Exp $
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

#include <CommonTools/UtilAlgos/interface/TFileService.h>
#include <FWCore/ServiceRegistry/interface/Service.h>


//
// class declaration
//

class DileptonMonitor : public edm::EDProducer {
   public:
      explicit DileptonMonitor(const edm::ParameterSet&);
      ~DileptonMonitor();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      // ----------member data ---------------------------
      edm::InputTag src_;
      

      struct DileptonCategory {
          DileptonCategory( const std::string& name, const std::string& cut) : name(name), selector(cut) {}
              std::string name;
          StringCutObjectSelector<hww::DileptonView > selector;
      };
      std::vector<DileptonCategory> categories_;

};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

using namespace std;

//
// constructors and destructor
//
DileptonMonitor::DileptonMonitor(const edm::ParameterSet& iConfig)
{
    //register your products
    produces< map<string,int> >();

    src_ = iConfig.getParameter<edm::InputTag>("src");
    edm::ParameterSet catPset = iConfig.getParameter<edm::ParameterSet>("categories");
    
    vector<string> catNames = catPset.getParameterNamesForType<string>();
    vector<string>::iterator iCat;
    for ( iCat = catNames.begin(); iCat != catNames.end(); ++iCat ) {
//         cout << *iCat << "  '" << catPset.getParameter<string>(*iCat) << "'" << endl;
        categories_.push_back(DileptonCategory(*iCat, catPset.getParameter<string>(*iCat) ));
    }

}


DileptonMonitor::~DileptonMonitor()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
    void
DileptonMonitor::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    using namespace std;

    auto_ptr<map<string,int> > counts( new map<string,int>() );

    Handle<hww::DileptonViewVec> dileptons;
    iEvent.getByLabel(src_, dileptons);

    hww::DileptonViewVec::const_iterator iDiLep;
    
    vector<DileptonCategory>::iterator iCat;
    for( iCat = categories_.begin(); iCat != categories_.end(); ++iCat ) {
        for( iDiLep = dileptons->begin(); iDiLep != dileptons->end(); ++iDiLep ) {
            if ( iCat->selector(*iDiLep) ) 
               (*counts)[iCat->name]++; 
        }
    }
    
    iEvent.put(counts);
    
}

// ------------ method called once each job just before starting event loop  ------------
void 
DileptonMonitor::beginJob()
{
//     edm::Service<TFileService> fs;
//     
//     fs->make<TH1D>("test","this is a test", 10, 0, 10);
}

// ------------ method called once each job just after ending the event loop  ------------
void 
DileptonMonitor::endJob() {
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
DileptonMonitor::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(DileptonMonitor);
