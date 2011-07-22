// -*- C++ -*-
//
// Package:    WeightsCollector
// Class:      WeightsCollector
// 
/**\class WeightsCollector WeightsCollector.cc HWWAnalysis/WeightsCollector/src/WeightsCollector.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Thu Jun 23 15:18:30 CEST 2011
// $Id: WeightsCollector.cc,v 1.2 2011/07/22 08:28:53 thea Exp $
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
#include <SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h>
#include "HWWAnalysis/Misc/interface/Tools.h"


//
// class declaration
//

class WeightsCollector : public edm::EDProducer {
   public:
      explicit WeightsCollector(const edm::ParameterSet&);
      ~WeightsCollector();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      // ----------member data ---------------------------
      edm::InputTag puInfoSrc_;
      edm::InputTag ptWeightSrc_;

      std::vector<double> puWeights_;
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
WeightsCollector::WeightsCollector(const edm::ParameterSet& iConfig)
{
    //register your products
    produces< vector<double> >();

    puInfoSrc_      = iConfig.getParameter<edm::InputTag>("puInfoSrc");
    puWeights_      = iConfig.getParameter<std::vector<double> >("pileupWeights");
    if( iConfig.existsAs<edm::InputTag>("ptWeightSrc") ) {
        ptWeightSrc_ = iConfig.getParameter<edm::InputTag> ("ptWeightSrc");
    } 
}


WeightsCollector::~WeightsCollector()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
    void
WeightsCollector::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    std::auto_ptr<vector<double> > pWeights( new vector<double> );

        // pileup
    int nPileUp = -1;
    
    //  __      __    _      _   _      
    //  \ \    / /___(_)__ _| |_| |_ ___
    //   \ \/\/ // -_) / _` | ' \  _(_-<
    //    \_/\_/ \___|_\__, |_||_\__/__/
    //                 |___/   
         
    if ( !iEvent.isRealData() ) {
        // pileup weights
        Handle<std::vector<PileupSummaryInfo> > puInfo;
        iEvent.getByLabel(puInfoSrc_, puInfo);

        std::vector<PileupSummaryInfo>::const_iterator puIt;
        // search for in-time pu and to the weight
        for(puIt = puInfo->begin(); puIt != puInfo->end(); ++puIt)
            // in time pu
            if ( puIt->getBunchCrossing() == 0 ) 
                break;


        if ( puIt == puInfo->end() ) 
            THROW_RUNTIME("-- Event " << iEvent.id().event() << " didn't find the in time pileup info");

        nPileUp = puIt->getPU_NumInteractions();

        double puWeight = 1.;
        if ( nPileUp < 0 )
            THROW_RUNTIME(" nPU = " << nPileUp << " what's going on?!?");
        if ( nPileUp > (int)puWeights_.size() )
//             THROW_RUNTIME("Simulated Pu [" << nPileUp <<"] larger than available puFactors [" << puWeights_.size()  << "]" );
            puWeight = 0.;
        else
            puWeight = puWeights_[ nPileUp ];

        pWeights->push_back( puWeight );

        // get the ptWeight if required
        if ( !(ptWeightSrc_ == edm::InputTag()) ) {
            edm::Handle<double> ptWeight;
            iEvent.getByLabel(ptWeightSrc_, ptWeight);

//             weight_ *= *ptWeight;
            pWeights->push_back( *ptWeight );
        }
    }

    iEvent.put(pWeights);

}

// ------------ method called once each job just before starting event loop  ------------
void 
WeightsCollector::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
WeightsCollector::endJob() {
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
WeightsCollector::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(WeightsCollector);
