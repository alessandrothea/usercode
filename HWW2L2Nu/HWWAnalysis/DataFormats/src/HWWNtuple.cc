/*
 * HWWSkimmedEvent.cpp
 *
 *  Created on: Nov 23, 2010
 *      Author: ale
 */
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"

// ClassImp(HWWNtuple)

HWWNtuple::HWWNtuple() {

	Clear();
}

HWWNtuple::~HWWNtuple() {

}

void HWWNtuple::Clear( Option_t* option ){

	type = -1;

	pA = TLorentzVector();
	pB = TLorentzVector();
	cA = 0;
	cB = 0;
	d0A = 0;
	d0B = 0;
	dZA = 0;
	dZB = 0;

	mll = 0;
	pfMet = 0;
	tcMet = 0;
	chargedMet = 0;
	pfMetDphi = 0;
	tcMetDphi = 0;
	chargedMetDphi = 0;
	projPfMet = 0;
	projTcMet = 0;
	projChargedMet = 0;
	dPhi = 0;
	nPfJets = 0;
	nJets = 0;
	softMus = false;
	bJets  = false;
}
