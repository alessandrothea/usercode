#ifndef _PSETREADER_H_
#define _PSETREADER_H_

#include <string>
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/PythonParameterSet/interface/MakeParameterSets.h"

class PsetReader {
    public:
        PsetReader(const std::string& name);

        edm::ParameterSet read( int argc, char**argv );
        edm::ParameterSet pset() { return _pset; }
    private:
        std::string _psetName;
        boost::shared_ptr<edm::ParameterSet> _pyConfig;
        edm::ParameterSet _pset;
};


#endif
