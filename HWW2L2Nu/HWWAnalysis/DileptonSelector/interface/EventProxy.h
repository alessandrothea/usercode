/*
 * =====================================================================================
 * 
 *       Filename:  EventProxy.h
 * 
 *    Description:  
 * 
 *        Version:  1.0
 *        Created:  04/16/11 19:02:52 CEST
 *       Revision:  none
 *       Compiler:  gcc
 * 
 *         Author:  A.Thea (), 
 *        Company:  CERN
 * 
 * =====================================================================================
 */

#ifndef EVENTPROXY_H_
#define EVENTPROXY_H_

#include "FWCore/Framework/interface/Event.h"
#include <DataFormats/Common/interface/Handle.h>
#include <DataFormats/PatCandidates/interface/Electron.h>
#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/PatCandidates/interface/Jet.h>
#include <DataFormats/VertexReco/interface/Vertex.h>
#include <DataFormats/METReco/interface/MET.h>
#include <DataFormats/METReco/interface/PFMET.h>


class EventProxy {
    public:
        EventProxy( const edm::Event& event , const edm::EventSetup& setup );

        /*
           Double_t getGenMET();
           Int_t* getHLTResults();
         */

        Double_t getRun();
        Double_t getEvent();
        Double_t getLumiSection();
        Double_t getTCMET();
        Double_t getTCMETphi();
        Double_t getPFMET();
        Double_t getPFMETphi();

        Double_t getNVrtx();
        Int_t    getPrimVtxIsFake();
        Int_t    getPrimVtxGood();
        Double_t getPrimVtxNdof();
        Double_t getPrimVtxRho();
        Double_t getPrimVtxx();
        Double_t getPrimVtxy();
        Double_t getPrimVtxz();

        //  apply the correction for the endcaps

        Int_t    getNEles();
        Double_t getElDeltaEtaSuperClusterAtVtx( int i );
        Double_t getElDeltaPhiSuperClusterAtVtx( int i );
        Double_t getElPt( int i );
        Double_t getElSCEta( int i );
        Double_t getElCaloEnergy( int i );
        Int_t    getElCharge( int i );
        Double_t getElConvPartnerTrkDCot( int i );
        Double_t getElConvPartnerTrkDist( int i );
        Double_t getElD0PV( int i );
        Double_t getElDR03EcalRecHitSumEt( int i );
        Double_t getElDR03HcalTowerSumEt( int i );
        Double_t getElDR03HcalFull( int i );
        Double_t getElDR03TkSumPt( int i );
        Double_t getElDR04EcalRecHitSumEt( int i );
        Double_t getElDR04HcalTowerSumEt( int i );
        Double_t getElDzPV( int i );
        Double_t getElE( int i );
        Double_t getElEta( int i );
        Double_t getElHcalOverEcal( int i );
        Int_t    getElNumberOfMissingInnerHits( int i );
        Double_t getElPx( int i );
        Double_t getElPy( int i );
        Double_t getElPz( int i );
        Double_t getElSigmaIetaIeta( int i );
        Double_t getElRho( int i );
          Bool_t getElIsEb(int i);

        Int_t    getNMus();
        Int_t    getMuCharge( int i );
        Double_t getMuD0PV( int i );
        Double_t getMuDzPV( int i );
        Double_t getMuE( int i );  
        Double_t getMuEta( int i );
        Int_t    getMuIsGlobalMuon( int i );
        Int_t    getMuIsTMLastStationAngTight( int i );
        Int_t    getMuIsTrackerMuon( int i );
        Double_t getMuIso03EmEt( int i );
        Double_t getMuIso03HadEt( int i );
        Double_t getMuIso03SumPt( int i );
        Double_t getMuNChi2( int i );
        Int_t    getMuNMatches( int i );
        Int_t    getMuNMuHits( int i );
        Int_t    getMuNPxHits( int i );
        Int_t    getMuNTkHits( int i );
        Double_t getMuPt( int i );
        Double_t getMuPtE( int i );          
        Double_t getMuPx( int i );
        Double_t getMuPy( int i );
        Double_t getMuPz( int i );
        Double_t getMuRho( int i );

        Double_t getPFNJets();
        Double_t getPFJChEmfrac( int i );
        Double_t getPFJChHadfrac( int i );
        Double_t getPFJE( int i );
        Double_t getPFJEta( int i );
        Int_t    getPFJNConstituents( int i );
        Double_t getPFJNeuEmfrac( int i );
        Double_t getPFJNeuHadfrac( int i );
        Double_t getPFJPt( int i );
        Double_t getPFJPx( int i );
        Double_t getPFJPy( int i );
        Double_t getPFJPz( int i );
        Double_t getPFJbTagProbTkCntHighEff( int i );      
    protected:
        const edm::Event& _event;
        const edm::EventSetup& _setup;

        edm::Handle<std::vector<reco::Vertex> >  _vertexes;
        edm::Handle<std::vector<pat::Electron> > _electrons;
        edm::Handle<std::vector<pat::Muon> >     _muons;
        edm::Handle<std::vector<pat::Jet> >      _jets;
        edm::Handle<std::vector<reco::MET> >     _tcMet;
        edm::Handle<std::vector<reco::PFMET> >   _pfMet;
};

#endif /* EVENTPROXY_H_ */
