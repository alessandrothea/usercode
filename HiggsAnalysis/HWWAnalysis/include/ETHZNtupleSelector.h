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

class ETHZNtupleSelector: public ETHZNtupleReader, public TObject {
public:
	ETHZNtupleSelector( int argc, char** argv );
	virtual ~ETHZNtupleSelector();

	virtual void Start();
	virtual void Analyze();
	virtual void Finish();
	virtual void Book() = 0;
	virtual void BeginJob() = 0;
	virtual void Loop();
	virtual void Process( Long64_t iEvent ) = 0;
	virtual void EndJob() = 0;

	virtual Bool_t Notify();

	void SetInputFile( const std::string& path ) { _inputFile = path; }
	void SetOutputFile( const std::string& path ) { _outputFile = path; }
protected:

	void EnableBranches( char mode );
	void AddBranch( const std::string& name, unsigned short mode);
	// configuration file
	CommandLine _config;

	std::string _treeName;
	std::string _inputFile;
	std::string _outputFile;
	long long _firstEvent;
	long long _nEvents;

	long long _currentEvent;

	TTree* fSkimmedTree;
	TFile* fSkimmedFile;
	std::string _skimmedTreeName;

	TBenchmark _benchmark;

};

#endif /* ETHZNTUPLESELECTOR_H_ */
