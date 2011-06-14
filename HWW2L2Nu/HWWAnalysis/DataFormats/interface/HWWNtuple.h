/*
 * HWWSkimmedEvent.h
 *
 *  Created on: Nov 23, 2010
 *      Author: ale
 */

#ifndef HWWNTUPLE_H_
#define HWWNTUPLE_H_

#include "DataFormats/Math/interface/LorentzVector.h"

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

    unsigned long tags;

//     TLorentzVector pA;
//     TLorentzVector pB;
    math::XYZTLorentzVector pA;
    math::XYZTLorentzVector pB;

	int cA;
	int cB;

	double d0A;
	double d0B;
	double dZA;
	double dZB;

    unsigned int nVrtx;
    unsigned int nPileUp;

    double met;
    double projMet;

	double pfMet;
	double tcMet;
	double chargedMet;
	double pfMetDphi;
	double tcMetDphi;
	double chargedMetDphi;

	double projPfMet;
	double projTcMet;
	double projChargedMet;
    double minProjMet;

	double mll;
	double dPhi;
    double mrStar;
    double gammaMRstar;
    double razor;

	unsigned nJets;
	unsigned nSoftMus;
	unsigned nBJets;
    // 1 jet only
    double dPhillj;
    // additional
	unsigned nCentralJets;
	unsigned nCentralJets40;

//     ClassDef(HWWNtuple,1)
};

#endif /* HWWNTUPLE_H_ */
