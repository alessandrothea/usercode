// -*- C++ -*-
//
// Package:    DileptonSelector
// Class:      DileptonSelector
// 
/**

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Thu Apr 14 12:29:55 CEST 2011
// $Id$
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
#include <HWWAnalysis/DataFormats/interface/HWWEvent.h>
#include <HWWAnalysis/DileptonSelector/interface/HWWCandidates.h>
#include <HWWAnalysis/DileptonSelector/interface/EventProxy.h>
#include <TTree.h>
#include <TH1F.h>
#include <bitset>
#include <fstream>

//
// class declaration
//

class DileptonSelector : public edm::EDAnalyzer {
   public:
      explicit DileptonSelector(const edm::ParameterSet&);
      ~DileptonSelector();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

    // container for the working point cuts
      struct WorkingPoint {
          char partition;
          int efficiency;
          float See;
          float dPhi;
          float dEta;
          float HoE;
//           float tkIso;
//           float ecalIso;
//           float hcalIso;
          float combIso;
          int   missHits;
          float dist;
          float cot;
          void print();
      };


      enum WpPartition {
          kBarrel,
          kEndcap
      };

      enum LlBins {
          kLLBinAll,
          kLLBinHLT,
          kLLBinVertex,
          kLLBinDilepton,
          kLLBinEtaPt,
          kLLBinId,
          kLLBinIso,
          kLLBinNoConv,
          kLLBinIp,
          kLLBinExtraLep,
          kLLBinLast
      };

      std::ostream& Debug(int level); 
    
      virtual EventProxy* getEvent() { return _eventProxy; }

      WorkingPoint getWorkingPoint(unsigned short part, int eff);
      virtual void readWorkingPoints( const std::string& path );
      virtual void loadWorkingPoints( const std::vector<edm::ParameterSet>& points );      
      void makeElectronHistograms( TFileDirectory* fd, std::vector<TH1F*>& histograms );
      TH1F* makeLabelHistogram( TFileDirectory* fd, const std::string& name, const std::string& title, std::map<int,std::string> labels);
      virtual void book();
      virtual bool matchDataHLT();
      virtual bool hasGoodVertex();
      virtual void electronIsoId( LepCandidate::elBitSet& tags, int idx, int eff );
      virtual void tagElectrons();
      virtual void tagMuons();
      virtual void countPairs();
      virtual void fillCounts( TH1F* h, const std::vector<unsigned int>& counts);
      virtual void fillCtrlHistograms();
      virtual void findSoftMus();
      virtual void cleanJets();
      virtual void clear();
      virtual bool selectAndClean();
      virtual void assembleNtuple();
      virtual bool checkExtraLeptons();

      
      // ----------new stuff -----------------------------
      std::vector<double> _puFactors;
      double _eventWeight;

      enum ElCuts { 
          kElEta,
          kElPt,
          kElD0,
          kElDz,
          kElSee,
          kElDeta,
          kElDphi,
          kElCombIso,
          kElCutsSize
      };

      TH1F* _puNInteractionsUnweighted;
      TH1F* _puNInteractions;
      TH1F* _puNVertexes;
      void checkPileUp( const edm::Event& iEvent );

      std::vector<TH1F*> _electronHistograms;
      std::vector<TH1F*> _muonHistograms;
      
      // ----------member data ---------------------------
      static const float _etaMaxEB;
      static const float _etaMinEE;
      static const float _etaMaxEE;
      static const float _etaMaxMu;
      
      int _debugLvl; 
      std::vector< WorkingPoint > _elWorkingPoints;

      std::string _wpFile;

      // vrtx
      float _vrtxCut_nDof;
      float _vrtxCut_rho;
      float _vrtxCut_z;

        // lep common
      float _lepCut_leadingPt;
      float _lepCut_trailingPt;
      float _lepCut_D0PV;
      float _lepCut_DzPV;

      int   _elCut_TightWorkingPoint;
      int   _elCut_LooseWorkingPoint;
      float _elCut_EtaSCEbEe;

      int   _muCut_NMuHist;
      int   _muCut_NMuMatches;
      int   _muCut_NTrackerHits;
      int   _muCut_NPixelHits;
      int   _muCut_NChi2;
      float _muCut_relPtRes;
      float _muCut_combIsoOverPt;

      float _muSoftCut_Pt;
      float _muSoftCut_HighPt;
      float _muSoftCut_NotIso;

      float _jetCut_Pt;
      float _jetCut_Dr;
      float _jetCut_Eta;
      float _jetCut_BtagProb;

      double _nEvents;
      double _nSelectedEvents;

      TTree* _tree;
      HWWEvent* _diLepEvent;
      EventProxy* _eventProxy;

      TH1F*     _hEntries;

      TH1F* _llCounters;
      TH1F* _eeCounters;
      TH1F* _emCounters;
      TH1F* _meCounters;
      TH1F* _mmCounters;

      TH1F* _elTightCtrl;
      TH1F* _elLooseCtrl;
      TH1F* _muGoodCtrl;
      TH1F* _muExtraCtrl;

      std::vector<ElCandicate> _elTagged;
      std::vector<MuCandidate> _muTagged;

      std::vector<LepPair>     _selectedPairs;

      std::set< unsigned int > _selectedEls;
      std::set< unsigned int > _selectedMus;

      std::set< unsigned int > _softMus;
      std::set< unsigned int > _selectedJets;
      std::set< unsigned int > _selectedPFJets;
      std::set< unsigned int > _btaggedJets;

//       std::ofstream _debugFile;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//


