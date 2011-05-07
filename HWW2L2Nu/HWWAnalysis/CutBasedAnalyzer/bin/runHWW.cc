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
#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include <TSystem.h>

int main( int argc, char **argv ) {

    // load framework libraries
    gSystem->Load( "libFWCoreFWLite" );
    AutoLibraryLoader::enable();
	try {
		HWWAnalyzer analyzer(argc,argv);
		analyzer.Analyze();

	} catch ( std::exception &e ) {
		std::cout << "---" << TermColors::kRed << " Caught exception " << TermColors::kReset << e.what() << std::endl;
        return -1;
	}
	return 0;
}
