#include "HWWAnalysis/DataFormats/interface/DileptonView.h"
#include <iostream>
#include <limits>

using namespace std;

namespace hww {
    DileptonView::DileptonView( const refPtr& l1, const refPtr& l2 ) {
        leptons_.push_back(l1);
        leptons_.push_back(l2);
        std::sort(leptons_.begin(), leptons_.end(), PtrGreaterByPt());

//         cout << "l1.pt():" << setw(10) << leptons_[0]->pt() << endl;        
//         cout << "l2.pt():" << setw(10) << leptons_[1]->pt() << endl;        
    }

    void
    DileptonView::add( const refPtr& l ) {
        // add lepton to the dilepton system
        if ( leptons_.size() >= 2 ) return;
        leptons_.push_back(l);
        std::sort(leptons_.begin(), leptons_.end(), PtrGreaterByPt());

    }

    void
    DileptonView::addExtra( const refPtr& e ) {
        // add an extra lepton
        extra_.push_back(e);
        std::sort(extra_.begin(), extra_.end(), PtrGreaterByPt());
    }

    bool
    DileptonView::isElEl() const {
        return leptons_.size() == 2 
            && abs(leptons_[0]->pdgId()) == 11
            && abs(leptons_[1]->pdgId()) == 11;
    }

    bool
    DileptonView::isElMu() const {
        return leptons_.size() == 2 
            && abs(leptons_[0]->pdgId()) == 11
            && abs(leptons_[1]->pdgId()) == 13;
    }

    bool
    DileptonView::isMuEl() const {
        return leptons_.size() == 2 
            && abs(leptons_[0]->pdgId()) == 13
            && abs(leptons_[1]->pdgId()) == 11;
    }

    bool
    DileptonView::isMuMu() const {
        return leptons_.size() == 2 
            && abs(leptons_[0]->pdgId()) == 13
            && abs(leptons_[1]->pdgId()) == 13;
    }
    
    bool
    DileptonView::sameSign() const {
        if( leptons_.size() != 2 ) return false;
        return (leptons_[0]->charge() * leptons_[1]->charge()) > 0;
    
    }

    bool
    DileptonView::oppositeSign() const {
        if( leptons_.size() != 2 ) return false;
        return (leptons_[0]->charge() * leptons_[1]->charge()) < 0;
    }

    int
    DileptonView::chargeSum() const {
        int sum(0);
        for( uint i(0); i < leptons_.size(); ++i)
            sum += leptons_[i]->charge();

        return sum;
    }

    double
    DileptonView::mll() const {
        if ( leptons_.size() != 2 ) return numeric_limits<double>::quiet_NaN();
        return (leptons_[0]->p4()+leptons_[1]->p4()).mass();
    }


    const pat::Electron*
    DileptonView::getElectron( uint i ) {
        if ( i >= leptons_.size() ) return 0x0;

        return static_cast<const pat::Electron*>(leptons_[i].get());
    }

    const pat::Muon*
    DileptonView::getMuon( uint i ) {
        return getLepton<pat::Muon>(i);
    }
    
    const reco::RecoCandidate*
    DileptonView::leading() const {
        return getLepton<reco::RecoCandidate>(0);
    }

    const reco::RecoCandidate*
    DileptonView::trailing() const {
        return getLepton<reco::RecoCandidate>(1);
    }
}
