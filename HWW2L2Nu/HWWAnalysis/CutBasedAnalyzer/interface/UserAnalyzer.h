/*
 * UserAnalyzer.h
 *
 *  Created on: Nov 26, 2010
 *      Author: ale
 */

#ifndef USERANALYZER_H_
#define USERANALYZER_H_

#include <TObject.h>
#include <TBenchmark.h>
#include "FWCore/ParameterSet/interface/ParameterSet.h"

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
	void setInitialized() { _initialized = true; }
	bool isInitialized() { return _initialized; }

	std::string _treeName;
	std::string _folder;
    std::vector<std::string> _inputFiles;
	std::string _outputFile;
	long long _firstEvent;
	long long _nEvents;

    edm::ParameterSet _config;

	TBenchmark _benchmark;

	TChain* _chain;
	TFile* _output;

private:
	bool _initialized;

};

#endif /* USERANALYZER_H_ */
