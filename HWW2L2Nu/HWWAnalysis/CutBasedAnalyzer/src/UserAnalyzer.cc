/*
 * UserAnalyzer.cc
 *
 *  Created on: Nov 26, 2010
 *      Author: ale
 */

#include "HWWAnalysis/CutBasedAnalyzer/interface/UserAnalyzer.h"
#include <TChain.h>
#include <TFile.h>
#include <TMath.h>
#include <iostream>
#include <stdexcept>
#include <fstream>
#include "HWWAnalysis/Misc/interface/Tools.h"
#include "HWWAnalysis/CutBasedAnalyzer/interface/PsetReader.h"


using namespace std;
//_____________________________________________________________________________
UserAnalyzer::UserAnalyzer( int argc, char** argv ) : _chain(0x0), _output(0x0), _initialized(false) {
	// TODO Auto-generated constructor stub

    PsetReader reader("process");
	_config = reader.read(argc,argv);

	_treeName   = _config.getParameter<string>("treeName");

	_folder  = _config.getParameter<string>("folder");
	_inputFiles = _config.getParameter< vector<string> >("inputFiles");
	_outputFile = _config.getParameter<string>("outputFile");
	_firstEvent = _config.getParameter<long long>("firstEvent");
	_nEvents    = _config.getParameter<long long>("maxEvents");

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
    return true;
}

//_____________________________________________________________________________
void UserAnalyzer::Analyze() {
	Start();
	Loop();
	Finish();
}

//_____________________________________________________________________________
void UserAnalyzer::Start() {
	std::cout << "--- " << TermColors::kLightBlue << "Start" << TermColors::kReset << " - [" << TDatime().AsString() << "]" << std::endl;
	_benchmark.Start("main");

//     if ( ::access(_inputFile.c_str(), F_OK ) )
//         THROW_RUNTIME("Input file " << _inputFile << " not accessible");

	std::string dotRoot  = ".root";
//     std::string dotInput = ".input";
//     std::string dotDcap  = ".dcap";

	// build the TChain
	_chain = new TChain((_folder+'/'+_treeName).c_str());

    
    for( uint i(0); i<_inputFiles.size(); ++i )
        _chain->AddFile(_inputFiles[i].c_str());

	// check if it's a single rootfile or a list
//     if ( std::equal(dotRoot.rbegin(), dotRoot.rend(),_inputFile.rbegin()) ) {
//         // single rootfile
//         std::cout << "Input file " << _inputFile << " is a ROOTFile" << std::endl;
//         _chain->AddFile(_inputFile.c_str());

//     } else if ( std::equal(dotInput.rbegin(), dotInput.rend(),_inputFile.rbegin())
//         || std::equal(dotDcap.rbegin(), dotDcap.rend(),_inputFile.rbegin()) ) {
//         // proper list of files
//         std::cout << "Input file " << _inputFile << " is a list of ROOTFiles" << std::endl;

//         // read the list of files
//         ifstream fileList(_inputFile.c_str(), ifstream::in);
//         if ( !fileList.is_open() )
//             THROW_RUNTIME("File " << _inputFile << " not found");

//         std::string line;
//         while( fileList.good() ) {
//             getline(fileList, line);
//             // clean up the line using the streamer
//             std::stringstream ss(line);
//             std::string filepath;

//             ss >> filepath;
//             // if comment, continue
//             if ( filepath.empty() || filepath[0] == '#') continue;
//             _chain->AddFile(line.c_str());
//             std::cout << "Adding "<< filepath << std::endl;
//         }

//     } else {
//         THROW_RUNTIME("Input file extension  not supported" << _inputFile);
//     }

	_chain->SetNotify(this);

	// open the new file
	if ( !_outputFile.empty() && !(_output = TFile::Open(_outputFile.c_str(),"recreate")) )
		THROW_RUNTIME("Could not open " << _outputFile);
	Book();
	setInitialized();
	BeginJob();
}

//_____________________________________________________________________________
void UserAnalyzer::Loop() {

	std::cout << "Checking inpufiles: " <<_chain->GetEntries() << " events found" << std::endl;

	// loop over the events (to be moved to the parent class?)
	Long64_t lastEvent = _firstEvent + _nEvents;
	if ( _nEvents == -1 ) {
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
        if ( i==0 || ( TMath::FloorNint(i*100/(double)_nEvents) == TMath::CeilNint( (i-1)*100/(double)_nEvents) ) ) {
//         if ( i%1000 == 0 ) {
			watch.Stop();
            if ( i!=0 ) std::cout << '\r';
            int barLen = 100;
            int progress = TMath::Nint(i*barLen/(double)_nEvents);
            std::string bar(progress, '=');
            bar[progress-1] = '>';
            bar.resize(barLen,' ');

			std::cout << " |" << bar << " " << TMath::Nint(i*100/(double)_nEvents) << "% i = " << i << " RT: " << watch.RealTime() << " Cpu : " << watch.CpuTime() << std::flush;
			watch.Continue();
		}
		Process( i );
	}
    std::cout << std::endl;
}

//_____________________________________________________________________________
void UserAnalyzer::Finish() {
	EndJob();
	_output->Write();
	_output->Close();
	std::cout << "--- " << TermColors::kLightBlue << "Finish" << TermColors::kReset << " - " << _nEvents << " Events Processed - [" << TDatime().AsString() << "]"  << std::endl;
	_benchmark.Stop("main");
}
