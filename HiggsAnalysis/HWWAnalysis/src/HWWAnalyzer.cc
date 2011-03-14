/*
 * HWWAnalyzer.cc
 *
 *  Created on: Dec 14, 2010
 *      Author: ale
 */

#include "HWWAnalyzer.h"
#include <TChain.h>
#include <TFile.h>
#include <TVector3.h>
#include <TLorentzVector.h>
#include "Tools.h"
#include "HWWEvent.h"
#include "HWWNtuple.h"
#include <stdexcept>
#include <fstream>
#include <TH1F.h>
#include <TDatabasePDG.h>
#include <TParticlePDG.h>
#include <THashList.h>

//_____________________________________________________________________________
void HWWAnalyzer::HiggsCutSet::print() {
//	std::cout << hMass << '\t'
//			<< ll << '\t'
//			<< etaMax << '\t'
//			<< etaMaxHard << '\t'
//			<< etaMaxSoft << '\t'
//			<< metMin << '\t'
//			<< metMax << '\t'
//			<< invMassMax << '\t'
//			<< deltaPhi << '\t'
//			<< ptMaxMin << '\t'
//			<< ptMaxMax << '\t'
//			<< ptMinMax << std::endl;
		std::cout << hMass << '\t'
				<< minPtHard << '\t'
				<< minPtSoft << '\t'
				<< maxMll << '\t'
				<< maxDphi << '\t'
				<< std::endl;
}

//_____________________________________________________________________________
HWWAnalyzer::HWWAnalyzer(int argc, char** argv) : UserAnalyzer(argc,argv), _nthMask(kNumCuts),
		_analysisTree(0x0), _event(0x0), _ntuple(0x0) {
	// TODO Auto-generated constructor stub

	_analysisTreeName = _config.getValue<std::string>("HWWAnalyzer.analysisTreeName");
	_higgsMass        = _config.getValue<int>("HWWAnalyzer.higgsMass");

	_maxD0            = _config.getValue<float>("HWWAnalyzer.maxD0");
	_maxDz            = _config.getValue<float>("HWWAnalyzer.maxDz");
	_cutFile          = _config.getValue<std::string>("HWWAnalyzer.cutFile");
	_minMet           = _config.getValue<float>("HWWAnalyzer.minMet");
	_minMll           = _config.getValue<float>("HWWAnalyzer.minMll");
	_zVetoWidth       = _config.getValue<float>("HWWAnalyzer.zVetoWidth");

	_minProjMetEM     = _config.getValue<float>("HWWAnalyzer.minProjMetEM");
	_minProjMetLL     = _config.getValue<float>("HWWAnalyzer.minProjMetLL");

	_histLabels = _config.getVector<std::string>("HWWAnalyzer.copyHistograms");

	std::ostream_iterator< std::string > output( std::cout, "," );
	std::copy(_histLabels.begin(), _histLabels.end(), output);

	TDatabasePDG* pdg = TDatabasePDG::Instance();
	_Z0 = pdg->GetParticle("Z0");

	readHiggsCutSet( _cutFile );

	_theCuts = getHiggsCutSet( _higgsMass );

	// initialize the bitmask
	higgsBitWord dummy( (1 << kNumCuts )-1);
	dummy.set(0,0).set(1,0);
	_theMask = dummy;

	// initialize the n-1 masks
	for( int k=2; k<kNumCuts; ++k) {
		_nthMask[k] = _theMask;
		_nthMask[k].set(k,false);
	}

//	std::cout << "----" << std::endl;
//
//	std::cout << kCharge << "  " << _nthMask[kCharge].to_string() << std::endl;
//	std::cout << kZveto << "  " << _nthMask[kZveto].to_string() << std::endl;
//	std::cout << kMaxMll << "  " << _nthMask[kMaxMll].to_string() << std::endl;
//
//	std::cout << "----" << std::endl;
//
//	higgsBitWord wTest, wK;
//
//	wTest.set(kCharge,1).set(kD0,1).set(kDz,1)
//			.set(kMinMet,1).set(kMinMll,1).set(kZveto,1)
//			.set(kProjMet,1).set(kJetVeto,1).set(kSoftMuon,1)
//			.set(kHardPtMin,1).set(kSoftPtMin,1).set(kMaxMll,1).set(kDeltaPhi,1);
//
//	std::cout << _theMask.to_string() << "   " << wTest.to_string() << std::endl;
//	std::cout << "are the same?" << (_theMask == wTest) << std::endl;
//
//	std::cout << wK <<  "  " << (_theMask & wK).to_string() << std::endl;

//	THROW_RUNTIME("End Test");
}

//_____________________________________________________________________________
HWWAnalyzer::~HWWAnalyzer() {
	// TODO Auto-generated destructor stub
}

//_____________________________________________________________________________
void HWWAnalyzer::Book() {
	if (!_output) return;

	_output->cd();

	std::map<int,std::string> labels;

	labels[kDileptons] = "N_{l^{+}l^{-}}";
//	labels[kCharge]    = "Opposite charge";
//	labels[kD0]        = "D0";
//	labels[kDz]        = "Dz";
	labels[kMinMet]    = "Met_{min}";
	labels[kMinMll]    = "m^{ll}_{min}";
	labels[kZveto]     = "Z veto";
	labels[kProjMet]   = "ProjMet";
	labels[kJetVeto]   = "n_{jets} == 0";
	labels[kSoftMuon]  = "No Soft #mu";
	labels[kTopVeto]   = "Top Veto";
	labels[kMaxMll]    = "m^{ll}_{max}";
	labels[kHardPtMin] = "p^{hard}_{min}";
	labels[kSoftPtMin] = "p^{soft}_{min}";
	labels[kDeltaPhi]  = "#Delta#Phi_{ll}";


	_eeCounters = new TH1F("eeCounters","eeCounters",labels.size(),1,labels.size()+1);
	_mmCounters = new TH1F("mmCounters","mmCounters",labels.size(),1,labels.size()+1);
	_emCounters = new TH1F("emCounters","emCounters",labels.size(),1,labels.size()+1);
	_llCounters = new TH1F("llCounters","llCounters",labels.size(),1,labels.size()+1);

	std::map<int,std::string>::iterator it;
	for ( it = labels.begin(); it != labels.end(); ++it) {
		_eeCounters->GetXaxis()->SetBinLabel(it->first, it->second.c_str());
		_mmCounters->GetXaxis()->SetBinLabel(it->first, it->second.c_str());
		_emCounters->GetXaxis()->SetBinLabel(it->first, it->second.c_str());
		_llCounters->GetXaxis()->SetBinLabel(it->first, it->second.c_str());
	}

	_jetN      = new TH1F("jetN",    "n_{jets}", 15, 0, 15);
	_jetPt     = new TH1F("jetPt",   "Jet Pt",   100, 0, 1000);
	_jetEta    = new TH1F("jetEta",  "Jet Eta",  100, -5, 5);
	_projMet   = new TH1F("projMet", "Projected MET", 100, 0, 100);
	_ptHardLet = new TH1F("hardPt",  "p^{hard}", 100, 0, 3.*_theCuts.minPtHard);
	_ptSoftLep = new TH1F("softPt",  "p^{soft}", 100, 0, 3.*_theCuts.minPtSoft);
	_mll       = new TH1F("mll",     "m^{ll}",   100, 0,  100);
	_deltaPhi  = new TH1F("deltaPhi","#Delta#Phi_{ll}", 100, 0, TMath::Pi());

	_output->mkdir("ll")->cd();
	bookCutHistograms( _llNm1Hist, "llNm1", "ll N-1 Plot - " );

	_output->mkdir("ee")->cd();
	bookCutHistograms( _eeNm1Hist, "eeNm1", "ee N-1 Plot - " );

	_output->mkdir("em")->cd();
	bookCutHistograms( _emNm1Hist, "emNm1", "e#mu N-1 Plot - " );

	_output->mkdir("mm")->cd();
	bookCutHistograms( _mmNm1Hist, "mmNm1", "#mu#mu N-1 Plot - " );

	_output->mkdir("checks")->cd();
	bookCutHistograms( _preCutHist, "pre", "PreCut - ");
	bookCutHistograms( _postCutHist, "post", "PostCut - ");

	_output->cd();

	_analysisTree = new TTree(_analysisTreeName.c_str(),"HWW variables Tree");
	_analysisTree->Branch("nt","HWWNtuple",&_ntuple);

}

//_____________________________________________________________________________
Bool_t HWWAnalyzer::Notify() {
	if (  _chain->GetCurrentFile() ) {
		std::cout << "--- Notify(): New file opened: "<<  _chain->GetCurrentFile()->GetName() << std::endl;
		bool add = TH1::AddDirectoryStatus();
		TH1::AddDirectory(kFALSE);
		std::vector<std::string>::iterator it;
		for( it = _histLabels.begin(); it!=_histLabels.end();it++) {
			//std::cout << *it << "  " << _chain->GetCurrentFile()->Get(it->c_str()) << std::endl;
			TH1F* h = (TH1F*)_chain->GetCurrentFile()->Get(it->c_str());
			if ( _hists.find(*it) == _hists.end() ) {
				_hists[*it] = (TH1F*)h->Clone();
			} else {
				_hists[*it]->Add(h);
			}
		}
		TH1::AddDirectory(add);

	} else {
		std::cout << "--- Notify(): No file opened yet" << std::endl;
	}
}

//_____________________________________________________________________________
void HWWAnalyzer::BeginJob() {
	_chain->SetBranchAddress("ev", &_event);

}

//_____________________________________________________________________________
void HWWAnalyzer::bookCutHistograms( std::vector<TH1F*>& histograms , const std::string& nPrefix, const std::string& lPrefix ) {

	// all numbers to 0, just to be sure;
	histograms.assign(kNumCuts,0x0);

//	histograms[kCharge] 	= new TH1F((nPrefix+"Charge").c_str(),     (lPrefix+"Charge").c_str(),3,-1,2);
//	histograms[kD0]			= new TH1F((nPrefix+"D0").c_str(),         (lPrefix+"D0").c_str(), 100, -3*_maxD0, 3*_maxD0);
//	histograms[kDz]			= new TH1F((nPrefix+"Dz").c_str(),         (lPrefix+"Dz").c_str(), 100, -3*_maxDz, 3*_maxDz);
	histograms[kMinMet]		= new TH1F((nPrefix+"MinMet").c_str(),     (lPrefix+"Met_{min}").c_str(),	    100, 0, 100);
	histograms[kMinMll]		= new TH1F((nPrefix+"MinMll").c_str(),     (lPrefix+"m^{ll}_{min}").c_str(),    100, 0, 100);
	histograms[kZveto]		= new TH1F((nPrefix+"Zveto").c_str(),      (lPrefix+"Z veto").c_str(), 		    100, 0, 120);
	histograms[kProjMet]	= new TH1F((nPrefix+"MinProjMet").c_str(), (lPrefix+"Projected MET").c_str(),   100, 0, 100);
	histograms[kJetVeto]	= new TH1F((nPrefix+"JetVeto").c_str(),    (lPrefix+"n_{jets} = 0").c_str(),     15, 0, 15);
	histograms[kSoftMuon]	= new TH1F((nPrefix+"SoftMuon").c_str(),   (lPrefix+"No Soft #mu").c_str(),       2, 0, 2);
	histograms[kTopVeto]	= new TH1F((nPrefix+"TopVeto").c_str(),    (lPrefix+"Top Veto").c_str(),          2, 0, 2);
	histograms[kHardPtMin]	= new TH1F((nPrefix+"MinHardPt").c_str(),  (lPrefix+"p^{hard}_{min}").c_str(),  100, 0, 3.*_theCuts.minPtHard);
	histograms[kSoftPtMin]	= new TH1F((nPrefix+"MinSoftPt").c_str(),  (lPrefix+"p^{soft}_{min}").c_str(),  100, 0, 3.*_theCuts.minPtSoft);
	histograms[kMaxMll]		= new TH1F((nPrefix+"MaxMll").c_str(),     (lPrefix+"m^{ll}_{max}").c_str(),    100, 0,  100);
	histograms[kDeltaPhi]	= new TH1F((nPrefix+"DeltaPhi").c_str(),   (lPrefix+"#Delta#Phi_{ll}").c_str(), 100, 0, TMath::Pi());

}

//_____________________________________________________________________________
void HWWAnalyzer::readHiggsCutSet( const std::string& path ) {

	std::cout << "Reading cuts from file " << path << std::endl;

	ifstream cutFile(path.c_str(), ifstream::in);
	if ( !cutFile.is_open() ) {
		THROW_RUNTIME(std::string("File ") + path + " not found");
	}

	std::string line;
	while( cutFile.good() ) {
		getline(cutFile, line);
		// remove trailing and leading spaces

		std::stringstream ss(line), ssTmp(line);
		std::string dummy, a;

		ssTmp >> dummy;
		if ( dummy.empty() || dummy[0]=='#') continue;

		HiggsCutSet h;
		ss >> h.hMass;

		ss >> h.minPtHard >> h.minPtSoft >> h.maxMll >> h.maxDphi;

		h.print();

		_cutVector.push_back(h);
	}
}

//_____________________________________________________________________________
HWWAnalyzer::HiggsCutSet HWWAnalyzer::getHiggsCutSet(int mass) {
	std::vector<HiggsCutSet>::iterator it;
	for ( it=_cutVector.begin(); it != _cutVector.end(); ++it) {
		if ( (*it).hMass == mass )
			return *it;
	}

	std::stringstream msg;
	msg << "Higgs Cut set " << mass << " not found";
	THROW_RUNTIME(msg.str());

}

//_____________________________________________________________________________
void HWWAnalyzer::calcNtuple(){

	TLorentzVector pA, pB;
	Int_t cA, cB;
	double d0A, d0B;
	double dZA, dZB;
	double maxProjMet;
	TH1F* counters;

    switch ( _event->NEles ) {
    case 2:
    	// A has the highst pT?
    	pA = _event->Els[0].P;
    	pB = _event->Els[1].P;

    	cA = _event->Els[0].Charge;
    	cB = _event->Els[1].Charge;

    	d0A = _event->Els[0].D0PV;
    	d0B = _event->Els[1].D0PV;

    	dZA = _event->Els[0].DzPV;
    	dZB = _event->Els[1].DzPV;

    	maxProjMet = _minProjMetLL;
    	counters = _eeCounters;
    	break;
    case 1:
    	if ( _event->Els[0].P.Pt() > _event->Mus[0].P.Pt() ) {
        	pA = _event->Els[0].P;
        	pB = _event->Mus[0].P;

        	cA = _event->Els[0].Charge;
        	cB = _event->Mus[0].Charge;

        	d0A = _event->Els[0].D0PV;
        	d0B = _event->Mus[0].D0PV;

        	dZA = _event->Els[0].DzPV;
        	dZB = _event->Mus[0].DzPV;
    	} else {
        	pA = _event->Mus[0].P;
        	pB = _event->Els[0].P;

        	cA = _event->Mus[0].Charge;
        	cB = _event->Els[0].Charge;

        	d0A = _event->Mus[0].D0PV;
        	d0B = _event->Els[0].D0PV;

        	dZA = _event->Mus[0].DzPV;
        	dZB = _event->Els[0].DzPV;
    	}

    	maxProjMet = _minProjMetEM;
    	counters = _emCounters;
    	break;
    case 0:
    	// A has the highst pT?
    	pA = _event->Mus[0].P;
    	pB = _event->Mus[1].P;

    	cA = _event->Mus[0].Charge;
    	cB = _event->Mus[1].Charge;

    	d0A = _event->Mus[0].D0PV;
    	d0B = _event->Mus[1].D0PV;

    	dZA = _event->Mus[0].DzPV;
    	dZB = _event->Mus[1].DzPV;

    	maxProjMet = _minProjMetLL;
    	counters = _mmCounters;
    	break;
    }

    // we work on the assumption A is the highet pT lepton, B is not. This is a watchdog
    if ( pB.Pt() > pA.Pt() ) {
    	THROW_RUNTIME("A.Pt < B.Pt");
    }

    // opposite charge
    bool oppositeCharge = ( cA*cB < 0 );

    // 3 - invariant mass
    double mll = (pA+pB).Mag();

    // 4a pfMet
	double pfMet = _event->PFMET;
	// 4b - muMet
	double muMet = _event->MuCorrMET;

	// 5 - projected MeT
	// 5a - projPfMet
	short i;

	TLorentzVector pfMetV;
	pfMetV.SetPtEtaPhiE(_event->PFMET, 0, _event->PFMETphi,0);

	double pfMetDphi = TMath::Min(TMath::Abs(pA.DeltaPhi(pfMetV)), TMath::Abs(pB.DeltaPhi(pfMetV)));
	double projPfMet = pfMetDphi < TMath::PiOver2() ? pfMet*TMath::Sin(pfMetDphi) : pfMet;


	// 5b - projMuMet
	TLorentzVector muMetV;
	muMetV.SetPtEtaPhiE(_event->MuCorrMET, 0, _event->MuCorrMETphi, 0);

	double muMetDphi = TMath::Min(TMath::Abs(pA.DeltaPhi(muMet)), TMath::Abs(pB.DeltaPhi(muMet)));
	double projMuMet = muMetDphi < TMath::PiOver2() ? muMet*TMath::Sin(muMetDphi) : muMet;

	// 6 - dPhiEE
	double dPhiLL = TMath::Abs(pA.DeltaPhi(pB));

	// 7 - jet veto
	// 7a - pf jets
	int nPfJets = _event->PFNJets;
	// 7b - calo jets
	int nJets   = _event->NJets;

	double pTHard = pA.Pt();
	double pTSoft = pB.Pt();

	// 8 soft  muon
	bool softMu = _event->HasSoftMus;

	_ntuple->type = _event->NEles;

    _ntuple->cA = cA;
    _ntuple->cB = cB;

    _ntuple->pA = pA;
    _ntuple->pB = pB;

    _ntuple->d0A = d0A;
    _ntuple->d0B = d0B;

    _ntuple->dZA = dZA;
    _ntuple->dZB = dZB;

	_ntuple->mll        = mll;
	_ntuple->pfMet      = pfMet;
	_ntuple->muMet      = muMet;
	_ntuple->projPfMet  = projPfMet;
	_ntuple->projMuMet  = projMuMet;
	_ntuple->dPhi     = dPhiLL;
	_ntuple->nPfJets	 = nPfJets;
	_ntuple->nJets      = nJets;
	_ntuple->softMus     = softMu;

	_analysisTree->Fill();

}

//_____________________________________________________________________________
void HWWAnalyzer::cutAndFill() {

	higgsBitWord word;

	word.set(kMinMet, _ntuple->pfMet > _minMet );

	word.set(kMinMll, _ntuple->type == 1 || _ntuple->mll > _minMll);

	word.set(kZveto, _ntuple->type == 1 || TMath::Abs(_ntuple->mll - _Z0->Mass()) > _zVetoWidth );

	float minProjMet = _ntuple->type == 1 ? _minProjMetEM : _minProjMetLL;
	word.set(kProjMet, _ntuple->projPfMet > minProjMet);

	word.set(kJetVeto, _ntuple->nPfJets == 0);

	word.set(kSoftMuon, _ntuple->softMus == 0);

	word.set(kTopVeto, !_ntuple->bJets);

	word.set(kHardPtMin, _ntuple->pA.Pt() > _theCuts.minPtHard);

	word.set(kSoftPtMin, _ntuple->pB.Pt() > _theCuts.minPtSoft);

	//TODO check if maxMll applies to all the combinations
	word.set(kMaxMll, _ntuple->mll < _theCuts.maxMll);

	word.set(kDeltaPhi, _ntuple->dPhi < _theCuts.maxDphi*TMath::DegToRad() );

	// type-dependent settings
	TH1F* counters(0x0);
    std::vector<TH1F*>* nm1;
	switch ( _ntuple->type ) {
	case 2:
		counters = _eeCounters;
        nm1 = &_eeNm1Hist;
		break;
	case 1:
		counters = _emCounters;
        nm1 = &_emNm1Hist;
		break;
	case 0:
		counters = _mmCounters;
        nm1 = &_mmNm1Hist;
		break;
	default:
		THROW_RUNTIME("Wrong event type (NEles): " << _ntuple->type );
	};

	if ( (word & _nthMask[kMinMet]) == _nthMask[kMinMet] )
		nm1->at(kMinMet)->Fill(_ntuple->pfMet);

	if ( (word & _nthMask[kMinMll]) == _nthMask[kMinMll] )
		nm1->at(kMinMll)->Fill(_ntuple->mll);

	if ( (word & _nthMask[kZveto]) == _nthMask[kZveto] )
		nm1->at(kZveto)->Fill(_ntuple->mll);

	if ( (word & _nthMask[kProjMet]) == _nthMask[kProjMet] )
		nm1->at(kProjMet)->Fill(_ntuple->projPfMet);

	if ( (word & _nthMask[kJetVeto]) == _nthMask[kJetVeto] )
		nm1->at(kJetVeto)->Fill(_ntuple->nPfJets);

	if ( (word & _nthMask[kSoftMuon]) == _nthMask[kSoftMuon] )
		nm1->at(kSoftMuon)->Fill(_ntuple->softMus);

	if ( (word & _nthMask[kTopVeto]) == _nthMask[kTopVeto] )
		nm1->at(kTopVeto)->Fill(_ntuple->bJets);

	if ( (word & _nthMask[kHardPtMin]) == _nthMask[kHardPtMin] )
		nm1->at(kHardPtMin)->Fill(_ntuple->pA.Pt());

	if ( (word & _nthMask[kSoftPtMin]) == _nthMask[kSoftPtMin] )
		nm1->at(kSoftPtMin)->Fill(_ntuple->pB.Pt());

	if ( (word & _nthMask[kMaxMll]) == _nthMask[kMaxMll] )
		nm1->at(kMaxMll)->Fill(_ntuple->mll);

	if ( (word & _nthMask[kDeltaPhi]) == _nthMask[kDeltaPhi] )
		nm1->at(kDeltaPhi)->Fill(_ntuple->dPhi);




	counters->Fill(kDileptons);
	// min missing Et
	_preCutHist[kMinMet]->Fill(_ntuple->pfMet);
	if ( !word[kMinMet] ) return;
	counters->Fill(kMinMet);
	_postCutHist[kMinMet]->Fill(_ntuple->pfMet);

	// min invariant mass
	_preCutHist[kMinMll]->Fill(_ntuple->mll);
	if ( !word[kMinMll] ) return;
	counters->Fill(kMinMll);
	_postCutHist[kMinMll]->Fill(_ntuple->mll);

	// Z veto (m_ll-m_Z < 15 GeV)
	_preCutHist[kZveto]->Fill(_ntuple->mll);
	if ( !word[kZveto] ) return;
	counters->Fill(kZveto);
	_postCutHist[kZveto]->Fill(_ntuple->mll);

	// proj Met (20 GeV for ee)
	_preCutHist[kProjMet]->Fill(_ntuple->projPfMet);
	if ( !word[kProjMet] ) return;
	counters->Fill(kProjMet);
	_postCutHist[kProjMet]->Fill(_ntuple->projPfMet);

	// pause here for jet pt and eta
	_jetN->Fill(_event->PFJets.size());
	for ( int i(0); i<_event->PFJets.size(); ++i) {
		_jetPt->Fill(_event->PFJets[i].P.Pt());
		_jetEta->Fill(_event->PFJets[i].P.Eta());
	}

	// njets == 0
	_preCutHist[kJetVeto]->Fill(_ntuple->nPfJets);
	if ( !word[kJetVeto] ) return;
	counters->Fill(kJetVeto);
	_postCutHist[kJetVeto]->Fill(_ntuple->nPfJets);

	// soft muon
	_preCutHist[kSoftMuon]->Fill(_ntuple->softMus);
	if ( !word[kSoftMuon] ) return;
	counters->Fill(kSoftMuon);
	_postCutHist[kSoftMuon]->Fill(_ntuple->softMus);

	// soft muon
	_preCutHist[kTopVeto]->Fill(_ntuple->bJets);
	if ( !word[kTopVeto] ) return;
	counters->Fill(kTopVeto);
	_postCutHist[kTopVeto]->Fill(_ntuple->bJets);

	// hard pt cut
	_preCutHist[kHardPtMin]->Fill(_ntuple->pA.Pt());
	if ( !word[kHardPtMin] ) return;
	counters->Fill(kHardPtMin);
	_postCutHist[kHardPtMin]->Fill(_ntuple->pA.Pt());

	// soft pt cut
	_preCutHist[kSoftPtMin]->Fill(_ntuple->pB.Pt());
	if ( !word[kSoftPtMin] ) return;
	counters->Fill(kSoftPtMin);
	_postCutHist[kSoftPtMin]->Fill(_ntuple->pB.Pt());

	_preCutHist[kMaxMll]->Fill(_ntuple->mll);
	// Mll_max
	if ( !word[kMaxMll] ) return;
	counters->Fill(kMaxMll);
	_postCutHist[kMaxMll]->Fill(_ntuple->mll);

	// delta phi
	_preCutHist[kDeltaPhi]->Fill(_ntuple->dPhi);
	if ( !word[kDeltaPhi] ) return;
	counters->Fill(kDeltaPhi);
	_postCutHist[kDeltaPhi]->Fill(_ntuple->dPhi);

	_projMet->Fill(_ntuple->projPfMet);
	_ptHardLet->Fill(_ntuple->pA.Pt());
	_ptSoftLep->Fill(_ntuple->pB.Pt());
	_mll->Fill(_ntuple->mll);
	_deltaPhi->Fill(_ntuple->dPhi);

}

//_____________________________________________________________________________
void HWWAnalyzer::Process( Long64_t iEvent ) {
//	std::cout << iEvent <<  std::endl;
	_chain->GetEntry(iEvent);

	_ntuple->Clear();

	if ( _event->NEles + _event->NMus != 2 )
		THROW_RUNTIME("Wrong number of leptons in the event: NEles = " << _event->NEles << " NMus = " << _event->NMus  );

	calcNtuple();
	cutAndFill();

}

//_____________________________________________________________________________
void HWWAnalyzer::EndJob() {

	_llCounters->Add(_eeCounters);
	_llCounters->Add(_emCounters);
	_llCounters->Add(_mmCounters);

	for ( int k(0); k<_llNm1Hist.size(); ++k) {
		if (!_llNm1Hist[k] ) continue;
		_llNm1Hist[k]->Add(_eeNm1Hist[k]);
		_llNm1Hist[k]->Add(_emNm1Hist[k]);
		_llNm1Hist[k]->Add(_mmNm1Hist[k]);
	}

	_output->mkdir("lepSelection")->cd();
	std::map<std::string,TH1F*>::iterator it;
	for( it = _hists.begin(); it!=_hists.end();it++) {
		it->second->Write();
	}

	_output->mkdir("fullSelection")->cd();
	glueCounters(_eeCounters);
	glueCounters(_emCounters);
	glueCounters(_mmCounters);
	glueCounters(_llCounters);

}

//_____________________________________________________________________________
TH1F* HWWAnalyzer::glueCounters(TH1F* c) {

	std::string name = c->GetName();
	std::map<std::string,TH1F*>::iterator it = _hists.find(name);
	if ( it == _hists.end() ) return 0x0;
	TH1F* cPre = it->second;

	bool add = TDirectory::AddDirectoryStatus();
	TDirectory::AddDirectory(kFALSE);
	TH1F* cClone = dynamic_cast<TH1F*>(c->Clone("cClone"));
	TDirectory::AddDirectory(add);

	int nBins    = cClone->GetNbinsX();
	int nBinsPre = cPre->GetNbinsX();

	// check bin content
	if ( cPre->GetBinContent(nBinsPre) != cClone->GetBinContent(1) )
		THROW_RUNTIME("Bin mismatch: Wrong histogram? "<<nBins << "  "<<nBinsPre );

	cClone->Fill(1,cClone->GetBinContent(1)*-1);

	// matching possible, build labels
	THashList labels;
	labels.AddAll(cPre->GetXaxis()->GetLabels());
	labels.AddAll(cClone->GetXaxis()->GetLabels());
	labels.RemoveAt(nBinsPre);

//	TIter iter(&labels);
//	while( TObjString* str = (TObjString*)iter.Next() )
//		std::cout << str->GetName() << std::endl;

	int nBinsNew = nBinsPre+nBins-1;

	float xmin = cPre->GetXaxis()->GetXmin();
	float xmax = xmin+nBinsNew;
	TH1F* hNew = new TH1F(cPre->GetName(),cPre->GetTitle(),nBinsNew,xmin,xmax);

	TAxis* ax = hNew->GetXaxis();
	for( int i(0); i<labels.GetEntries(); ++i)
		ax->SetBinLabel(i+1,labels.At(i)->GetName());

	THashList histograms;
	histograms.Add(cPre);
	histograms.Add(cClone);

	hNew->Merge(&histograms);
	if ( hNew->GetNbinsX() != nBinsNew )
		THROW_RUNTIME("Merge screwed it up! "<< hNew->GetNbinsX() << "  " << nBinsNew );

	for( int i(1);i<=cPre->GetNbinsX(); ++i)
		if( hNew->GetBinContent(i) != cPre->GetBinContent(i))
			THROW_RUNTIME("Failed HA check:" << i << ":"<< hNew->GetBinContent(i) << "  "<< cPre->GetBinContent(i))
	for( int i(2);i<=cClone->GetNbinsX(); ++i)
		if( hNew->GetBinContent(i+cPre->GetNbinsX()-1) != cClone->GetBinContent(i))
			THROW_RUNTIME("Failed HB check:" << i << ":"<< hNew->GetBinContent(i+cPre->GetNbinsX()-1) << "  "<< cClone->GetBinContent(i))

	delete cClone;

	return hNew;

}
