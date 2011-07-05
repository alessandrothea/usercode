/*
 * HWWAnalyzer.h
 *
 *  Created on: Dec 14, 2010
 *      Author: ale
 */

#ifndef HWWANALYZER_H_
#define HWWANALYZER_H_

#include "HWWAnalysis/CutBasedAnalyzer/interface/UserAnalyzer.h"
#include "HWWAnalysis/DataFormats/interface/HWWEvent.h"
#include <bitset>
#include <set>

class HWWEvent;
class HWWPFJet;
class HWWNtuple;
class TTree;
class TH1D;
class TH2D;
class TParticlePDG;


class HWWAnalyzer : public UserAnalyzer {
public:
	HWWAnalyzer(int argc,char** argv);
	virtual ~HWWAnalyzer();

	virtual Bool_t Notify();
	virtual void Book();
	virtual void BeginJob();
	virtual void Process( Long64_t iEvent );
	virtual void EndJob();

protected:

	struct HiggsCutSet {
		int hMass;
		int ll;
		float minPtHard;
		float minPtSoft;
		float maxMll;
		float maxDphi;
		float minR;
		float maxR;
		void print();
	};

    struct HistogramSet { 
        TH1D* counters;
        TH2D* jetNVsNvrtx;
        std::vector<TH1D*> dileptons;
        std::vector<TH1D*> preCuts;
        std::vector<TH1D*> postCuts;
        std::vector<TH1D*> extra;
        std::vector<TH1D*> nm1Cut;
        std::vector<std::vector<TH1D*> > cutByCut;
    };

    // enumerators
	enum Lep_t {
		kEl_t,
		kMu_t
	};

	enum LL_t {
		kElEl_t = kEl_t*11,
		kElMu_t = kEl_t*10+kMu_t,
		kMuEl_t = kMu_t*10+kEl_t,
		kMuMu_t = kMu_t*11
	};

    // dilepton enum
    enum allDi {
        kDiPfMet,
        kDiTcMet,
        kDiChargedMet,
        kDiProjPfMet,
        kDiProjTcMet,
        kDiProjChargedMet,
        kDiLeadPt,
        kDiTrailPt,
        kDiMll,
        kDiDeltaPhi,
        kDiGammaMRStar,
        kDiSize
    };

    //
    enum extraHist {
        kExtraDeltaPhi,
        kExtraDeltaPhiBands,
        kExtraSize
    };

    // logged variables
    enum LoggedVars_t {
        kLogNJets,
        kLogNSoftMus,
        kLogNBjets,
        kLogMet,
        kLogProjMet,
        kLogMll,
        kLogPtLead,
        kLogPtTrail,
        kLogDphi,
        kLogRazor,
        kLogSize
    };

    // yeild histogram enum
	enum HCuts_t {
		kSkimmed = 1,
		kMinMet,
		kMinMll,
		kZveto,
		kProjMet,
		kJetVeto,
		kSoftMuon,
		kTopVeto,
		kMaxMll,
		kLeadPtMin,
		kTrailPtMin,
		kDeltaPhi,
        kRazor,
		kCutsSize
	};

    // main functions 
	void buildNtuple();
	void cutAndFill();
    uint countJets( double ptMin, double etaMax );
    uint countBtags( double thres, double ptMin = 0.);
    std::pair<HWWLepton*,HWWLepton*> buildPair();
    

    // constants
	const static unsigned short _wordLen = 32;
	static const double _Z0Mass;

	typedef std::bitset<_wordLen> higgsBitWord;


	higgsBitWord _theMask;
	std::vector< higgsBitWord > _nthMask;

    // interface with cfg files
	void readHiggsCutSet( const std::string& path );
	HiggsCutSet getHiggsCutSet(int mass);

    // histogram maker helper methods
    void bookHistogramSet( HistogramSet& set, const std::string& name );
	void bookCutHistograms(std::vector<TH1D*>&, const std::string& nPrefix, const std::string& lPrefix);
	void bookDiHistograms(std::vector<TH1D*>&, const std::string& nPrefix, const std::string& lPrefix);
	void bookExtraHistograms(std::vector<TH1D*>&, const std::string& nPrefix, const std::string& lPrefix);

	TH2D* makeNjetsNvrtx( const std::string& name, const std::string& prefix = "");
    TH1D* makeVarHistogram( int code, const std::string& name, const std::string& title );

	TH1D* makeLabelHistogram( const std::string& name, const std::string& title, std::map<int,std::string> labels);
	TH1D* glueCounters(TH1D* h);

    double getWeight() { return _event->Weight; }
    
    // transverse mass calculator
    double transverseMass(math::XYZTLorentzVector lep, math::XYZTLorentzVector met);

    // helper methods for the analysis

    void fillDiLeptons(std::vector<TH1D*>& histograms );
    void fillExtra(std::vector<TH1D*>& histograms );
    void fillVariables( HistogramSet* histograms, HCuts_t cutCode );
    void fillNminus1(std::vector<TH1D*>& nm1, higgsBitWord word );
    void fillBtaggers();

 
    // cuts
    double _minJetPt;
    double _maxJetEta;
	double _minMet;
	double _minMll;
	double _zVetoWidth;

	double _minProjMetEM;
	double _minProjMetLL;
    double _bThreshold;

    // end cuts

	std::vector<std::string> _histLabels;
	std::map<std::string,TH1D*> _hists;

	HiggsCutSet _theCuts;

    // vars used in the selection
	int   _higgsMass;
	std::string _cutFile;
	std::vector<HiggsCutSet> _cutVector;

    std::string _bDiscriminator;
    uint        _bIdx;
	std::string _analysisTreeName;
	
    // root obj
    TTree*      _analysisTree;

	HWWEvent*   _event;
	HWWNtuple*  _ntuple;

    // histograms
	TH1D* _hScalars;

	TH1D* _nVrtx;
	TH1D* _jetN;
	TH1D* _jetPt;
	TH1D* _jetEta;

    TH1D* _btagCombinedSecondaryVertex;
    TH1D* _btagCombinedSecondaryVertexMVA;
    TH1D* _btagSimpleSecondaryVertexHighEff;
    TH1D* _btagSimpleSecondaryVertexHighPur;
    TH1D* _btagJetBProbability;
    TH1D* _btagJetProbability;
    TH1D* _btagTrackCountingHighEff;
    TH1D* _btagTrackCountingHighPur;

	TH2D* _llJetNVsNvrtx;
	TH2D* _eeJetNVsNvrtx;
	TH2D* _emJetNVsNvrtx;
	TH2D* _meJetNVsNvrtx; //TODO
	TH2D* _mmJetNVsNvrtx;

    HistogramSet    _llHistograms;
    HistogramSet    _eeHistograms;
    HistogramSet    _emHistograms;
    HistogramSet    _meHistograms;
    HistogramSet    _mmHistograms;


};

#endif /* HWWANALYZER_H_ */
