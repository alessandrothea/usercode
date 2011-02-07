/*
 * HWWSkimmedEvent.cpp
 *
 *  Created on: Nov 23, 2010
 *      Author: ale
 */
#include "HWWNtuple.h"
#include <TClonesArray.h>

ClassImp(HWWNtuple)
ClassImp(HWWElectron)
ClassImp(HWWMuon)
ClassImp(HWWJet)
ClassImp(HWWPFJet)

//______________________________________________________________________________
HWWNtuple::HWWNtuple() : NEles(0), NMus(0), NJets(0), PFNJets(0) {
	// TODO Auto-generated constructor stub

//	Els = new TClonesArray("HWWElectron",2);
//	Muons = new TClonesArray("HWWMuon",2);
//	Jets = new TClonesArray("HWWJet",20);
//	PFJets = new TClonesArray("HWWPFJet",20);
	Clear();
}

//______________________________________________________________________________
HWWNtuple::~HWWNtuple() {
	// TODO Auto-generated destructor stub
//	delete Els;
//	delete Muons;
//	delete Jets;
//	delete PFJets;
}

//______________________________________________________________________________
void HWWNtuple::Clear( Option_t* option ){
	Run          = 0;
	Event        = 0;
	LumiSection  = 0;

	PrimVtxGood  = 0;
	PrimVtxx     = 0;
	PrimVtxy     = 0;
	PrimVtxz     = 0;
	NVrtx        = 0;

	PFMET        = 0;
	PFMETphi     = 0;
	SumEt        = 0;
	MuCorrMET    = 0;
	MuCorrMETphi = 0;

	HasSoftMus   = kFALSE;
	NEles        = 0;
	NMus         = 0;
	NJets        = 0;
	PFNJets      = 0;

	Els.clear();
	Mus.clear();
	Jets.clear();
	PFJets.clear();
}
