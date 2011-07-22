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

    // qualtiy variables
    
    sigmaIetaIetaA = -99.9;
    sigmaIetaIetaB = -99.9;
    deltaEtaSuperClusterAtVtxA = -99.9;
    deltaEtaSuperClusterAtVtxB = -99.9;
    deltaPhiSuperClusterAtVtxA = -99.9;
    deltaPhiSuperClusterAtVtxB = -99.9;
    caloEnergyA = -99.9;
    caloEnergyB = -99.9;
    hcalOverEcalA = -99.9;
    hcalOverEcalB = -99.9;
    numberOfMissingInnerHitsA = -99;
    numberOfMissingInnerHitsB = -99;
    convPartnerTrkDCotA = -99.9;
    convPartnerTrkDCotB = -99.9;
    convPartnerTrkDistA = -99.9;
    convPartnerTrkDistB = -99.9;
    dr03EcalRecHitSumEtA = -99.9;
    dr03EcalRecHitSumEtB = -99.9;
    dr03HcalTowerSumEtA = -99.9;
    dr03HcalTowerSumEtB = -99.9;
    dr03TkSumPtA = -99.9;
    dr03TkSumPtB = -99.9;
    dR03HcalFullA = -99.9;
    dR03HcalFullB = -99.9;
    pAtVtxA = -99.9;
    pAtVtxB = -99.9;





    dzPVA = -99.9;
    dzPVB = -99.9;
    d0PVA = -99.9;
    d0PVB = -99.9;
    nMatchesA = 99;
    nMatchesB = 99;
    nChi2A = -99.9;
    nChi2B = -99.9;
    nMuHitsA = -99.9;
    nMuHitsB = -99.9;
    nNPxHitsA = 99;
    nNPxHitsB = 99;
    nTkHitsA = 99;
    nTkHitsB = 99;
    muIso03EmEtA = -99.9;
    muIso03EmEtB = -99.9;
    muIso03HadEtA = -99.9;
    muIso03HadEtB = -99.9;
    muIso03SumPtA = -99.9;
    muIso03SumPtB = -99.9;

}
