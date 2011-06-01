/*
 * HWWEvent.h
 *
 *  Created on: Feb 18, 2011
 *      Author: ale
 */

#ifndef HWWEVENT_H_

#include <TObject.h>
// #include <TLorentzVector.h>
#include "DataFormats/Math/interface/LorentzVector.h"


class HWWElectron {
public:
	HWWElectron() {}
	virtual ~HWWElectron() {}
//     TLorentzVector 	P;
    math::XYZTLorentzVector P;
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

//     ClassDef(HWWElectron,1)
};

class HWWMuon {
public:
	HWWMuon() {}
	virtual ~HWWMuon() {}
//     TLorentzVector	P;
    math::XYZTLorentzVector P;
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

//     ClassDef(HWWMuon, 1)
};

class HWWPFJet {
public:
//     TLorentzVector P;
    math::XYZTLorentzVector P;
	Double_t        ChHadfrac;
	Double_t        NeuHadfrac;
	Double_t        ChEmfrac;
	Double_t        NeuEmfrac;
	Double_t        TrkCountingHighEffBJet;
	Int_t           NConstituents;
    Double_t        BTagProbTkCntHighEff;

//     ClassDef(HWWPFJet,1)
};

class HWWBTaggers {
public:
    // 2 elements vectors with btagger min and max for the event
    // empty if no additional jet was found
    std::vector<double> CombSecVrtx;
    std::vector<double> CombSecVrtxMVA;
    std::vector<double> SimpleSecVrtxHighEff;
    std::vector<double> SimpleSecVrtxHighPur;
    std::vector<double> JetBProb;
    std::vector<double> JetProb;
    std::vector<double> TkCntHighEff;
    std::vector<double> TkCntHighPur;

//     ClassDef(HWWBTaggers,1)
};

class HWWEvent {
public:
	HWWEvent();
	virtual ~HWWEvent();

	void Clear( Option_t* option="" );

	// Run
	UInt_t    Run;
	UInt_t    Event;
	UInt_t    LumiSection;
    Double_t  Weight;

	// Vertex
	Int_t    PrimVtxGood;
	Double_t PrimVtxx;
	Double_t PrimVtxy;
	Double_t PrimVtxz;
	UInt_t   NVrtx;
	UInt_t   NPileUp;

	// Met
//     TLorentzVector TCMet;
//     TLorentzVector PFMet;
//     TLorentzVector ChargedMet;
    math::XYZTLorentzVector TCMet;
    math::XYZTLorentzVector PFMet;
    math::XYZTLorentzVector ChargedMet;

	Bool_t   NSoftMus;
	Bool_t	 NBTaggedJets;
	Int_t	 NEles;   // Electrons
	Int_t 	 NMus;    // Mus
	Int_t    PFNJets; // Particle flow

	std::vector<HWWElectron> Els;
	std::vector<HWWMuon> 	 Mus;
	std::vector<HWWPFJet>	 PFJets;

    HWWBTaggers BTaggers;
//     ClassDef(HWWEvent,1)
};

#define HWWEVENT_H_


#endif /* HWWEVENT_H_ */

