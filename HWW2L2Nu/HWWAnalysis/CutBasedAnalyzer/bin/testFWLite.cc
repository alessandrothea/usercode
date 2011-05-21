/*
 * runHWW.cc
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#include <iostream>
#include <fstream>
#include <stdexcept>
#include <vector>
// #include "HWWAnalysis/CutBasedAnalyzer/interface/HWWAnalyzer.h"
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Utils/interface/StringObjectFunction.h"

#include "HWWAnalysis/Misc/interface/Tools.h"
#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include "FWCore/Utilities/interface/Parse.h"
#include "FWCore/PythonParameterSet/interface/MakeParameterSets.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include <Reflex/Object.h>
#include <TSystem.h>
#include <TChain.h>

int main( int argc, char **argv ) {

    // load framework libraries
    gSystem->Load( "libFWCoreFWLite" );
    AutoLibraryLoader::enable();
    
    if ( argc < 2 )
        THROW_RUNTIME("No file defined"); 

    if ( argv[1][1] == '-' )
        THROW_RUNTIME("Usage " << argv[0] << " config.py opts")
    
    std::string cfgStr = edm::read_whole_file( argv[1] );

//     std::cout << argc << std::endl;
    std::vector<std::string> args;
    for ( int i=1; i<argc; ++i ) 
        args.push_back(argv[i]);

    std::stringstream header;
    header << "import sys\n";
    header << "sys.argv = []\n";
    for ( unsigned int i(0); i<args.size(); ++i) 
        header << "sys.argv.append('" << args[i] << "')\n";
    
    
//     std::cout << header.str() << std::endl;

    cfgStr = header.str()+cfgStr;
//     std::cout << cfgStr << std::endl;
    

    boost::shared_ptr<edm::ParameterSet> pyConfig = edm::readPSetsFrom(cfgStr);
    if( !pyConfig->existsAs<edm::ParameterSet>("process") ){
        THROW_RUNTIME(" ERROR: ParametersSet 'process' is missing in your configuration file");
    }

    edm::ParameterSet config =  pyConfig->getParameter<edm::ParameterSet>("process");
    std::cout << config << std::endl;

    std::vector<std::string> inputFiles = config.getParameter<std::vector<std::string> >("inputFiles");

    TChain c("hwwAnalysis");

    std::vector<std::string>::iterator it;
    for ( it = inputFiles.begin(); it != inputFiles.end(); ++it )
        c.Add(it->c_str());

    HWWNtuple* nt = 0x0;
    c.SetBranchAddress("nt",&nt);
    
    std::cout << c.GetEntries() << std::endl;

    StringCutObjectSelector<HWWNtuple> testCut("mll > 70 ");
    StringCutObjectSelector<HWWNtuple> testBit("test_bit(tags,4) ");
    StringObjectFunction<HWWNtuple> testFun("mll");
    Long64_t nEntries = c.GetEntriesFast();
    nEntries = 100;
    for ( Long64_t i(0); i<nEntries; ++i) {
        c.GetEntry(i);
        std::cout << i << " - " << nt->mll << " / " << testCut(*nt) << '|' << testBit(*nt) <<  " mll:" << testFun(*nt) << std::endl; 
    }
    
	return 0;
}
