/*
 * HWWSkimmedEvent.h
 *
 *  Created on: Nov 23, 2010
 *      Author: ale
 */

#ifndef HWWNTUPLE_H_
#define HWWNTUPLE_H_

#include <TObject.h>
#include <TLorentzVector.h>

class HWWNtuple : public TObject {
public:
	HWWNtuple();
	virtual ~HWWNtuple();

	void Clear( Option_t* option="" );

	char type;

    UInt_t run;
    UInt_t lumiSection;
    UInt_t event;
    Bool_t selected;
    Double_t weight;

	TLorentzVector pA;
	TLorentzVector pB;
	Int_t cA;
	Int_t cB;
	double d0A;
	double d0B;
	double dZA;
	double dZB;

	double mll;

    unsigned int    nVrtx;
    unsigned int    nPileUp;
	double pfMet;
	double tcMet;
	double chargedMet;
	double pfMetDphi;
	double tcMetDphi;
	double chargedMetDphi;
	double projPfMet;
	double projTcMet;
	double projChargedMet;
	double dPhi;
	int    nPfJets;
	int    nJets;
	bool   softMus;
	bool   bJets;

	ClassDef(HWWNtuple,1)
};

#endif /* HWWNTUPLE_H_ */
