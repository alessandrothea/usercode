/*
 * runHWW.cc
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#include <iostream>
#include <stdexcept>
#include "HWWSelectorB.h"
#include "Tools.h"
#include "CommandLine.h"

#include <bitset>

int main( int argc, char **argv ) {

//	for( int i=0; i<argc; ++i) {
//		std::cout << " " << i << " " << argv[i] <<std::endl;
//	}

	try {
		HWWSelectorB selector( argc, argv );
		selector.Analyze();
	} catch ( std::exception &e ) {
		std::cout << "---" << TermColors::kRed << " Caught exception " << TermColors::kReset << e.what() << std::endl;
		return -1;
	}
	return 0;
}
