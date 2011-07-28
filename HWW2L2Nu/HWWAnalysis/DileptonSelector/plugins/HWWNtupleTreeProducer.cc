// -*- C++ -*-
//
// Package:    HWWNtupleTreeProducer
// Class:      HWWNtupleTreeProducer
// 
/**\class HWWNtupleTreeProducer HWWNtupleTreeProducer.cc HWWAnalysis/HWWNtupleTreeProducer/src/HWWNtupleTreeProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Wed Jul 13 11:03:24 CEST 2011
// $Id: HWWNtupleTreeProducer.cc,v 1.5 2011/07/22 13:41:58 jueugste Exp $
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
#include <TTree.h>
#include <CommonTools/UtilAlgos/interface/TFileService.h>
#include <FWCore/ServiceRegistry/interface/Service.h>

#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"
#include "HWWAnalysis/Misc/interface/RootUtils.h"
      
#include "HWWAnalysis/Misc/interface/Tools.h"
#include "HWWAnalysis/DataFormats/interface/EventView.h"

//
// class declaration
//

class HWWNtupleTreeProducer : public edm::EDAnalyzer {
   public:
      explicit HWWNtupleTreeProducer(const edm::ParameterSet&);
      ~HWWNtupleTreeProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);

      // ----------member data ---------------------------
      std::string treeName_;
      TTree*      tree_;
      HWWNtuple*  ntuple_;
      TH1D*       scalars_;

      edm::InputTag weightSrc_;
      edm::InputTag viewSrc_;
      
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
HWWNtupleTreeProducer::HWWNtupleTreeProducer(const edm::ParameterSet& iConfig)
: tree_(0x0), ntuple_(0x0), scalars_(0x0)
{
    //now do what ever initialization is needed
    treeName_       = iConfig.getParameter<std::string>("treeName");
//     weightSrc_      = iConfig.getParameter<edm::InputTag>("weightSrc");
    viewSrc_        = iConfig.getParameter<edm::InputTag>("viewSrc");

}


HWWNtupleTreeProducer::~HWWNtupleTreeProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
HWWNtupleTreeProducer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    // TODO
    // primary verterx coordinates
    // pileup info
    // trigger info
    using namespace edm;

//     Handle<std::vector<double> > weights;
//     iEvent.getByLabel(weightSrc_, weights);

    edm::Handle<edm::View<hww::EventView> > eventViews;
    iEvent.getByLabel(viewSrc_,eventViews);

    if ( eventViews->size() == 0 ) return;
    ntuple_->clear();


    double weight(1.);
//     for( uint i(0); i<weights->size(); ++i)
//         weight *= weights->at(i);

    // use the view with the highest pt sum
    const hww::EventView& v = eventViews->front();
    
    uint idA = TMath::Abs(v.pair()->leading()->pdgId());
    uint idB = TMath::Abs(v.pair()->trailing()->pdgId());

    unsigned short type = 0;
    if( idA == 11 && idB == 11 ) {
        type = HWWNtuple::elel;
    } else if (idA == 11 && idB == 13) {
        type = HWWNtuple::elmu;
    } else if (idA == 13 && idB == 11) {
        type = HWWNtuple::muel;
    } else if (idA == 13 && idB == 13) {
        type = HWWNtuple::mumu;
    } else {
        THROW_RUNTIME("Pair with particle ids " << idA << " " << idB << " not supported");
    }

    ntuple_->run                        = iEvent.id().run();
    ntuple_->lumiSection                = iEvent.id().luminosityBlock();
    ntuple_->event                      = iEvent.id().event();

    ntuple_->weight                     = weight;

    ntuple_->singleMuBit                = v.bit("singleMuDataPaths");               
    ntuple_->doubleMuBit                = v.bit("doubleMuDataPaths");               
    ntuple_->singleElBit                = v.bit("singleElDataPaths");               
    ntuple_->doubleElBit                = v.bit("doubleElDataPaths");               
    ntuple_->muEGBit                    = v.bit("muEGDataPaths");               

    ntuple_->type                       = type;
    ntuple_->nExtra                     = v.pair()->nExtra();

    ntuple_->pA                         = v.pair()->leading()->p4();
    ntuple_->pB                         = v.pair()->trailing()->p4();
    ntuple_->ptA                        = v.pair()->leading()->p4().pt();
    ntuple_->ptB                        = v.pair()->trailing()->p4().pt();

    ntuple_->deltaRll                   = v.pair()->dR();
    ntuple_->dileptonPt                 = v.pair()->p4ll().pt();

    ntuple_->cA                         = v.pair()->leading()->charge();
    ntuple_->cB                         = v.pair()->trailing()->charge();
    ntuple_->mll                        = v.pair()->mll();
    ntuple_->dPhi                       = v.pair()->dPhi();

    ntuple_->pfMet                      = v.pfMet();
    ntuple_->tcMet                      = v.tcMet();
    ntuple_->chargedMet                 = v.chargedMet();
    ntuple_->chargedMetSmurf            = v.chargedMetSmurf();

    ntuple_->pfMetPhi                   = v.phiPfMet();
    ntuple_->tcMetPhi                   = v.phiTcMet();
    ntuple_->chargedMetPhi              = v.phiChargedMet();
    ntuple_->chargedMetSmurfPhi         = v.phiChargedMetSmurf();

    ntuple_->tcMetDphi                  = v.dPhiTcMet();
    ntuple_->pfMetDphi                  = v.dPhiPfMet();
    ntuple_->chargedMetDphi             = v.dPhiChargedMet();
    ntuple_->chargedMetSmurfDphi        = v.dPhiChargedMetSmurf();

    ntuple_->projPfMet                  = v.projPfMet();
    ntuple_->projTcMet                  = v.projTcMet();
    ntuple_->projChargedMet             = v.projChargedMet();
    ntuple_->projChargedMetSmurf        = v.projChargedMetSmurf();

    ntuple_->minProjMet                 = TMath::Min(ntuple_->projPfMet, ntuple_->projChargedMetSmurf);

    ntuple_->met                        = ntuple_->pfMet;
    ntuple_->projMet                    = ntuple_->minProjMet;

    ntuple_->mrStar                     = v.pair()->mRstar();
    ntuple_->gammaMRstar                = v.pair()->gammaMRstar();

    ntuple_->mtA                        = v.mtl(0,hww::EventView::kPfMET);
    ntuple_->mtB                        = v.mtl(1,hww::EventView::kPfMET);
    ntuple_->mtll                       = v.mtll(hww::EventView::kPfMET);
    ntuple_->mt2                        = v.mt2(hww::EventView::kPfMET);

    ntuple_->nSoftMus                   = v.nSoftMuons();
    ntuple_->nBJets                     = v.nBJetsAbove("trackCountingHighEffBJetTags",2.1,0.,5.);
    ntuple_->nJets                      = v.nJets(30.,5.);
    ntuple_->nCentralJets               = v.nJets(30.,2.5);

    ntuple_->dPhillj                    = v.dPhiJll(15.,5.);
//     ntuple_->dPhillj0jet                = v.dPhiJll(15.,5.);

    ntuple_->sumPtJetsScalar            = v.jetPtSum(30.,5.);
    ntuple_->sumPtCentralJetsScalar     = v.jetPtSum(30.,2.5);

    ntuple_->sumPtJetsVectorial         = v.jetSumP4(30., 5.).pt();
    ntuple_->sumPtCentralJetsVectorial  = v.jetSumP4(30., 2.5).pt();

    ntuple_->centralityLeptonsVectorial = v.pair()->centrality();
    ntuple_->centralityLeptonsScalar    = v.pair()->centralityScal();

    ntuple_->centralityJetsVectorial    = v.jetCentrality(30.,5.);
    ntuple_->centralityJetsScalar       = v.jetCentralityScal(30.,5.);

    ntuple_->jet1pt                     = ( v.nJets(30.,5.) > 0 ? v.jet(0)->pt(): -99. );
    ntuple_->jet1phi                    = ( v.nJets(30.,5.) > 0 ? v.jet(0)->phi(): -99. );
    ntuple_->jet1eta                    = ( v.nJets(30.,5.) > 0 ? v.jet(0)->eta(): -99. );
    ntuple_->jet1bTagProb               = ( v.nJets(30.,5.) > 0 ? v.jet(0)->bDiscriminator("trackCountingHighEffBJetTags"): -99.) ;
           
    ntuple_->jet2pt                     = ( v.nJets(30.,5.) > 1 ? v.jet(1)->pt(): -99. );
    ntuple_->jet2phi                    = ( v.nJets(30.,5.) > 1 ? v.jet(1)->phi(): -99. );
    ntuple_->jet2eta                    = ( v.nJets(30.,5.) > 1 ? v.jet(1)->eta(): -99. );
    ntuple_->jet2bTagProb               = ( v.nJets(30.,5.) > 1 ? v.jet(1)->bDiscriminator("trackCountingHighEffBJetTags"): -99.) ;
           
    ntuple_->sumJet12bTagProb           = ( v.nJets(30.,5.) > 1 ? v.jet(0)->bDiscriminator("trackCountingHighEffBJetTags")+v.jet(1)->bDiscriminator("trackCountingHighEffBJetTags"): -99.);

    // threshold here?
    std::vector<double> btagProb;
    const std::vector<hww::JetPtr>& jets = v.jets(); 
    if ( jets.size() > 0 ) {
        for( uint i(0); i<jets.size(); ++i) {
            btagProb.push_back(jets[i]->bDiscriminator("trackCountingHighEffBJetTags"));
        }
        ntuple_->maxbtagProb                = *max_element(btagProb.begin(), btagProb.end());
    }


    // quality variables
    
    // first check what type of event it is
    if (type == HWWNtuple::elel) {
        const pat::Electron* elA = dynamic_cast<const pat::Electron*>(v.pair()->leading());
        const pat::Electron* elB = dynamic_cast<const pat::Electron*>(v.pair()->trailing());
        ntuple_->sigmaIetaIetaA = elA->sigmaIetaIeta();
        ntuple_->sigmaIetaIetaB = elB->sigmaIetaIeta();
        ntuple_->deltaEtaSuperClusterAtVtxA = elA->deltaEtaSuperClusterTrackAtVtx();
        ntuple_->deltaEtaSuperClusterAtVtxB = elB->deltaEtaSuperClusterTrackAtVtx();
        ntuple_->deltaPhiSuperClusterAtVtxA = elA->deltaPhiSuperClusterTrackAtVtx();
        ntuple_->deltaPhiSuperClusterAtVtxB = elB->deltaPhiSuperClusterTrackAtVtx();
        ntuple_->caloEnergyA = elA->caloEnergy();
        ntuple_->caloEnergyB = elB->caloEnergy();
        ntuple_->hcalOverEcalA = elA->hcalOverEcal();
        ntuple_->hcalOverEcalB = elB->hcalOverEcal();
        ntuple_->numberOfMissingInnerHitsA = elA->gsfTrack()->trackerExpectedHitsInner().numberOfHits();
        ntuple_->numberOfMissingInnerHitsB = elB->gsfTrack()->trackerExpectedHitsInner().numberOfHits();
        ntuple_->convPartnerTrkDCotA = elA->userFloat("convValueMapProd:dcot");
        ntuple_->convPartnerTrkDCotB = elB->userFloat("convValueMapProd:dcot");
        ntuple_->convPartnerTrkDistA = elA->userFloat("convValueMapProd:dist");
        ntuple_->convPartnerTrkDistB = elB->userFloat("convValueMapProd:dist");
        ntuple_->dr03EcalRecHitSumEtA = elA->dr03EcalRecHitSumEt();
        ntuple_->dr03EcalRecHitSumEtB = elB->dr03EcalRecHitSumEt();
        ntuple_->dr03HcalTowerSumEtA = elA->dr03HcalTowerSumEt();
        ntuple_->dr03HcalTowerSumEtB = elB->dr03HcalTowerSumEt();
        ntuple_->dr03TkSumPtA = elA->dr03TkSumPt();
        ntuple_->dr03TkSumPtB = elB->dr03TkSumPt();
        ntuple_->dR03HcalFullA = elA->userFloat("hcalFull");
        ntuple_->dR03HcalFullB = elB->userFloat("hcalFull");
        ntuple_->pAtVtxA = elA->trackMomentumAtVtx().R();
        ntuple_->pAtVtxB = elB->trackMomentumAtVtx().R();


        ntuple_->dzPVA = elA->userFloat("dzPV");
        ntuple_->dzPVB = elB->userFloat("dzPV");
        ntuple_->d0PVA = elA->userFloat("d0PV");
        ntuple_->d0PVB = elB->userFloat("d0PV");


        }
    else if (type == HWWNtuple::elmu) {
        const pat::Electron* el = dynamic_cast<const pat::Electron*>(v.pair()->leading());
        const pat::Muon* mu = dynamic_cast<const pat::Muon*>(v.pair()->trailing());
        ntuple_->sigmaIetaIetaA = el->sigmaIetaIeta();
        ntuple_->deltaEtaSuperClusterAtVtxA = el->deltaEtaSuperClusterTrackAtVtx();
        ntuple_->deltaPhiSuperClusterAtVtxA = el->deltaPhiSuperClusterTrackAtVtx();
        ntuple_->caloEnergyA = el->caloEnergy();
        ntuple_->hcalOverEcalA = el->hcalOverEcal();
        ntuple_->numberOfMissingInnerHitsA = el->gsfTrack()->trackerExpectedHitsInner().numberOfHits();
        ntuple_->convPartnerTrkDCotA = el->userFloat("convValueMapProd:dcot");
        ntuple_->convPartnerTrkDistA = el->userFloat("convValueMapProd:dist");
        ntuple_->dr03EcalRecHitSumEtA = el->dr03EcalRecHitSumEt();
        ntuple_->dr03HcalTowerSumEtA = el->dr03HcalTowerSumEt();
        ntuple_->dr03TkSumPtA = el->dr03TkSumPt();
        ntuple_->dR03HcalFullA = el->userFloat("hcalFull");




        ntuple_->dzPVA = el->userFloat("dzPV");
        ntuple_->dzPVB = mu->userFloat("dzPV");
        ntuple_->d0PVA = el->userFloat("d0PV");
        ntuple_->d0PVB = mu->userFloat("d0PV");

        ntuple_->nMatchesB = mu->numberOfMatches();
        ntuple_->nChi2B = mu->isGlobalMuon() ? mu->globalTrack()->normalizedChi2() : -99.9;
        ntuple_->nMuHitsB = mu->isGlobalMuon() ? mu->globalTrack()->hitPattern().numberOfValidMuonHits() : 0.;
        ntuple_->nNPxHitsB = mu->innerTrack()->hitPattern().numberOfValidPixelHits();
        ntuple_->nTkHitsB = mu->innerTrack()->found();
        ntuple_->muIso03EmEtB = mu->isolationR03().emEt;
        ntuple_->muIso03HadEtB = mu->isolationR03().hadEt;
        ntuple_->muIso03SumPtB = mu->isolationR03().sumPt;






    }
    else if (type == HWWNtuple::muel) {
        const pat::Muon* mu = dynamic_cast<const pat::Muon*>(v.pair()->leading());
        const pat::Electron* el = dynamic_cast<const pat::Electron*>(v.pair()->trailing());
        ntuple_->sigmaIetaIetaB = el->sigmaIetaIeta();
        ntuple_->deltaEtaSuperClusterAtVtxB = el->deltaEtaSuperClusterTrackAtVtx();
        ntuple_->deltaPhiSuperClusterAtVtxB = el->deltaPhiSuperClusterTrackAtVtx();
        ntuple_->caloEnergyB = el->caloEnergy();
        ntuple_->hcalOverEcalB = el->hcalOverEcal();
        ntuple_->numberOfMissingInnerHitsB = el->gsfTrack()->trackerExpectedHitsInner().numberOfHits();
        ntuple_->convPartnerTrkDCotB = el->userFloat("convValueMapProd:dcot");
        ntuple_->convPartnerTrkDistB = el->userFloat("convValueMapProd:dist");
        ntuple_->dr03EcalRecHitSumEtB = el->dr03EcalRecHitSumEt();
        ntuple_->dr03HcalTowerSumEtB = el->dr03HcalTowerSumEt();
        ntuple_->dr03TkSumPtB = el->dr03TkSumPt();
        ntuple_->dR03HcalFullB = el->userFloat("hcalFull");





        ntuple_->dzPVA = mu->userFloat("dzPV");
        ntuple_->dzPVB = el->userFloat("dzPV");
        ntuple_->d0PVA = mu->userFloat("d0PV");
        ntuple_->d0PVB = el->userFloat("d0PV");

        ntuple_->nMatchesA = mu->numberOfMatches();
        ntuple_->nChi2A = mu->isGlobalMuon() ? mu->globalTrack()->normalizedChi2() : -99.9;
        ntuple_->nMuHitsA = mu->isGlobalMuon() ? mu->globalTrack()->hitPattern().numberOfValidMuonHits() : 0.;
        ntuple_->nNPxHitsA = mu->innerTrack()->hitPattern().numberOfValidPixelHits();
        ntuple_->nTkHitsA = mu->innerTrack()->found();
        ntuple_->muIso03EmEtA = mu->isolationR03().emEt;
        ntuple_->muIso03HadEtA = mu->isolationR03().hadEt;
        ntuple_->muIso03SumPtA = mu->isolationR03().sumPt;





    }

    if (type == HWWNtuple::mumu) {
        const pat::Muon* muA = dynamic_cast<const pat::Muon*>(v.pair()->leading());
        const pat::Muon* muB = dynamic_cast<const pat::Muon*>(v.pair()->trailing());
        ntuple_->nMatchesA = muA->numberOfMatches();
        ntuple_->nMatchesB = muB->numberOfMatches();
        ntuple_->nChi2A = muA->isGlobalMuon() ? muA->globalTrack()->normalizedChi2() : -99.9;
        ntuple_->nChi2B = muB->isGlobalMuon() ? muB->globalTrack()->normalizedChi2() : -99.9;
        ntuple_->nMuHitsA = muA->isGlobalMuon() ? muA->globalTrack()->hitPattern().numberOfValidMuonHits() : 0.;
        ntuple_->nMuHitsB = muB->isGlobalMuon() ? muB->globalTrack()->hitPattern().numberOfValidMuonHits() : 0.;
        ntuple_->nNPxHitsA = muA->innerTrack()->hitPattern().numberOfValidPixelHits();
        ntuple_->nNPxHitsB = muB->innerTrack()->hitPattern().numberOfValidPixelHits();
        ntuple_->nTkHitsA = muA->innerTrack()->found();
        ntuple_->nTkHitsB = muB->innerTrack()->found();
        ntuple_->muIso03EmEtA = muA->isolationR03().emEt;
        ntuple_->muIso03EmEtB = muB->isolationR03().emEt;
        ntuple_->muIso03HadEtA = muA->isolationR03().hadEt;
        ntuple_->muIso03HadEtB = muB->isolationR03().hadEt;
        ntuple_->muIso03SumPtA = muA->isolationR03().sumPt;
        ntuple_->muIso03SumPtB = muB->isolationR03().sumPt;





        ntuple_->dzPVA = muA->userFloat("dzPV");
        ntuple_->dzPVB = muB->userFloat("dzPV");
        ntuple_->d0PVA = muA->userFloat("d0PV");
        ntuple_->d0PVB = muB->userFloat("d0PV");
        

    }

    // common variables
    



    tree_->Fill();

}


// ------------ method called once each job just before starting event loop  ------------
void 
HWWNtupleTreeProducer::beginJob()
{
    edm::Service<TFileService> fs;
    TFileDirectory* here = fs.operator->();
    tree_ = fs->make<TTree>(treeName_.c_str(), treeName_.c_str());
    tree_->Branch("nt","HWWNtuple", &ntuple_);
    std::map<int,std::string> scalarLabels;
    scalarLabels[0] = "Selected Entries";
    scalarLabels[1] = "Selected Weighted Entries";
    scalars_ = hww::makeLabelHistogram(here, "scalars","HWW preselection scalars",scalarLabels);

}

// ------------ method called once each job just after ending the event loop  ------------
void 
HWWNtupleTreeProducer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
HWWNtupleTreeProducer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
HWWNtupleTreeProducer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
HWWNtupleTreeProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(HWWNtupleTreeProducer);
