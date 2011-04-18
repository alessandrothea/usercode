/*
 * ETHZNtupleSelector.h
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#ifndef ETHZNTUPLESELECTOR_H_
#define ETHZNTUPLESELECTOR_H_

#include <sstream>
#include "CommandLine.h"

#include "ETHZNtupleReader.h"
#include "Configurator.h"
#include <TBenchmark.h>
#include <TEnv.h>

class ETHZEvent {
public:
	ETHZEvent( ETHZNtupleReader* reader ) { _reader = reader; }

	Double_t getGenMET();
	Int_t* getHLTResults();

    Double_t getRun();
    Double_t getEvent();
    Double_t getLumiSection();
    Double_t getPrimVtxx();
    Double_t getPrimVtxy();
    Double_t getNVrtx();
    Double_t getTCMET();
    Double_t getTCMETphi();
    Double_t getPFMET();
    Double_t getPFMETphi();
    Double_t getSumEt(); 

    Double_t getMuCorrMET();
    Double_t getMuCorrMETphi();

	Double_t getPrimVtxNdof();
	Int_t 	 getPrimVtxGood();
	Int_t    getPrimVtxIsFake();
	Double_t getPrimVtxRho();
	Double_t getPrimVtxz();


	// apply the correction for the endcaps

	Int_t    getNEles();
	Double_t getElDeltaEtaSuperClusterAtVtx( int i );
	Double_t getElDeltaPhiSuperClusterAtVtx( int i );
	Double_t getElPt( int i );
	Double_t getElSCEta( int i );
    Double_t getElCaloEnergy( int i );
    Int_t    getElCharge( int i );
    Double_t getElConvPartnerTrkDCot( int i );
    Double_t getElConvPartnerTrkDist( int i );
    Double_t getElD0PV( int i );
    Double_t getElDR03EcalRecHitSumEt( int i );
    Double_t getElDR03HcalTowerSumEt( int i );
    Double_t getElDR03TkSumPt( int i );
    Double_t getElDR04EcalRecHitSumEt( int i );
    Double_t getElDR04HcalTowerSumEt( int i );
    Double_t getElDzPV( int i );
    Double_t getElE( int i );
    Double_t getElEta( int i );
    Double_t getElHcalOverEcal( int i );
    Int_t    getElNumberOfMissingInnerHits( int i );
    Double_t getElPx( int i );
    Double_t getElPy( int i );
    Double_t getElPz( int i );
    Double_t getElSigmaIetaIeta( int i );

	Int_t    getNMus();
    Int_t    getMuCharge( int i );
    Double_t getMuD0PV( int i );
    Double_t getMuDzPV( int i );
    Double_t getMuE( int i );  
    Double_t getMuEta( int i );
    Int_t    getMuIsGlobalMuon( int i );
    Int_t    getMuIsTMLastStationAngTight( int i );
    Int_t    getMuIsTrackerMuon( int i );
    Double_t getMuIso03EmEt( int i );
    Double_t getMuIso03HadEt( int i );
    Double_t getMuIso03SumPt( int i );
    Double_t getMuNChi2( int i );
    Int_t    getMuNMatches( int i );
    Int_t    getMuNMuHits( int i );
    Int_t    getMuNPxHits( int i );
    Int_t    getMuNTkHits( int i );
    Double_t getMuPt( int i );
    Double_t getMuPtE( int i );          
    Double_t getMuPx( int i );
    Double_t getMuPy( int i );
    Double_t getMuPz( int i );

    //FIXME
//    Double_t  getNJets();
//    Double_t getJE( int i );
//    Double_t getJEMfrac( int i );
//    Double_t getJEta( int i );
//    Double_t getJID_ECALTow( int i );
//    Double_t getJID_HCALTow( int i );
//    Double_t getJID_HPD( int i );
//    Double_t getJID_RBX( int i );
//    Double_t getJID_n90Hits( int i );
//    Double_t getJID_resEMF( int i );
//    Int_t    getJNConstituents( int i );
//    Double_t getJPt( int i );
//    Double_t getJPx( int i );
//    Double_t getJPy( int i );
//    Double_t getJPz( int i );

    Double_t  getPFNJets();
    Double_t getPFJChEmfrac( int i );
    Double_t getPFJChHadfrac( int i );
    Double_t getPFJE( int i );
    Double_t getPFJEta( int i );
    Int_t    getPFJNConstituents( int i );
    Double_t getPFJNeuEmfrac( int i );
    Double_t getPFJNeuHadfrac( int i );
    Double_t getPFJPt( int i );
    Double_t getPFJPx( int i );
    Double_t getPFJPy( int i );
    Double_t getPFJPz( int i );
    Double_t getPFJbTagProbTkCntHighEff( int i );      

protected:
	ETHZNtupleReader* _reader;
};

class ETHZNtupleSelector: public TObject {
public:
	ETHZNtupleSelector( int argc, char** argv );
	virtual ~ETHZNtupleSelector();
	std::ostream& Debug(int level);

	virtual void Start();
	virtual void Analyze();
	virtual void Finish();
	virtual void Book() = 0;
	virtual void SaveConfig();
	virtual void BeginJob() = 0;
	virtual void Loop();
	virtual void Process( Long64_t iEvent ) = 0;
	virtual void EndJob() = 0;

	virtual Bool_t Notify();

	void SetInputFile( const std::string& path ) { _inputFile = path; }
	void SetOutputFile( const std::string& path ) { _outputFile = path; }
protected:

	// configuration file
	CommandLine _config;

	TTree* getChain() { return _reader->fChain;}
	Int_t  getEntry( Long64_t entry ) { return _reader->GetEntry( entry ); }
	ETHZEvent* getEvent() { return _event; }


	int _debugLvl;
	std::string _treeName;
	std::string _inputFile;
	std::string _outputFile;
	long long _firstEvent;
	long long _nEvents;

	long long   _currentEvent;
	TDirectory* _rootConfigDir;
	TEnv*       _rootConfigMap;

	TTree* fSkimmedTree;
	TFile* fSkimmedFile;
	std::string _skimmedTreeName;

	TBenchmark _benchmark;

private:
	ETHZEvent* _event;
	ETHZNtupleReader* _reader;
};

#endif /* ETHZNTUPLESELECTOR_H_ */
