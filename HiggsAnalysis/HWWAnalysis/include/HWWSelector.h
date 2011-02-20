/*
 * HWWSelector.h
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#ifndef HWWSELECTOR_H_
#define HWWSELECTOR_H_

#include "ETHZNtupleSelector.h"
#include "HWWEvent.h"
#include <bitset>

class TH1F;

class HWWSelector: public ETHZNtupleSelector {
public:
	HWWSelector( int argc, char** argv );
	virtual ~HWWSelector();

	virtual void Book();
	virtual void BeginJob();
	virtual void Process(Long64_t iEvent);
	virtual void EndJob();


protected:

	static const float _etaMaxEB;
	static const float _etaMinEE;
	static const float _etaMaxEE;
	static const float _etaMaxMu;

	enum ElCuts {
		kElEta,
		kElPt,
		kElId,
		kElIso,
		kElNoConv,
		kElSee,
		kElDeta,
		kElDphi,
		kElHoE,
		kElTkIso,
		kElEcalIso,
		kElHcalIso,
		kElCombIso,
		kElHits,
		kElDist,
		kElCot,
		kElNumBits
	};

	enum MuCuts {
		kMuEta,
		kMuPt,
		kMuId,
		kMuIso,
		kMuSoft,
		kMuSoftPt,
		kMuIsGlobal,
		kMuIsTracker,
		kMuNChi2,
		kMuNMuHits,
		kMuNTkHits,
		kMuIsTMLastStationAngTight,
		kMuD0PV,
		kMuNumBits
	};

	enum Partition {
		kBarrel,
		kEndcap
	};

	const static unsigned short _wordLen = 32;

	typedef std::bitset<_wordLen> elBitSet;
	typedef std::bitset<_wordLen> muBitSet;
	typedef std::vector< std::pair<unsigned int, std::bitset<_wordLen> > > wordVector;

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
		int  hits;
		float dist;
		float cot;
		void print();
	};

	template<size_t N>
	unsigned int countCuts( ElCuts cut, std::vector< std::bitset<N> > array);

	virtual bool selectAndClean();
	virtual void assembleNtuple();
	WorkingPoint getWorkingPoint(unsigned short part, int eff);
	virtual void readWorkingPoints( const std::string& path );
	virtual elBitSet electronID( int eff, int i );

	virtual void tagElectrons();
	virtual void tagMuons();
	virtual void count();
	virtual std::vector<unsigned int> countElectrons( const wordVector& bits, std::vector<unsigned int>& candidates );
	virtual std::vector<unsigned int> countMuons(     const wordVector& bits, std::vector<unsigned int>& candidates );
	virtual std::vector<unsigned int> countSoftMuons( const wordVector& bits, std::vector<unsigned int>& candidates );
	virtual void cleanJets();
	virtual void clear();

	int _elTightWorkingPoint;
	int _elLooseWorkingPoint;
	float _leptonPtCut;
	float _jetPtCut;
	float _jetDrCut;
	long long _nSelectedEvents;

	HWWEvent* _event;
	TH1F* _elTightCounters;
	TH1F* _elLooseCounters;
	TH1F* _muCounters;
	TH1F* _counters;

	std::string _wpFile;

	std::vector< WorkingPoint > _elWorkingPoints;

	std::vector< unsigned int > _elTightCandidates;
	std::vector< unsigned int > _elLooseCandidates;

	std::vector< std::pair<unsigned int, elBitSet > > _elTightBits; // not used for now
	std::vector< std::pair<unsigned int, elBitSet > > _elLooseBits; // not used for now
	std::vector< std::pair<unsigned int, muBitSet > > _muBits;      // not used for now

	std::vector< unsigned int > _muCandidates;
	std::vector< unsigned int > _softMuCandidates;
	std::vector< unsigned int > _jetCandidates;
	std::vector< unsigned int > _pfJetCandidates;
};

template<size_t N>
unsigned int HWWSelector::countCuts( ElCuts cut, std::vector< std::bitset<N> > array ){
	 unsigned int k=0;
//	 for ( it = array.begin(); it != array.end(); ++it )
	 for( size_t i(0); i<array.size(); ++i)
		 if ( array[i][cut] ) ++k;
	 return k;
}

#endif /* HWWSELECTOR_H_ */
