
#include "HWWAnalysis/DileptonSelector/interface/HltBitChecker.h"
#include <HWWAnalysis/Misc/interface/Tools.h>
#include <boost/algorithm/string.hpp>
#include <boost/regex.hpp>
#include <FWCore/Common/interface/TriggerNames.h>

const char HltBitChecker::wildcard_ = '*';

using namespace std;

//______________________________________________________________________________
HltBitChecker::HltBitChecker( const edm::vstring& config ) : currentRun_(0) {

    boost::regex e("(\\d+)-(\\d+):(.*)");
    boost::smatch what;

    edm::vstring::const_iterator iStr; 
    for( iStr = config.begin(); iStr != config.end(); ++iStr ) {
        RunRange interval( *iStr );
        if ( boost::regex_match( *iStr, what, e) ) {
//             cout << "all     " << what[0] << endl; 
//             cout << "start   " << what[1] << endl; 
//             cout << "end     " << what[2] << endl; 
//             cout << "pattern " << what[3] << endl;

            interval.start = ::atoi(what[1].str().c_str());
            interval.end   = ::atoi(what[2].str().c_str());
            interval.path  = what[3]; 

        } else {
            // do nothing, we assume there is no run range in front
//             THROW_RUNTIME("Corrupted run range definition: " << *iStr);
        }
        ranges_.push_back(interval);
    
    }

//     cout << ranges_.size() << " ranges loaded" << endl;


}

//______________________________________________________________________________
void HltBitChecker::update( const edm::EventBase &iEvent, const edm::TriggerResults& results ) const {

    // don't update if the run number didn't change
    if ( iEvent.id().run() == currentRun_ ) return;

    currentRun_ = iEvent.id().run();

    indexes_.clear();
    const edm::TriggerNames &names = iEvent.triggerNames( results );

    edm::vstring::iterator iTrg;
    vector<RunRange>::const_iterator iRange;
    for( iRange = ranges_.begin(); iRange != ranges_.end(); ++iRange ) {
//         cout << "Updating " << iRange->start << "  " << iRange->end << "  " << iRange->path <<  endl;
        // run not in range, continue
        if ( currentRun_ < iRange->start || currentRun_ > iRange->end ) continue;
        
        // get all the matches for the path
        edm::vstring matches = this->search(iRange->path, names.triggerNames() );
        // store the indexes
        for( iTrg = matches.begin(); iTrg != matches.end(); ++iTrg ) {
           indexes_.push_back( names.triggerIndex(*iTrg) ); 
//            cout << *iTrg << " " << indexes_.back() << endl;
        }

//         cout << indexes_.size() << " triggers found " << endl;
    }

    
}

//______________________________________________________________________________
bool HltBitChecker::check( const edm::EventBase &iEvent, const edm::TriggerResults&  results ) const {

    this->update(iEvent,results);

    vector<unsigned>::const_iterator idx;
    for( idx = indexes_.begin(); idx != indexes_.end(); ++idx )
        if ( results.accept( *idx ) ) return true;

    return false;
}

//______________________________________________________________________________
std::vector<std::string> HltBitChecker::search( const std::string& pattern,const std::vector< std::string >& nameVec ) const {

    std::vector<std::string> matches;

    // Special cases first
    // Always false for empty vector to check
    if ( nameVec.empty() ) return matches;

    if ( pattern == std::string(1,wildcard_) ) {
        // special case: wildcard only
        matches = nameVec;
        return matches;
    } else if ( pattern.find_first_not_of( wildcard_ ) == std::string::npos ) {
        // Always true for general wild-card(s)
        // no wildcard case
        // basic loop without wildcard evalutation
        for ( std::vector< std::string >::const_iterator iVec = nameVec.begin(); iVec != nameVec.end(); ++iVec ) {
            if ( *iVec == pattern )
                matches.push_back(*iVec);
        }
    } else {
        // wildcard case
        // Split pattern to evaluate in parts, seperated by wild-cards
        std::vector< std::string > namePartsVec;
        boost::split( namePartsVec, pattern, boost::is_any_of( std::string( 1, wildcard_ ) ), boost::token_compress_on );
        // Iterate over vector of names to search
        for ( std::vector< std::string >::const_iterator iVec = nameVec.begin(); iVec != nameVec.end(); ++iVec ) {
            // Not failed yet
            bool failed( false );
            // Start searching at the first character
            size_t index( 0 );
            // Iterate over evaluation pattern parts
            for ( std::vector< std::string >::const_iterator iName = namePartsVec.begin(); iName != namePartsVec.end(); ++iName ) {
                // Empty parts due to
                // - wild-card at beginning/end or
                // - multiple wild-cards (should be supressed by 'boost::token_compress_on')
                if ( iName->length() == 0 ) continue;
                // Search from current index and
                // set index to found occurence
                index = iVec->find( *iName, index );
                // Failed and exit loop, if
                // - part not found
                // - part at beginning not found there
                if ( index == std::string::npos || ( iName == namePartsVec.begin() && index > 0 ) ) {
                    failed = true;
                    break;
                }
                // Increase index by length of found part
                index += iName->length();
            }
            // Failed, if end of pattern not reached
            if ( index < iVec->length() && namePartsVec.back().length() != 0 ) failed = true;
            // Match found!
            if ( ! failed ) //return true;
            matches.push_back(*iVec);
        }
    }
    // No match found!
    return matches;
}
