// -*- C++ -*-
//
// Package:    HWWTreeProducer
// Class:      HWWTreeProducer
// 
/**\class HWWTreeProducer HWWTreeProducer.cc HWWAnalysis/HWWTreeProducer/src/HWWTreeProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Fri Jun 24 12:10:37 CEST 2011
// $Id: HWWTreeProducer.cc,v 1.2 2011/06/30 14:25:57 thea Exp $
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

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include <DataFormats/METReco/interface/MET.h>
#include <DataFormats/METReco/interface/PFMET.h>

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"

#include <SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h>
#include "PhysicsTools/SelectorUtils/interface/strbitset.h"

#include "HWWAnalysis/DataFormats/interface/HWWEvent.h"
#include <TTree.h>
#include "HWWAnalysis/Misc/interface/Tools.h"
#include "HWWAnalysis/Misc/interface/RootUtils.h"
//
// class declaration
//

class HWWTreeProducer : public edm::EDAnalyzer {
    public:
        explicit HWWTreeProducer(const edm::ParameterSet&);
        ~HWWTreeProducer();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


    private:
        virtual void beginJob() ;
        virtual void analyze(const edm::Event&, const edm::EventSetup&);
        virtual void endJob() ;

        virtual void book();
        virtual void clear();

        virtual void beginRun(edm::Run const&, edm::EventSetup const&);
        virtual void endRun(edm::Run const&, edm::EventSetup const&);
        virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
        virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

        // ----------member data ---------------------------

        edm::InputTag weightSrc_;
        edm::InputTag hltSummarySrc_;
        edm::InputTag puInfoSrc_;

        edm::InputTag electronSrc_;
        edm::InputTag muonSrc_;
        edm::InputTag jetSrc_;
        edm::InputTag softMuonSrc_;

        edm::InputTag pfMetSrc_;
        edm::InputTag tcMetSrc_;
        edm::InputTag chargedMetSrc_;
        edm::InputTag vertexSrc_;
        edm::InputTag chCandSrc_;

        edm::InputTag sptSrc_;
        edm::InputTag spt2Src_;

        edm::InputTag ptWeightSrc_;

        std::vector<double> puWeights_;

        std::vector<std::string> bTaggers_;
        std::vector<std::string> hltPaths_;

        std::string treeName_;
        TTree*      tree_;
        HWWEvent*   event_;
        TH1D*       scalars_;
        StringCutObjectSelector<pat::Jet> jetSelector_;
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
HWWTreeProducer::HWWTreeProducer(const edm::ParameterSet& iConfig)
: tree_(0x0), event_(0x0), jetSelector_(iConfig.getParameter<std::string>("jetCut"))
{
    //now do what ever initialization is needed
    
    treeName_       = iConfig.getParameter<std::string>("treeName");

    weightSrc_      = iConfig.getParameter<edm::InputTag>("weightSrc");
    hltSummarySrc_  = iConfig.getParameter<edm::InputTag>("hltSummarySrc");
    puInfoSrc_      = iConfig.getParameter<edm::InputTag>("puInfoSrc");

    electronSrc_	= iConfig.getParameter<edm::InputTag>("electronSrc");
    muonSrc_	    = iConfig.getParameter<edm::InputTag>("muonSrc");
    jetSrc_	        = iConfig.getParameter<edm::InputTag>("jetSrc");
    softMuonSrc_	= iConfig.getParameter<edm::InputTag>("softMuonSrc");

    pfMetSrc_	    = iConfig.getParameter<edm::InputTag>("pfMetSrc");
    tcMetSrc_	    = iConfig.getParameter<edm::InputTag>("tcMetSrc");
    chargedMetSrc_	= iConfig.getParameter<edm::InputTag>("chargedMetSrc");
    vertexSrc_	    = iConfig.getParameter<edm::InputTag>("vertexSrc");
    chCandSrc_	    = iConfig.getParameter<edm::InputTag>("chCandSrc");
    
    sptSrc_	        = iConfig.getParameter<edm::InputTag>("sptSrc");
    spt2Src_	    = iConfig.getParameter<edm::InputTag>("spt2Src");

//     puWeights_      = iConfig.getParameter<std::vector<double> >("pileupWeights");

    bTaggers_       = iConfig.getParameter<std::vector<std::string> >("jetBTaggers");
    hltPaths_       = iConfig.getParameter<std::vector<std::string> >("hltPaths");
    

//     if( iConfig.existsAs<edm::InputTag>("ptWeightSrc") ) {
//         ptWeightSrc_ = iConfig.getParameter<edm::InputTag> ("ptWeightSrc");
//     } 
}


HWWTreeProducer::~HWWTreeProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

using namespace std;

// ------------ method called for each event  ------------
void
HWWTreeProducer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    clear();

    Handle<std::vector<double> > weights;
    iEvent.getByLabel(weightSrc_, weights);

    Handle<std::vector<reco::Vertex> > vertexes;
    iEvent.getByLabel(vertexSrc_, vertexes);

    Handle<pat::strbitset> hltBits;
    iEvent.getByLabel(hltSummarySrc_,hltBits);

    // leptons: maybe here I can use directly a pat::ElectronCollection and a pat::MuonCollection
    edm::Handle<edm::View<reco::RecoCandidate> > electrons;
    iEvent.getByLabel(electronSrc_,electrons);

    edm::Handle<edm::View<reco::RecoCandidate> > muons;
    iEvent.getByLabel(muonSrc_,muons);

    // jets
    Handle<pat::JetCollection> jets;
    iEvent.getByLabel(jetSrc_, jets);

    Handle<edm::View<pat::Muon> > softMuons;
    iEvent.getByLabel(softMuonSrc_, softMuons);

    // Met
    Handle<std::vector<reco::MET> > tcMet;
    iEvent.getByLabel(tcMetSrc_, tcMet);

    Handle<std::vector<reco::PFMET> > pfMet;
    iEvent.getByLabel(pfMetSrc_, pfMet);

    Handle<edm::ValueMap<reco::PFMET> > chargedMet;
    iEvent.getByLabel(chargedMetSrc_, chargedMet);
    
    // reduced charged pf candidates
    edm::Handle<reco::CandidateCollection> reducedPfCandidates;
    iEvent.getByLabel(chCandSrc_,reducedPfCandidates);
    

    //  __      __    _      _   _      
    //  \ \    / /___(_)__ _| |_| |_ ___
    //   \ \/\/ // -_) / _` | ' \  _(_-<
    //    \_/\_/ \___|_\__, |_||_\__/__/
    //                 |___/   
   
    double weight = 1.;
    vector<double>::const_iterator iW;
    for( iW = weights->begin(); iW != weights->end(); ++iW ) {
        weight *= *iW;    
    } 


    // pileup info, get them only if the event is MC
    int nPileUp = -1;
    
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

        if ( nPileUp < 0 )
            THROW_RUNTIME(" nPU = " << nPileUp << " what's going on?!?");
//         if ( nPileUp > (int)puWeights_.size() )
//             THROW_RUNTIME("Simulated Pu [" << nPileUp <<"] larger than available puFactors");

//         weight *= puWeights_[ nPileUp ];

//         // get the ptWeight if required
//         if ( !(ptWeightSrc_ == edm::InputTag()) ) {
//             edm::Handle<double> ptWeightHandle;
//             iEvent.getByLabel(ptWeightSrc_, ptWeightHandle);

//             weight *= *ptWeightHandle;
//         }
    }

    // to do
    // clean soft muons
    // clean jets
    // btagged jets

    if ( !event_ || !tree_ ) return;

    event_->Run          = iEvent.id().run();
	event_->Event        = iEvent.id().event();
	event_->LumiSection  = iEvent.id().luminosityBlock();
	event_->Weight       = weight;

	event_->PrimVtxPosition  = (*vertexes)[0].position();
	event_->PrimVtxx     = (*vertexes)[0].position().x();
	event_->PrimVtxy     = (*vertexes)[0].position().y();
	event_->PrimVtxz     = (*vertexes)[0].position().z();
    event_->NVrtx        = vertexes->size();
    event_->NPileUp      = nPileUp;
    

    event_->TCMet = (*tcMet)[0].p4();
    event_->PFMet = (*pfMet)[0].p4();
    event_->ChargedMet = chargedMet->get(0).p4();

    event_->NSoftMus         = softMuons->size();

    event_->NBTaggedJets     = -1;

	event_->NEles            = electrons->size();
	event_->NMus             = muons->size();


    event_->HltPaths.resize( hltPaths_.size() );
    for( uint k(0); k<hltPaths_.size(); ++k) 
        event_->HltPaths[k] = hltBits->test(hltPaths_[k]);

    // fill electrons
	event_->Els.resize(event_->NEles);
	for( int i(0); i < event_->NEles ; ++i) {
        HWWElectron &hwwEl = event_->Els[i];
        
        const pat::Electron& patEl = dynamic_cast<const pat::Electron&>(electrons->at(i));

        hwwEl.P                         = patEl.p4();
        hwwEl.Charge                    = patEl.charge();
        hwwEl.PdgId                     = patEl.pdgId();

        hwwEl.SigmaIetaIeta		        = patEl.sigmaIetaIeta();
        hwwEl.CaloEnergy 			    = patEl.caloEnergy();
        hwwEl.DR03TkSumPt 				= patEl.dr03TkSumPt();
        hwwEl.DR03EcalRecHitSumEt		= patEl.dr03EcalRecHitSumEt();
        hwwEl.DR03HcalTowerSumEt 		= patEl.dr03HcalTowerSumEt();
        hwwEl.DR04EcalRecHitSumEt		= patEl.dr04EcalRecHitSumEt();
        hwwEl.DR04HcalTowerSumEt 		= patEl.dr04HcalTowerSumEt();
        hwwEl.NumberOfMissingInnerHits 	= patEl.gsfTrack()->trackerExpectedHitsInner().numberOfHits();
        hwwEl.DeltaPhiSuperClusterAtVtx	= patEl.deltaPhiSuperClusterTrackAtVtx();
        hwwEl.DeltaEtaSuperClusterAtVtx	= patEl.deltaEtaSuperClusterTrackAtVtx();
        hwwEl.D0PV 						= patEl.userFloat("dxyPV");
        hwwEl.DzPV 						= patEl.userFloat("dzPV");

	}

    // fill muons
    event_->Mus.resize(event_->NMus);
    for( int i(0); i < event_->NMus; ++i ) {
        HWWMuon &hwwMu = event_->Mus[i];
        const pat::Muon& patMu = dynamic_cast<const pat::Muon&>(muons->at(i));

        hwwMu.P                         = patMu.p4();
        hwwMu.Charge                    = patMu.charge();
        hwwMu.PdgId                     = patMu.pdgId();

        hwwMu.Iso03SumPt                = patMu.isolationR03().sumPt;
        hwwMu.Iso03EmEt                 = patMu.isolationR03().emEt;
        hwwMu.Iso03HadEt                = patMu.isolationR03().hadEt;
        hwwMu.NMuHits                   = patMu.isGlobalMuon() ? patMu.globalTrack()->hitPattern().numberOfValidMuonHits() : 0.;
        hwwMu.NTkHits                   = patMu.innerTrack()->found();
        hwwMu.NChi2                     = patMu.isGlobalMuon() ? patMu.globalTrack()->normalizedChi2() : 1000.;

        hwwMu.IsGlobalMuon              = patMu.isGlobalMuon();
        hwwMu.IsTrackerMuon             = patMu.isTrackerMuon();
        hwwMu.IsTMLastStationAngTight   = patMu.muonID("TMLastStationTight");
        hwwMu.D0PV 						= patMu.userFloat("dxyPV");
        hwwMu.DzPV 						= patMu.userFloat("dzPV");
    }

    // prefilter jets;
    // fill jets (already cleaned
//     event_->PFJets.resize(event_->PFNJets);
//     for( int i(0); i < event_->PFNJets; ++i) {
    event_->PFJets.reserve(jets->size());
    event_->JetBtags.resize(jets->size());
    for( uint i(0); i < jets->size(); ++i) {
    
        const pat::Jet& patJet = jets->at(i);

        HWWSlimBTags& btags = event_->JetBtags[i] ;
        btags.pt = patJet.pt();
        btags.values.resize( bTaggers_.size() );

        for ( uint k = 0; k<bTaggers_.size(); ++k )
            btags.values[k] = patJet.bDiscriminator(bTaggers_[k]);
        
		HWWPFJet pfj;
        if (!jetSelector_(patJet)) continue;

        pfj.P               = patJet.p4();
        pfj.ChHadfrac       = patJet.chargedHadronEnergyFraction();
		pfj.NeuHadfrac      = patJet.neutralHadronEnergyFraction();
		pfj.ChEmfrac        = patJet.chargedEmEnergyFraction();
		pfj.NeuEmfrac       = patJet.neutralEmEnergyFraction();
		pfj.NConstituents   = patJet.numberOfDaughters();
        pfj.BTagProbTkCntHighEff = patJet.bDiscriminator("trackCountingHighEffBJetTags");
        pfj.BTaggers        = btags.values;

        event_->PFJets.push_back(pfj);
	}
    event_->PFNJets = event_->PFJets.size();

    // collction of reduced pd candidates
    reco::CandidateCollection::const_iterator iCand, bC = reducedPfCandidates->begin(), eC = reducedPfCandidates->end();
    for( iCand = bC; iCand != eC; ++iCand )
        event_->ReducedPFMomenta.push_back(iCand->p4());

    tree_->Fill(); 
    scalars_->Fill(0);
    scalars_->Fill(1,weight);

}

void
HWWTreeProducer::book()
{
    edm::Service<TFileService> fs;
    TFileDirectory* here = fs.operator->();
    tree_ = fs->make<TTree>(treeName_.c_str(), treeName_.c_str());
    tree_->Branch("ev","HWWEvent", &event_);

    // store the btagger labels as userinfo
    std::vector<std::string>::const_iterator iBtag, bBt = bTaggers_.begin(), eBt = bTaggers_.end();
    TObjArray* bLabels = new TObjArray;
    bLabels->SetName("BtagLabels");
    for( iBtag = bBt; iBtag != eBt; ++iBtag) {
        bLabels->Add(new TObjString(iBtag->c_str()));
    }
    tree_->GetUserInfo()->Add(bLabels);

    // store the hlt path summary
    vector<std::string>::const_iterator iPath, bP = hltPaths_.begin(), eP = hltPaths_.end();
    TObjArray* hltLabels = new TObjArray;
    hltLabels->SetName("hltPathLabels");
    for( iPath = bP; iPath != eP; ++iPath) {
        hltLabels->Add(new TObjString(iPath->c_str()));
    }
    tree_->GetUserInfo()->Add(hltLabels);


    std::map<int,std::string> scalarLabels;
    scalarLabels[0] = "Selected Entries";
    scalarLabels[1] = "Selected Weighted Entries";
    scalars_ = hww::makeLabelHistogram(here, "scalars","HWW preselection scalars",scalarLabels);
    
//     scalars_ = fs->make<TH1D>("scalars","scalars",2,0,2);
//     scalars_->GetXaxis()->SetBinLabel(1,"selected");
//     scalars_->GetXaxis()->SetBinLabel(2,"selectedWeighted");

}

void
HWWTreeProducer::clear() 
{
   if ( event_ ) event_->Clear();
}

// ------------ method called once each job just before starting event loop  ------------
void 
HWWTreeProducer::beginJob()
{
    book();
}

// ------------ method called once each job just after ending the event loop  ------------
void 
HWWTreeProducer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
HWWTreeProducer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
HWWTreeProducer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
HWWTreeProducer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
HWWTreeProducer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
HWWTreeProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(HWWTreeProducer);
