#ifndef HWWAnalysis_DileptonSelector_PATFlagger_h
#define HWWAnalysis_DileptonSelector_PATFlagger_h

#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "CommonTools/Utils/interface/StringObjectFunction.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"

#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Tau.h"
#include "DataFormats/PatCandidates/interface/Photon.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/MET.h"
#include "DataFormats/PatCandidates/interface/GenericParticle.h"

#include <boost/ptr_container/ptr_vector.hpp>

namespace pat {
    
    template<class PATObjType>
    class PATFlagger : public edm::EDProducer {
        public:
            explicit PATFlagger(const edm::ParameterSet & iConfig);
            virtual ~PATFlagger() {}

            virtual void produce(edm::Event & iEvent, const edm::EventSetup & iSetup);
        private:
            typedef StringCutObjectSelector<PATObjType> Selector;

            struct Tag {
                Tag(const std::string& name, const std::string& cut ) : name_(name), selector_(cut) {}
                std::string name_;
                Selector selector_;
            };

            edm::InputTag src_;
            boost::ptr_vector<Tag> tags_;
        };
}

template<class PATObjType>
pat::PATFlagger<PATObjType>::PATFlagger(const edm::ParameterSet & iConfig) :
    src_(iConfig.getParameter<edm::InputTag>("src"))
{
    edm::ParameterSet tagsPSet = iConfig.getParameter<edm::ParameterSet>("tags");
    // get all the names of the tests (all nested PSets in this PSet)
    std::vector<std::string> tagNames = tagsPSet.getParameterNamesForType<std::string>();
    for (std::vector<std::string>::const_iterator itn = tagNames.begin(); itn != tagNames.end(); ++itn) {
        tags_.push_back( new Tag(*itn, tagsPSet.getParameter<std::string>(*itn) ) );
    }

    produces<std::vector<PATObjType> >();
}

template<class PATObjType>
void
pat::PATFlagger<PATObjType>::produce(edm::Event & iEvent, const edm::EventSetup & iSetup) {
    // Read the input. We use edm::View<> in case the input happes to be something different than a std::vector<>
    edm::Handle<edm::View<PATObjType> > candidates;
    iEvent.getByLabel(src_, candidates);

    // Prepare a collection for the output
    std::auto_ptr< std::vector<PATObjType> > output(new std::vector<PATObjType>());

    for (typename edm::View<PATObjType>::const_iterator it = candidates->begin(), ed = candidates->end(); it != ed; ++it) {
        // add thte candidate to the list
        output->push_back(*it);
        PATObjType &obj = output->back();
        
        // loop over the tags and add an userInt for each of them
        for( typename boost::ptr_vector<Tag>::iterator itag = tags_.begin(), et = tags_.end(); itag != et; ++itag ){
           obj.addUserInt(itag->name_, itag->selector_(obj) ? 1 : 0 ); 
        }
    }

     iEvent.put(output);
}


#endif /* HWWAnalysis_DileptonSelector_PATFlagger_h */
