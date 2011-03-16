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
	const static unsigned short _wordLen = 32;
	typedef std::bitset<_wordLen> elBitSet;
	typedef std::bitset<_wordLen> muBitSet;

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

	// contains the basic info used by the selection
	class LepCandidate {
	public:
		enum {
			kMu_t = 0,
			kEl_t = 1
		};

		LepCandidate( char t, unsigned int i ) : type(t), idx(i) {}
		short type;
		unsigned int idx;
		short charge;

		virtual bool isPtEta() = 0;
		virtual bool isVertex() = 0;
		virtual bool isIso() = 0;
		virtual bool isId() = 0;
		virtual bool isNoConv() = 0;
		virtual bool isGood() = 0;
		virtual bool isExtra() = 0;

	};

	class LepPair {
	public:
		LepPair( LepCandidate* lA, LepCandidate* lB) : _lA(lA), _lB(lB) {}

		LepCandidate* _lA;
		LepCandidate* _lB;

		static const char kEE_t = LepCandidate::kEl_t*2;
		static const char kEM_t = LepCandidate::kEl_t+LepCandidate::kMu_t;
		static const char kMM_t = LepCandidate::kMu_t*2;

		virtual bool isOpposite() { return (_lA->charge * _lB->charge < 0 );}
		virtual bool isPtEta()  { return this->isOpposite() && (_lA->isPtEta() && _lB->isPtEta()); }
		virtual bool isVertex() { return this->isOpposite() && (_lA->isVertex() && _lB->isVertex()); }
		virtual bool isIso()    { return this->isOpposite() && (_lA->isIso() && _lB->isIso()); }
		virtual bool isId()     { return this->isOpposite() && (_lA->isId() && _lB->isId()); }
		virtual bool isNoConv() { return this->isOpposite() && (_lA->isNoConv() && _lB->isNoConv()); }
		virtual bool isGood()   { return this->isOpposite() && (_lA->isGood() && _lB->isGood()); }

		virtual int  finalState() { return _lA->type + _lB->type; }

		LepCandidate* operator[]( unsigned int i);
	};


	class ElCandicate : public LepCandidate {
	public:
		ElCandicate( unsigned int i ) : LepCandidate(kEl_t, i) {}

		elBitSet tightTags;
		elBitSet looseTags;

		virtual bool isPtEta();
		virtual bool isVertex();
		virtual bool isIso();
		virtual bool isId();
		virtual bool isNoConv();
		virtual bool isGood();
		virtual bool isLooseIso();
		virtual bool isLooseId();
		virtual bool isLooseNoConv();
		virtual bool isExtra();

	};

	class MuCandidate : public LepCandidate {
	public:
		MuCandidate( unsigned int i ) : LepCandidate(kMu_t, i) {}

		muBitSet tags;

		virtual bool isPtEta();
		virtual bool isVertex();
		virtual bool isIso();
		virtual bool isId();
		virtual bool isNoConv() { return true; }
		virtual bool isGood();
		virtual bool isExtra();
		virtual bool isSoft();
	};

	enum WpPartition {
		kBarrel,
		kEndcap
	};


	enum elTags {
		kElTagEta,
		kElTagPt,
		kElTagD0PV,
		kElTagDzPV,
		kElTagSee,
		kElTagDeta,
		kElTagDphi,
		kElTagHoE,
		kElTagCombIso,
		kElTagHits,
		kElTagDist,
		kElTagCot,
	};

	enum muTags {
		kMuTagEta,
		kMuTagPt,
		kMuTagExtraPt,
		kMuTagD0PV,
		kMuTagDzPV,
		kMuTagIsGlobal,
		kMuTagIsTracker,
		kMuTagNMuHits,
		kMuTagNMatches,
		kMuTagNTkHits,
		kMuTagNPxHits,
		kMuTagNChi2,
		kMuTagRelPtRes,
		kMuTagCombIso,

		kMuTagSoftPt,
		kMuTagSoftHighPt,
		kMuTagIsTMLastStationAngTight,
		kMuTagNotIso
	};

	enum lepTags {
		kLepTagAll,
		kLepTagEta,
		kLepTagPt,
		kLepTagD0,
		kLepTagDz,
		kLepTagIsolation,
		kLepTagId,
		kLepTagNoConv,
		kLepTagLast
	};

	enum LlBins {
		kLLBinAll,
		kLLBinHLT,
		kLLBinDilepton,
		kLLBinEtaPt,
		kLLBinVertex,
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
	virtual elBitSet electronIsoId( elBitSet& tags, int idx, int eff );
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
	float _lepCut_Pt;
	float _lepCut_extraPt;
	float _lepCut_D0PV;
	float _lepCut_DzPV;

	float _jetCut_Pt;
	float _jetCut_Dr;
	float _jetCut_BtagProb;

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

	HWWEvent* _event;

	std::string _runInfoName;
	std::vector<std::string>  _hltAllNames;
	std::vector<std::string>  _hltActiveNames;
	std::vector<unsigned int> _hltIdx;

	std::string _wpFile;

	std::vector< WorkingPoint > _elWorkingPoints;

	std::vector<ElCandicate> _elTagged;
	std::vector<MuCandidate> _muTagged;

	std::vector<LepPair>     _selectedPairs;

	std::set< unsigned int > _selectedEls;
	std::set< unsigned int > _selectedMus;

	std::set< unsigned int > _softMus;
	std::set< unsigned int > _selectedJets;
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
