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
// $Id: WeightsCollector.cc,v 1.1 2011/07/03 17:04:49 thea Exp $
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
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/Candidate/interface/Candidate.h"
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
        bool doMap_;
        bool doPu_;
        bool doPt_; 

        edm::InputTag candidateSrc_;
        edm::InputTag puInfoSrc_;
        std::vector<double> puWeights_;
        edm::InputTag ptWeightSrc_;
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
WeightsCollector::WeightsCollector(const edm::ParameterSet& iConfig) :
    doMap_( iConfig.existsAs<edm::InputTag>("src") ),
    doPu_( iConfig.existsAs<edm::InputTag>("puInfoSrc") ),
    doPt_( iConfig.existsAs<edm::InputTag>("ptWeightSrc") ),

    candidateSrc_(  doMap_ ? iConfig.getParameter<edm::InputTag>("src")       : edm::InputTag()),
    puInfoSrc_(     doPu_  ? iConfig.getParameter<edm::InputTag>("puInfoSrc") : edm::InputTag()),
    puWeights_(     doPu_  ? iConfig.getParameter<std::vector<double> >("pileupWeights") : std::vector<double>() ),
    ptWeightSrc_(   doPt_  ? iConfig.getParameter<edm::InputTag>("ptWeightSrc_") : edm::InputTag()) {
    
    //register your products
    produces< vector<double> >();
    if ( doMap_ ) {
        produces< edm::ValueMap<float> >();
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
    double weight = 1.;
    
    //  __      __    _      _   _      
    //  \ \    / /___(_)__ _| |_| |_ ___
    //   \ \/\/ // -_) / _` | ' \  _(_-<
    //    \_/\_/ \___|_\__, |_||_\__/__/
    //                 |___/   
         
    if ( !iEvent.isRealData() ) {
        // pileup weights
        if ( doPu_ ) {
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
                puWeight = 0.;
            else
                puWeight = puWeights_[ nPileUp ];

            pWeights->push_back( puWeight );
            weight *= puWeight;
        }

        // get the ptWeight if required
        if ( doPt_ ) {
            edm::Handle<double> ptWeight;
            iEvent.getByLabel(ptWeightSrc_, ptWeight);

            pWeights->push_back( *ptWeight );
            weight *= *ptWeight;
        }
    }

    iEvent.put(pWeights);
    
    if ( doMap_ ) {
        edm::Handle<edm::View<reco::Candidate> > cands;
        iEvent.getByLabel(candidateSrc_ ,cands);
        std::auto_ptr<edm::ValueMap<float> > floatMap(new edm::ValueMap<float>);
        std::vector<float> floatVec(cands->size(),weight);
        edm::ValueMap<float>::Filler filler(*floatMap);
        filler.insert(cands, floatVec.begin(), floatVec.end());
        filler.fill();
        iEvent.put(floatMap);

    }

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
