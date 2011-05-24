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
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Utils/interface/StringObjectFunction.h"

#include "HWWAnalysis/Misc/interface/Tools.h"
#include "HWWAnalysis/CutBasedAnalyzer/interface/PsetReader.h"
#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include <Reflex/Object.h>
#include <TSystem.h>
#include <TChain.h>

typedef std::vector<std::pair<std::string, StringCutObjectSelector<HWWNtuple> > > CutVector;
typedef std::vector<std::pair<std::string, StringObjectFunction<HWWNtuple> > >    VarVector;

int main( int argc, char **argv ) {

    // load framework libraries
    gSystem->Load( "libFWCoreFWLite" );
    AutoLibraryLoader::enable();
    
    PsetReader reader("process");

    edm::ParameterSet config = reader.read( argc, argv );
    std::cout << config << std::endl;


    std::vector<std::string> inputFiles = config.getParameter<std::vector<std::string> >("inputFiles");

    TChain c("hwwAnalysis");

    std::vector<std::string>::iterator it;
    for ( it = inputFiles.begin(); it != inputFiles.end(); ++it )
        c.Add(it->c_str());

    edm::VParameterSet cutPars = config.getParameter<edm::VParameterSet>("cuts");
    edm::VParameterSet varPars = config.getParameter<edm::VParameterSet>("variables");

    edm::VParameterSet::iterator itPset;

    CutVector cutFlow; 

    for( itPset = cutPars.begin(); itPset != cutPars.end(); ++itPset) {
        std::string label = itPset->getParameter<std::string>("label");
        std::string cut   = itPset->getParameter<std::string>("cut");
        cutFlow.push_back( std::make_pair( label,  StringCutObjectSelector<HWWNtuple>(cut) ) );
    }

    VarVector vars;
    for( itPset = varPars.begin(); itPset != varPars.end(); ++itPset) {
        std::string label = itPset->getParameter<std::string>("label");
        vars.push_back( std::make_pair( label, StringObjectFunction<HWWNtuple>(label) ) ); 
    }

   


    HWWNtuple* nt = 0x0;
    c.SetBranchAddress("nt",&nt);
    
    std::cout << c.GetEntries() << std::endl;

    StringCutObjectSelector<HWWNtuple> testCut("mll > 70 ");
    StringCutObjectSelector<HWWNtuple> testBit("test_bit(tags,4) ");
    StringObjectFunction<HWWNtuple> testFun("mll");
    Long64_t nEntries = c.GetEntriesFast();
    nEntries = 100;
    
    CutVector::iterator cut;
    VarVector::iterator var;

    for ( Long64_t i(0); i<nEntries; ++i) {
        c.GetEntry(i);

        std::stringstream ss;
        for ( var = vars.begin(); var != vars.end(); ++var ) {
            ss << var->first << ": " << var->second(*nt);
        }
        ss << " >-< ";
        for ( cut = cutFlow.begin(); cut != cutFlow.end(); ++cut ) {
            ss << cut->first << ": " << cut->second(*nt) << ' | ';
        } 
        std::cout << "+ " << ss.str() << std::endl;

//         std::cout << i << " - " << nt->mll << " / " << testCut(*nt) << '|' << testBit(*nt) <<  " mll:" << testFun(*nt) << std::endl; 
    }
    
	return 0;
}
