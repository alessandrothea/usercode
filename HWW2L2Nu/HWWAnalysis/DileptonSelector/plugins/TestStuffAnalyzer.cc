// -*- C++ -*-
//
// Package:    TestStuffAnalyzer
// Class:      TestStuffAnalyzer
// 
/**\class TestStuffAnalyzer TestStuffAnalyzer.cc HWWAnalysis/TestStuffAnalyzer/src/TestStuffAnalyzer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Fri Jun 24 12:10:56 CEST 2011
// $Id: TestStuffAnalyzer.cc,v 1.1 2011/06/29 22:16:06 thea Exp $
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
#include "HWWAnalysis/DataFormats/interface/DileptonView.h"


#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"

#include "HWWAnalysis/DataFormats/interface/EventView.h"

//
// class declaration
//

class TestStuffAnalyzer : public edm::EDAnalyzer {
   public:
      explicit TestStuffAnalyzer(const edm::ParameterSet&);
      ~TestStuffAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      // ----------member data ---------------------------

      edm::InputTag electronSrc_;
      edm::InputTag muonSrc_;
      edm::InputTag jetsSrc_;
      edm::InputTag cleanJetsSrc_;
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
TestStuffAnalyzer::TestStuffAnalyzer(const edm::ParameterSet& iConfig)

{
   //now do what ever initialization is needed

    electronSrc_  = iConfig.getParameter<edm::InputTag>("electronSrc");
    muonSrc_      = iConfig.getParameter<edm::InputTag>("muonSrc");
    jetsSrc_      = iConfig.getParameter<edm::InputTag>("jetSrc");
    cleanJetsSrc_ = iConfig.getParameter<edm::InputTag>("cleanJetSrc");
    viewSrc_      = iConfig.getParameter<edm::InputTag>("viewSrc");
}


TestStuffAnalyzer::~TestStuffAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
    void
TestStuffAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    using namespace std;

    edm::Handle<edm::View<reco::RecoCandidate> > electrons;
    iEvent.getByLabel(electronSrc_,electrons);

    edm::Handle<edm::View<reco::RecoCandidate> > muons;
    iEvent.getByLabel(muonSrc_,muons);

    edm::Handle<edm::View<pat::Jet> > jets;
    iEvent.getByLabel(jetsSrc_,jets);

    edm::Handle<edm::View<pat::Jet> > cleanJets;
    iEvent.getByLabel(cleanJetsSrc_,cleanJets);

    edm::Handle<edm::View<hww::EventView> > eventViews;
    iEvent.getByLabel(viewSrc_,eventViews);

//     if ( eventViews->size() < 2 ) return;
    cout << "--" << iEvent.id().event() << "---" << endl;
    cout << " Views : " << eventViews->size() << endl;
    for ( uint i(0); i < eventViews->size(); ++i) {
        const hww::EventView &v = eventViews->at(i);
        cout << setw(7) << i << " ptSum: " << v.pair()->ptSum() << '\n'
        << setw(7) << "tcmet: " << setw(10) << v.met(hww::EventView::kTcMET) 
        << setw(7) << "  pfmet: " << setw(10) << v.met(hww::EventView::kPfMET)
        << setw(7) << "  chmet: " << setw(10) << v.met(hww::EventView::kChargedMET)
        << setw(7) << "  chmetsmurf: " << setw(10) << v.met(hww::EventView::kChargedMETSmurf) << endl;
        uint c1(15), c2(15);
        cout << setw(c1) << "nLep:"        << setw(c2) << v.pair()->nLeptons()
             << setw(c1) << "nEl:"         << setw(c2) << v.pair()->nElectrons() 
             << setw(c1) << "nMu:"         << setw(c2) << v.pair()->nMuons() 
             << setw(c1) << "nSoft:"       << setw(c2) << v.nSoftMuons() << endl;    
        cout << setw(c1) << "nJets:"       << setw(c2) << v.nJets() 
             << setw(c1) << "nJets(15):"   << setw(c2) << v.nJets(15.)
             << setw(c1) << "nJets(30):"   << setw(c2) << v.nJets(30.)
             << setw(c1) << "nJets(30,5):" << setw(c2) << v.nJets(30., 5.)
            << endl;
        cout << setw(c1) << "nBjets^(2.1):" << setw(c2) << v.nBJetsAbove("trackCountingHighEffBJetTags",2.1)
             << setw(c1) << "nBJetsv(2.1):" << setw(c2) << v.nBJetsBelow("trackCountingHighEffBJetTags",2.1)
             << endl;
        cout << setw(c1) << "mtA(pf)" << setw(c2) << v.mtl(0,hww::EventView::kPfMET) << setw(c1) << "mtB(pf)" << setw(c2) << v.mtl(1,hww::EventView::kPfMET)
            << setw(c1) << "mtll(pf)" << setw(c2) << v.mtll(hww::EventView::kPfMET) << setw(c1) << "mt2(pf)" << setw(c2) << v.mt2(hww::EventView::kPfMET) << endl;
        cout << setw(c1) << "mtA(chS)" << setw(c2) << v.mtl(1,hww::EventView::kChargedMETSmurf) << setw(c1) << "mtB(chS)" << setw(c2) << v.mtl(1,hww::EventView::kChargedMETSmurf)
            << setw(c1) << "mtll(chS)" << setw(c2) << v.mtll(hww::EventView::kChargedMETSmurf) << setw(c1) << "mt2(chS)" << setw(c2) << v.mt2(hww::EventView::kChargedMETSmurf) << endl;
    }




//     cout << "Els :" << electrons->size() << " Mus :" << muons->size() << " jets :" << jets->size() << " cleanJets : " << cleanJets->size() << endl;

//     cout << "  muons:" << muonSrc_ << endl;
//     for( uint i(0); i<muons->size(); ++i) {
//         cout << "pt: " << muons->at(i).pt() << " eta: " << muons->at(i).eta() << " phi: " << muons->at(i).phi() << endl;
//     }

//     cout << "  electrons:" << electronSrc_ << endl;
//     for( uint i(0); i<electrons->size(); ++i) {
//         cout << "pt: " << electrons->at(i).pt() << " eta: " << electrons->at(i).eta() << " phi: " << electrons->at(i).phi() << endl;
//     }

//     cout << "  jets:" << jetsSrc_ << endl;
//     for( uint i(0); i<jets->size(); ++i) {
//         cout << "pt: " << jets->at(i).pt() << " eta: " << jets->at(i).eta() << " phi: " << jets->at(i).phi() << endl;
//     }

//     cout << "  cleanJets:" << cleanJetsSrc_ << endl;
//     for( uint i(0); i<cleanJets->size(); ++i) {
//         cout << "pt: " << cleanJets->at(i).pt() << " eta: " << cleanJets->at(i).eta() << " phi: " << cleanJets->at(i).phi() << endl;
//     }
//     StringCutObjectSelector<hww::DileptonView> signCut("oppositeSign()");

//     vector<edm::Ptr<reco::RecoCandidate> > allLeps;
//     for( uint i(0); i<electrons->size(); ++i) 
//         allLeps.push_back(electrons->ptrAt(i));

//     for( uint i(0); i<muons->size(); ++i)
//         allLeps.push_back(muons->ptrAt(i));

//     std::vector<hww::DileptonView> pairs;
//     for( uint i(0); i<allLeps.size(); ++i)
//         for( uint j(i+1); j<allLeps.size(); ++j) {
//             hww::DileptonView p( allLeps[i], allLeps[j]);
//             cout << "opposite: " << p.oppositeSign() << " chSum : " << p.chargeSum() << " leading : " << p.leading()->pt() << " trailing: " << p.trailing()->pt() << endl;
//             if (p.sameSign() ) return;
//             if ( signCut(p) ) {
//                 cout << " is opposite!!!" << endl;
//                 pairs.push_back(p);
//             }
//         }

//     cout << (pairs.size() ? "selected " : "rejected") << endl;

}


// ------------ method called once each job just before starting event loop  ------------
void 
TestStuffAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
TestStuffAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
TestStuffAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
TestStuffAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
TestStuffAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
TestStuffAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
TestStuffAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TestStuffAnalyzer);
