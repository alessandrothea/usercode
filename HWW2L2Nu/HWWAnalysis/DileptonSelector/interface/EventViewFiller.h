// -*- C++ -*-
//
// Package:    EventViewFiller
// Class:      EventViewFiller
// 
/**\class EventViewFiller EventViewFiller.cc HWWAnalysis/EventViewFiller/src/EventViewFiller.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Sat Jul  9 16:39:20 CEST 2011
// $Id: EventViewFiller.h,v 1.1 2011/07/28 16:11:13 thea Exp $
//
//


#ifndef HWWAnalysis_DileptonSelector_EventViewFiller_h
#define HWWAnalysis_DileptonSelector_EventViewFiller_h


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Event.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "HWWAnalysis/DataFormats/interface/EventView.h"
#include "Math/VectorUtil.h"
#include "PhysicsTools/SelectorUtils/interface/strbitset.h"

//
// class declaration
//

namespace hww {
namespace helper {

class EventViewFiller {
	public:
		explicit EventViewFiller(const edm::ParameterSet&);
		~EventViewFiller();

		template<class C>
		void fill( std::vector<C>& views, const edm::Event& iEvent) {
			// this should work for classes inheriting from hww::EventView
			uint size = this->count( iEvent );
			views.resize(size);
			// fill a vector of pointers
			std::vector<hww::EventView*> viewPtrs;
			for ( uint i(0); i<size; ++i)
				viewPtrs.push_back( &(views.at(i)) );

			doFill(viewPtrs,iEvent);

		} 

	private:
		virtual uint count( const edm::Event& ) const;
		virtual void doFill(std::vector<hww::EventView*>, const edm::Event& );

		// ----------member data ---------------------------

		edm::InputTag hltSummarySrc_;
		edm::InputTag dileptonSrc_;
		edm::InputTag jetSrc_;
		edm::InputTag softMuonSrc_;
		edm::InputTag pfMetSrc_;
		edm::InputTag tcMetSrc_;
		edm::InputTag chargedMetSrc_;
		edm::InputTag vertexSrc_;
		edm::InputTag pfChCandSrc_;

		bool checkLeptonJetOverlap_;
		double leptonJetDr_;
};

}
}

#endif /* HWWAnalysis_DileptonSelector_EventViewFiller_h */
