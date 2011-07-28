#ifndef HWWAnalysis_Dataformats_DileptonView_h
#define HWWAnalysis_Dataformats_DileptonView_h

#include "DataFormats/Common/interface/Ptr.h"
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"

namespace hww {

    typedef edm::Ptr<reco::RecoCandidate> RecoCandPtr;

    class DileptonView {
        public:
        
        // --- static stuff ---
        static const double kNotFound;
        
        DileptonView(){}
        DileptonView( const RecoCandPtr& l1, const RecoCandPtr& l2 );

        void addExtra( const RecoCandPtr& );

        const pat::Electron* getElectron( uint i );
        const pat::Muon*     getMuon( uint i );
        const reco::RecoCandidate* leading() const;
        const reco::RecoCandidate* trailing() const;
        const reco::RecoCandidate* operator[]( uint i ) const;

        // --- info methonds -- (double, int, bool, const)
        bool isEl( uint i ) const;
        bool isMu( uint i ) const;

        bool isElEl() const;
        bool isElMu() const;
        bool isMuEl() const;
        bool isMuMu() const;

        bool oppositeSign() const;
        bool sameSign() const;
        

        int  chargeSum() const;
        
        double mll() const;
        int    nExtra() const;
        int    nLeptons() const;
        int    nElectrons() const;
        int    nMuons() const;
        double dPhi() const;
        double dR() const;
        double centrality() const;
        double centralityScal() const;
        double ptSum() const;
        double eSum() const;

        double gammaMRstar() const;
        double mRstar() const;

        double worstEGammaLikelihood() const;
        math::XYZTLorentzVector p4ll() const;

        // --- getters ---
        const std::vector<RecoCandPtr>& leptons() const { return dilepton_; } 
        const std::vector<RecoCandPtr>& extra() const { return extra_; } 
        const std::vector<RecoCandPtr>& muons() const { return muons_; }
        const std::vector<RecoCandPtr>& electrons() const { return electrons_; }

        template<class T>
        const T* getLepton( uint i ) const {
            if ( i >= dilepton_.size() ) return 0x0;
            return static_cast<const T*>(dilepton_[i].get());
        }

        template<class T>
        const T* getExtra(uint i ) const {
            if ( i >= extra_.size() ) return 0x0;
            return static_cast<const T*>(extra_[i].get());
        }
        
        private:
        // add the lep to muons/electrons
        void sortByFlavor( const RecoCandPtr& );

        std::vector<RecoCandPtr> dilepton_;
        std::vector<RecoCandPtr> extra_;
        std::vector<RecoCandPtr> muons_;
        std::vector<RecoCandPtr> electrons_;
    };

    typedef std::vector<DileptonView> DileptonViewVec;

    namespace helper {
        struct lessByPt {
            bool operator()( const RecoCandPtr & t1, const RecoCandPtr & t2 ) const {
                return t1->pt() < t2->pt();
            }
        };
 
        struct greaterByPt {
            bool operator()( const RecoCandPtr & t1, const RecoCandPtr & t2 ) const {
                return t1->pt() > t2->pt();
            }
        };
        
        struct lessByPtSum {
            bool operator()( const DileptonView& a, const DileptonView& b );
        };

        struct greaterByPtSum {
            bool operator()( const DileptonView& a, const DileptonView& b );
        };
    }
}
#endif /* HWWAnalysis_Dataformats_DileptonView_h */
