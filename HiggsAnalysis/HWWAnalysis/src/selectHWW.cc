/*
 * runHWW.cc
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#include <iostream>
#include <stdexcept>
#include "HWWSelector.h"
#include "Tools.h"
#include "CommandLine.h"

#include <bitset>

int main( int argc, char **argv ) {

	for( int i=0; i<argc; ++i) {
		std::cout << " " << i << " " << argv[i] <<std::endl;
	}

//	std::bitset<8> mask(0x15);
//	std::bitset<8> word(0x77);
//
//	std::cout << "mask " << mask.to_string() << " word " << word.to_string() << std::endl;
//	std::cout << "test " << (mask & word).to_string() << " " << (( mask & word ) == mask)<< std::endl;
//	return 0;

	try {
		HWWSelector selector( argc, argv );
		selector.Analyze();
	} catch ( std::exception &e ) {
		std::cout << "---" << TermColors::kRed << " Caught exception " << TermColors::kReset << e.what() << std::endl;
	}
	return 0;
}
