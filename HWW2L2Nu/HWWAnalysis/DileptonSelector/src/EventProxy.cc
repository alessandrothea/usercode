/*
 * =====================================================================================
 *
 *       Filename:  EventProxy.cc
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  04/16/11 19:02:40 CEST
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  A.Thea (), 
 *        Company:  CERN
 *
 * =====================================================================================
 */
#include <HWWAnalysis/DileptonSelector/interface/EventProxy.h>

EventProxy::EventProxy( const edm::Event& event , const edm::EventSetup& setup ) : _event(event), _setup(setup) {

    _event.getByLabel("offlinePrimaryVertices", _vertexes);
    _event.getByLabel("boostedElectrons", _electrons);
    _event.getByLabel("boostedMuons", _muons);
    _event.getByLabel("slimPatJetsTriggerMatch", _jets);
    _event.getByLabel("tcMet", _tcMet);
    _event.getByLabel("pfMet", _pfMet);
    _event.getByLabel("chargedMetProducer", _chargedMet);


}
/*
Double_t EventProxy::getGenMET() { return _reader->GenMET;}
Int_t* EventProxy::getHLTResults() { return _reader->HLTResults;}
*/

Double_t EventProxy::getRun() { return _event.id().run();}
Double_t EventProxy::getEvent() { return _event.id().event();}
Double_t EventProxy::getLumiSection() { return _event.luminosityBlock();}
Double_t EventProxy::getTCMET() { return (*_tcMet)[0].pt();}
Double_t EventProxy::getTCMETphi() { return (*_tcMet)[0].phi();}
Double_t EventProxy::getPFMET() { return (*_pfMet)[0].pt();}
Double_t EventProxy::getPFMETphi() { return (*_pfMet)[0].phi();}
Double_t EventProxy::getChargedMET() { return (*_chargedMet).get(0).pt();}
Double_t EventProxy::getChargedMETphi() { return (*_chargedMet).get(0).phi();}

Double_t EventProxy::getNVrtx() { return _vertexes->size();}
   Int_t EventProxy::getPrimVtxGood() { return 0; }
   Int_t EventProxy::getPrimVtxIsFake() { return (*_vertexes)[0].isFake(); }
Double_t EventProxy::getPrimVtxNdof() { return (*_vertexes)[0].ndof(); }
Double_t EventProxy::getPrimVtxRho() { return (*_vertexes)[0].position().rho(); }
Double_t EventProxy::getPrimVtxx() { return (*_vertexes)[0].position().x(); }
Double_t EventProxy::getPrimVtxy() { return (*_vertexes)[0].position().y(); }
Double_t EventProxy::getPrimVtxz() { return (*_vertexes)[0].position().z(); }

// apply the correction for the endcaps

Int_t EventProxy::getNEles() { return _electrons->size();}

Double_t EventProxy::getElDeltaEtaSuperClusterAtVtx(int i) { return (*_electrons)[i].deltaEtaSuperClusterTrackAtVtx();}
Double_t EventProxy::getElDeltaPhiSuperClusterAtVtx(int i) { return (*_electrons)[i].deltaPhiSuperClusterTrackAtVtx();}
Double_t EventProxy::getElPt(int i) { return (*_electrons)[i].pt();}
Double_t EventProxy::getElCaloEnergy(int i) { return (*_electrons)[i].caloEnergy();}
   Int_t EventProxy::getElCharge(int i) { return (*_electrons)[i].charge();}
Double_t EventProxy::getElDR03EcalRecHitSumEt(int i) { return (*_electrons)[i].dr03EcalRecHitSumEt();}
Double_t EventProxy::getElDR03HcalTowerSumEt(int i) { return (*_electrons)[i].dr03HcalTowerSumEt();}
Double_t EventProxy::getElDR03HcalFull(int i) { return (*_electrons)[i].userFloat("hcalFull");}
Double_t EventProxy::getElDR03TkSumPt(int i) { return (*_electrons)[i].dr03TkSumPt();}
Double_t EventProxy::getElDR04EcalRecHitSumEt(int i) { return (*_electrons)[i].dr04EcalRecHitSumEt();}
Double_t EventProxy::getElDR04HcalTowerSumEt(int i) { return (*_electrons)[i].dr04HcalTowerSumEt();}

Double_t EventProxy::getElDzPV(int i) { return (*_electrons)[i].userFloat("dzPV");}
Double_t EventProxy::getElD0PV(int i) { return (*_electrons)[i].userFloat("dxyPV");}
Double_t EventProxy::getElConvPartnerTrkDCot(int i) { return (*_electrons)[i].userFloat("convValueMapProd:dcot"); }
Double_t EventProxy::getElConvPartnerTrkDist(int i) { return (*_electrons)[i].userFloat("convValueMapProd:dist"); }

Double_t EventProxy::getElE(int i) { return (*_electrons)[i].energy();}
Double_t EventProxy::getElEta(int i) { return (*_electrons)[i].eta();}

Double_t EventProxy::getElHcalOverEcal(int i) { return (*_electrons)[i].hcalOverEcal();}
Int_t EventProxy::getElNumberOfMissingInnerHits(int i) { return (*_electrons)[i].gsfTrack()->trackerExpectedHitsInner().numberOfHits();}
Double_t EventProxy::getElPx(int i) { return (*_electrons)[i].px();}
Double_t EventProxy::getElPy(int i) { return (*_electrons)[i].py();}
Double_t EventProxy::getElPz(int i) { return (*_electrons)[i].pz();}
Double_t EventProxy::getElSigmaIetaIeta(int i) { return (*_electrons)[i].sigmaIetaIeta();}

Double_t EventProxy::getElRho(int i) { return (*_electrons)[i].userFloat("rhoEl");}
  Bool_t EventProxy::getElIsEb(int i) { return (*_electrons)[i].isEB(); }
  Bool_t EventProxy::getElIsEe(int i) { return (*_electrons)[i].isEE(); }



Int_t EventProxy::getNMus() { return _muons->size();}

   Int_t EventProxy::getMuCharge(int i) { return (*_muons)[i].charge();}
Double_t EventProxy::getMuD0PV(int i) { return (*_muons)[i].userFloat("dxyPV");}
Double_t EventProxy::getMuDzPV(int i) { return (*_muons)[i].userFloat("dzPV");}
Double_t EventProxy::getMuE(int i) { return (*_muons)[i].energy();}  
Double_t EventProxy::getMuEta(int i) { return (*_muons)[i].eta();}
Double_t EventProxy::getMuIso03EmEt(int i) { return (*_muons)[i].isolationR03().emEt;}
Double_t EventProxy::getMuIso03HadEt(int i) { return (*_muons)[i].isolationR03().hadEt;}
Double_t EventProxy::getMuIso03SumPt(int i) { return (*_muons)[i].isolationR03().sumPt;}

// global mu id
   Int_t EventProxy::getMuIsGlobalMuon(int i) { return (*_muons)[i].isGlobalMuon() ? 1 : 0;}
   Int_t EventProxy::getMuNMatches(int i) { return (*_muons)[i].numberOfMatches();}
Double_t EventProxy::getMuNChi2(int i) { return (*_muons)[i].isGlobalMuon() ? (*_muons)[i].globalTrack()->normalizedChi2() : 0;}
   Int_t EventProxy::getMuNMuHits(int i) { return (*_muons)[i].isGlobalMuon() ? (*_muons)[i].globalTrack()->hitPattern().numberOfValidMuonHits() : 0;}

   // trk mu id
   Int_t EventProxy::getMuIsTrackerMuon(int i) { return (*_muons)[i].isTrackerMuon() ? 1 : 0;}
   Int_t EventProxy::getMuIsTMLastStationAngTight(int i) { return (*_muons)[i].muonID("TMLastStationAngTight") ? 1:0;}
   Int_t EventProxy::getMuNPxHits(int i) { return (*_muons)[i].innerTrack()->hitPattern().numberOfValidPixelHits();}
   Int_t EventProxy::getMuNTkHits(int i) { return (*_muons)[i].innerTrack()->found();}

Double_t EventProxy::getMuPt(int i) { return (*_muons)[i].pt();}
Double_t EventProxy::getMuPtE(int i) { return (*_muons)[i].track()->ptError();}          
Double_t EventProxy::getMuPx(int i) { return (*_muons)[i].px();}
Double_t EventProxy::getMuPy(int i) { return (*_muons)[i].py();}
Double_t EventProxy::getMuPz(int i) { return (*_muons)[i].pz();}
Double_t EventProxy::getMuRho(int i) { return (*_muons)[i].userFloat("rhoMu");}

// PFJets
Double_t  EventProxy::getPFNJets() { return _jets->size(); }

Double_t EventProxy::getPFJChEmfrac(int i) { return (*_jets)[i].chargedEmEnergyFraction();}
Double_t EventProxy::getPFJChHadfrac(int i) { return (*_jets)[i].chargedHadronEnergyFraction();}
Double_t EventProxy::getPFJE(int i) { return (*_jets)[i].energy();}
Double_t EventProxy::getPFJEta(int i) { return (*_jets)[i].eta();}
   Int_t EventProxy::getPFJNConstituents(int i) { return (*_jets)[i].numberOfDaughters();}
Double_t EventProxy::getPFJNeuEmfrac(int i) { return (*_jets)[i].neutralEmEnergyFraction();}
Double_t EventProxy::getPFJNeuHadfrac(int i) { return (*_jets)[i].neutralHadronEnergyFraction()+(*_jets)[i].correctedJet("Uncorrected").HFHadronEnergyFraction();}
Double_t EventProxy::getPFJPt(int i) { return (*_jets)[i].pt();}
Double_t EventProxy::getPFJPx(int i) { return (*_jets)[i].px();}
Double_t EventProxy::getPFJPy(int i) { return (*_jets)[i].py();}
Double_t EventProxy::getPFJPz(int i) { return (*_jets)[i].pz();}
Double_t EventProxy::getPFJbTagProbTkCntHighEff(int i) { return (*_jets)[i].bDiscriminator("trackCountingHighEffBJetTags");}      
