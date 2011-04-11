/*
 * ETHZHltChecker.h
 *
 *  Created on: Apr 8, 2011
 *      Author: ale
 */

#ifndef ETHZHLTCHECKER_H_
#define ETHZHLTCHECKER_H_

#include <string>
#include <map>
#include <vector>

class TTree;

class ETHZHltChecker {
public:
	ETHZHltChecker();
	virtual ~ETHZHltChecker();

	void connect( TTree* chain, const std::string& runInfoName );
	void add( const std::string& mode, const std::string& path );
	void set( const std::string& mode, int state);

	void updateIds();
	bool match( const int hltResults[] );
	void print();

	enum {
		kIgnore,
		kMatch,
		kReject
	};
protected:

	class HLTSet {
	public:
		HLTSet() : status(kIgnore) {}
		unsigned short status;
		std::vector<std::string> paths;
	};

	std::map<std::string, HLTSet > _hltMap;
	std::vector<unsigned int> _matchIds;
	std::vector<unsigned int> _rejectIds;
	std::vector<std::string> _labels;

	TTree* _chain;
	std::string _runInfoName;
};

#endif /* ETHZHLTCHECKER_H_ */
