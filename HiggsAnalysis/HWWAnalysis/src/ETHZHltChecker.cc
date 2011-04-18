/*
 * ETHZHltChecker.cpp
 *
 *  Created on: Apr 8, 2011
 *      Author: ale
 */

#include "ETHZHltChecker.h"
#include <TTree.h>
#include <TFile.h>
#include "Tools.h"
#include <iostream>

//_____________________________________________________________________________
ETHZHltChecker::ETHZHltChecker() : _chain(0x0){
	// TODO Auto-generated constructor stub
}

//_____________________________________________________________________________
ETHZHltChecker::~ETHZHltChecker() {
	// TODO Auto-generated destructor stub
}

void ETHZHltChecker::print() {

	std::map<std::string,HLTSet>::iterator it;
	for ( it = _hltMap.begin(); it != _hltMap.end(); ++it ){
		std::cout << "--- HLTSet " << it->first << " : " << it->second.status << std::endl;
		std::vector<std::string>& paths = it->second.paths;
		std::vector<std::string>::iterator pt;
		for ( pt = paths.begin(); pt != paths.end(); ++pt)
			std::cout << "   . " << *pt << std::endl;

	}
}
//_____________________________________________________________________________
void ETHZHltChecker::connect( TTree* chain, const std::string& runInfoName ) {
	_chain = chain;
	_runInfoName = runInfoName;

	if ( !_chain )
		THROW_RUNTIME("Input Chain is "<< _chain );

	if ( _chain->GetCurrentFile() ) {
		std::cout << "- HltChecker: open file found. Updating ids" << std::endl;
		updateIds();
	}
}

//_____________________________________________________________________________
void ETHZHltChecker::updateIds() {

	if ( !_chain )
		//THROW_RUNTIME("No input chain defined!")
		// no chain no party
		return;

//		std::cout << "Chain" << _chain << "GetCurrentFile " << _chain->GetCurrentFile() << std::endl;
	if ( !_chain->GetCurrentFile() ) {
		std::cout << "No file defined" << std::endl;
		return;
	}

	_labels.clear();

	std::vector<std::string>*names = 0;
	TTree* runInfo = (TTree*)(_chain->GetCurrentFile()->Get(_runInfoName.c_str()));
	runInfo->SetBranchAddress("HLTNames",&names);
	runInfo->GetEntry(0);
	_labels = *names;

	_matchIds.clear();
	_rejectIds.clear();

	std::map<std::string,HLTSet>::iterator it;
	std::vector<std::string>::iterator jt;

	for( it = _hltMap.begin(); it != _hltMap.end(); ++it) {
//		std::cout << it->first << "  " << it->second.status << std::endl;
		std::vector<unsigned int>* ids;
		switch( it->second.status ) {
		case kIgnore:
			ids = 0x0;
			break;
		case kMatch:
			ids = &_matchIds;
			break;
		case kReject:
			ids = &_rejectIds;
			break;
		default:
			THROW_RUNTIME("Corrupted hlt path set state " << it->second.status);
		}

		// ignore
		if ( !ids ) continue;

		std::vector<std::string>& paths =  it->second.paths;

		for( unsigned int i(0); i < _labels.size(); ++i) {
			for( jt = paths.begin(); jt != paths.end(); ++jt) {
				if( *jt ==  _labels[i] )
					ids->push_back(i);
			}
		}
	}
	std::vector<unsigned int>::iterator kt;
	std::cout << "-- matchId : ";
	for ( kt = _matchIds.begin(); kt != _matchIds.end(); ++kt) {
		std::cout << *kt << ", ";
	}
	std::cout << std::endl;

	std::cout << "-- rejectId : ";
	for ( kt = _rejectIds.begin(); kt != _rejectIds.end(); ++kt) {
		std::cout << *kt << ", ";
	}
	std::cout << std::endl;

}

//_____________________________________________________________________________
bool ETHZHltChecker::match( const int hltResults[] ) {

	bool match = false;
	bool reject = false;

	for ( unsigned int i(0); i<_matchIds.size(); ++i)
		match |= hltResults[_matchIds[i]];

	for ( unsigned int i(0); i<_rejectIds.size(); ++i)
		reject |= hltResults[_rejectIds[i]];

	return ( match && !reject );
}

//_____________________________________________________________________________
void ETHZHltChecker::add( const std::string& mode, const std::string& path ) {
	 HLTSet& set = _hltMap[mode];
	 set.paths.push_back(path);
}

//_____________________________________________________________________________
void ETHZHltChecker::set( const std::string& mode, int state) {
	std::map<std::string,HLTSet>::iterator it = _hltMap.find(mode);

	if ( it == _hltMap.end() )
		THROW_RUNTIME("Mode "+mode+" not found");

	it->second.status = state;
}
