/*
 * HWWEvent.h
 *
 *  Created on: Feb 18, 2011
 *      Author: ale
 */

#ifndef HWWEVENT_H_

#include <TObject.h>
#include <TLorentzVector.h>
#include <TClonesArray.h>

class HWWElectron : public TObject {
public:
	HWWElectron() {}
	virtual ~HWWElectron() {}
	TLorentzVector 	P;
	Int_t           Charge;
	Double_t        SigmaIetaIeta;
	Double_t        CaloEnergy;
	Double_t        DR03TkSumPt;
	Double_t        DR04EcalRecHitSumEt;
	Double_t        DR04HcalTowerSumEt;
	Int_t           NumberOfMissingInnerHits;
	Double_t        DeltaPhiSuperClusterAtVtx;
	Double_t        DeltaEtaSuperClusterAtVtx;
	Double_t        D0PV;
	Double_t        DzPV;

	ClassDef(HWWElectron,1)
};

class HWWMuon : public TObject {
public:
	HWWMuon() {}
	virtual ~HWWMuon() {}
	TLorentzVector	P;
	Int_t           Charge;
	Double_t        Iso03SumPt;
	Double_t        Iso03EmEt;
	Double_t        Iso03HadEt;
	Int_t           NMuHits;
	Int_t           NTkHits;
	Double_t        NChi2;
	Int_t           IsGlobalMuon;
	Int_t           IsTrackerMuon;
	Int_t           IsTMLastStationAngTight;
	Double_t        D0PV;
	Double_t        DzPV;

	ClassDef(HWWMuon, 1)
};

class HWWPFJet : public TObject {
public:
	TLorentzVector  P;
	Double_t        ChHadfrac;
	Double_t        NeuHadfrac;
	Double_t        ChEmfrac;
	Double_t        NeuEmfrac;
	Double_t        TrkCountingHighEffBJet;
	Int_t           NConstituents;
    Double_t        BTagProbTkCntHighEff;

	ClassDef(HWWPFJet,1)
};

class HWWEvent : public TObject {
public:
	HWWEvent();
	virtual ~HWWEvent();

	void Clear( Option_t* option="" );

	// Run
	Int_t    Run;
	Int_t    Event;
	Int_t    LumiSection;
    Double_t Weight;

	// Vertex
	Int_t    PrimVtxGood;
	Double_t PrimVtxx;
	Double_t PrimVtxy;
	Double_t PrimVtxz;
	Int_t    NVrtx;

	// Met
	Double_t TCMET;
	Double_t TCMETphi;
	Double_t PFMET;
	Double_t PFMETphi;
    Double_t ChargedMET;
    Double_t ChargedMETphi;

	Bool_t   HasSoftMus;
	Bool_t	 HasBTaggedJets;
	Int_t	 NEles;   // Electrons
	Int_t 	 NMus;    // Mus
	Int_t    PFNJets; // Particle flow

	std::vector<HWWElectron> Els;
	std::vector<HWWMuon> 	 Mus;
	std::vector<HWWPFJet>	 PFJets;

	ClassDef(HWWEvent,1)
};

#define HWWEVENT_H_


#endif /* HWWEVENT_H_ */

