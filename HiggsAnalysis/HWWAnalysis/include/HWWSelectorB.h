/*
 * HWWSelectorB.h
 *
 *  Created on: Mar 3, 2011
 *      Author: ale
 */

#ifndef HWWSELECTORB_H_
#define HWWSELECTORB_H_

#include "ETHZNtupleSelector.h"
#include "HWWEvent.h"
#include "HWWCandidates.h"
#include "ETHZHltChecker.h"
#include <TH1F.h>
#include <bitset>

class HWWSelectorB: public ETHZNtupleSelector {
public:
	HWWSelectorB( int argc, char** argv );
	virtual ~HWWSelectorB();

	virtual void Book();
	virtual void BeginJob();
	virtual void Process(Long64_t iEvent);
	virtual void EndJob();

	virtual Bool_t Notify();

protected:


	// container for the working point cuts
	struct WorkingPoint {
		char partition;
		int efficiency;
		float See;
		float dPhi;
		float dEta;
		float HoE;
		float tkIso;
		float ecalIso;
		float hcalIso;
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
		kLLBinIp,
		kLLBinIso,
		kLLBinId,
		kLLBinNoConv,
		kLLBinExtraLep,
		kLLBinLast
	};

	WorkingPoint getWorkingPoint(unsigned short part, int eff);
	virtual void readWorkingPoints( const std::string& path );
	TH1F* makeLabelHistogram( const std::string& name, const std::string& title, std::map<int,std::string> labels);

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


	static const float _etaMaxEB;
	static const float _etaMinEE;
	static const float _etaMaxEE;
	static const float _etaMaxMu;

	int _elCut_TightWorkingPoint;
	int _elCut_LooseWorkingPoint;

	// cuts
	// vrtx
	float _vrtxCut_nDof;
	float _vrtxCut_rho;
	float _vrtxCut_z;

	// lep common
	float _lepCut_leadingPt;
	float _lepCut_trailingPt;
	float _lepCut_D0PV;
	float _lepCut_DzPV;

	float _jetCut_Pt;
	float _jetCut_Dr;
	float _jetCut_Eta;
	float _jetCut_BtagProb;

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

	long long _nSelectedEvents;

	TH1F*	  _hEntries;
	HWWEvent* _diLepEvent;

	std::string _hltMode;
	std::string _runInfoName;
	ETHZHltChecker _hlt;

	std::string _wpFile;

	std::vector< WorkingPoint > _elWorkingPoints;

	std::vector<ElCandicate> _elTagged;
	std::vector<MuCandidate> _muTagged;

	std::vector<LepPair>     _selectedPairs;

	std::set< unsigned int > _selectedEls;
	std::set< unsigned int > _selectedMus;

	std::set< unsigned int > _softMus;
	std::set< unsigned int > _selectedPFJets;
	std::set< unsigned int > _btaggedJets;

	TH1F* _llCounters;
	TH1F* _eeCounters;
	TH1F* _emCounters;
	TH1F* _mmCounters;

	TH1F* _elTightCtrl;
	TH1F* _elLooseCtrl;
	TH1F* _muGoodCtrl;
	TH1F* _muExtraCtrl;

};

#endif /* HWWSELECTORB_H_ */
