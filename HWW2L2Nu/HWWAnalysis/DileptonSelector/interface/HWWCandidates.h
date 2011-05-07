#ifndef HWWCANDIDATES_H_
#define HWWCANDIDATES_H_

#include <bitset>
#include <algorithm>
#include <DataFormats/Candidate/interface/Candidate.h>
#include <DataFormats/PatCandidates/interface/Electron.h>
#include <DataFormats/PatCandidates/interface/Muon.h>


enum elTags {
	kElTagEta,              // 0
	kElTagLeadingPt,        // 1
	kElTagTrailingPt,       // 1
	kElTagIp3D,             // 2
    // VBTF flags
	kElTagSee,              // 3
	kElTagDeta,             // 4
	kElTagDphi,             // 5
	kElTagHoE,              // 6
	kElTagCombIso,          // 7
	kElTagHits,             // 8
	kElTagDist,             // 9
	kElTagCot,              // 0
    // LH Flags
    kElTagLH_Likelihood,    // 1
    kElTagLH_CombIso,       // 2
    kElTagLH_Hits,          // 3
	kElTagLH_Dist,          // 4
	kElTagLH_Cot,           // 5 
    kElTagSize
};

enum muTags {
	kMuTagEta,                      // 0
	kMuTagLeadingPt,                // 1
	kMuTagTrailingPt,               // 2
	kMuTagIp2D,                     // 3
	kMuTagDzPV,                     // 4

	kMuTagIsGlobal,                 // 5
	kMuTagNChi2,                    // 6
	kMuTagNMuHits,                  // 7
	kMuTagNMatches,                 // 8

	kMuTagIsTracker,                // 9
	kMuTagIsTMLastStationAngTight,  // 0

	kMuTagNTkHits,                  // 1
	kMuTagNPxHits,                  // 2
	kMuTagRelPtRes,                 // 3

	kMuTagCombIso,                  // 4
                                    
	kMuTagSoftPt,                   // 5
	kMuTagSoftHighPt,               // 6
	kMuTagNotIso,                   // 7
    kMuTagSize
};

enum lepTags {
	kLepTagAll,
	kLepTagEta,
	kLepTagPt,
	kLepTagIsolation,
	kLepTagId,
	kLepTagIp,
	kLepTagNoConv,
	kLepTagLast
};

// contains the basic info used by the selection
class LepCandidate {
public:
	enum {
		kMu_t = 0,
		kEl_t = 1
	};

	typedef std::bitset<kElTagSize> elBitSet;
	typedef std::bitset<kMuTagSize> muBitSet;

	LepCandidate( char t, unsigned int i ) : type(t), idx(i), candidate(0x0) {}
	short type;
	unsigned int idx;
//     short charge;
//     float pt;
    const reco::Candidate* candidate;

	virtual bool isPtEtaLeading() = 0;
	virtual bool isPtEtaTrailing() = 0;
	virtual bool isIp() = 0;
	virtual bool isIso() = 0;
	virtual bool isId() = 0;
	virtual bool isNoConv() = 0;
	virtual bool isGood() = 0;
	virtual bool isExtra() = 0;

};

class LepPair {
public:
	LepPair( LepCandidate* lA, LepCandidate* lB);

    
	LepCandidate* _lA;
	LepCandidate* _lB;

	static const char kEE_t = LepCandidate::kEl_t*11;
	static const char kEM_t = LepCandidate::kEl_t*10+LepCandidate::kMu_t;
	static const char kME_t = LepCandidate::kMu_t*10+LepCandidate::kEl_t;
	static const char kMM_t = LepCandidate::kMu_t*11;

	virtual bool isOpposite() { return (_lA->candidate->charge() * _lB->candidate->charge() < 0 );}
	virtual bool isPtEta()  { return this->isOpposite() && (_lA->isPtEtaLeading() && _lB->isPtEtaTrailing()); }
	virtual bool isIp() { return this->isOpposite() && (_lA->isIp() && _lB->isIp()); }
	virtual bool isIso()    { return this->isOpposite() && (_lA->isIso() && _lB->isIso()); }
	virtual bool isId()     { return this->isOpposite() && (_lA->isId() && _lB->isId()); }
	virtual bool isNoConv() { return this->isOpposite() && (_lA->isNoConv() && _lB->isNoConv()); }
	virtual bool isGood()   { return this->isOpposite() && (_lA->isGood() && _lB->isGood()); }

	virtual int  finalState() { return _lA->type*10 + _lB->type; }
    LepCandidate* leading() { return _lA; }
    LepCandidate* trailing() { return _lB; }

	LepCandidate* operator[]( unsigned int i);
};

class ElCandicate : public LepCandidate {
public:
	ElCandicate( unsigned int i ) : LepCandidate(kEl_t, i) {}

	elBitSet tightTags;
	elBitSet looseTags;

    const pat::Electron* el() { return static_cast<const pat::Electron*>( candidate ); }

	virtual bool isPtEtaLeading();
	virtual bool isPtEtaTrailing();
	virtual bool isIp();
	virtual bool isIso();
	virtual bool isId();
	virtual bool isNoConv();
	virtual bool isGood();
	virtual bool isExtra();

    virtual bool isIsoLH();
    virtual bool isIdLH();
	virtual bool isNoConvLH();

    virtual bool isIsoVBTF();
    virtual bool isIdVBTF();
	virtual bool isNoConvVBTF();

	virtual bool isLooseIso();
	virtual bool isLooseId();
	virtual bool isLooseNoConv();

};

class MuCandidate : public LepCandidate {
public:
	MuCandidate( unsigned int i ) : LepCandidate(kMu_t, i) {}

	muBitSet tags;

    const pat::Muon* mu() { return static_cast<const pat::Muon*>( candidate ); }

	virtual bool isPtEtaLeading();
	virtual bool isPtEtaTrailing();
	virtual bool isIp();
	virtual bool isIso();
	virtual bool isId();
	virtual bool isNoConv() { return true; }
	virtual bool isGood();
	virtual bool isExtra();
	virtual bool isSoft();
};

#endif /* HWWCANDIDATES_H_ */
