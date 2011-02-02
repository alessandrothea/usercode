/*
 * UserAnalyzer.h
 *
 *  Created on: Nov 26, 2010
 *      Author: ale
 */

#ifndef USERANALYZER_H_
#define USERANALYZER_H_

#include "CommandLine.h"
#include <TObject.h>
#include <TBenchmark.h>

class TChain;
class TFile;

class UserAnalyzer : public TObject {
public:
	UserAnalyzer( int argc, char** argv );
	virtual ~UserAnalyzer();

	virtual void Start();
	virtual void Analyze();
	virtual void Finish();

	virtual void Book() = 0;
	virtual void BeginJob() = 0;
	virtual void Loop();
	virtual void Process( Long64_t iEvent ) = 0;
	virtual void EndJob() = 0;
	virtual Bool_t Notify();

protected:
	std::string _treeName;
	std::string _inputFile;
	std::string _outputFile;
	long long _firstEvent;
	long long _nEvents;

	CommandLine _config;

	TBenchmark _benchmark;

	TChain* _chain;
	TFile* _output;
};

#endif /* USERANALYZER_H_ */
