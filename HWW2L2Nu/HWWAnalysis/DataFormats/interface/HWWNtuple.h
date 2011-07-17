/*
 * HWWSkimmedEvent.h
 *
 *  Created on: Nov 23, 2010
 *      Author: ale
 */

#ifndef HWWNTUPLE_H_
#define HWWNTUPLE_H_

#include "DataFormats/Math/interface/LorentzVector.h"
#include <vector>

class HWWNtuple {
public:
	HWWNtuple();
	virtual ~HWWNtuple();

	void clear();

    enum pairtype {
        elel = 0,
        elmu = 1,
        muel = 10,
        mumu = 11
    };

    bool is( pairtype t ) const { return type == t; }
    bool same() const { return is(elel) || is(mumu); }
    bool different() const { return is(elmu) || is(muel); }
	short type;

    unsigned int run;
    unsigned int lumiSection;
    unsigned int event;
    bool selected;
    double weight;

    bool singleMuBit;
    bool doubleMuBit;
    bool singleElBit;
    bool doubleElBit;
    bool muEGBit;

    unsigned long tags;

    unsigned int nExtra;
//     TLorentzVector pA;
//     TLorentzVector pB;
    math::XYZTLorentzVector pA;
    math::XYZTLorentzVector pB;

	int cA;
	int cB;

    unsigned int nVrtx;
    unsigned int nPileUp;

    double met;
    double projMet;

	double pfMet;
	double pfMetPhi;
	double tcMet;
	double tcMetPhi;
	double chargedMet;
	double chargedMetPhi;
    double chargedMetSmurf;
    double chargedMetSmurfPhi;
	double pfMetDphi;
	double tcMetDphi;
	double chargedMetDphi;
    double chargedMetSmurfDphi;

    double projPfMet;
	double projTcMet;
	double projChargedMet;
	double projChargedMetSmurf;
    double minProjMet;

	double mll;
	// di-lepton vars from the shopping list
	double ptA;
	double ptB;
	double mtA;
	double mtB;
	double mt2;
	double deltaRll;
	double dileptonPt;

	double dPhi;
    double mrStar;
    double gammaMRstar;
    double razor;

	unsigned nJets;
	// single jets
	double jet1pt;
	double jet2pt;
	double jet1phi;
	double jet2phi;
	double jet1eta;
	double jet2eta;
	// btag prob
	double jet1bTagProb;
	double jet2bTagProb;
	double sumJet12bTagProb;
	double maxbtagProb;


	unsigned nSoftMus;
	unsigned nBJets;
    // 1 jet only
    double dPhillj;
    double dPhillj0jet;

    double mtll;

    // additional
	unsigned nCentralJets;

	double sumPtJetsScalar;
	double sumPtCentralJetsScalar;
	double sumPtJetsVectorial;
	double sumPtCentralJetsVectorial;

	double centralityJetsScalar;
	double centralityJetsVectorial;
	double centralityLeptonsScalar;
	double centralityLeptonsVectorial;


//     ClassDef(HWWNtuple,1)
};

#endif /* HWWNTUPLE_H_ */
