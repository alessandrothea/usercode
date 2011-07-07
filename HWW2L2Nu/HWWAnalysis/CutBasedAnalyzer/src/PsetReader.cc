#include "HWWAnalysis/CutBasedAnalyzer/interface/PsetReader.h"
#include "HWWAnalysis/Misc/interface/Tools.h"
#include "FWCore/PythonParameterSet/interface/MakeParameterSets.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/Parse.h"
#include <sstream>
#include "boost/algorithm/string/predicate.hpp"

//______________________________________________________________________________
PsetReader::PsetReader( const std::string& name ) {
    _psetName = name;
}


//______________________________________________________________________________
edm::ParameterSet PsetReader::read( int argc, char**argv ) {
    if ( argc < 2 )
        THROW_RUNTIME("No Python config file defined"); 

    if ( !boost::algorithm::ends_with(argv[1],".py") )
        THROW_RUNTIME("Usage " << argv[0] << " config.py opts")

    std::string cfgStr = edm::read_whole_file( argv[1] );

    std::vector<std::string> args;
    for ( int i=1; i<argc; ++i ) 
        args.push_back(argv[i]);

    std::stringstream header;
    header << "import sys\n";
    header << "sys.argv = []\n";
    for ( unsigned int i(0); i<args.size(); ++i) 
        header << "sys.argv.append('" << args[i] << "')\n";
    
    

    cfgStr = header.str()+cfgStr;
    boost::shared_ptr<edm::ParameterSet> _pyConfig = edm::readPSetsFrom(cfgStr);

// for CMSSW >  4_1_4
//     boost::shared_ptr<edm::ParameterSet> _pyConfig =  edm::readConfig(argv[0],argc,argv);	
    
    if( !_pyConfig->existsAs<edm::ParameterSet>( _psetName ) ){
        THROW_RUNTIME(" ERROR: ParametersSet 'process' is missing in your configuration file");
    }

    edm::ParameterSet _pset = _pyConfig->getParameter<edm::ParameterSet>(_psetName);

    return _pset;

}



