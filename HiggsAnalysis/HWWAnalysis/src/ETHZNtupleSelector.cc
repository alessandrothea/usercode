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
ETHZNtupleSelector::ETHZNtupleSelector( int argc, char** argv ) : _firstEvent(0), _nEvents(0),
	fSkimmedFile(0x0), fSkimmedTree(0x0) {
	// TODO Auto-generated constructor stub

	_config.parse(argc, argv);

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

}

//_____________________________________________________________________________
void ETHZNtupleSelector::Analyze() {
	Start();
	Loop();
	Finish();
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

	// initialize the input
	Init( chain );
	fChain->SetNotify(this);
	std::cout << " input tree build: " << fChain->GetEntries() << " found" << std::endl;
	if ( fChain->GetEntriesFast() == 0 ){
		THROW_RUNTIME("No events in the tree. Check the file list and the tree name?");
	}

	// open the output file
	fSkimmedFile = new TFile(_outputFile.c_str(), "recreate");
	if ( !fSkimmedFile->IsOpen( ) ){
		THROW_RUNTIME(std::string("File ") + _outputFile + " not found");
	}

	// book the new tree
	fSkimmedTree = new TTree(_skimmedTreeName.c_str(),_skimmedTreeName.c_str());
	Book();
	BeginJob();

}

//_____________________________________________________________________________
void ETHZNtupleSelector::Loop() {
	// loop over the events (to be moved to the parent class?)
	Long64_t lastEvent = _firstEvent + _nEvents;
	if ( _nEvents == 0 ) {
		// run over all the events in the dataset
		lastEvent = fChain->GetEntriesFast();
		_nEvents = fChain->GetEntriesFast();
	} else if ( lastEvent > fChain->GetEntriesFast() ) {
		// if last event is larger of the number of events in the chain, adjust it to the maximum number
		std::cout << "Last computed event is higher than the number of available events ("
				<< lastEvent << " > " << fChain->GetEntriesFast() << ")." << std::endl;
		lastEvent = fChain->GetEntriesFast();
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
		Process( i );
	}
}

//_____________________________________________________________________________
Bool_t ETHZNtupleSelector::Notify() {
	if (  fChain->GetCurrentFile() ) {
		std::cout << "--- Notify(): New file opened: "<<  fChain->GetCurrentFile()->GetName() << std::endl;
	} else {
		std::cout << "--- Notify(): No file opened yet" << std::endl;
	}
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

