/*
 * runHWW.cc
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#include <iostream>
#include <stdexcept>
#include "HWWAnalyzer.h"
#include "CommandLine.h"
#include "Tools.h"

int main( int argc, char **argv ) {

	try {
		HWWAnalyzer analyzer(argc,argv);
		analyzer.Analyze();

	} catch ( std::exception &e ) {
		std::cout << "---" << TermColors::kRed << " Caught exception " << TermColors::kReset << e.what() << std::endl;
		return -1;
	}
	return 0;
}
