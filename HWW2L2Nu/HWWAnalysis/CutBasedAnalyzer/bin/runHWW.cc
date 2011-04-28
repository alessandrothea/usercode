/*
 * runHWW.cc
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#include <iostream>
#include <stdexcept>
#include "HWWAnalysis/CutBasedAnalyzer/interface/HWWAnalyzer.h"
#include "HWWAnalysis/CutBasedAnalyzer/interface/CommandLine.h"
#include "HWWAnalysis/CutBasedAnalyzer/interface/Tools.h"

int main( int argc, char **argv ) {

	try {
		HWWAnalyzer analyzer(argc,argv);
		analyzer.Analyze();

	} catch ( std::exception &e ) {
		std::cout << "---" << TermColors::kRed << " Caught exception " << TermColors::kReset << e.what() << std::endl;
	}
	return 0;
}
