/*
 * HWWCandidates.cc
 *
 *  Created on: Apr 13, 2011
 *      Author: ale
 */

#include "HWWAnalysis/DileptonSelector/interface/HWWCandidates.h"
#include "HWWAnalysis/DileptonSelector/interface/Tools.h"

//_____________________________________________________________________________
LepPair::LepPair( LepCandidate* l1, LepCandidate* l2) {
	if ( l1->candidate->pt() >= l2->candidate->pt() ) {
		_lA = l1;
		_lB = l2;
	} else {
		_lA = l2;
		_lB = l1;
	}
}

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
bool LepPair::isOpposite() {
    return (_lA->candidate->charge() * _lB->candidate->charge() < 0 );
}

//_____________________________________________________________________________
bool LepPair::isPtEta()    {
    return this->isOpposite() && (_lA->isPtEtaLeading() &&  _lB->isPtEtaTrailing() ); 
}

//_____________________________________________________________________________
bool LepPair::isIp()       {
    return this->isOpposite() && (_lA->isIp() && _lB->isIp()); 
}

//_____________________________________________________________________________
bool LepPair::isIso()      {
    return this->isOpposite() && (_lA->isIso() && _lB->isIso()); 
}

//_____________________________________________________________________________
bool LepPair::isId()       {
    return this->isOpposite() && (_lA->isId() && _lB->isId()); 
}

//_____________________________________________________________________________
bool LepPair::isNoConv()   {
    return this->isOpposite() && (_lA->isNoConv() && _lB->isNoConv()); 
}

//_____________________________________________________________________________
bool LepPair::isGood()     {
    return this->isOpposite() && (_lA->isGood() && _lB->isGood()); 
}



/*
 ___  ___                      
 |  \/  |                      
 | .  . |_   _  ___  _ __  ___ 
 | |\/| | | | |/ _ \| '_ \/ __|
 | |  | | |_| | (_) | | | \__ \
 \_|  |_/\__,_|\___/|_| |_|___/

 */                               

//_____________________________________________________________________________
bool MuCandidate::isPtEtaLeading(){
	return (tags[kMuTagLeadingPt] && tags[kMuTagEta]);
}

//_____________________________________________________________________________
bool MuCandidate::isPtEtaTrailing(){
	return (tags[kMuTagTrailingPt] && tags[kMuTagEta]);
}

//_____________________________________________________________________________
bool MuCandidate::isIp() {
	return (tags[kMuTagIp2D] && tags[kMuTagDzPV] );
}

//_____________________________________________________________________________
bool MuCandidate::isId() {
    return  (
            ( ( tags[kMuTagIsGlobal] && tags[kMuTagNChi2] && tags[kMuTagNMuHits] && tags[kMuTagNMatches] )
              || ( tags[kMuTagIsTracker] && tags[kMuTagIsTMLastStationAngTight] ) )
            && tags[kMuTagNTkHits] && tags[kMuTagNPxHits] && tags[kMuTagRelPtRes] 
            );
}


//_____________________________________________________________________________
bool MuCandidate::isIso() {
	return tags[kMuTagCombIso];
}

//_____________________________________________________________________________
bool MuCandidate::isExtra() {
	return (tags[kMuTagEta] && tags[kMuTagExtraPt])
		&& this->isIp()
		&& this->isId()
		&& this->isIso();
}

//_____________________________________________________________________________
bool MuCandidate::isGood() {
	return this->isPtEtaLeading()
		&& this->isIp()
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
			tags[kMuTagIp2D] &&
			( !tags[kMuTagSoftHighPt] || (tags[kMuTagSoftHighPt] && tags[kMuTagNotIso]) )
		);

}

/*
 _____ _           _                       
|  ___| |         | |                      
| |__ | | ___  ___| |_ _ __ ___  _ __  ___ 
|  __|| |/ _ \/ __| __| '__/ _ \| '_ \/ __|
| |___| |  __/ (__| |_| | | (_) | | | \__ \
\____/|_|\___|\___|\__|_|  \___/|_| |_|___/

*/

//_____________________________________________________________________________
bool ElCandicate::isPtEtaLeading() {
	return (tightTags[kElTagLeadingPt] && tightTags[kElTagEta]);
}

//_____________________________________________________________________________
bool ElCandicate::isPtEtaTrailing() {
	return (tightTags[kElTagTrailingPt] && tightTags[kElTagEta]);
}

//_____________________________________________________________________________
bool ElCandicate::isIp() {
//     return (tightTags[kElTagD0PV] && tightTags[kElTagDzPV] );
	return (tightTags[kElTagIp3D] );
}

//______________________________________________________________________________
bool ElCandicate::isIso() {
    return isIsoLH();
}

//______________________________________________________________________________
bool ElCandicate::isId() {
    return isIdLH();
}

//______________________________________________________________________________
bool ElCandicate::isNoConv() {
    return isNoConvLH();
}

//_____________________________________________________________________________
bool ElCandicate::isGood() {
	return this->isPtEtaLeading()
		&& this->isIp()
		&& this->isIso()
		&& this->isId()
		&& this->isNoConv();
}

//_____________________________________________________________________________
bool ElCandicate::isExtra() {
	return
			// ptEta
			(tightTags[kElTagExtraPt] && tightTags[kElTagEta])
			// vertex
			&& tightTags[kElTagIp3D]
			// iso
			&& isIso()
			// id
            && isId()
            // no conversion
            && isNoConv();
}

// likelikood specific
//______________________________________________________________________________
bool ElCandicate::isIsoLH() {
    return tightTags[kElTagLH_CombIso];
}

//______________________________________________________________________________
bool ElCandicate::isIdLH() {
    return tightTags[kElTagLH_Likelihood];
}

//_____________________________________________________________________________
bool ElCandicate::isNoConvLH() {
	// !conversion
	return  ( tightTags[kElTagLH_Dist] || tightTags[kElTagLH_Cot] ) && tightTags[kElTagLH_Hits];
}

// vbtf specific
//_____________________________________________________________________________
bool ElCandicate::isIsoVBTF() {
	return tightTags[kElTagCombIso];
}

//_____________________________________________________________________________
bool ElCandicate::isIdVBTF() {
//FIXME     return tightTags[kElTagSee] && tightTags[kElTagDphi] && tightTags[kElTagDeta] && tightTags[kElTagHoE];
	return tightTags[kElTagSee] && tightTags[kElTagDphi] && tightTags[kElTagDeta];
}

//_____________________________________________________________________________
bool ElCandicate::isNoConvVBTF() {
	// !conversion
	return !( ( tightTags[kElTagDist] && tightTags[kElTagCot] ) || tightTags[kElTagHits]);
}

// loose id (discontinued?)
//_____________________________________________________________________________
bool ElCandicate::isLooseIso() {
	return looseTags[kElTagCombIso];
}

//_____________________________________________________________________________
bool ElCandicate::isLooseId() {
//FIXME     return looseTags[kElTagSee] && looseTags[kElTagDphi] && looseTags[kElTagDeta] && looseTags[kElTagHoE];
	return looseTags[kElTagSee] && looseTags[kElTagDphi] && looseTags[kElTagDeta];
}

//_____________________________________________________________________________
bool ElCandicate::isLooseNoConv() {
	// !conversion
	return  ( looseTags[kElTagDist] || looseTags[kElTagCot] ) && looseTags[kElTagHits];
}

