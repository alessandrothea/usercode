/*
 * HWWAnalyzer.h
 *
 *  Created on: Dec 14, 2010
 *      Author: ale
 */

#ifndef HWWANALYZER_H_
#define HWWANALYZER_H_

#include "UserAnalyzer.h"
#include <bitset>

class HWWEvent;
class HWWNtuple;
class TTree;
class TH1F;
class TParticlePDG;


class HWWAnalyzer : public UserAnalyzer {
public:
	HWWAnalyzer(int argc,char** argv);
	virtual ~HWWAnalyzer();

	virtual void Book();
	virtual void BeginJob();
	virtual void Process( Long64_t iEvent );
	virtual void calcNtuple();
	virtual void cutAndFill();
	virtual void EndJob();

protected:

	struct HiggsCutSet {
		int hMass;
		int ll;
		float minPtHard;
		float minPtSoft;
		float maxMll;
		float maxDphi;
		void print();
	};

	enum LL_t {
		kEE,
		kMM,
		kEM
	};

	enum HCuts_t {
		kDileptons = 1,
		kCharge,
		kD0,
		kDz,
		kMinMet,
		kMinMll,
		kZveto,
		kProjMet,
		kJetVeto,
		kSoftMuon,
		kHardPtMin,
		kSoftPtMin,
		kMaxMll,
		kDeltaPhi,
		kNumCuts
	};

	const static unsigned short _wordLen = 32;

	typedef std::bitset<_wordLen> higgsBitWord;

	TParticlePDG* _Z0;

	higgsBitWord _theMask;
	std::vector< higgsBitWord > _nthMask;

	void bookNm1Histograms(std::vector<TH1F*>&, const std::string& nPrefix, const std::string& lPrefix);

	void readHiggsCutSet( const std::string& path );
	HiggsCutSet getHiggsCutSet(int mass);
//	HiggsCutSet getHiggsCutSet(int mass, int ll);

	std::string _analysisTreeName;

	int   _higgsMass;

	float _maxD0;
	float _maxDz;
	float _minMet;
	float _minMll;
	float _zVetoWidth;

	float _minProjMetEM;
	float _minProjMetLL;

	HiggsCutSet _theCuts;
//	HiggsCutSet _eeCuts;
//	HiggsCutSet _mmCuts;
//	HiggsCutSet _emCuts;

	TH1F* _eeCounters;
	TH1F* _mmCounters;
	TH1F* _emCounters;
	TH1F* _llCounters;

	TH1F* _jetPt;
	TH1F* _jetEta;

	std::vector<TH1F*> _llNm1Hist;
	std::vector<TH1F*> _eeNm1Hist;
	std::vector<TH1F*> _emNm1Hist;
	std::vector<TH1F*> _mmNm1Hist;
	std::vector<TH1F*> _preCutHist;
	std::vector<TH1F*> _postCutHist;

	std::string _cutFile;

	std::vector<HiggsCutSet> _cutVector;

	TTree* _analysisTree;

	HWWEvent* _event;
	HWWNtuple* _ntuple;

};

#endif /* HWWANALYZER_H_ */
