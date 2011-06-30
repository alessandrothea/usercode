/*
 * HWWEvent.h
 *
 *  Created on: Feb 18, 2011
 *      Author: ale
 */

#ifndef HWWEVENT_H_

#include <TObject.h>
#include "DataFormats/Math/interface/LorentzVector.h"
#include "DataFormats/Math/interface/Point3D.h"


struct HWWLepton{
    math::XYZTLorentzVector P;
	Int_t           Charge;
    Int_t           PdgId;
};

struct HWWElectron : public HWWLepton {
	Double_t        SigmaIetaIeta;
	Double_t        CaloEnergy;
	Double_t        DR03TkSumPt;
	Double_t        DR03EcalRecHitSumEt;
	Double_t        DR03HcalTowerSumEt;
	Double_t        DR04EcalRecHitSumEt;
	Double_t        DR04HcalTowerSumEt;
	Int_t           NumberOfMissingInnerHits;
	Double_t        DeltaPhiSuperClusterAtVtx;
	Double_t        DeltaEtaSuperClusterAtVtx;
	Double_t        D0PV;
	Double_t        DzPV;

};

struct HWWMuon : HWWLepton {
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

};

class HWWPFJet {
public:
    math::XYZTLorentzVector P;
	Double_t                ChHadfrac;
	Double_t                NeuHadfrac;
	Double_t                ChEmfrac;
	Double_t                NeuEmfrac;
	Double_t                TrkCountingHighEffBJet;
	Int_t                   NConstituents;
    Double_t                BTagProbTkCntHighEff;
    std::vector<double>     BTaggers;
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

};

struct HWWSlimBTags {
    double pt;
    std::vector<double> values;
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
    math::XYZPoint PrimVtxPosition;
	Double_t PrimVtxx;
	Double_t PrimVtxy;
	Double_t PrimVtxz;
	UInt_t   NVrtx;
	UInt_t   NPileUp;

	// Met
    math::XYZTLorentzVector TCMet;
    math::XYZTLorentzVector PFMet;
    math::XYZTLorentzVector ChargedMet;

    std::vector<math::XYZTLorentzVector> ReducedPFMomenta;

	Int_t    NSoftMus;
	Int_t	 NBTaggedJets;
	Int_t	 NEles;   // Electrons
	Int_t 	 NMus;    // Mus
	Int_t    PFNJets; // Particle flow

	std::vector<HWWElectron> Els;
	std::vector<HWWMuon> 	 Mus;
	std::vector<HWWPFJet>	 PFJets;

    std::vector<HWWSlimBTags>   JetBtags;
    std::vector<bool>           HltPaths;

    HWWBTaggers BTaggers;
};

#define HWWEVENT_H_


#endif /* HWWEVENT_H_ */

