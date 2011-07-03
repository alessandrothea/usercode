// -*- C++ -*-
//
// Package:    LeptonYieldAnalyzer
// Class:      LeptonYieldAnalyzer
// 
/**\class LeptonYieldAnalyzer LeptonYieldAnalyzer.cc tmp/LeptonYieldAnalyzer/src/LeptonYieldAnalyzer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Fri Jun 24 22:23:11 CEST 2011
// $Id: LeptonYieldAnalyzer.cc,v 1.1 2011/06/29 22:16:06 thea Exp $
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include <CommonTools/UtilAlgos/interface/TFileService.h>
#include <FWCore/ServiceRegistry/interface/Service.h>

#include "HWWAnalysis/Misc/interface/RootUtils.h"

//
// class declaration
//

class LeptonYieldAnalyzer : public edm::EDAnalyzer {
   public:
      explicit LeptonYieldAnalyzer(const edm::ParameterSet&);
      ~LeptonYieldAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      // ----------member data ---------------------------
      
      struct YieldBin {
        YieldBin() : index(-1) {}
        std::string   name;
        edm::InputTag src;
        uint index;

      };

      struct Category {
          Category( std::string name ) : name(name), yield(0x0) {}
          std::string name;
          TH1D*       yield;
      };

      std::vector<Category>     categories_;
      std::vector<YieldBin>     bins_;
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
LeptonYieldAnalyzer::LeptonYieldAnalyzer(const edm::ParameterSet& iConfig)

{
    //now do what ever initialization is needed

    vector<string> cats = iConfig.getParameter< vector< string > >("categories");
    for( uint i(0); i < cats.size(); ++i)
        categories_.push_back( Category(cats[i] ) );

    edm::VParameterSet binVPset = iConfig.getParameter<edm::VParameterSet>("bins");
//     edm::VPset::const_iterator iBin, bB = iBin.begin(), eB = iBin.end();
//     for( iBin = bB; iBin != eB; ++iBin ) {
    for( uint k(0); k < binVPset.size(); ++k ) {
        YieldBin bin;
        bin.name = binVPset[k].getParameter<string>("name");
        bin.src  = binVPset[k].getParameter<edm::InputTag>("src");
        bins_.push_back(bin); 
    }

}


LeptonYieldAnalyzer::~LeptonYieldAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
LeptonYieldAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    vector<Category>::const_iterator iCat, bC = categories_.begin(), eC = categories_.end();
    // fill the 0 bin
    for( iCat = bC; iCat != eC; ++iCat )
        iCat->yield->Fill(0);

    std::vector<YieldBin>::const_iterator iBin, bB = bins_.begin(), eB = bins_.end();
    for( iBin = bB; iBin != eB; ++iBin ) {
        Handle< map<string,int> > monSummary;
        iEvent.getByLabel(iBin->src, monSummary);
        
        if ( !monSummary.isValid() ) break;


        // fill the bin
//         map<string, int>::const_iterator iCat;
//         for ( iCat = monSummary->begin(); iCat != monSummary->end(); ++iCat ) {
//             cout << iCat->first << "  " << iCat->second << endl;
//         } 
        for( iCat = bC; iCat != eC; ++iCat ) {
            if ( monSummary->count( iCat->name ) != 0 ) {
                // what about the weights?
                iCat->yield->Fill( iBin->index );
            }
        }
    }



}


// ------------ method called once each job just before starting event loop  ------------
void 
LeptonYieldAnalyzer::beginJob()
{
    edm::Service<TFileService> fs;
    TFileDirectory* here = &(*fs);

    // make labels
    map<int,string> labels;
    labels[0] = "All events";
    for( uint i(0); i < bins_.size(); ++i) {
        labels[i+1] = bins_[i].name;
        bins_[i].index = i+1;
    }

    vector<Category>::iterator iCat, bC = categories_.begin(), eC = categories_.end();
    for( iCat = bC; iCat != eC; ++iCat ) {
        iCat->yield = hww::makeLabelHistogram( here, (iCat->name+"Yield").c_str(), (iCat->name+" Yields").c_str(), labels); 
    }
        
    

}

// ------------ method called once each job just after ending the event loop  ------------
void 
LeptonYieldAnalyzer::endJob() 
{
}
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
LeptonYieldAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(LeptonYieldAnalyzer);
