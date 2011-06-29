#ifndef HWWAnalysis_DileptonSelector_interface_HltBitChecker_h
#define HWWAnalysis_DileptonSelector_interface_HltBitChecker_h

#include "FWCore/Common/interface/EventBase.h"
#include <string>
#include <DataFormats/Common/interface/TriggerResults.h>

namespace edm {
    typedef std::vector<std::string> vstring;
}

class HltBitChecker {
    public:
        struct RunRange {
            RunRange( const std::string& name ) : path(name), start(0), end(99999999) {}

            std::string path;
            unsigned start;
            unsigned end;
        };

        HltBitChecker( const edm::vstring& paths );
        HltBitChecker( ) {};

        void update( const edm::EventBase &iEvent, const edm::TriggerResults& ) const;
        bool check( const edm::EventBase &iEvent, const edm::TriggerResults& ) const;
    private:
        std::vector<std::string> search( const std::string& name,const std::vector< std::string >& nameVec ) const;

        std::vector<RunRange> ranges_;

        mutable std::vector<unsigned> indexes_;
        mutable unsigned long currentRun_;

        static const char wildcard_;// = '*';
};

#endif /* HWWAnalysis_DileptonSelector_interface_HltBitChecker_h */

