#ifndef HWWCANDIDATES_H_
#define HWWCANDIDATES_H_

#include <bitset>


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
	kElTagCot
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

// contains the basic info used by the selection
class LepCandidate {
public:
	enum {
		kMu_t = 0,
		kEl_t = 1
	};

	const static unsigned short _wordLen = 32;
	typedef std::bitset<_wordLen> elBitSet;
	typedef std::bitset<_wordLen> muBitSet;

	LepCandidate( char t, unsigned int i ) : type(t), idx(i) {}
	short type;
	unsigned int idx;
	short charge;
	float pt;

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
	LepPair( LepCandidate* lA, LepCandidate* lB);

	LepCandidate* _lA;
	LepCandidate* _lB;

	static const char kEE_t = LepCandidate::kEl_t*11;
	static const char kEM_t = LepCandidate::kEl_t*10+LepCandidate::kMu_t;
	static const char kME_t = LepCandidate::kMu_t*10+LepCandidate::kEl_t;
	static const char kMM_t = LepCandidate::kMu_t*11;

	virtual bool isOpposite() { return (_lA->charge * _lB->charge < 0 );}
	virtual bool isPtEta()  { return this->isOpposite() && (_lA->isPtEta() && _lB->isPtEta()); }
	virtual bool isVertex() { return this->isOpposite() && (_lA->isVertex() && _lB->isVertex()); }
	virtual bool isIso()    { return this->isOpposite() && (_lA->isIso() && _lB->isIso()); }
	virtual bool isId()     { return this->isOpposite() && (_lA->isId() && _lB->isId()); }
	virtual bool isNoConv() { return this->isOpposite() && (_lA->isNoConv() && _lB->isNoConv()); }
	virtual bool isGood()   { return this->isOpposite() && (_lA->isGood() && _lB->isGood()); }

	virtual int  finalState() { return _lA->type*10 + _lB->type; }

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

#endif /* HWWCANDIDATES_H_ */
