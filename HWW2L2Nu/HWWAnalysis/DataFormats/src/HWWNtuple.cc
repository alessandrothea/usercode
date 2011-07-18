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

    singleMuBit = false;
    doubleMuBit = false;
    singleElBit = false;
    doubleElBit = false;
    muEGBit     = false;

    tags = 0;

    nExtra = 0;
	pA = math::XYZTLorentzVector();
	pB = math::XYZTLorentzVector();
	cA = 0;
	cB = 0;

    nVrtx = 0;
    nPileUp = 0;

    met = 0;
    projMet = 0;

    pfMet = 0;
    tcMet = 0;
    chargedMet = 0;
    chargedMetSmurf = 0;

    pfMetDphi = 0;
    tcMetDphi = 0;
    chargedMetDphi = 0;
    chargedMetSmurfDphi = 0;
    
    projPfMet = 0;
    projTcMet = 0;
    projChargedMet = 0;
    projChargedMetSmurf = 0;
    minProjMet = 0;

	mll = 0;
	dPhi = 0;
    mrStar = 0;
    gammaMRstar = 0;
    razor = 0;
	nJets = 0;
	nCentralJets    = 0;
	nSoftMus = 0;
	nBJets  = 0;

    dPhillj = 0.;

    mtll    = 0.;

    // from here on the new shopping list variables
    ptA = 0;
    ptB = 0;
    deltaRll = 0;
    dileptonPt = 0;
    pfMetPhi = 0;
    tcMetPhi = 0;
    chargedMetPhi = 0;
    jet1pt = -99.9;
    jet2pt = -99.9;
    jet1phi = -99.9;
    jet2phi = -99.9;
    jet1eta = -99.9;
    jet2eta = -99.9;
    mtA = 0;
    mtB = 0;
    mt2 = 0;
    sumPtJetsScalar = 0;
    sumPtCentralJetsScalar = 0.;    
    jet1bTagProb = -99.9;
    jet2bTagProb = -99.9;
    sumJet12bTagProb = -99.9;
    maxbtagProb = -99.9;
    centralityLeptonsScalar = -99.9;
    centralityLeptonsVectorial = -99.9;


}
