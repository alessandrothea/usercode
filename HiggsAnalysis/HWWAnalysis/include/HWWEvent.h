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
	TLorentzVector 	ElP;
	Int_t           ElCharge;
	Double_t        ElSigmaIetaIeta;
	Double_t        ElCaloEnergy;
	Double_t        ElDR03TkSumPt;
	Double_t        ElDR04EcalRecHitSumEt;
	Double_t        ElDR04HcalTowerSumEt;
	Int_t           ElNumberOfMissingInnerHits;
	Double_t        ElDeltaPhiSuperClusterAtVtx;
	Double_t        ElDeltaEtaSuperClusterAtVtx;
	Double_t        ElD0PV;
	Double_t        ElDzPV;

	ClassDef(HWWElectron,1)
};

class HWWMuon : public TObject {
public:
	HWWMuon() {}
	virtual ~HWWMuon() {}
	TLorentzVector	MuP;
	Int_t           MuCharge;
	Double_t        MuIso03SumPt;
	Double_t        MuIso03EmEt;
	Double_t        MuIso03HadEt;
	Int_t           MuNMuHits;
	Int_t           MuNTkHits;
	Double_t        MuNChi2;
	Int_t           MuIsGlobalMuon;
	Int_t           MuIsTrackerMuon;
	Int_t           MuIsTMLastStationAngTight;
	Double_t        MuD0PV;
	Double_t        MuDzPV;

	ClassDef(HWWMuon, 1)
};

class HWWJet : public TObject {
public:
	TLorentzVector	JP;
	Double_t        JEMfrac;
	Int_t           JNConstituents;
	Double_t        JID_HPD;
	Double_t        JID_RBX;
	Double_t        JID_n90Hits;
	Double_t        JID_resEMF;
	Double_t        JID_HCALTow;
	Double_t        JID_ECALTow;


	ClassDef(HWWJet,1)
};

class HWWPFJet : public TObject {
public:
	TLorentzVector  PFJP;
	Double_t        PFJChHadfrac;
	Double_t        PFJNeuHadfrac;
	Double_t        PFJChEmfrac;
	Double_t        PFJNeuEmfrac;
	Int_t           PFJNConstituents;

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

	// Vertex
	Int_t    PrimVtxGood;
	Double_t PrimVtxx;
	Double_t PrimVtxy;
	Double_t PrimVtxz;
	Int_t    NVrtx;

	// Met
	Double_t PFMET;
	Double_t PFMETphi;
	Double_t SumEt;
	Double_t MuCorrMET;
	Double_t MuCorrMETphi;

	Bool_t   HasSoftMus;
	Int_t	 NEles;   // Electrons
	Int_t 	 NMus;    // Mus
	Int_t    NJets;	  //Jets
	Int_t    PFNJets; // Particle flow

	std::vector<HWWElectron> Els;
	std::vector<HWWMuon> 	 Mus;
	std::vector<HWWJet>	 	 Jets;
	std::vector<HWWPFJet>	 PFJets;

	ClassDef(HWWEvent,1)
};

#define HWWEVENT_H_


#endif /* HWWEVENT_H_ */
