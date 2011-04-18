/*
 * HWWCandidates.cc
 *
 *  Created on: Apr 13, 2011
 *      Author: ale
 */

#include "HWWCandidates.h"
#include "Tools.h"

//_____________________________________________________________________________
LepCandidate* LepPair::operator [](unsigned int i){
	switch (i) {
	case 0:
		return _lA;
	case 1:
		return _lB;
	default:
		THROW_RUNTIME("index out of bound i="<< i)
	}
}
//_____________________________________________________________________________
bool MuCandidate::isPtEta(){
	return (tags[kMuTagPt] && tags[kMuTagEta]);
}

//_____________________________________________________________________________
bool MuCandidate::isVertex() {
	return (tags[kMuTagD0PV] && tags[kMuTagDzPV] );
}

//_____________________________________________________________________________
bool MuCandidate::isId() {
	return ( tags[kMuTagIsGlobal] &&
				tags[kMuTagIsTracker] &&
				tags[kMuTagNMuHits] &&
				tags[kMuTagNMatches] &&
				tags[kMuTagNTkHits] &&
				tags[kMuTagNPxHits] &&
				tags[kMuTagNChi2] &&
				tags[kMuTagRelPtRes]
			);
}

//_____________________________________________________________________________
bool MuCandidate::isIso() {
	return tags[kMuTagCombIso];
}

//_____________________________________________________________________________
bool MuCandidate::isExtra() {
	return (tags[kMuTagPt] && tags[kMuTagExtraPt])
		&& this->isVertex()
		&& this->isId()
		&& this->isIso();
}

//_____________________________________________________________________________
bool MuCandidate::isGood() {
	return this->isPtEta()
		&& this->isVertex()
		&& this->isId()
		&& this->isIso();
}

//_____________________________________________________________________________
bool MuCandidate::isSoft() {
	return ( tags[kMuTagEta] &&
			tags[kMuTagSoftPt] &&
			tags[kMuTagIsTracker] &&
			tags[kMuTagIsTMLastStationAngTight] &&
			tags[kMuTagNTkHits] &&
			tags[kMuTagD0PV] &&
			( !tags[kMuTagSoftHighPt] || tags[kMuTagSoftHighPt] && tags[kMuTagNotIso] )
		);

}

//_____________________________________________________________________________
bool ElCandicate::isPtEta() {
	return (tightTags[kElTagPt] && tightTags[kElTagEta]);
}

//_____________________________________________________________________________
bool ElCandicate::isVertex() {
	return (tightTags[kElTagD0PV] && tightTags[kElTagDzPV] );
}

//_____________________________________________________________________________
bool ElCandicate::isIso() {
	return tightTags[kElTagCombIso];
}

//_____________________________________________________________________________
bool ElCandicate::isId() {
	return tightTags[kElTagSee] && tightTags[kElTagDphi] && tightTags[kElTagDeta] && tightTags[kElTagHoE];
}

//_____________________________________________________________________________
bool ElCandicate::isNoConv() {
	// !conversion
	return !( ( tightTags[kElTagDist] && tightTags[kElTagCot] ) || tightTags[kElTagHits]);
}

//_____________________________________________________________________________
bool ElCandicate::isLooseIso() {
	return looseTags[kElTagCombIso];
}

//_____________________________________________________________________________
bool ElCandicate::isLooseId() {
	return looseTags[kElTagSee] && looseTags[kElTagDphi] && looseTags[kElTagDeta] && looseTags[kElTagHoE];
}

//_____________________________________________________________________________
bool ElCandicate::isLooseNoConv() {
	// !conversion
	return !( ( looseTags[kElTagDist] && looseTags[kElTagCot] ) || looseTags[kElTagHits]);
}

//_____________________________________________________________________________
bool ElCandicate::isGood() {
	return this->isPtEta()
		&& this->isVertex()
		&& this->isIso()
		&& this->isId()
		&& this->isNoConv();
}

//_____________________________________________________________________________
bool ElCandicate::isExtra() {
	return
			// ptEta
			(looseTags[kElTagPt] && looseTags[kElTagEta])
			// vertex
			&& (looseTags[kElTagD0PV] && looseTags[kElTagDzPV] )
			// iso
			&& isLooseIso()
			// id
            && isLooseId()
            // no conversion
            && isLooseNoConv();
}
