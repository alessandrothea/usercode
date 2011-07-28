#include "HWWAnalysis/DataFormats/interface/DileptonView.h"
#include <iostream>
#include <limits>
#include "Math/VectorUtil.h"

using namespace std;

namespace hww {
    const double DileptonView::kNotFound = -9999.;

    DileptonView::DileptonView( const RecoCandPtr& l1, const RecoCandPtr& l2 ) {
        dilepton_.push_back(l1);
        dilepton_.push_back(l2);
        std::sort(dilepton_.begin(), dilepton_.end(), helper::greaterByPt());

        for( uint i(0); i<dilepton_.size(); ++i )
            sortByFlavor(dilepton_[i]);
       
//         cout << "l1.pt():" << setw(10) << dilepton_[0]->pt() << endl;        
//         cout << "l2.pt():" << setw(10) << dilepton_[1]->pt() << endl;        
    }


/*
 * 
 *  _____      _   _                
 * /  ___|    | | | |               
 * \ `--.  ___| |_| |_ ___ _ __ ___ 
 *  `--. \/ _ \ __| __/ _ \ '__/ __|
 * /\__/ /  __/ |_| ||  __/ |  \__ \
 * \____/ \___|\__|\__\___|_|  |___/
 * 
 */
    void
    DileptonView::sortByFlavor( const RecoCandPtr& l ) {
    // adds the lepton to the 

        if ( abs(l->pdgId()) == 11 ) {
            electrons_.push_back(l); 
            sort(electrons_.begin(), electrons_.end(), helper::greaterByPt());
        } else if ( abs(l->pdgId()) == 13 ) {
            muons_.push_back(l); 
            sort(muons_.begin(), muons_.end(), helper::greaterByPt());
        }

    }

    void
    DileptonView::addExtra( const RecoCandPtr& e ) {
        // add an extra lepton
        extra_.push_back(e);
        std::sort(extra_.begin(), extra_.end(), helper::greaterByPt());
        sortByFlavor(e);
    }


/*
 *  _____       __       ______                    
 * |_   _|     / _|      |  ___|                   
 *   | | _ __ | |_ ___   | |_ _   _ _ __   ___ ___ 
 *   | || '_ \|  _/ _ \  |  _| | | | '_ \ / __/ __|
 *  _| || | | | || (_) | | | | |_| | | | | (__\__ \
 *  \___/_| |_|_| \___/  \_|  \__,_|_| |_|\___|___/
 *  
 */                                                
    
    bool
    DileptonView::isEl( uint i ) const {
        return ( i < dilepton_.size() && abs(dilepton_[i]->pdgId()) == 11 );
    }

    bool
    DileptonView::isMu( uint i ) const {
        return ( i < dilepton_.size() && abs(dilepton_[i]->pdgId()) == 13 );
    }


    bool
    DileptonView::isElEl() const {
        return isEl(0) && isEl(1);
    }

    bool
    DileptonView::isElMu() const {
        return isEl(0) && isMu(1);
    }

    bool
    DileptonView::isMuEl() const {
        return isMu(0) && isEl(1);
    }

    bool
    DileptonView::isMuMu() const {
        return isMu(0) && isMu(1);
    }
    
    bool
    DileptonView::sameSign() const {
        if( dilepton_.size() != 2 ) return false;
        return (dilepton_[0]->charge() * dilepton_[1]->charge()) > 0;
    
    }

    bool
    DileptonView::oppositeSign() const {
        if( dilepton_.size() != 2 ) return false;
        return (dilepton_[0]->charge() * dilepton_[1]->charge()) < 0;
    }

    int
    DileptonView::chargeSum() const {
        int sum(0);
        for( uint i(0); i < dilepton_.size(); ++i)
            sum += dilepton_[i]->charge();

        return sum;
    }

    double
    DileptonView::mll() const {
        if ( dilepton_.size() != 2 ) return numeric_limits<double>::quiet_NaN();
        return (dilepton_[0]->p4()+dilepton_[1]->p4()).mass();
    }

    double
    DileptonView::dPhi() const {
        return TMath::Abs(ROOT::Math::VectorUtil::DeltaPhi(this->leading()->p4(), this->trailing()->p4()) );
    }

    double
    DileptonView::dR() const {
        return TMath::Abs(ROOT::Math::VectorUtil::DeltaR(this->leading()->p4(), this->trailing()->p4()) );
    }

    double
    DileptonView::centrality() const {
        math::XYZTLorentzVector p4 = this->p4ll();
        return p4.pt()/p4.e();
    }

    double
    DileptonView::centralityScal() const {
        return (this->leading()->p4().pt()+this->trailing()->p4().pt())
            /( this->leading()->p4().e()+this->trailing()->p4().e());
    }

    double
    DileptonView::ptSum() const {
        return this->leading()->p4().pt()+this->trailing()->p4().pt();
    }

    double
    DileptonView::eSum() const {
        return this->leading()->p4().e()+this->trailing()->p4().e();
    }


//     MRstar(const math::XYZTLorentzVector& ja, const math::XYZTLorentzVector& jb){
    double
    DileptonView::mRstar() const {
        //
        // this is the 'new' MRstar
        //
        // double MRstar(const TLorentzVector& ja, const TLorentzVector& jb){
        const math::XYZTLorentzVector& ja = this->leading()->p4();
        const math::XYZTLorentzVector& jb = this->trailing()->p4();
        double A = ja.P();
        double B = jb.P();
        double az = ja.Pz();
        double bz = jb.Pz();
        math::XYZVector jaT, jbT;
        jaT.SetXYZ(ja.Px(),ja.Py(),0.0);
        jbT.SetXYZ(jb.Px(),jb.Py(),0.0);

        double temp = sqrt((A+B)*(A+B)-(az+bz)*(az+bz)-
                (jbT.Dot(jbT)-jaT.Dot(jaT))*(jbT.Dot(jbT)-jaT.Dot(jaT))/(jaT+jbT).Mag2());

        return temp;
    }

    double
    DileptonView::gammaMRstar() const {
        //
        // this is the 'new' MRstar, times 'gamma_{R*}' - I would recommend making 'R*' with this as
        // the denominator and 'M_{T}^{R}' as the numerator (the next function in this file)
        //
        const math::XYZTLorentzVector& ja = this->leading()->p4();
        const math::XYZTLorentzVector& jb = this->trailing()->p4();
        double A = ja.P();
        double B = jb.P();
        double az = ja.Pz();
        double bz = jb.Pz();
        math::XYZVector jaT, jbT;
        jaT.SetXYZ(ja.Px(),ja.Py(),0.0);
        jbT.SetXYZ(jb.Px(),jb.Py(),0.0);
        double ATBT = (jaT+jbT).Mag2();

        double temp = sqrt((A+B)*(A+B)-(az+bz)*(az+bz)-
                (jbT.Dot(jbT)-jaT.Dot(jaT))*(jbT.Dot(jbT)-jaT.Dot(jaT))/(jaT+jbT).Mag2());

        double mybeta = (jbT.Dot(jbT)-jaT.Dot(jaT))/
            sqrt(ATBT*((A+B)*(A+B)-(az+bz)*(az+bz)));

        double mygamma = 1./sqrt(1.-mybeta*mybeta);

        //gamma times MRstar                                                                                                                                                                                                                     
        temp *= mygamma;

        return temp;
    }

    math::XYZTLorentzVector
    DileptonView::p4ll() const {
        return dilepton_[0]->p4()+dilepton_[1]->p4();
    }


    int
    DileptonView::nLeptons() const {
        return dilepton_.size() + extra_.size();
    }

    int
    DileptonView::nExtra() const {
        return extra_.size();
    }

    int
    DileptonView::nElectrons() const {
        return electrons_.size();
    }

    int
    DileptonView::nMuons() const {
        return muons_.size();
    }

    double
    DileptonView::worstEGammaLikelihood() const {
        const pat::Electron* el1 = dynamic_cast<const pat::Electron*>(dilepton_[0].get());
        const pat::Electron* el2 = dynamic_cast<const pat::Electron*>(dilepton_[1].get());
        if ( isElEl() ) 
            return TMath::Min( 
                    el1->electronID("egammaIDLikelihood"),
                    el2->electronID("egammaIDLikelihood")
                    );
        else if ( isElMu() ) 
            return el1->electronID("egammaIDLikelihood");
        else if ( isElMu() ) 
            return el2->electronID("egammaIDLikelihood");
        else 
            return kNotFound;
    }

/*
 *  _____      _   _                
 * |  __ \    | | | |               
 * | |  \/ ___| |_| |_ ___ _ __ ___ 
 * | | __ / _ \ __| __/ _ \ '__/ __|
 * | |_\ \  __/ |_| ||  __/ |  \__ \
 *  \____/\___|\__|\__\___|_|  |___/
 *                                  
 */


    const pat::Electron*
    DileptonView::getElectron( uint i ) {
        if ( i >= electrons_.size() ) return 0x0;
        return static_cast<const pat::Electron*>(electrons_[i].get());
    }

    const pat::Muon*
    DileptonView::getMuon( uint i ) {
        if ( i >= muons_.size() ) return 0x0;
        return static_cast<const pat::Muon*>(muons_[i].get());
    }


    
    const reco::RecoCandidate*
    DileptonView::operator[]( uint i ) const {
        //TODO: exception?
        if ( i >= dilepton_.size() ) return 0x0;
        return dilepton_[i].get();
    }
    
    const reco::RecoCandidate*
    DileptonView::leading() const {
        return dilepton_[0].get();
    }

    const reco::RecoCandidate*
    DileptonView::trailing() const {
        return dilepton_[1].get();
    }


    namespace helper {
        bool
        lessByPtSum::operator()( const DileptonView& a, const DileptonView& b ) {
            return a.ptSum() < b.ptSum();
        }
        
        bool
        greaterByPtSum::operator()( const DileptonView& a, const DileptonView& b ) {
            return a.ptSum() > b.ptSum();
        }
    }

}
