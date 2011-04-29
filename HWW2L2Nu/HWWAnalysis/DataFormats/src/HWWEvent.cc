/*
 * HWWEvent.cc
 *
 *  Created on: Feb 18, 2011
 *      Author: ale
 */
#include "HWWAnalysis/DataFormats/interface/HWWEvent.h"
#include <TClonesArray.h>

//______________________________________________________________________________
HWWEvent::HWWEvent() : NEles(0), NMus(0), PFNJets(0) {
	// TODO Auto-generated constructor stub

	Clear();
}

//______________________________________________________________________________
HWWEvent::~HWWEvent() {
	// TODO Auto-generated destructor stub

}

//______________________________________________________________________________
void HWWEvent::Clear( Option_t* option ){
	Run            = 0;
	Event          = 0;
	LumiSection    = 0;
    Weight         = 1;

	PrimVtxGood    = 0;
	PrimVtxx       = 0;
	PrimVtxy       = 0;
	PrimVtxz       = 0;
	NVrtx          = 0;

	PFMET          = 0;
	PFMETphi       = 0;

	HasSoftMus     = kFALSE;
	HasBTaggedJets = kFALSE;
	NEles          = 0;
	NMus           = 0;
	PFNJets        = 0;

	Els.clear();
	Mus.clear();
	PFJets.clear();
}

