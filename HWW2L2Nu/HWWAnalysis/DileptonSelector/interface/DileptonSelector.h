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
// $Id: DileptonSelector.h,v 1.7 2011/05/21 18:07:04 thea Exp $
//
//
// system include files

#ifndef HWWAnalysisDileptonSelector_DileptonSelector_h
#define HWWAnalysisDileptonSelector_DileptonSelector_h

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
#include <TH1D.h>
#include <bitset>
#include <fstream>


class HltObjMatcher;

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
        struct VBTFWorkingPoint {
            char partition;
            int efficiency;
            float See;
            float dPhi;
            float dEta;
            float HoE;
            float combIso;
            int   missHits;
            float dist;
            float cot;
            void print();
        };

        struct LHWorkingPoint {
            char  partition;
            int   efficiency;
            float lh0brem; 
            float lh1brem; 
            float combIso;
            int   missHits;
            float dist;
            float cot;
            void  print();
        };


        enum WpPartition {
            kBarrel,
            kEndcap
        };

        enum LlBins {
            kLLBinAll,
            //           kLLBinVertex,
            kLLBinDilepton,
            kLLBinEtaPt,
            kLLBinId,
            kLLBinIso,
            kLLBinNoConv,
            kLLBinIp,
            kLLBinExtraLep,
            kLLBinHltBits,
            kLLBinHltObject,
            kLLBinLast
        };

        std::ostream& Debug(int level); 

        virtual EventProxy* getEvent() { return _eventProxy; }

        VBTFWorkingPoint getVBTFWorkingPoint(unsigned short part, int eff);
        LHWorkingPoint getLHWorkingPoint(unsigned short part, int eff);
        virtual void loadVBFTId( const std::vector<edm::ParameterSet>& points );      
        virtual void loadLikelihoodId( const std::vector<edm::ParameterSet>& points );      
        void makeElectronHistograms( TFileDirectory* fd, std::vector<TH1D*>& histograms );
        TH1D* makeLabelHistogram( TFileDirectory* fd, const std::string& name, const std::string& title, std::map<int,std::string> labels);
        virtual void book();
        virtual bool matchHlt();
        //       virtual bool hasGoodVertex();
        virtual void electronIsoId( ElCandicate&, LepCandidate::elBitSet& tags, int eff );
        virtual void tagElectrons();
        virtual void tagMuons();
        virtual void countPairs();
        virtual void fillCounts( TH1D* h, const std::vector<unsigned int>& counts);
        virtual void fillCtrlHistograms();
        virtual void findSoftMus();
        virtual void cleanJets();
        virtual void clear();
        virtual bool selectAndClean();
        virtual void assembleEvent();
        virtual bool checkExtraLeptons();


        // ----------new stuff -----------------------------
        std::vector<double> _puFactors;
        double _eventWeight;
        unsigned int _nPileUp;

        enum ElCuts { 
            kElBinEta,
            kElBinPt,
            kElBinIp3D,
            kElBinSee,
            kElBinDeta,
            kElBinDphi,
            kElBinCombIso,
            kElBinSize
        };

        TH1D* _puNInteractionsUnweighted;
        TH1D* _puNInteractions;
        TH1D* _puNVertexes;
        void calculateWeight( const edm::Event& iEvent );
        bool jetLooseId( const pat::Jet& jet );
        double weight() { return _eventWeight; }

        std::vector<TH1D*> _electronHistograms;
        std::vector<TH1D*> _muonHistograms;
        TH1D* _jetBTagProbTkCntHighEff;

        HltObjMatcher* _hltMatcher;

        //-----------tags & containers----------------------
        edm::InputTag _ptWeightSrc;

        edm::InputTag _puInfoSrc;
        edm::InputTag _vertexSrc;
        edm::InputTag _electronSrc;
        edm::InputTag _muonSrc;
        edm::InputTag _jetSrc;
        edm::InputTag _tcMetSrc;
        edm::InputTag _pfMetSrc;
        edm::InputTag _chMetSrc;

        
        // not used so far
        edm::Handle<std::vector<PileupSummaryInfo> >    _puInfo;
        edm::Handle<std::vector<reco::Vertex> >         _vertexes;
        edm::Handle<std::vector<pat::Electron> >        _electrons;
        edm::Handle<std::vector<pat::Muon> >            _muons;
        edm::Handle<std::vector<pat::Jet> >             _jets;
        edm::Handle<std::vector<reco::MET> >            _tcMet;
        edm::Handle<std::vector<reco::PFMET> >          _pfMet;
        edm::Handle<edm::ValueMap<reco::PFMET> >        _chargedMet;

        // ----------member data ---------------------------
        static const double _etaMaxTrk;
        static const double _etaMaxEB;
        static const double _etaMinEE;
        static const double _etaMaxEE;
        static const double _etaMaxMu;

        int _debugLvl; 
        std::vector< VBTFWorkingPoint > _elVBTFWorkingPoints;
        std::vector< LHWorkingPoint > _elLHWorkingPoints;

        //       std::string _wpFile;

        // vrtx
        double _vrtxCut_nDof;
        double _vrtxCut_rho;
        double _vrtxCut_z;

        // lep common
        double _lepCut_extraPt;

        int    _elCut_TightWorkingPoint;
        int    _elCut_LooseWorkingPoint;

        double _elCut_leadingPt;
        double _elCut_trailingPt;
        double _elCut_ip3D;

        double _muCut_leadingPt;
        double _muCut_trailingPt;
        double _muCut_ip2D;
        double _muCut_dZPrimaryVertex;
        int    _muCut_NMuHits;
        int    _muCut_NMuMatches;
        int    _muCut_NTrackerHits;
        int    _muCut_NPixelHits;
        int    _muCut_NChi2;
        double _muCut_relPtRes;
        double _muCut_combIsoOverPt;

        double _muSoftCut_Pt;
        double _muSoftCut_HighPt;
        double _muSoftCut_NotIso;

        double _jetCut_Pt;
        double _jetCut_Dr;
        double _jetCut_Eta;
        double _jetCut_BtagProb;
        double _jetCut_neutralEmFrac;
        double _jetCut_neutralHadFrac;
        int    _jetCut_multiplicity;
        double _jetCut_chargedEmFrac;
        double _jetCut_chargedHadFrac;
        int    _jetCut_chargedMulti;

        double _nEvents;
        double _nSelectedEvents;

        TTree* _tree;
        HWWEvent* _diLepEvent;
        EventProxy* _eventProxy;

        TH1D*     _hEntries;

        TH1D* _llCounters;
        TH1D* _eeCounters;
        TH1D* _emCounters;
        TH1D* _meCounters;
        TH1D* _mmCounters;

        TH1D* _elTightCtrl;
        TH1D* _elLooseCtrl;
        TH1D* _muGoodCtrl;
        TH1D* _muExtraCtrl;

        std::vector<ElCandicate> _elTagged;
        std::vector<MuCandidate> _muTagged;

        std::vector<LepPair>     _selectedPairs;

        std::set< unsigned int > _selectedEls;
        std::set< unsigned int > _selectedMus;

        std::set< unsigned int > _softMus;
        std::set< unsigned int > _selectedPFJets;
        std::set< unsigned int > _btaggedJets;

        std::vector<double>      _btag_combinedSecondaryVertex;
        std::vector<double>      _btag_combinedSecondaryVertexMVA;
        std::vector<double>      _btag_simpleSecondaryVertexHighEff;
        std::vector<double>      _btag_simpleSecondaryVertexHighPur;
        std::vector<double>      _btag_jetBProbability;
        std::vector<double>      _btag_jetProbability;
        std::vector<double>      _btag_trackCountingHighEff;
        std::vector<double>      _btag_trackCountingHighPur;


        //       std::ofstream _debugFile;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//


#endif // HWWAnalysisDileptonSelector_DileptonSelector_h
