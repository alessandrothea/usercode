#ifndef HWWAnalysis_Dataformats_DileptonView_h
#define HWWAnalysis_Dataformats_DileptonView_h

#include "DataFormats/Common/interface/Ptr.h"
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"

namespace hww {

    class DileptonView {
        public:
        
        typedef edm::Ptr<reco::RecoCandidate> refPtr;
        
        DileptonView(){}
        DileptonView( const refPtr& l1, const refPtr& l2 );

        void add( const refPtr& );
        void addExtra( const refPtr& );

        const pat::Electron* getElectron( uint i );
        const pat::Muon*     getMuon( uint i );
        const reco::RecoCandidate* leading() const;
        const reco::RecoCandidate* trailing() const;

//         const reco::RecoCandidate* getLepton( uint i );
        bool isElEl() const;
        bool isElMu() const;
        bool isMuEl() const;
        bool isMuMu() const;

        bool oppositeSign() const;
        bool sameSign() const;
        int  chargeSum() const;
        
        double mll() const;

        const std::vector<refPtr>& getLeptons() { return leptons_; } 
        const std::vector<refPtr>& getExtra() { return extra_; } 

        template<class T>
        const T* getLepton( uint i ) const {
            if ( i >= leptons_.size() ) return 0x0;
            return static_cast<const T*>(leptons_[i].get());
        }

        template<class T>
        const T* getExtra(uint i ) const {
            if ( i >= extra_.size() ) return 0x0;
            return static_cast<const T*>(extra_[i].get());
        }
        
        private:
        struct PtrLessByPt {
            bool operator()( const refPtr & t1, const refPtr & t2 ) const {
                return t1->pt() < t2->pt();
            }
        };
 
        struct PtrGreaterByPt {
            bool operator()( const refPtr & t1, const refPtr & t2 ) const {
                return t1->pt() > t2->pt();
            }
        };
        
        std::vector<refPtr> leptons_;
        std::vector<refPtr> extra_;
    };

    typedef std::vector<DileptonView> DileptonViewVec;
}
#endif /* HWWAnalysis_Dataformats_DileptonView_h */
