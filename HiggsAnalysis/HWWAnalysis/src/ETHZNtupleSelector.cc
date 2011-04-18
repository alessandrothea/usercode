/*
 * ETHZNtupleSelector.cpp
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#include "ETHZNtupleSelector.h"
#include <iostream>
#include <fstream>
#include <stdexcept>
#include <algorithm>
#include <TBenchmark.h>
#include "Tools.h"


//_____________________________________________________________________________
Double_t ETHZEvent::getGenMET() { return _reader->GenMET;}
  Int_t* ETHZEvent::getHLTResults() { return _reader->HLTResults;}

Double_t ETHZEvent::getRun() { return _reader->Run;}
Double_t ETHZEvent::getEvent() { return _reader->Event;}
Double_t ETHZEvent::getLumiSection() { return _reader->LumiSection;}
Double_t ETHZEvent::getPrimVtxx() { return _reader->PrimVtxx;}
Double_t ETHZEvent::getPrimVtxy() { return _reader->PrimVtxy;}
Double_t ETHZEvent::getNVrtx() { return _reader->NVrtx;}
Double_t ETHZEvent::getTCMET() { return _reader->TCMET;}
Double_t ETHZEvent::getTCMETphi() { return _reader->TCMETphi;}
Double_t ETHZEvent::getPFMET() { return _reader->PFMET;}
Double_t ETHZEvent::getPFMETphi() { return _reader->PFMETphi;}
//Double_t ETHZEvent::getSumEt() { return _reader->SumEt;}

//Double_t ETHZEvent::getMuCorrMET() { return _reader->MuCorrMET;}
//Double_t ETHZEvent::getMuCorrMETphi() { return _reader->MuCorrMETphi;}

Double_t ETHZEvent::getPrimVtxNdof() { return _reader->PrimVtxNdof;}
   Int_t ETHZEvent::getPrimVtxGood() { return _reader->PrimVtxGood; }
   Int_t ETHZEvent::getPrimVtxIsFake() { return _reader->PrimVtxIsFake;}
Double_t ETHZEvent::getPrimVtxRho() { return _reader->PrimVtxRho;}
Double_t ETHZEvent::getPrimVtxz() { return _reader->PrimVtxz;}


	// apply the correction for the endcaps

   Int_t ETHZEvent::getNEles() { return _reader->NEles;}

Double_t ETHZEvent::getElDeltaEtaSuperClusterAtVtx(int i) { return _reader->ElDeltaEtaSuperClusterAtVtx[i];}
Double_t ETHZEvent::getElDeltaPhiSuperClusterAtVtx(int i) { return _reader->ElDeltaPhiSuperClusterAtVtx[i];}
Double_t ETHZEvent::getElPt(int i) { return _reader->ElPt[i];}
Double_t ETHZEvent::getElSCEta(int i) { return _reader->ElSCEta[i];}
Double_t ETHZEvent::getElCaloEnergy(int i) { return _reader->ElCaloEnergy[i];}
   Int_t ETHZEvent::getElCharge(int i) { return _reader->ElCharge[i];}
Double_t ETHZEvent::getElConvPartnerTrkDCot(int i) { return _reader->ElConvPartnerTrkDCot[i];}
Double_t ETHZEvent::getElConvPartnerTrkDist(int i) { return _reader->ElConvPartnerTrkDist[i];}
Double_t ETHZEvent::getElD0PV(int i) { return _reader->ElD0PV[i];}
Double_t ETHZEvent::getElDR03EcalRecHitSumEt(int i) { return _reader->ElDR03EcalRecHitSumEt[i];}
Double_t ETHZEvent::getElDR03HcalTowerSumEt(int i) { return _reader->ElDR03HcalTowerSumEt[i];}
Double_t ETHZEvent::getElDR03TkSumPt(int i) { return _reader->ElDR03TkSumPt[i];}
Double_t ETHZEvent::getElDR04EcalRecHitSumEt(int i) { return _reader->ElDR04EcalRecHitSumEt[i];}
Double_t ETHZEvent::getElDR04HcalTowerSumEt(int i) { return _reader->ElDR04HcalTowerSumEt[i];}
Double_t ETHZEvent::getElDzPV(int i) { return _reader->ElDzPV[i];}
Double_t ETHZEvent::getElE(int i) { return _reader->ElE[i];}
Double_t ETHZEvent::getElEta(int i) { return _reader->ElEta[i];}
Double_t ETHZEvent::getElHcalOverEcal(int i) { return _reader->ElHcalOverEcal[i];}
   Int_t ETHZEvent::getElNumberOfMissingInnerHits(int i) { return _reader->ElNumberOfMissingInnerHits[i];}
Double_t ETHZEvent::getElPx(int i) { return _reader->ElPx[i];}
Double_t ETHZEvent::getElPy(int i) { return _reader->ElPy[i];}
Double_t ETHZEvent::getElPz(int i) { return _reader->ElPz[i];}
Double_t ETHZEvent::getElSigmaIetaIeta(int i) { return _reader->ElSigmaIetaIeta[i];}

	Int_t ETHZEvent::getNMus() { return _reader->NMus;}

   Int_t ETHZEvent::getMuCharge(int i) { return _reader->MuCharge[i];}
Double_t ETHZEvent::getMuD0PV(int i) { return _reader->MuD0PV[i];}
Double_t ETHZEvent::getMuDzPV(int i) { return _reader->MuDzPV[i];}
Double_t ETHZEvent::getMuE(int i) { return _reader->MuE[i];}  
Double_t ETHZEvent::getMuEta(int i) { return _reader->MuEta[i];}
   Int_t ETHZEvent::getMuIsGlobalMuon(int i) { return _reader->MuIsGlobalMuon[i];}
   Int_t ETHZEvent::getMuIsTMLastStationAngTight(int i) { return _reader->MuIsTMLastStationAngTight[i];}
   Int_t ETHZEvent::getMuIsTrackerMuon(int i) { return _reader->MuIsTrackerMuon[i];}
Double_t ETHZEvent::getMuIso03EmEt(int i) { return _reader->MuIso03EmEt[i];}
Double_t ETHZEvent::getMuIso03HadEt(int i) { return _reader->MuIso03HadEt[i];}
Double_t ETHZEvent::getMuIso03SumPt(int i) { return _reader->MuIso03SumPt[i];}
Double_t ETHZEvent::getMuNChi2(int i) { return _reader->MuNChi2[i];}
   Int_t ETHZEvent::getMuNMatches(int i) { return _reader->MuNMatches[i];}
   Int_t ETHZEvent::getMuNMuHits(int i) { return _reader->MuNMuHits[i];}
   Int_t ETHZEvent::getMuNPxHits(int i) { return _reader->MuNPxHits[i];}
   Int_t ETHZEvent::getMuNTkHits(int i) { return _reader->MuNTkHits[i];}
Double_t ETHZEvent::getMuPt(int i) { return _reader->MuPt[i];}
Double_t ETHZEvent::getMuPtE(int i) { return _reader->MuPtE[i];}          
Double_t ETHZEvent::getMuPx(int i) { return _reader->MuPx[i];}
Double_t ETHZEvent::getMuPy(int i) { return _reader->MuPy[i];}
Double_t ETHZEvent::getMuPz(int i) { return _reader->MuPz[i];}


//FIXME Jets
//Double_t  ETHZEvent::getNJets() { return _reader->NJets; }
//
//Double_t ETHZEvent::getJE(int i) { return _reader->JE[i];}
//Double_t ETHZEvent::getJEMfrac(int i) { return _reader->JEMfrac[i];}
//Double_t ETHZEvent::getJEta(int i) { return _reader->JEta[i];}
//Double_t ETHZEvent::getJID_ECALTow(int i) { return _reader->JID_ECALTow[i];}
//Double_t ETHZEvent::getJID_HCALTow(int i) { return _reader->JID_HCALTow[i];}
//Double_t ETHZEvent::getJID_HPD(int i) { return _reader->JID_HPD[i];}
//Double_t ETHZEvent::getJID_RBX(int i) { return _reader->JID_RBX[i];}
//Double_t ETHZEvent::getJID_n90Hits(int i) { return _reader->JID_n90Hits[i];}
//Double_t ETHZEvent::getJID_resEMF(int i) { return _reader->JID_resEMF[i];}
//   Int_t ETHZEvent::getJNConstituents(int i) { return _reader->JNConstituents[i];}
//Double_t ETHZEvent::getJPt(int i) { return _reader->JPt[i];}
//Double_t ETHZEvent::getJPx(int i) { return _reader->JPx[i];}
//Double_t ETHZEvent::getJPy(int i) { return _reader->JPy[i];}
//Double_t ETHZEvent::getJPz(int i) { return _reader->JPz[i];}



// PFJets
Double_t  ETHZEvent::getPFNJets() { return _reader->PFNJets; }

Double_t ETHZEvent::getPFJChEmfrac(int i) { return _reader->PFJChEmfrac[i];}
Double_t ETHZEvent::getPFJChHadfrac(int i) { return _reader->PFJChHadfrac[i];}
Double_t ETHZEvent::getPFJE(int i) { return _reader->PFJE[i];}
Double_t ETHZEvent::getPFJEta(int i) { return _reader->PFJEta[i];}
   Int_t ETHZEvent::getPFJNConstituents(int i) { return _reader->PFJNConstituents[i];}
Double_t ETHZEvent::getPFJNeuEmfrac(int i) { return _reader->PFJNeuEmfrac[i];}
Double_t ETHZEvent::getPFJNeuHadfrac(int i) { return _reader->PFJNeuHadfrac[i];}
Double_t ETHZEvent::getPFJPt(int i) { return _reader->PFJPt[i];}
Double_t ETHZEvent::getPFJPx(int i) { return _reader->PFJPx[i];}
Double_t ETHZEvent::getPFJPy(int i) { return _reader->PFJPy[i];}
Double_t ETHZEvent::getPFJPz(int i) { return _reader->PFJPz[i];}
Double_t ETHZEvent::getPFJbTagProbTkCntHighEff(int i) { return _reader->PFJbTagProbTkCntHighEff[i];}      


//_____________________________________________________________________________
ETHZNtupleSelector::ETHZNtupleSelector( int argc, char** argv ) : _firstEvent(0), _nEvents(0),_currentEvent(0),
	fSkimmedTree(0x0), fSkimmedFile(0x0) {
	// TODO Auto-generated constructor stub

	// reader
	_reader = new ETHZNtupleReader();
	// and event interface
	_event = new ETHZEvent( _reader );

	_rootConfigMap = new TEnv();

	_config.parse(argc, argv);

	_debugLvl    = _config.getValue<int>("Selector.debugLevel",0);
	_treeName	 = _config.getValue<std::string>("Selector.treeName");
	_inputFile   = _config.getValue<std::string>("Selector.inputFile");
	_outputFile  = _config.getValue<std::string>("Selector.outputFile");
	_firstEvent  = _config.getValue<long long>("Selector.firstEvent");
	_nEvents     = _config.getValue<long long>("Selector.nEvents");
	_skimmedTreeName = _config.getValue<std::string>("Selector.skimmedTreeName");

}

//_____________________________________________________________________________
ETHZNtupleSelector::~ETHZNtupleSelector() {
	// TODO Auto-generated destructor stub
	delete _rootConfigMap;
	delete _reader;

}

//_____________________________________________________________________________
std::ostream& ETHZNtupleSelector::Debug(int level) {
	static std::ostream rc(std::clog.rdbuf());
	rc.rdbuf(level <= _debugLvl ? std::clog.rdbuf() : 0);
	return rc;
}

//_____________________________________________________________________________
void ETHZNtupleSelector::Analyze() {
	Start();
	Loop();
	Finish();
}

//_____________________________________________________________________________
void ETHZNtupleSelector::SaveConfig() {
	Debug(0) << "Adding configuration map" << std::endl;

	_rootConfigDir->cd();
    std::map<std::string, std::string> pars = _config.getOptionMap();
    std::map<std::string, std::string>::iterator it;
    for( it = pars.begin(); it != pars.end(); ++it) {
    	_rootConfigMap->SetValue(it->first.c_str(),it->second.c_str());
    }

    _rootConfigDir->cd();
    _rootConfigMap->Write("selectorConfig");

}

//_____________________________________________________________________________
void ETHZNtupleSelector::Book(){
	std::cout << __FUNCTION__ << " not implemented" << std::endl;
}

//_____________________________________________________________________________
void ETHZNtupleSelector::Start() {
	std::cout << "--- " << TermColors::kLightBlue << "Start" << TermColors::kReset << " - " << TDatime().AsString() << std::endl;
	_benchmark.Start("MainLoop");
	if (!_config.check() )
		THROW_RUNTIME("Broken configuration")
	_config.print();

	if ( ::access(_inputFile.c_str(), F_OK ) )
		THROW_RUNTIME("Input file " << _inputFile << " not accessible");

	std::string dotRoot = ".root";
	std::string dotInput = ".input";
	std::string dotDcap = ".dcap";

	// build the TChain
	TChain* chain = new TChain(_treeName.c_str());

	// check if it's a single rootfile or a list
	if ( std::equal(dotRoot.rbegin(), dotRoot.rend(),_inputFile.rbegin()) ) {
		// single rootfile
		std::cout << "Input file " << _inputFile << " is a ROOTFile" << std::endl;
		chain->AddFile(_inputFile.c_str());

	} else if ( std::equal(dotInput.rbegin(), dotInput.rend(),_inputFile.rbegin())
		|| std::equal(dotDcap.rbegin(), dotDcap.rend(),_inputFile.rbegin()) ) {
		// proper list of files
		std::cout << "Input file " << _inputFile << " is a list of ROOTFiles" << std::endl;

		// read the list of files
		ifstream fileList(_inputFile.c_str(), ifstream::in);
		if ( !fileList.is_open() )
			THROW_RUNTIME("File " << _inputFile << " not found");

		std::string line;
		while( fileList.good() ) {
			getline(fileList, line);
			// clean up the line using the streamer
			std::stringstream ss(line);
			std::string filepath;

			ss >> filepath;
			// if comment, continue
			if ( filepath.empty() || filepath[0] == '#') continue;
			chain->AddFile(line.c_str());
			std::cout << "Adding "<< filepath << std::endl;
		}

	} else {
		THROW_RUNTIME("Input file extension  not supported" << _inputFile);
	}



	// open the output file
	fSkimmedFile = new TFile(_outputFile.c_str(), "recreate");
	if ( !fSkimmedFile->IsOpen( ) ){
		THROW_RUNTIME(std::string("File ") + _outputFile + " not found");
	}

	// book the new tree before booking the rest
	fSkimmedTree = new TTree(_skimmedTreeName.c_str(),_skimmedTreeName.c_str());

	_rootConfigDir = fSkimmedFile->mkdir("config");
	// call book from child classes
	Book();
	SaveConfig();

	// initialize the input _after booking_ otherwise it could mess stuff up in Notify
	_reader->Init( chain );
	this->getChain()->SetNotify(this);
	std::cout << " input tree build: " << this->getChain()->GetEntries() << " found" << std::endl;
	if ( this->getChain()->GetEntriesFast() == 0 ){
		THROW_RUNTIME("No events in the tree. Check the file list and the tree name?");
	}

	BeginJob();

}

//_____________________________________________________________________________
void ETHZNtupleSelector::Loop() {
	// loop over the events (to be moved to the parent class?)
	Long64_t lastEvent = _firstEvent + _nEvents;
	if ( _nEvents == 0 ) {
		// run over all the events in the dataset
		lastEvent = this->getChain()->GetEntriesFast();
		_nEvents = this->getChain()->GetEntriesFast();
	} else if ( lastEvent > this->getChain()->GetEntriesFast() ) {
		// if last event is larger of the number of events in the chain, adjust it to the maximum number
		std::cout << "Last computed event is higher than the number of available events ("
				<< lastEvent << " > " << this->getChain()->GetEntriesFast() << ")." << std::endl;
		lastEvent = this->getChain()->GetEntriesFast();
		_nEvents = lastEvent-_firstEvent;
		std::cout << "lastEvent set to " << std::endl;
	}
	TStopwatch watch;
	for (Long64_t i=_firstEvent; i<lastEvent; ++i) {
		if ( i%1000 == 0 ) {
			watch.Stop();
			std::cout << "i = " << i << " RealTime : " << watch.RealTime() << " Cpu : " << watch.CpuTime() << std::endl;
			watch.Continue();
		}
		_currentEvent = i;
		Process( _currentEvent );
	}
}

//_____________________________________________________________________________
Bool_t ETHZNtupleSelector::Notify() {
	if (  this->getChain()->GetCurrentFile() ) {
		std::cout << "--- Notify(): New file opened: "<<  this->getChain()->GetCurrentFile()->GetName() << std::endl;
	} else {
		std::cout << "--- Notify(): No file opened yet" << std::endl;
	}

    return kTRUE;
}

//_____________________________________________________________________________
void ETHZNtupleSelector::Finish() {
	EndJob();
	fSkimmedFile->Write();
	fSkimmedTree->AutoSave();
	fSkimmedFile->Close();
	std::cout << "--- " << TermColors::kLightBlue << "Finish" << TermColors::kReset << " - "<< TDatime().AsString() << std::endl;
	_benchmark.Stop("MainLoop");
}

