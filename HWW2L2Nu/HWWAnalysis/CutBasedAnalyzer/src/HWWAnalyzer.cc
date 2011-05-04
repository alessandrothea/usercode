/*
 * HWWAnalyzer.cc
 *
 *  Created on: Dec 14, 2010
 *      Author: ale
 */

#include "HWWAnalysis/CutBasedAnalyzer/interface/HWWAnalyzer.h"
#include "HWWAnalysis/CutBasedAnalyzer/interface/Tools.h"
#include "HWWAnalysis/DataFormats/interface/HWWEvent.h"
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"
#include <TChain.h>
#include <TFile.h>
#include <TVector3.h>
#include <TLorentzVector.h>
#include <stdexcept>
#include <fstream>
#include <TH1F.h>
#include <THashList.h>
#include <TH2F.h>


const double HWWAnalyzer::_Z0Mass = 9.11869999999999976e+01;

//_____________________________________________________________________________
void HWWAnalyzer::HiggsCutSet::print() {
		std::cout << hMass << '\t'
				<< minPtHard << '\t'
				<< minPtSoft << '\t'
				<< maxMll << '\t'
				<< maxDphi << '\t'
				<< std::endl;
}

//_____________________________________________________________________________
HWWAnalyzer::HWWAnalyzer(int argc, char** argv) : UserAnalyzer(argc,argv), _nthMask(kNumCuts),
		_hEntries(0x0), _analysisTree(0x0), _event(0x0), _ntuple(0x0) {
	// TODO Auto-generated constructor stub

	_analysisTreeName = _config.getValue<std::string>("HWWAnalyzer.analysisTreeName");

	_higgsMass        = _config.getValue<int>("HWWAnalyzer.higgsMass");

	_cutFile          = _config.getValue<std::string>("HWWAnalyzer.cutFile");
	_minMet           = _config.getValue<float>("HWWAnalyzer.minMet");
	_minMll           = _config.getValue<float>("HWWAnalyzer.minMll");
	_zVetoWidth       = _config.getValue<float>("HWWAnalyzer.zVetoWidth");

	_minProjMetEM     = _config.getValue<float>("HWWAnalyzer.minProjMetEM");
	_minProjMetLL     = _config.getValue<float>("HWWAnalyzer.minProjMetLL");

//     _jetVeto_n        = _config.getValue<int>("HWWAnalyzer.jetVeto.n");// = 0.
//     _jetVeto_pt       = _config.getValue<float>("HWWAnalyzer.jetVeto.pt"); // = 25.
//     _jetVeto_eta      = _config.getValue<float>("HWWAnalyzer.jetVeto.eta");// = 5.
//     _topVeto_bTagProb = _config.getValue<float>("HWWAnalyzer.topVeto.bTagProb");// = 2.1


	_histLabels = _config.getVector<std::string>("HWWAnalyzer.copyHistograms");

	//std::copy(_histLabels.begin(), _histLabels.end(), output);

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

}

//_____________________________________________________________________________
HWWAnalyzer::~HWWAnalyzer() {
	// TODO Auto-generated destructor stub
}

//_____________________________________________________________________________
void HWWAnalyzer::Book() {
	if (!_output) return;

	_output->cd();
	std::map<int,std::string> entriesLabels;
	entriesLabels[0] = "Entries";
	entriesLabels[1] = "Pre-selected Entries";
	_hEntries = makeLabelHistogram("entries","HWW selection entries",entriesLabels);

	std::map<int,std::string> labels;

	labels[kDileptons] = "N_{l^{+}l^{-}}";
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


	_eeCounters = makeLabelHistogram("eeCounters","eeCounters",labels);
	_mmCounters = makeLabelHistogram("mmCounters","mmCounters",labels);
	_emCounters = makeLabelHistogram("emCounters","emCounters",labels);
	_meCounters = makeLabelHistogram("meCounters","meCounters",labels);//TODO
	_llCounters = makeLabelHistogram("llCounters","llCounters",labels);


	_output->mkdir("jetVeto")->cd();
	_jetN      = new TH1F("jetN",    "n_{jets} (pre-veto)", 20, 0, 20);
	_jetPt     = new TH1F("jetPt",   "Jet Pt (pre-veto)",   100, 0, 1000);
	_jetEta    = new TH1F("jetEta",  "Jet Eta (pre-veto)",  100, -5, 5);

	_output->mkdir("alldileptons")->cd();
	_diLep_PfMet  	      = new TH1F("pfMet", "PfMET", 200, 0, 200);
	_diLep_TcMet  	      = new TH1F("tcMet",  "TcMET", 200, 0, 200);
	_diLep_ChargedMet     = new TH1F("chargedMet",  "ChargedMET", 200, 0, 200);
	_diLep_projPfMet      = new TH1F("projPfMet", "Projected PfMET", 200, 0, 200);
	_diLep_projTcMet      = new TH1F("projTcMet", "Projected TcMET", 200, 0, 200);
	_diLep_projChargedMet = new TH1F("projChargedMet", "Projected ChargedMET", 200, 0, 200);
	_diLep_ptLeadLep      = new TH1F("leadingPt",  "p^{lead}", 200, 0, 200);
	_diLep_ptTrailLep     = new TH1F("trailingPt",  "p^{trail}", 200, 0, 200);
	_diLep_mll            = new TH1F("mll",     "m^{ll}",   300, 0,  300);
	_diLep_deltaPhi       = new TH1F("deltaPhi","#Delta#Phi_{ll}", 100, 0, TMath::Pi());


	_output->mkdir("pileUp")->cd();
	_nVrtx	   = new TH1F("nVrtx",	 "n_{vrtx}", 20, 1, 21);
	_llJetNVsNvrtx = makeNjetsNvrtx("llNjetsNvrtx");
	_eeJetNVsNvrtx = makeNjetsNvrtx("eeNjetsNvrtx", "ee - ");
	_emJetNVsNvrtx = makeNjetsNvrtx("emNjetsNvrtx", "em - ");
	_meJetNVsNvrtx = makeNjetsNvrtx("meNjetsNvrtx", "me - ");//TODO
	_mmJetNVsNvrtx = makeNjetsNvrtx("mmNjetsNvrtx", "mm - ");

	_output->mkdir("llNminus1")->cd();
	bookCutHistograms( _llNm1Hist, "llNm1", "ll N-1 Plot - " );

	_output->mkdir("eeNminus1")->cd();
	bookCutHistograms( _eeNm1Hist, "eeNm1", "ee N-1 Plot - " );

	_output->mkdir("emNminus1")->cd();
	bookCutHistograms( _emNm1Hist, "emNm1", "e#mu N-1 Plot - " );

	_output->mkdir("meNminus1")->cd(); //TODO
	bookCutHistograms( _meNm1Hist, "meNm1", "#mu e N-1 Plot - " );

	_output->mkdir("mmNminus1")->cd();
	bookCutHistograms( _mmNm1Hist, "mmNm1", "#mu#mu N-1 Plot - " );

	_output->mkdir("llCuts")->cd();
	bookCutHistograms( _llPreCutHist,  "llPre",  "ll PreCut - ");
	bookCutHistograms( _llPostCutHist, "llPost", "ll PostCut - ");

	_output->mkdir("eeCuts")->cd();
	bookCutHistograms( _eePreCutHist,  "eePre",  "ee PreCut - ");
	bookCutHistograms( _eePostCutHist, "eePost", "ee PostCut - ");

	_output->mkdir("emCuts")->cd();
	bookCutHistograms( _emPreCutHist,  "emPre",  "em PreCut - ");
	bookCutHistograms( _emPostCutHist, "emPost", "em PostCut - ");

	_output->mkdir("meCuts")->cd(); //TODO
	bookCutHistograms( _mePreCutHist,  "mePre",  "me PreCut - ");
	bookCutHistograms( _mePostCutHist, "mePost", "me PostCut - ");

	_output->mkdir("mmCuts")->cd();
	bookCutHistograms( _mmPreCutHist,  "mmPre",  "mm PreCut - ");
	bookCutHistograms( _mmPostCutHist, "mmPost", "mm PostCut - ");

	_output->cd();

	_analysisTree = new TTree(_analysisTreeName.c_str(),"HWW variables Tree");
	_analysisTree->Branch("nt","HWWNtuple",&_ntuple);

}

//_____________________________________________________________________________
Bool_t HWWAnalyzer::Notify() {

	if ( !isInitialized() ) {
		std::cout << "Analyzer not initialized yet" << std::endl;
		return true;
	}


	if (  _chain->GetCurrentFile() ) {
		std::cout << "--- Notify(): New file opened: "<<  _chain->GetCurrentFile()->GetName() << std::endl;
		bool add = TH1::AddDirectoryStatus();
		TH1::AddDirectory(kFALSE);

//         std::cout << _hEntries << std::endl;
		TH1F* entries = (TH1F*)_chain->GetCurrentFile()->Get((_folder+"/entries").c_str());
		if ( !entries )
			std::cout << "Warning: Preselection entries not found" << std::endl;
		else
			_hEntries->Add(entries);

		std::vector<std::string>::iterator it;
		for( it = _histLabels.begin(); it!=_histLabels.end();it++) {
			TH1F* h = (TH1F*)_chain->GetCurrentFile()->Get( (_folder+'/'+*it).c_str());
			if ( !h ) {
				std::cout << "Warning: histogram "<< *it << " not found" << std::endl;
				continue;
			}

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

	return true;
}

//_____________________________________________________________________________
void HWWAnalyzer::BeginJob() {
	_chain->SetBranchAddress("ev", &_event);

}

//_____________________________________________________________________________
void HWWAnalyzer::bookCutHistograms( std::vector<TH1F*>& histograms , const std::string& nPrefix, const std::string& lPrefix ) {

	// all numbers to 0, just to be sure;
	histograms.assign(kNumCuts,0x0);

	histograms[kMinMet]		= new TH1F(("01_"+nPrefix+"MinMet").c_str(),     (lPrefix+"Met_{min}").c_str(),	      100, 0, 100);
	histograms[kMinMll]		= new TH1F(("02_"+nPrefix+"MinMll").c_str(),     (lPrefix+"m^{ll}_{min}").c_str(),    300, 0, 300);
	histograms[kZveto]		= new TH1F(("03_"+nPrefix+"Zveto").c_str(),      (lPrefix+"Z veto").c_str(), 		  300, 0, 300);
	histograms[kProjMet]	= new TH1F(("04_"+nPrefix+"MinProjMet").c_str(), (lPrefix+"Projected MET").c_str(),   100, 0, 100);
	histograms[kJetVeto]	= new TH1F(("05_"+nPrefix+"JetVeto").c_str(),    (lPrefix+"n_{jets} = 0").c_str(),     15, 0, 15);
	histograms[kSoftMuon]	= new TH1F(("06_"+nPrefix+"SoftMuon").c_str(),   (lPrefix+"No Soft #mu").c_str(),       2, 0, 2);
	histograms[kTopVeto]	= new TH1F(("07_"+nPrefix+"TopVeto").c_str(),    (lPrefix+"Top Veto").c_str(),          2, 0, 2);
	histograms[kHardPtMin]	= new TH1F(("08_"+nPrefix+"MinHardPt").c_str(),  (lPrefix+"p^{hard}_{min}").c_str(),  100, 0, 3.*_theCuts.minPtHard);
	histograms[kSoftPtMin]	= new TH1F(("09_"+nPrefix+"MinSoftPt").c_str(),  (lPrefix+"p^{soft}_{min}").c_str(),  100, 0, 3.*_theCuts.minPtSoft);
	histograms[kMaxMll]		= new TH1F(("10_"+nPrefix+"MaxMll").c_str(),     (lPrefix+"m^{ll}_{max}").c_str(),    300, 0,  300);
	histograms[kDeltaPhi]	= new TH1F(("11_"+nPrefix+"DeltaPhi").c_str(),   (lPrefix+"#Delta#Phi_{ll}").c_str(), 100, 0, TMath::Pi());

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

//______________________________________________________________________________
// int HWWAnalyzer::sortJets() {
//     

//     std::vector<HWWPFJet>::iterator jt;
//     for( jt = _event->PFJets.begin(); jt != _event->PFJets.end(); ++jt ) {
//         if ( jt->P.Pt() > _jetVeto_pt && jt->P.Eta() < _jetVeto_eta ) {
//             _selectedJets.insert(&(*jt));
//         } else if ( jt->BTagProbTkCntHighEff > _topVeto_bTagProb ) {
//             _btaggedJets.insert(&(*jt));
//         } // nothing else
//     }

//     return _selectedJets.size();
// }

//_____________________________________________________________________________
void HWWAnalyzer::calcNtuple(){

	TLorentzVector pA, pB;
	Int_t cA(0), cB(0);
	double d0A(0), d0B(0);
	double dZA(0), dZB(0);
	double maxProjMet(0);
	TH1F* counters;
	unsigned short type = 0;


//	std::cout << "Neles " << _event->NEles << "   NMus " << _event->NMus << std::endl;

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
    	type = kElEl_t;
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
        	counters = _emCounters;
        	type = kElMu_t;
    	} else {
        	pA = _event->Mus[0].P;
        	pB = _event->Els[0].P;

        	cA = _event->Mus[0].Charge;
        	cB = _event->Els[0].Charge;

        	d0A = _event->Mus[0].D0PV;
        	d0B = _event->Els[0].D0PV;

        	dZA = _event->Mus[0].DzPV;
        	dZB = _event->Els[0].DzPV;
        	counters = _meCounters;
        	type = kMuEl_t;
    	}

    	maxProjMet = _minProjMetEM;

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
    	type = kMuMu_t;

    	break;
    }

    // we work on the assumption A is the highet pT lepton, B is not. This is a watchdog
    if ( pB.Pt() > pA.Pt() ) {
    	THROW_RUNTIME("A.Pt < B.Pt");
    }

    // 3 - invariant mass
    double mll = (pA+pB).Mag();

    // 4a pfMet
	double pfMet = _event->PFMET;
	// 4b - tcMet
	double tcMet = _event->TCMET;
	// 4b - tcMet
	double chargedMet = _event->ChargedMET;

	// 5 - projected MeT
	// 5a - projPfMet
	TLorentzVector pfMetV;
	pfMetV.SetPtEtaPhiE(_event->PFMET, 0, _event->PFMETphi,0);

	double pfMetDphi = TMath::Min(TMath::Abs(pA.DeltaPhi(pfMetV)), TMath::Abs(pB.DeltaPhi(pfMetV)));
	double projPfMet = pfMetDphi < TMath::PiOver2() ? pfMet*TMath::Sin(pfMetDphi) : pfMet;

	// 5b - projTcMet
	TLorentzVector tcMetV;
	tcMetV.SetPtEtaPhiE(_event->TCMET, 0, _event->TCMETphi,0);

	double tcMetDphi = TMath::Min(TMath::Abs(pA.DeltaPhi(tcMetV)), TMath::Abs(pB.DeltaPhi(tcMetV)));
	double projTcMet = tcMetDphi < TMath::PiOver2() ? tcMet*TMath::Sin(tcMetDphi) : tcMet;

	// 5c - projChargedMet
	TLorentzVector chargedMetV;
	chargedMetV.SetPtEtaPhiE(_event->ChargedMET, 0, _event->ChargedMETphi,0);

	double chargedMetDphi = TMath::Min(TMath::Abs(pA.DeltaPhi(chargedMetV)), TMath::Abs(pB.DeltaPhi(chargedMetV)));
	double projChargedMet = chargedMetDphi < TMath::PiOver2() ? chargedMet*TMath::Sin(chargedMetDphi) : chargedMet;

    // 6 - dPhiEE
	double dPhiLL = TMath::Abs(pA.DeltaPhi(pB));

	// 7 - jet veto
    int nPfJets = _event->PFNJets;
//     int nPfJets = _selectedJets.size();

	// 8 soft  muon
	bool softMu = _event->HasSoftMus;

    bool bJets  = _event->HasBTaggedJets;
//     bool bJets  = _btaggedJets.size() > 0;

	_ntuple->type = type;

    _ntuple->cA = cA;
    _ntuple->cB = cB;

    _ntuple->pA = pA;
    _ntuple->pB = pB;

    _ntuple->d0A = d0A;
    _ntuple->d0B = d0B;

    _ntuple->dZA = dZA;
    _ntuple->dZB = dZB;

	_ntuple->mll           = mll;
	_ntuple->pfMet         = pfMet;
	_ntuple->tcMet		   = tcMet;
	_ntuple->chargedMet    = chargedMet;
	_ntuple->pfMetDphi     = pfMetDphi;
	_ntuple->tcMetDphi	   = tcMetDphi;
	_ntuple->chargedMetDphi	= chargedMetDphi;
	_ntuple->projPfMet     = projPfMet;
	_ntuple->projTcMet     = projTcMet;
	_ntuple->projChargedMet  = projChargedMet;
	_ntuple->dPhi          = dPhiLL;
	_ntuple->nPfJets	   = nPfJets;
	_ntuple->softMus       = softMu;
	_ntuple->bJets         = bJets;

	_analysisTree->Fill();

}

//_____________________________________________________________________________
void HWWAnalyzer::cutAndFill() {

	higgsBitWord word;

//     double met = _ntuple->tcMet;
//     double projMet = _ntuple->projTcMet;
//     double met = _ntuple->pfMet;
//     double projMet = _ntuple->projPfMet;
    
    double met = _ntuple->pfMet;
    double projMet = TMath::Abs(_ntuple->projPfMet, _ntuple->projChargedMet);

	word[kMinMet]    = ( met > _minMet );

	word[kMinMll]    = ( _ntuple->mll > _minMll);

	word[kZveto]     = ( _ntuple->type == 1 || TMath::Abs(_ntuple->mll - _Z0Mass) > _zVetoWidth );

	float minProjMet = _ntuple->type == 1 ? _minProjMetEM : _minProjMetLL;
	word[kProjMet]   = ( projMet > minProjMet);

	word[kJetVeto]   = ( _ntuple->nPfJets == 0);

	word[kSoftMuon]  = ( _ntuple->softMus == 0);

	word[kTopVeto]   = (!_ntuple->bJets);

	word[kHardPtMin] = ( _ntuple->pA.Pt() > _theCuts.minPtHard);

	word[kSoftPtMin] = ( _ntuple->pB.Pt() > _theCuts.minPtSoft);

	//TODO check if maxMll applies to all the combinations
	word.set(kMaxMll, _ntuple->mll < _theCuts.maxMll);

	word.set(kDeltaPhi, _ntuple->dPhi < _theCuts.maxDphi*TMath::DegToRad() );

	// type-dependent settings
	TH1F* counters(0x0);
	std::vector<TH1F*>* nm1;
	std::vector<TH1F*>* preCuts;
	std::vector<TH1F*>* postCuts;
	TH2F* nJnV;
	switch ( _ntuple->type ) {
	case kElEl_t:
		counters = _eeCounters;
        nm1      = &_eeNm1Hist;
        preCuts  = &_eePreCutHist;
        postCuts = &_eePostCutHist;
        nJnV	 = _eeJetNVsNvrtx;
		break;
	case kElMu_t:
		counters = _emCounters;
        nm1 	 = &_emNm1Hist;
        preCuts  = &_emPreCutHist;
        postCuts = &_emPostCutHist;
        nJnV 	 = _emJetNVsNvrtx;
		break;
	case kMuEl_t:
		counters = _meCounters;
        nm1 	 = &_emNm1Hist;
        preCuts  = &_emPreCutHist;
        postCuts = &_emPostCutHist;
        nJnV 	 = _emJetNVsNvrtx;
		break;

	case kMuMu_t:
		counters = _mmCounters;
        nm1 	 = &_mmNm1Hist;
        preCuts  = &_mmPreCutHist;
        postCuts = &_mmPostCutHist;
        nJnV	 = _mmJetNVsNvrtx;
		break;
	default:
		THROW_RUNTIME("Wrong event type : " << _ntuple->type );
	};

	if ( (word & _nthMask[kMinMet]) == _nthMask[kMinMet] )
		nm1->at(kMinMet)->Fill(_ntuple->pfMet, getWeight() );

	if ( (word & _nthMask[kMinMll]) == _nthMask[kMinMll] )
		nm1->at(kMinMll)->Fill(_ntuple->mll, getWeight() );

	if ( (word & _nthMask[kZveto]) == _nthMask[kZveto] )
		nm1->at(kZveto)->Fill(_ntuple->mll, getWeight() );

	if ( (word & _nthMask[kProjMet]) == _nthMask[kProjMet] )
		nm1->at(kProjMet)->Fill( projMet , getWeight() );

	if ( (word & _nthMask[kJetVeto]) == _nthMask[kJetVeto] )
		nm1->at(kJetVeto)->Fill(_ntuple->nPfJets, getWeight() );

	if ( (word & _nthMask[kSoftMuon]) == _nthMask[kSoftMuon] )
		nm1->at(kSoftMuon)->Fill(_ntuple->softMus, getWeight() );

	if ( (word & _nthMask[kTopVeto]) == _nthMask[kTopVeto] )
		nm1->at(kTopVeto)->Fill(_ntuple->bJets, getWeight() );

	if ( (word & _nthMask[kHardPtMin]) == _nthMask[kHardPtMin] )
		nm1->at(kHardPtMin)->Fill(_ntuple->pA.Pt(), getWeight() );

	if ( (word & _nthMask[kSoftPtMin]) == _nthMask[kSoftPtMin] )
		nm1->at(kSoftPtMin)->Fill(_ntuple->pB.Pt(), getWeight() );

	if ( (word & _nthMask[kMaxMll]) == _nthMask[kMaxMll] )
		nm1->at(kMaxMll)->Fill(_ntuple->mll, getWeight() );

	if ( (word & _nthMask[kDeltaPhi]) == _nthMask[kDeltaPhi] )
		nm1->at(kDeltaPhi)->Fill(_ntuple->dPhi, getWeight() );



	_nVrtx->Fill(_event->NVrtx, getWeight() );

	_diLep_PfMet->Fill(_ntuple->pfMet, getWeight() );
	_diLep_TcMet->Fill(_ntuple->tcMet, getWeight() );
	_diLep_ChargedMet->Fill(_ntuple->tcMet, getWeight() );

	_diLep_projPfMet->Fill(_ntuple->projPfMet, getWeight() );
	_diLep_projTcMet->Fill(_ntuple->projTcMet, getWeight() );
	_diLep_projChargedMet->Fill(_ntuple->projTcMet, getWeight() );

	_diLep_ptLeadLep->Fill(_ntuple->pA.Pt(), getWeight() );
	_diLep_ptTrailLep->Fill(_ntuple->pB.Pt(), getWeight() );
	_diLep_mll->Fill(_ntuple->mll, getWeight() );
	_diLep_deltaPhi->Fill(_ntuple->dPhi, getWeight() );

	counters->Fill(kDileptons, getWeight() );
	// min missing Et
	preCuts->at(kMinMet)->Fill(met, getWeight() );
	if ( !word[kMinMet] ) return;
	counters->Fill(kMinMet, getWeight() );
	postCuts->at(kMinMet)->Fill(met, getWeight() );

	// min invariant mass
	preCuts->at(kMinMll)->Fill(_ntuple->mll, getWeight() );
	if ( !word[kMinMll] ) return;
	counters->Fill(kMinMll, getWeight() );
	postCuts->at(kMinMll)->Fill(_ntuple->mll, getWeight() );

	// Z veto (m_ll-m_Z < 15 GeV)
	preCuts->at(kZveto)->Fill(_ntuple->mll, getWeight() );
	if ( !word[kZveto] ) return;
	counters->Fill(kZveto, getWeight() );
	postCuts->at(kZveto)->Fill(_ntuple->mll, getWeight() );

	// proj Met (20 GeV for ee)
	preCuts->at(kProjMet)->Fill(projMet, getWeight() );
	if ( !word[kProjMet] ) return;
	counters->Fill(kProjMet, getWeight() );
	postCuts->at(kProjMet)->Fill(projMet, getWeight() );

	// pause here for jet pt and eta
	_jetN->Fill(_event->PFJets.size(), getWeight() );
	for ( unsigned int i(0); i<_event->PFJets.size(); ++i) {
		_jetPt->Fill(_event->PFJets[i].P.Pt(), getWeight() );
		_jetEta->Fill(_event->PFJets[i].P.Eta(), getWeight() );
	}

	nJnV->Fill(_event->NVrtx, _event->PFJets.size(), getWeight() );

	// njets == 0
	preCuts->at(kJetVeto)->Fill(_ntuple->nPfJets, getWeight() );
	if ( !word[kJetVeto] ) return;
	counters->Fill(kJetVeto, getWeight() );
	postCuts->at(kJetVeto)->Fill(_ntuple->nPfJets, getWeight() );

	// soft muon
	preCuts->at(kSoftMuon)->Fill(_ntuple->softMus, getWeight() );
	if ( !word[kSoftMuon] ) return;
	counters->Fill(kSoftMuon, getWeight() );
	postCuts->at(kSoftMuon)->Fill(_ntuple->softMus, getWeight() );

	// soft muon
	preCuts->at(kTopVeto)->Fill(_ntuple->bJets, getWeight() );
	if ( !word[kTopVeto] ) return;
	counters->Fill(kTopVeto, getWeight() );
	postCuts->at(kTopVeto)->Fill(_ntuple->bJets, getWeight() );

	// hard pt cut
	preCuts->at(kHardPtMin)->Fill(_ntuple->pA.Pt(), getWeight() );
	if ( !word[kHardPtMin] ) return;
	counters->Fill(kHardPtMin, getWeight() );
	postCuts->at(kHardPtMin)->Fill(_ntuple->pA.Pt(), getWeight() );

	// soft pt cut
	preCuts->at(kSoftPtMin)->Fill(_ntuple->pB.Pt(), getWeight() );
	if ( !word[kSoftPtMin] ) return;
	counters->Fill(kSoftPtMin, getWeight() );
	postCuts->at(kSoftPtMin)->Fill(_ntuple->pB.Pt(), getWeight() );

	preCuts->at(kMaxMll)->Fill(_ntuple->mll, getWeight() );
	// Mll_max
	if ( !word[kMaxMll] ) return;
	counters->Fill(kMaxMll, getWeight() );
	postCuts->at(kMaxMll)->Fill(_ntuple->mll, getWeight() );

	// delta phi
	preCuts->at(kDeltaPhi)->Fill(_ntuple->dPhi, getWeight() );
	if ( !word[kDeltaPhi] ) return;
	counters->Fill(kDeltaPhi, getWeight() );
	postCuts->at(kDeltaPhi)->Fill(_ntuple->dPhi, getWeight() );



}

//_____________________________________________________________________________
void HWWAnalyzer::Process( Long64_t iEvent ) {
//	std::cout << iEvent <<  std::endl;
	_chain->GetEntry(iEvent);

	_ntuple->Clear();
//     _btaggedJets.clear();
//     _selectedJets.clear();

//     sortJets();

	if ( _event->NEles + _event->NMus != 2 )
		THROW_RUNTIME("Wrong number of leptons in the event: NEles = " << _event->NEles << " NMus = " << _event->NMus  );

	calcNtuple();
	cutAndFill();

}

//_____________________________________________________________________________
void HWWAnalyzer::EndJob() {

	_eeCounters->SetEntries(_eeCounters->GetBinContent(1));
	_emCounters->SetEntries(_emCounters->GetBinContent(1));
	_meCounters->SetEntries(_meCounters->GetBinContent(1)); //TODO
	_mmCounters->SetEntries(_mmCounters->GetBinContent(1));

	_llCounters->Add(_eeCounters);
	_llCounters->Add(_emCounters);
	_llCounters->Add(_meCounters);
	_llCounters->Add(_mmCounters);

	for ( unsigned int k(0); k<_llNm1Hist.size(); ++k) {
		if (!_llNm1Hist[k] ) continue;
		_llNm1Hist[k]->Add(_eeNm1Hist[k]);
		_llNm1Hist[k]->Add(_emNm1Hist[k]);
		_llNm1Hist[k]->Add(_meNm1Hist[k]);
		_llNm1Hist[k]->Add(_mmNm1Hist[k]);
	}

	for ( unsigned int k(0); k<_llPreCutHist.size(); ++k ) {
		if( !_llPreCutHist[k] ) continue;
		_llPreCutHist[k]->Add( _eePreCutHist[k]);
		_llPreCutHist[k]->Add( _emPreCutHist[k]);
		_llPreCutHist[k]->Add( _mePreCutHist[k]);
		_llPreCutHist[k]->Add( _mmPreCutHist[k]);
	}

	for ( unsigned int k(0); k<_llPostCutHist.size(); ++k ) {
		if( !_llPreCutHist[k] ) continue;
		_llPostCutHist[k]->Add( _eePostCutHist[k]);
		_llPostCutHist[k]->Add( _emPostCutHist[k]);
		_llPostCutHist[k]->Add( _mePostCutHist[k]); //TODO
		_llPostCutHist[k]->Add( _mmPostCutHist[k]);
	}

	_llJetNVsNvrtx->Add(_eeJetNVsNvrtx);
	_llJetNVsNvrtx->Add(_emJetNVsNvrtx);
	_llJetNVsNvrtx->Add(_meJetNVsNvrtx); //TODO
	_llJetNVsNvrtx->Add(_mmJetNVsNvrtx);

	_output->mkdir("lepSelection")->cd();
	std::map<std::string,TH1F*>::iterator it;
	for( it = _hists.begin(); it!=_hists.end();it++) {
		it->second->Write();
	}

	_output->mkdir("fullSelection")->cd();


	glueCounters(_eeCounters);
	glueCounters(_emCounters);
	glueCounters(_meCounters);
	glueCounters(_mmCounters);
	glueCounters(_llCounters);

}

//_____________________________________________________________________________
TH2F* HWWAnalyzer::makeNjetsNvrtx( const std::string& name, const std::string& prefix  ) {
	int nJets(20), nVrtx(20);
	TH2F* h2 = new TH2F(name.c_str(),(prefix+"n_{jets} vs .n_{vrtx}").c_str(),
			nVrtx, 1, nVrtx+1, nJets, 0, nJets);
	h2->GetXaxis()->SetTitle("n_{vrtx}");
	h2->GetYaxis()->SetTitle("n_{jets} p_{T} > 25 GeV");
	return h2;
}

//_____________________________________________________________________________
TH1F* HWWAnalyzer::makeLabelHistogram( const std::string& name, const std::string& title, std::map<int,std::string> labels) {
	int xmin = labels.begin()->first;
	int xmax = labels.begin()->first;

	std::map<int, std::string>::iterator it;
	for( it = labels.begin(); it != labels.end(); ++it ) {
		xmin = it->first < xmin ? it->first : xmin;
		xmax = it->first > xmax ? it->first : xmax;
	}

	++xmax;
	int nbins = xmax-xmin;

	TH1F* h = new TH1F(name.c_str(), title.c_str(), nbins, xmin, xmax);
	for( it = labels.begin(); it != labels.end(); ++it ) {
		int bin = h->GetXaxis()->FindBin(it->first);
		h->GetXaxis()->SetBinLabel(bin, it->second.c_str());
	}

	return h;

}
//_____________________________________________________________________________
TH1F* HWWAnalyzer::glueCounters(TH1F* counters) {

	std::string name = counters->GetName();
	std::map<std::string,TH1F*>::iterator it = _hists.find(name);
	if ( it == _hists.end() ) return 0x0;
	TH1F* cntPreSel = it->second;


    // make a copy
	std::string clone_name = counters->GetName();
    clone_name += "_copy";
    bool add = TDirectory::AddDirectoryStatus();
	TDirectory::AddDirectory(kFALSE);
	TH1F* cntCopy = dynamic_cast<TH1F*>(counters->Clone( clone_name.c_str() ));
	TDirectory::AddDirectory(add);

	int nBins    = cntCopy->GetNbinsX();
	int nBinsPre = cntPreSel->GetNbinsX();

	// check bin content
    double preSelectedEntries = cntPreSel->GetBinContent(nBinsPre);
    double processedEntries = cntCopy->GetBinContent(1);
    // define mismtch ad the ratio bewtween the difference and the preselected entries
    double mismatch =TMath::Abs( (preSelectedEntries- processedEntries)/preSelectedEntries );

    std::cout << "mismatch = " << mismatch << std::endl;
	if ( TMath::Abs(mismatch) > 1E-6 )
        THROW_RUNTIME("Bin Content Mismatch: Wrong histogram?\n"
                << cntPreSel->GetName() << " (" << nBinsPre << ") : " << cntPreSel->GetXaxis()->GetBinLabel(nBinsPre) << "=" << preSelectedEntries << "\n"
                << cntCopy->GetName() << " (" << nBins << ") : " << cntCopy->GetXaxis()->GetBinLabel(1) << "="<< processedEntries);

    // what is this?
	cntCopy->Fill(1,cntCopy->GetBinContent(1)*-1);

	// matching possible, build labels
	THashList labels;
	labels.AddAll(cntPreSel->GetXaxis()->GetLabels());
	labels.AddAll(cntCopy->GetXaxis()->GetLabels());
	labels.RemoveAt(nBinsPre);

	int nBinsNew = nBinsPre+nBins-1;

	float xmin = cntPreSel->GetXaxis()->GetXmin();
	float xmax = xmin+nBinsNew;
	TH1F* hNew = new TH1F(cntPreSel->GetName(),cntPreSel->GetTitle(),nBinsNew,xmin,xmax);

	TAxis* ax = hNew->GetXaxis();
	for( int i(0); i<labels.GetEntries(); ++i)
		ax->SetBinLabel(i+1,labels.At(i)->GetName());

	THashList histograms;
	histograms.Add(cntPreSel);
	histograms.Add(cntCopy);

	hNew->Merge(&histograms);
	if ( hNew->GetNbinsX() != nBinsNew )
		THROW_RUNTIME("Merge screwed it up! "<< hNew->GetNbinsX() << "  " << nBinsNew );

	for( int i(1);i<=cntPreSel->GetNbinsX(); ++i)
		if( hNew->GetBinContent(i) != cntPreSel->GetBinContent(i))
			THROW_RUNTIME("Failed HA check:" << i << ":"<< hNew->GetBinContent(i) << "  "<< cntPreSel->GetBinContent(i))
	for( int i(2);i<=cntCopy->GetNbinsX(); ++i)
		if( hNew->GetBinContent(i+cntPreSel->GetNbinsX()-1) != cntCopy->GetBinContent(i))
			THROW_RUNTIME("Failed HB check:" << i << ":"<< hNew->GetBinContent(i+cntPreSel->GetNbinsX()-1) << "  "<< cntCopy->GetBinContent(i))

	delete cntCopy;

	//being a counter histogram, set the number of entries to the first bin:
	hNew->SetEntries(hNew->GetBinContent(1));
	return hNew;

}
