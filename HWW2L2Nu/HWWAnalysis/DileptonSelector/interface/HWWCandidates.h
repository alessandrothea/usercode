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
	kElTagTrailingPt,       // 2
	kElTagExtraPt,          // 3
	kElTagIp3D,             // 4
    // VBTF flags
	kElTagSee,              // 5
	kElTagDeta,             // 6
	kElTagDphi,             // 7
	kElTagHoE,              // 8
	kElTagCombIso,          // 9
	kElTagHits,             // 0
	kElTagDist,             // 1
	kElTagCot,              // 2
    // LH Flags
    kElTagLH_Likelihood,    // 3
    kElTagLH_CombIso,       // 4
    kElTagLH_Hits,          // 5
	kElTagLH_Dist,          // 6
	kElTagLH_Cot,           // 7 
    kElTagSize
};

enum muTags {
	kMuTagEta,                      // 0
	kMuTagLeadingPt,                // 1
	kMuTagTrailingPt,               // 2
	kMuTagExtraPt,                  // 3
	kMuTagIp2D,                     // 4
	kMuTagDzPV,                     // 5

	kMuTagIsGlobal,                 // 6
	kMuTagNChi2,                    // 7
	kMuTagNMuHits,                  // 8
	kMuTagNMatches,                 // 9

	kMuTagIsTracker,                // 0
	kMuTagIsTMLastStationAngTight,  // 1

	kMuTagNTkHits,                  // 2
	kMuTagNPxHits,                  // 3
	kMuTagRelPtRes,                 // 4

	kMuTagCombIso,                  // 5
                                    
	kMuTagSoftPt,                   // 6
	kMuTagSoftHighPt,               // 7
	kMuTagNotIso,                   // 8
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

	static const unsigned short kEE_t = LepCandidate::kEl_t*11;
	static const unsigned short kEM_t = LepCandidate::kEl_t*10+LepCandidate::kMu_t;
	static const unsigned short kME_t = LepCandidate::kMu_t*10+LepCandidate::kEl_t;
	static const unsigned short kMM_t = LepCandidate::kMu_t*11;

	virtual bool isOpposite();
	virtual bool isPtEta();
	virtual bool isIp();
	virtual bool isIso();
	virtual bool isId();
	virtual bool isNoConv();
	virtual bool isGood();

	virtual unsigned short  finalState() { return _lA->type*10 + _lB->type; }
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
