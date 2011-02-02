/*
 * UserAnalyzer.cc
 *
 *  Created on: Nov 26, 2010
 *      Author: ale
 */

#include "UserAnalyzer.h"
#include <TChain.h>
#include <TFile.h>
#include <iostream>
#include <stdexcept>
#include <fstream>
#include "Tools.h"

//_____________________________________________________________________________
UserAnalyzer::UserAnalyzer( int argc, char** argv ) : _chain(0x0), _output(0x0) {
	// TODO Auto-generated constructor stub

	_config.parse(argc,argv);

	_treeName = _config.getValue<std::string>("UserAnalyzer.treeName");

	_inputFile = _config.getValue<std::string>("UserAnalyzer.inputFile");
	_outputFile = _config.getValue<std::string>("UserAnalyzer.outputFile");
	_firstEvent = _config.getValue<long long>("UserAnalyzer.firstEvent");
	_nEvents = _config.getValue<long long>("UserAnalyzer.nEvents");

}

//_____________________________________________________________________________
UserAnalyzer::~UserAnalyzer() {
	// TODO Auto-generated destructor stub
}

//_____________________________________________________________________________
Bool_t UserAnalyzer::Notify() {
	if (  _chain->GetCurrentFile() ) {
		std::cout << "--- Notify(): New file opened: "<<  _chain->GetCurrentFile()->GetName() << std::endl;
	} else {
		std::cout << "--- Notify(): No file opened yet" << std::endl;
	}
}

//_____________________________________________________________________________
void UserAnalyzer::Analyze() {
	Start();
	Loop();
	Finish();
}

//_____________________________________________________________________________
void UserAnalyzer::Start() {
	std::cout << "--- " << TermColors::kLightBlue << "Start" << TermColors::kReset << " - " << TDatime().AsString() << std::endl;
	_benchmark.Start("main");
	if (!_config.check() )
		THROW_RUNTIME("Broken configuration")
	_config.print();

	if ( ::access(_inputFile.c_str(), F_OK ) )
		THROW_RUNTIME("Input file " << _inputFile << " not accessible");

	std::string dotRoot = ".root";
	std::string dotInput = ".input";
	std::string dotDcap = ".dcap";

	// build the TChain
	_chain = new TChain(_treeName.c_str());

	// check if it's a single rootfile or a list
	if ( std::equal(dotRoot.rbegin(), dotRoot.rend(),_inputFile.rbegin()) ) {
		// single rootfile
		std::cout << "Input file " << _inputFile << " is a ROOTFile" << std::endl;
		_chain->AddFile(_inputFile.c_str());

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
			_chain->AddFile(line.c_str());
			std::cout << "Adding "<< filepath << std::endl;
		}

	} else {
		THROW_RUNTIME("Input file extension  not supported" << _inputFile);
	}

	_chain->SetNotify(this);
	std::cout << "Checking " << _inputFile << ": " <<_chain->GetEntries() << " events found" << std::endl;

	// open the new file
	if ( !_outputFile.empty() && !(_output = TFile::Open(_outputFile.c_str(),"recreate")) )
		THROW_RUNTIME("Could not open " << _outputFile);
	Book();
	BeginJob();
}

//_____________________________________________________________________________
void UserAnalyzer::Loop() {
	// loop over the events (to be moved to the parent class?)
	Long64_t lastEvent = _firstEvent + _nEvents;
	if ( _nEvents == 0 ) {
		// run over all the events in the dataset
		lastEvent = _chain->GetEntriesFast();
		_nEvents = _chain->GetEntriesFast();
	} else if ( lastEvent > _chain->GetEntriesFast() ) {
		// if last event is larger of the number of events in the chain, adjust it to the maximum number
		std::cout << "Last computed event is higher than the number of available events ("
				<< lastEvent << " > " << _chain->GetEntriesFast() << ")." << std::endl;
		lastEvent = _chain->GetEntriesFast();
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
void UserAnalyzer::Finish() {
	EndJob();
	_output->Write();
	_output->Close();
	std::cout << "--- " << TermColors::kLightBlue << "Finish" << TermColors::kReset << " - "<< TDatime().AsString() << std::endl;
	_benchmark.Stop("main");
}
