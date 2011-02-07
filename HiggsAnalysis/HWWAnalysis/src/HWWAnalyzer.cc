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
#include "HWWNtuple.h"
#include <stdexcept>
#include <fstream>
#include <TH1F.h>

float mZ = 91.1876;

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
HWWAnalyzer::HWWAnalyzer(int argc, char** argv) : UserAnalyzer(argc,argv), _analysisTree(0x0){
	// TODO Auto-generated constructor stub

	_higgsMass = _config.getValue<int>("HWWAnalyzer.higgsMass");

	_maxD0      = _config.getValue<float>("HWWAnalyzer.maxD0");
	_maxDz      = _config.getValue<float>("HWWAnalyzer.maxDz");
	_cutFile    = _config.getValue<std::string>("HWWAnalyzer.cutFile");
	_minMet     = _config.getValue<float>("HWWAnalyzer.minMet");
	_minMll     = _config.getValue<float>("HWWAnalyzer.minMll");
	_zVetoWidth = _config.getValue<float>("HWWAnalyzer.zVetoWidth");

	_maxProjMetEM = _config.getValue<float>("HWWAnalyzer.maxProjMetEM");
	_maxProjMetLL = _config.getValue<float>("HWWAnalyzer.maxProjMetLL");

	readHiggsCutSet( _cutFile );

//	_eeCuts = getHiggsCutSet( _higgsMass, kEE );
//	_mmCuts = getHiggsCutSet( _higgsMass, kMM );
//	_emCuts = getHiggsCutSet( _higgsMass, kEM );

	_theCuts = getHiggsCutSet( _higgsMass );
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

	labels[kDileptons] = "N_{dileptons}";
	labels[kCharge]    = "Opposite charge";
	labels[kD0]        = "D0";
	labels[kDz]        = "Dz";
	labels[kMinMet]    = "Met_{min}";
	labels[kMinMll]    = "m^{ll}_{min}";
	labels[kZveto]     = "Z veto";
	labels[kProjMet]   = "ProjMet";
	labels[kJetVeto]   = "n_{jets} == 0";
	labels[kSoftMuon]  = "No Soft #mu";
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

	_output->mkdir("ee");
	_output->mkdir("eu");
	_output->mkdir("uu");

	_output->cd();
	_analysisTree = new TTree("hww","HWW variables Tree");

}

//_____________________________________________________________________________
void HWWAnalyzer::BeginJob() {
	_chain->SetBranchAddress("ev", &_ntuple);

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
//		ss >> dummy;

//		if ( dummy == "ee" ) {
//			h.ll = kEE;
//		} else if ( dummy == "mm" ) {
//			h.ll = kMM;
//		} else if ( dummy == "em" ) {
//			h.ll = kEM;
//		} else {
//			std::cout << "Corrupted line: option " << dummy << " is not recognized\n" << line << std::endl;
//			continue;
//		}

		ss >> h.minPtHard >> h.minPtSoft >> h.maxMll >> h.maxDphi;
//		ss >> h.etaMax >> h.etaMaxHard >> h.etaMaxSoft >> h.metMin >> h.metMax >> h.invMassMax >> h.deltaPhi >> h.ptMaxMin >> h.ptMaxMax >> h.ptMinMax;

		h.print();

		_cutVector.push_back(h);
	}
}

//_____________________________________________________________________________
//HWWAnalyzer::HiggsCutSet HWWAnalyzer::getHiggsCutSet(int mass, int ll) {
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
void HWWAnalyzer::Process( Long64_t iEvent ) {
//	std::cout << iEvent <<  std::endl;
	_chain->GetEntry(iEvent);

	if ( _ntuple->NEles + _ntuple->NMus != 2 )
		THROW_RUNTIME("Wrong number of leptons in the event: NEles = " << _ntuple->NEles << " NMus = " << _ntuple->NMus  );


	TLorentzVector pA, pB;
	Int_t cA, cB;
	double d0A, d0B;
	double dZA, dZB;
	double maxProjMet;
	TH1F* counters;

    switch ( _ntuple->NEles ) {
    case 2:
    	// A has the highst pT?
    	pA = _ntuple->Els[0].ElP;
    	pB = _ntuple->Els[1].ElP;

    	cA = _ntuple->Els[0].ElCharge;
    	cB = _ntuple->Els[1].ElCharge;

    	d0A = _ntuple->Els[0].ElD0PV;
    	d0B = _ntuple->Els[1].ElD0PV;

    	dZA = _ntuple->Els[0].ElDzPV;
    	dZB = _ntuple->Els[1].ElDzPV;

    	maxProjMet = _maxProjMetLL;
    	counters = _eeCounters;
    	break;
    case 1:
    	if ( _ntuple->Els[0].ElP.Pt() > _ntuple->Mus[0].MuP.Pt() ) {
        	pA = _ntuple->Els[0].ElP;
        	pB = _ntuple->Mus[1].MuP;

        	cA = _ntuple->Els[0].ElCharge;
        	cB = _ntuple->Mus[1].MuCharge;

        	d0A = _ntuple->Els[0].ElD0PV;
        	d0B = _ntuple->Mus[1].MuD0PV;

        	dZA = _ntuple->Els[0].ElDzPV;
        	dZB = _ntuple->Mus[1].MuDzPV;
    	} else {
        	pA = _ntuple->Mus[0].MuP;
        	pB = _ntuple->Els[1].ElP;

        	cA = _ntuple->Mus[0].MuCharge;
        	cB = _ntuple->Els[1].ElCharge;

        	d0A = _ntuple->Mus[0].MuD0PV;
        	d0B = _ntuple->Els[1].ElD0PV;

        	dZA = _ntuple->Mus[0].MuDzPV;
        	dZB = _ntuple->Els[1].ElDzPV;
    	}

    	maxProjMet = _maxProjMetLL;
    	counters = _emCounters;
    	break;
    case 0:
    	// A has the highst pT?
    	pA = _ntuple->Mus[0].MuP;
    	pB = _ntuple->Mus[1].MuP;

    	cA = _ntuple->Mus[0].MuCharge;
    	cB = _ntuple->Mus[1].MuCharge;

    	d0A = _ntuple->Mus[0].MuD0PV;
    	d0B = _ntuple->Mus[1].MuD0PV;

    	dZA = _ntuple->Mus[0].MuDzPV;
    	dZB = _ntuple->Mus[1].MuDzPV;

    	maxProjMet = _maxProjMetLL;
    	counters = _mmCounters;
    	break;
    }


    // opposite charge
    bool oppositeCharge = ( cA*cB < 0 );

    // 3 - invariant mass
    double mll = (pA+pB).Mag();

    // 4a pfMet
	double pfMet = _ntuple->PFMET;
	// 4b - muMet
	double muMet = _ntuple->MuCorrMET;

	// 5 - projected MeT
	// 5a - projPfMet
	short i;

	TLorentzVector pfMetV;
	pfMetV.SetPtEtaPhiE(_ntuple->PFMET, 0, _ntuple->PFMETphi,0);

	//	double dPhiPfMet[2];
	//	dPhiPfMet[0] = TMath::Abs(pA.DeltaPhi(pfMetV));
	//	dPhiPfMet[1] = TMath::Abs(pB.DeltaPhi(pfMetV));
	//	i = TMath::LocMin(2,dPhiPfMet);

	//	double projPfMet = dPhiPfMet[i] < TMath::PiOver2() ? pfMet*TMath::Sin(dPhiPfMet[i]) : pfMet;


//	if ( dPhiPfMet[i] != minMetDphi ) {
//		std::cout << dPhiPfMet[i] << "   (" << minMetDphi << ")  " << dPhiPfMet[0] << "   " << dPhiPfMet[1] << std::endl;
//		THROW_RUNTIME("puppa");
//	}

	double pfMetDphi = TMath::Min(TMath::Abs(pA.DeltaPhi(pfMetV)), TMath::Abs(pB.DeltaPhi(pfMetV)));
	double projPfMet = pfMetDphi < TMath::PiOver2() ? pfMet*TMath::Sin(pfMetDphi) : pfMet;


	// 5b - projMuMet
	TLorentzVector muMetV;
	muMetV.SetPtEtaPhiE(_ntuple->MuCorrMET, 0, _ntuple->MuCorrMETphi, 0);
//	double dPhiMuMet[2];
//	dPhiMuMet[0] = TMath::Abs(pA.DeltaPhi(muMet));
//	dPhiMuMet[1] = TMath::Abs(pB.DeltaPhi(muMet));
//	i = TMath::LocMin(2,dPhiMuMet);
//	double projMuMet = dPhiMuMet[i] < TMath::PiOver2() ? muMet*TMath::Sin(dPhiMuMet[i]) : muMet;

	double muMetDphi = TMath::Min(TMath::Abs(pA.DeltaPhi(muMet)), TMath::Abs(pB.DeltaPhi(muMet)));
	double projMuMet = muMetDphi < TMath::PiOver2() ? muMet*TMath::Sin(muMetDphi) : muMet;

	// 6 - dPhiEE
	double dPhiEE = TMath::Abs(pA.DeltaPhi(pB));

	// 7 - jet veto
	// 7a - pf jets
	int nPfJetsEE = _ntuple->PFNJets;
	// 7b - calo jets
	int nJetsEE   = _ntuple->NJets;

	double pTHard = pA.Pt();
	double pTSoft = pB.Pt();

	// 8 soft  muon
	bool softMu = _ntuple->HasSoftMus;

	// start selection






	counters->Fill(kDileptons);
	// opposite charge
	if (!oppositeCharge) return;
	counters->Fill(kCharge);

	// d0
	if ( d0A > _maxD0 || d0B > _maxD0) return;
	counters->Fill(kD0);

	// dz
	if ( dZA > _maxDz || dZB > _maxDz) return;
	counters->Fill(kDz);

	// min missing Et
	if ( pfMet < _minMet ) return;
	counters->Fill(kMinMet);

	// min invariant mass
	if ( mll < _minMll && _ntuple->NEles == 1 ) return;
	counters->Fill(kMinMll);

	// Z veto (m_ll-m_Z < 15 GeV)
	if ( TMath::Abs(mll - mZ) < _zVetoWidth ) return;
	counters->Fill(kZveto);

	// proj Met (20 GeV for ee)
	if ( projPfMet < maxProjMet ) return;
	counters->Fill(kProjMet);

	// njets == 0
	if ( nPfJetsEE != 0 ) return;
	counters->Fill(kJetVeto);

	// soft muon
	if ( softMu ) return;
	counters->Fill(kSoftMuon);

	// hard pt cut
	if ( pTHard < kHardPtMin ) return;
	counters->Fill(kHardPtMin);
	//		kHardPtMin;

	// soft pt cut
	if ( pTSoft < kSoftPtMin ) return;
	counters->Fill(kSoftPtMin);
//		kSoftPtMin;

	std::cout << "mll " << mll <<  "   " << _theCuts.maxMll << std::endl;
	// Mll_max
//		if ( mll > _eeCuts.invMassMax) return;
	if ( mll > _theCuts.maxMll && _ntuple->NEles == 1 ) return;
	counters->Fill(kMaxMll);

	// met limits
	//if ( _eeCuts.metMin < pfMet || _eeCuts.metMax > pfMet) return;

	// delta phi
	if ( dPhiEE > _theCuts.maxDphi ) return;
	counters->Fill(kDeltaPhi);

	//XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


/*



	if ( _ntuple->NEles == 2 ) {

		//prepare variables ------------------------------------
		// .oppositeCharge
		// d0
		// dZ
		// _minEt
		// _minMll
		// Z Veto (dMz)
		// projMet
		// jet veto
		// soft mu
		// _maxMll


		// 1 - opposite charge
		bool oppositeCharge = (_ntuple->Els[0].ElCharge * _ntuple->Els[1].ElCharge < 0);

		// 2 - d0
		bool d0 = _ntuple->Els[0].ElD0PV < _maxD0 &&
				_ntuple->Els[1].ElD0PV < _maxD0;

		// 3 - invariant mass
		double mll = (_ntuple->Els[0].ElP+_ntuple->Els[1].ElP).Mag();
		// 4a - pfMet
		double pfMet = _ntuple->PFMET;
		// 4b - muMet
		double muMet = _ntuple->MuCorrMET;

		short i;
		// 5 - projected MeT
		// 5a - projPfMet
		TLorentzVector pfMetV;
		pfMetV.SetPtEtaPhiE(_ntuple->PFMET, 0, _ntuple->PFMETphi,0);
//		std::cout << "(" << pfMetV[0] << "," << pfMetV[1] << "," << pfMetV[2] << ")" << std::endl;

		double dPhiPfMet[2];
		dPhiPfMet[0] = TMath::Abs(_ntuple->Els[0].ElP.DeltaPhi(pfMetV));
		dPhiPfMet[1] = TMath::Abs(_ntuple->Els[1].ElP.DeltaPhi(pfMetV));
		i = TMath::LocMin(2,dPhiPfMet);
		double projPfMet = dPhiPfMet[i] < TMath::PiOver2() ? pfMet*TMath::Sin(dPhiPfMet[i]) : pfMet;

		// 5b - projMuMet
		TLorentzVector muMetV;
		muMetV.SetPtEtaPhiE(_ntuple->MuCorrMET, 0, _ntuple->MuCorrMETphi, 0);
		double dPhiMuMet[2];
		dPhiMuMet[0] = (_ntuple->Els[0].ElP.DeltaPhi(muMet));
		dPhiMuMet[1] = (_ntuple->Els[1].ElP.DeltaPhi(muMet));
		i = TMath::LocMin(2,dPhiMuMet);
		double projMuMet = dPhiMuMet[i] < TMath::PiOver2() ? muMet*TMath::Sin(dPhiMuMet[i]) : muMet;

		// 6 - dPhiEE
		double dPhiEE = TMath::Abs(_ntuple->Els[0].ElP.DeltaPhi(_ntuple->Els[1].ElP));

		// 7 - jet veto
		// 7a - pf jets
		int nPfJetsEE = _ntuple->PFNJets;
		// 7b - calo jets
		int nJetsEE   = _ntuple->NJets;

		double pTHard = TMath::Max(_ntuple->Els[0].ElP.Pt(), _ntuple->Els[1].ElP.Pt());
		double pTSoft = TMath::Min(_ntuple->Els[0].ElP.Pt(), _ntuple->Els[1].ElP.Pt());

		// 8 soft  muon
		bool softMu = _ntuple->HasSoftMus;
		//- apply selection ------------------------------------

		// start selection

		_eeCounters->Fill(kDileptons);
		// opposite charge
		if (!oppositeCharge) return;
		_eeCounters->Fill(kCharge);

		// d0
		if ( _ntuple->Els[0].ElD0PV > _maxD0 || _ntuple->Els[1].ElD0PV > _maxD0) return;
		_eeCounters->Fill(kD0);

		// dz
		if ( _ntuple->Els[0].ElDzPV > _maxDz || _ntuple->Els[1].ElD0PV > _maxDz) return;
		_eeCounters->Fill(kDz);

		// min missing Et
		if ( pfMet < _minMet ) return;
		_eeCounters->Fill(kMinMet);

		// min invariant mass
		if ( mll < _minMll) return;
		_eeCounters->Fill(kMinMll);

		// Z veto (m_ll-m_Z < 15 GeV)
		if ( TMath::Abs(mll - 91.1876) < _zVetoWidth ) return;
		_eeCounters->Fill(kZveto);

		// proj Met (20 GeV for ee)
		if ( projPfMet < _maxProjMetLL ) return;
		_eeCounters->Fill(kProjMet);

		// njets == 0
		if ( nPfJetsEE != 0 ) return;
		_eeCounters->Fill(kJetVeto);

		// soft muon
		if ( softMu ) return;
		_eeCounters->Fill(kSoftMuon);

		// hard pt cut
		if ( pTHard < kHardPtMin ) return;
		_eeCounters->Fill(kHardPtMin);
		//		kHardPtMin;

		// soft pt cut
		if ( pTSoft < kSoftPtMin ) return;
		_eeCounters->Fill(kSoftPtMin);
//		kSoftPtMin;

		std::cout << mll <<  "   " << _theCuts.maxMll << std::endl;
		// Mll_max
//		if ( mll > _eeCuts.invMassMax) return;
		if ( mll > _theCuts.maxMll ) return;
		_eeCounters->Fill(kMaxMll);

		// met limits
		//if ( _eeCuts.metMin < pfMet || _eeCuts.metMax > pfMet) return;

		// delta phi
		if ( dPhiEE > _theCuts.maxDphi ) return;
		_eeCounters->Fill(kDeltaPhi);

		// ptMax limits
		//if ( pTMax > _eeCuts.ptMaxMax || pTMax < _eeCuts.ptMaxMin ) return;
//
//		// maximim ptmin
//		if ( pTMin > _eeCuts.ptMinMax) return;

	} else if ( _ntuple->NMus == 2 ) {
	} else if ( _ntuple->NEles == 1 && _ntuple->NMus == 1) {
	} else {
		THROW_RUNTIME("Wrong number of leptons in the event: NEles = " << _ntuple->NEles << " NMus = " << _ntuple->NMus  );
	}

	// two leptons charge
	// d0 cut
	//

*/
}

void HWWAnalyzer::EndJob() {

	for ( int i(1); i<= _llCounters->GetNbinsX(); ++i) {
		float binc(0);
		binc += _eeCounters->GetBinContent(i);
		binc += _mmCounters->GetBinContent(i);
		binc += _emCounters->GetBinContent(i);

		_llCounters->SetBinContent(i,binc);
	}
}
