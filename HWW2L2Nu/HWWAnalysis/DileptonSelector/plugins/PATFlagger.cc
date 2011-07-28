#include "HWWAnalysis/DileptonSelector/plugins/PATFlagger.h"

#include "FWCore/Framework/interface/MakerMacros.h"

namespace pat {
    typedef pat::PATFlagger<pat::Electron>        PATElectronFlagger;
    typedef pat::PATFlagger<pat::Muon>            PATMuonFlagger;
//     typedef pat::PATFlagger<pat::Tau>             PATTauFlagger;
//     typedef pat::PATFlagger<pat::Photon>          PATPhotonFlagger;
//     typedef pat::PATFlagger<pat::Jet>             PATJetFlagger;
//     typedef pat::PATFlagger<pat::MET>             PATMETFlagger;
//     typedef pat::PATFlagger<pat::GenericParticle> PATGenericParticleFlagger;
}
using namespace pat;
DEFINE_FWK_MODULE(PATElectronFlagger);
DEFINE_FWK_MODULE(PATMuonFlagger);
// DEFINE_FWK_MODULE(PATTauFlagger);
// DEFINE_FWK_MODULE(PATPhotonFlagger);
// DEFINE_FWK_MODULE(PATJetFlagger);
// DEFINE_FWK_MODULE(PATMETFlagger);
// DEFINE_FWK_MODULE(PATGenericParticleFlagger);

