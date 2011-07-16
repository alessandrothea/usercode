#ifndef HWWAnalysis_DataFormats_EventView_h
#define HWWAnalysis_DataFormats_EventView_h

#include "DataFormats/Common/interface/Ptr.h"
#include "HWWAnalysis/DataFormats/interface/DileptonView.h"
#include "DataFormats/METReco/interface/MET.h"
#include "DataFormats/METReco/interface/METFwd.h"
#include "DataFormats/METReco/interface/PFMET.h"
#include "DataFormats/METReco/interface/PFMETFwd.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "PhysicsTools/SelectorUtils/interface/strbitset.h"


#include <memory>
#include <vector>

namespace hww {
    
    typedef edm::Ptr<reco::RecoCandidate> RecoCandPtr;
    typedef edm::Ptr<pat::Electron>       ElectronPtr;
    typedef edm::Ptr<pat::Muon>           MuonPtr;
    typedef edm::Ptr<pat::Jet>            JetPtr;
    typedef edm::Ptr<hww::DileptonView>   DileptonPtr;

    class EventView {
        public:
            enum MET_t {
                kTcMET,
                kPfMET,
                kChargedMET,
                kChargedMETSmurf
            };

        EventView();
        
        // --- static stuff ---
        static const double kNotFound;
        static const double kEtaMax;
        // --- setters and adders ---
        void setDilepton( const DileptonPtr& pair );

        void addSoftMuon( const MuonPtr& );
        void addJets( const JetPtr& );
        
        void setHltBits( const pat::strbitset& bitmap );
        void setTcMet( const reco::MET& tcMet );
        void setPFMet( const reco::PFMET& pfMet );
        void setChargedMet( const reco::PFMET& chMet );
        void setChargedMetSmurf( const reco::MET& chMetSmurf );
        
        // --- dilepton getter ---
        const DileptonView* pair() const { return dilep_.get(); }
        const DileptonView* dilep() const { return dilep_.get(); }
        // --- info methods ---
        // --- doubles ---
        // ... met stuff ...
        double met( MET_t t ) const;
        double phiMet( MET_t t ) const;
        double dPhiMet( MET_t t ) const;
        double projMet( MET_t t ) const;


        double tcMet() const;
        double pfMet() const;
        double chargedMet() const;
        double chargedMetSmurf() const;

        double phiTcMet() const;
        double phiPfMet() const;
        double phiChargedMet() const;
        double phiChargedMetSmurf() const;

        double dPhiTcMet() const;
        double dPhiPfMet() const;
        double dPhiChargedMet() const;
        double dPhiChargedMetSmurf() const;

        double projTcMet() const;
        double projPfMet() const;
        double projChargedMet() const;
        double projChargedMetSmurf() const;
        
        // ... transverse masses ...
        double mtl( uint i, MET_t type ) const;
        double mtll( MET_t type ) const;
        double mt2( MET_t type ) const;

        // ... jet stuff ...
        double dPhiJll( double pt = 0., double eta = kEtaMax ) const;
        double jetBtagger( uint i, const std::string& tag = "trackCountingHighEffBJetTags" ) const;

        double jetCentrality( double pt = 0., double eta = kEtaMax ) const;
        double jetCentralityScal( double pt = 0., double eta = kEtaMax ) const;


        double jetPtSum( double pt = 0., double eta = kEtaMax ) const;
        double jetESum( double pt = 0., double eta = kEtaMax ) const;

        // -- int --
        int nSoftMuons() const;
        int nJets( double pt = 0, double eta = kEtaMax) const;
        int nBJetsAbove( const std::string& tag, double threshold, double pt=0., double eta=kEtaMax ) const;
        int nBJetsBelow( const std::string& tag, double threshold, double pt=0., double eta=kEtaMax ) const;

        bool bit( const std::string& name ) const;
        // --- helpers ---
        // methods with non-base aguments or return values
        

        const std::vector<MuonPtr>& softMuons() const { return softMuons_; }
        const std::vector<JetPtr>&  jets() const { return jets_; }
        const reco::MET* metByType( MET_t type ) const;
        const pat::Jet* jet( uint i ) const;
        math::XYZTLorentzVector jetSumP4( double pt=0., double eta=kEtaMax ) const;
        double projMet( const math::XYZTLorentzVector& p4Met ) const; 
        double minDPhi( const math::XYZTLorentzVector& p4 ) const;
        double transverseMass(const math::XYZTLorentzVector& p4, const math::XYZTLorentzVector& met) const;
        double transverseMass2(double testmass, bool massive, const math::XYZTLorentzVector& visible1, const math::XYZTLorentzVector& visible2, const math::XYZTLorentzVector& MET ) const;

        protected:
        
       

        private:
        DileptonPtr                 dilep_;
        std::vector<MuonPtr>        softMuons_;
        std::vector<JetPtr>         jets_;

        pat::strbitset              hltBits_;

        reco::MET                   tcMet_;
        reco::PFMET                 pfMet_;
        reco::PFMET                 chargedMet_;
        reco::MET                   chargedMetSmurf_;
        // primary verterx coordinates
        // pileup info
        // weights

    };

    typedef std::vector<EventView> EventViewVec;

}
#endif /* HWWAnalysis_DataFormats_EventView_h */

