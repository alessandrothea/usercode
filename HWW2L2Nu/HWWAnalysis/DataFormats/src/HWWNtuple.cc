/*
 * HWWSkimmedEvent.cpp
 *
 *  Created on: Nov 23, 2010
 *      Author: ale
 */
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"

// ClassImp(HWWNtuple)

HWWNtuple::HWWNtuple() {

	clear();
}

HWWNtuple::~HWWNtuple() {

}

void HWWNtuple::clear(){

	type = -1;

    run = 0;
    lumiSection = 0;
    event = 0;
    selected = false;
    weight = 1.,

    tags = 0;

	pA = math::XYZTLorentzVector();
	pB = math::XYZTLorentzVector();
	cA = 0;
	cB = 0;
	d0A = 0;
	d0B = 0;
	dZA = 0;
	dZB = 0;

    nVrtx = 0;
    nPileUp = 0;

    met = 0;
    projMet = 0;

	pfMet = 0;
	tcMet = 0;
	chargedMet = 0;

	pfMetDphi = 0;
	tcMetDphi = 0;
	chargedMetDphi = 0;

	projPfMet = 0;
	projTcMet = 0;
	projChargedMet = 0;
    minProjMet = 0;

	mll = 0;
	dPhi = 0;
    mrStar = 0;
    gammaMRstar = 0;
    razor = 0;
	nJets = 0;
	nSoftMus = 0;
	nBJets  = 0;

    dPhillj = 0.;
}
