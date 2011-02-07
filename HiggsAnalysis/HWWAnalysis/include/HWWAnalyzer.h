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

class HWWNtuple;
class TTree;
class TH1F;


class HWWAnalyzer : public UserAnalyzer {
public:
	HWWAnalyzer(int argc,char** argv);
	virtual ~HWWAnalyzer();

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

	typedef std::bitset<_wordLen> higgsBitSet;

	void readHiggsCutSet( const std::string& path );
	HiggsCutSet getHiggsCutSet(int mass);
//	HiggsCutSet getHiggsCutSet(int mass, int ll);

	int   _higgsMass;

	float _maxD0;
	float _maxDz;
	float _minMet;
	float _minMll;
	float _zVetoWidth;

	float _maxProjMetEM;
	float _maxProjMetLL;

	HiggsCutSet _theCuts;
//	HiggsCutSet _eeCuts;
//	HiggsCutSet _mmCuts;
//	HiggsCutSet _emCuts;

	TH1F* _eeCounters;
	TH1F* _mmCounters;
	TH1F* _emCounters;
	TH1F* _llCounters;

	std::string _cutFile;

	std::vector<HiggsCutSet> _cutVector;

	HWWNtuple* _ntuple;
	TTree* _analysisTree;
};

#endif /* HWWANALYZER_H_ */
