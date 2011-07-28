#include "HWWAnalysis/DataFormats/interface/EventView.h"
#include "HWWAnalysis/DataFormats/interface/Davismt2.h"
#include "HWWAnalysis/Misc/interface/Tools.h"
#include "Math/VectorUtil.h"

using namespace ROOT::Math;

namespace hww {
    const double EventView::kNotFound = -9999.;
    const double EventView::kEtaMax   =  9999.;

    EventView::EventView() {
    }

    void
    EventView::setDilepton( const DileptonPtr& pair ) {
        dilep_ = pair;
    }

    void
    EventView::addSoftMuon( const MuonPtr& mu ) {
        softMuons_.push_back( mu );
    }
    void
    EventView::addJet( const JetPtr& jet ) {
        jets_.push_back( jet );
    }

    void
    EventView::addVrtx( const VertexPtr& vrtx ) {
        vertexes_.push_back( vrtx );
    }

    void
    EventView::setHltBits( const pat::strbitset& bitmap ) {
        hltBits_ = bitmap;
    }

    void
    EventView::setTcMet( const reco::MET& tcMet ) {
        tcMet_ = tcMet;
    }

    void
    EventView::setPFMet( const reco::PFMET& pfMet ) {
        pfMet_ = pfMet;
    }

    void
    EventView::setChargedMet( const reco::PFMET& chMet ) {
        chargedMet_ = chMet;
    }

    void
    EventView::setChargedMetSmurf( const reco::MET& chMetSmurf ) {
        chargedMetSmurf_ = chMetSmurf;
    }

    /*
     *  _        __            _             _     _      
     * (_)      / _|          | |           | |   | |     
     *  _ _ __ | |_ ___     __| | ___  _   _| |__ | | ___ 
     * | | '_ \|  _/ _ \   / _` |/ _ \| | | | '_ \| |/ _ \
     * | | | | | || (_) | | (_| | (_) | |_| | |_) | |  __/
     * |_|_| |_|_| \___/   \__,_|\___/ \__,_|_.__/|_|\___|
     *
     */

    // mets by enum
    double
    EventView::met( MET_t type ) const {
        return metByType(type)->p4().pt();
    }

    double
    EventView::phiMet( MET_t type ) const {
        return metByType(type)->p4().phi();
    }

    double 
    EventView::dPhiMet( MET_t type ) const {
        return minDPhil( metByType(type)->p4() ); 
    }


    double
    EventView::projMet( MET_t type ) const {
        return projMet( metByType(type)->p4() );
    }

    double
    EventView::dPhilMet( uint i, MET_t type ) const {
        return TMath::Abs(VectorUtil::DeltaPhi( (*dilep())[i]->p4(),  metByType(type)->p4()));
    }


    // straight mets
    double
    EventView::tcMet() const {
        return tcMet_.p4().pt();
    }

    double
    EventView::pfMet() const {
        return pfMet_.p4().pt();
    }

    double
    EventView::chargedMet() const {
        return chargedMet_.p4().pt();
    }

    double
    EventView::chargedMetSmurf() const {
        return chargedMetSmurf_.p4().pt();
    }

    double
    EventView::phiTcMet() const {
        return tcMet_.p4().phi();
    }

    double
    EventView::phiPfMet() const {
        return pfMet_.p4().phi();
    }

    double
    EventView::phiChargedMet() const {
        return chargedMet_.p4().phi();
    }

    double
    EventView::phiChargedMetSmurf() const {
        return chargedMetSmurf_.p4().phi();
    }

    double
    EventView::dPhiTcMet() const {
        return minDPhil( tcMet_.p4() );
    }

    double
    EventView::dPhiPfMet() const {
        return minDPhil( pfMet_.p4() ) ;
    
    }

    double
    EventView::dPhiChargedMet() const {
        return minDPhil( chargedMet_.p4() ); 
    }
    
    double
    EventView::dPhiChargedMetSmurf() const {
        return minDPhil( chargedMetSmurf_.p4() ); 
    }
    

    double
    EventView::projTcMet() const {
        return projMet( tcMet_.p4() );
    }

    double
    EventView::projPfMet() const {
        return projMet( pfMet_.p4() );
    }

    double
    EventView::projChargedMet() const {
        return projMet( chargedMet_.p4() );
    }

    double
    EventView::projChargedMetSmurf() const {
        return projMet( chargedMetSmurf_.p4() );
    }

    // ... transverse masses ...
    double
    EventView::mtl( uint i, MET_t type )  const {
        const reco::RecoCandidate* lepton = (*dilep_)[i];
        if ( !lepton ) return kNotFound;

        return transverseMass( lepton->p4(), this->metByType(type)->p4());
    }

    double
    EventView::mtll( MET_t type )  const {
        return transverseMass(dilep_->p4ll(), this->metByType(type)->p4());
    }

    double
    EventView::mt2( MET_t type )  const {
        return transverseMass2(0., false, (*dilep_)[0]->p4(), (*dilep())[1]->p4(), this->metByType(type)->p4() );
    }

    // --- jets stuff ---
    double
    EventView::dPhiJl( uint i, double pt, double eta ) const {
        const reco::RecoCandidate* lepton = (*dilep_)[i];
        if ( !lepton ) return kNotFound;
        
        const pat::Jet* leading = leadingJet( pt, eta );
        return leading != 0x0 ? TMath::Abs(VectorUtil::DeltaPhi( lepton->p4(), leading->p4() )) : kNotFound ; 
    }

    double
    EventView::dPhiJll( double pt, double eta ) const {
        // dPhi between the highest pt jet above pt and the ll system;
        // returns kNotFound if the jet doesn't exist

        const pat::Jet* leading = leadingJet( pt, eta );


        return leading != 0x0 ? TMath::Abs(VectorUtil::DeltaPhi( dilep_->p4ll(), leading->p4() )) : kNotFound ; 
    }

    double
    EventView::jetBtagger( uint i, const std::string& tag  ) const {
        if ( i >= jets_.size() ) return kNotFound;

        return jets_[i]->bDiscriminator( tag );
    }
    
    double
    EventView::jetPtSum( double pt, double eta ) const {
        double ptSum(0);
        for( uint i(0); i<jets_.size(); ++i ) {
            const pat::Jet& jet = *(jets_[i]);
            if ( jet.p4().pt() < pt )
                // jets sorted by pt
                // TODO: check!!
                break;
            if ( TMath::Abs(jet.p4().eta()) > eta ) continue;

            ptSum += jet.p4().pt();
        }
        return ptSum;

    }

    double
    EventView::jetESum( double pt, double eta ) const {
        double eSum(0);
        for( uint i(0); i<jets_.size(); ++i ) {
            const pat::Jet& jet = *(jets_[i]);
            if ( jet.p4().pt() < pt )
                // jets sorted by pt
                // TODO: check!!
                break;
            if ( TMath::Abs(jet.p4().eta()) > eta ) continue;

            eSum += jet.p4().e();
        }
        return eSum;

    }

    double
    EventView::jetCentrality( double pt, double eta )  const {
        math::XYZTLorentzVector p4 = this->jetSumP4( pt, eta );
        return p4.pt()/p4.e(); 
    }

    double
    EventView::jetCentralityScal( double pt, double eta ) const  {
        double ptSum(0), eSum(0);
        for( uint i(0); i<jets_.size(); ++i ) {
            const pat::Jet& jet = *(jets_[i]);
            if ( jet.p4().pt() < pt )
                // jets sorted by pt
                // TODO: check!!
                break;
            if ( TMath::Abs(jet.p4().eta()) > eta ) continue;

            ptSum += jet.p4().pt();
            eSum  += jet.p4().e();
        }
        return ptSum/eSum;
    }

    /*
     *  _        __        _       _   
     * (_)      / _|      (_)     | |  
     *  _ _ __ | |_ ___    _ _ __ | |_ 
     * | | '_ \|  _/ _ \  | | '_ \| __|
     * | | | | | || (_) | | | | | | |_ 
     * |_|_| |_|_| \___/  |_|_| |_|\__|
     *
     */

    int
    EventView::channel() const {
       if ( dilep_->isMuMu() ) return 0;
       else if ( dilep_->isElEl() ) return 1;
       else if ( dilep_->isElMu() ) return 2;
       else if ( dilep_->isMuEl() ) return 3;
       else return kNotFound;
    }
    
    int
    EventView::nVrtx() const {
        return vertexes_.size();
    }

    int
    EventView::nSoftMuons() const {
        return softMuons_.size();
    }

    int
    EventView::nJets( double pt, double eta ) const {
        if ( pt == 0. && eta == 100. ) return jets_.size();

        int counts(0);
        for( uint i(0); i<jets_.size(); ++i ) {
            const pat::Jet& jet = *(jets_[i]);
            if ( jet.p4().pt() < pt )
                // the jets are sorted by pt
                // TODO: check!!!
                break;
            if ( TMath::Abs(jet.p4().eta()) > eta ) continue;
            ++counts;
        }
        return counts;
    
    }

    int
    EventView::nBJetsAbove( const std::string& tagger, double threshold, double pt, double eta ) const {
        int bcounts(0);

        for( uint i(0); i<jets_.size(); ++i ) {
            const pat::Jet& jet = *(jets_[i]);
            if ( jet.p4().pt() < pt )
                // jets sorted by pt
                // TODO: check!!
                break;
            if ( TMath::Abs(jet.p4().eta()) > eta 
                    || jet.bDiscriminator(tagger) < threshold ) continue;
            ++bcounts;
        }
        return bcounts;

    }

    int
    EventView::nBJetsBelow( const std::string& tagger, double threshold, double pt, double eta ) const {
        int bcounts(0);

        for( uint i(0); i<jets_.size(); ++i ) {
            const pat::Jet& jet = *(jets_[i]);
            if ( jet.p4().pt() < pt )
                // jets sorted by pt
                // TODO: check!!
                break;
            if ( TMath::Abs(jet.p4().eta()) > eta 
                    || jet.bDiscriminator(tagger) > threshold ) continue; 
            ++bcounts;
        }
        return bcounts;
        
    }

    bool EventView::bit( const std::string& name ) const {
        return hltBits_[name];
    }

    /*                      _          
     *                     (_)         
     *  ___  ___ _ ____   ___  ___ ___ 
     * / __|/ _ \ '__\ \ / / |/ __/ _ \
     * \__ \  __/ |   \ V /| | (_|  __/
     * |___/\___|_|    \_/ |_|\___\___|
     *                                 
     */

    const reco::MET*
    EventView::metByType( MET_t type ) const {
        switch (type) {
            case kTcMET:
                return &tcMet_;
            case kPfMET:
                return &pfMet_;
            case kChargedMET:
                return &chargedMet_;
            case kChargedMETSmurf:
                return &chargedMetSmurf_;
            default:
                THROW_RUNTIME("This met doesn't exist: " << type );
        }
    }

    // TODO: move it in a satellite src
    double
    EventView::transverseMass(const math::XYZTLorentzVector& p4, const math::XYZTLorentzVector& met) const {
        double mt;
        double pt1 = p4.Pt();
        double pt2 = met.Pt();  // pt2=met
        double delPhi = TMath::Abs(ROOT::Math::VectorUtil::DeltaPhi(p4, met));
        mt = TMath::Sqrt(2*TMath::Abs(pt1)*TMath::Abs(pt2)*(1-TMath::Cos(delPhi)));
        return mt;
    }

    // TODO: move it in a satellite src
    double
    EventView::transverseMass2(double testmass, bool massive, const math::XYZTLorentzVector& visible1, const math::XYZTLorentzVector& visible2 , const math::XYZTLorentzVector& MET ) const {  
        double pa[3];
        double pb[3];
        double pmiss[3];

        pmiss[0] = 0;
        pmiss[1] = MET.Px();
        pmiss[2] = MET.Py();

        pa[0] = massive ? visible1.M() : 0;
        pa[1] = visible1.Px();
        pa[2] = visible1.Py();

        pb[0] = massive ? visible2.M() : 0;
        pb[1] = visible2.Px();
        pb[2] = visible2.Py();

        Davismt2 mt2;
        mt2.set_momenta(pa, pb, pmiss);
        mt2.set_mn(testmass);
        return mt2.get_mt2();
    }


    const pat::Jet*
    EventView::jet( uint i ) const {
        if ( i >= jets_.size() ) return 0x0;

        return jets_[i].get();
    }

    const pat::Jet*
    EventView::leadingJet( double pt, double eta) const {

        const pat::Jet* leading = 0x0;
        for( uint i(0); i<jets_.size(); ++i ) {
            const pat::Jet* jet = jets_[i].get();
            if ( jet->p4().pt() < pt )
                // jets sorted by pt
                // TODO: check!!
                return 0x0;
            if ( TMath::Abs(jet->p4().eta()) > eta ) continue;

            leading = jet;
            break;
        }

        return leading;

    }

    // TODO: move it to DileptonView
    double
    EventView::minDPhil( const math::XYZTLorentzVector& p4 ) const {
        return TMath::Min(
                TMath::Abs(VectorUtil::DeltaPhi( pair()->leptons()[0]->p4(), p4)),
                TMath::Abs(VectorUtil::DeltaPhi( pair()->leptons()[1]->p4(), p4))
                );
    }
    
    // TODO: move it to DileptonView
    double
    EventView::projMet( const math::XYZTLorentzVector& p4Met ) const {
        double minDPhill  = minDPhil(p4Met);
        return ( minDPhill < TMath::PiOver2() ? p4Met.pt()*TMath::Sin(minDPhill) : p4Met.pt()) ;
    }

    math::XYZTLorentzVector 
    EventView::jetSumP4( double pt, double eta ) const {
        math::XYZTLorentzVector p4;
        for( uint i(0); i<jets_.size(); ++i ) {
            const pat::Jet& jet = *(jets_[i]);
            if ( jet.p4().pt() < pt )
                // jets sorted by pt
                // TODO: check!!
                break;
            if ( TMath::Abs(jet.p4().eta()) > eta ) continue;

            p4 += jet.p4();
        }
        return p4;

    }


}
