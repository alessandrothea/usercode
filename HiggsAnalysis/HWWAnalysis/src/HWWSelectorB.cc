/*
 * HWWSelectorB.cc
 *
 *  Created on: Mar 3, 2011
 *      Author: ale
 */

#include "HWWSelectorB.h"
#include <iostream>
#include <stdexcept>
#include <fstream>
#include <sstream>
#include <bitset>
#include <TVector3.h>
#include <TStopwatch.h>
#include <TH1F.h>
#include "Tools.h"

const float HWWSelectorB::_etaMaxEB=1.4442;
const float HWWSelectorB::_etaMinEE=1.5660;
const float HWWSelectorB::_etaMaxEE=2.5000;
const float HWWSelectorB::_etaMaxMu=2.4000;

//_____________________________________________________________________________
void HWWSelectorB::WorkingPoint::print() {
	char p;
	switch( partition ) {
	case kBarrel:
		p = 'B';
	break;
	case kEndcap:
		p='E';
		break;
	}
	std::cout << p << "("
			<< efficiency << ")" << '\t'
			<< See << '\t'
			<< dPhi << "   "
			<< dEta << '\t'
			<< HoE << '\t'
			<< tkIso << '\t'
			<< ecalIso << '\t'
			<< hcalIso << '\t'
			<< combIso << '\t'
			<< missHits << '\t'
			<< dist << '\t'
			<< cot << '\t'
			<< std::endl;
}


HWWSelectorB::HWWSelectorB( int argc, char** argv ) : ETHZNtupleSelector( argc, argv ),
		_nSelectedEvents(0), _llCounters(0x0), _eeCounters(0x0), _emCounters(0x0), _mmCounters(0x0){

	_diLepEvent = new HWWEvent();

	std::cout <<  this->getChain()->GetName() << "   "<< this->getChain()->GetTree() << std::endl;

	_hltMode		  = _config.getValue<std::string>("HWWSelector.hltMode","el_mu");
	_runInfoName      = _config.getValue<std::string>("HWWSelector.runInfoName");

	_vrtxCut_nDof		 = _config.getValue<float>("HWWSelector.vrtxCut.nDof"); // 4
	_vrtxCut_rho 		 = _config.getValue<float>("HWWSelector.vrtxCut.rho"); // 2
	_vrtxCut_z			 = _config.getValue<float>("HWWSelector.vrtxCut.z"); // 24

	_elCut_TightWorkingPoint = _config.getValue<int>( "HWWSelector.elTightWorkingPoint");
	_elCut_LooseWorkingPoint = _config.getValue<int>( "HWWSelector.elLooseWorkingPoint");
	_elCut_EtaSCEbEe     = _config.getValue<float>("HWWSelector.elCut.etaSCEbEe"); // 1.479

	_wpFile				 = _config.getValue<std::string>( "HWWSelector.elWorkingPointFile");

	_lepCut_leadingPt	 = _config.getValue<float>("HWWSelector.lepCut.leadingPt"); // = 20.
	_lepCut_trailingPt 	 = _config.getValue<float>("HWWSelector.lepCut.trailingPt"); // =10.
	_lepCut_D0PV		 = _config.getValue<float>("HWWSelector.lepCut.d0PrimaryVertex");// = 0.2
	_lepCut_DzPV		 = _config.getValue<float>("HWWSelector.lepCut.dZPrimaryVertex");// = 10.

	_jetCut_Dr			 = _config.getValue<float>("HWWSelector.jetCut.Dr");// = 0.3
	_jetCut_Pt			 = _config.getValue<float>("HWWSelector.jetCut.Pt");// = 30
	_jetCut_Eta			 = _config.getValue<float>("HWWSelector.jetCut.Eta");// = 5
	_jetCut_BtagProb	 = _config.getValue<float>("HWWSelector.jetCut.BtagProb");// = 2.1

	_muCut_NMuHist       = _config.getValue<int>(  "HWWSelector.muCut.nMuHits");// = 0
	_muCut_NMuMatches    = _config.getValue<int>(  "HWWSelector.muCut.nMuMatches");// = 1
	_muCut_NTrackerHits  = _config.getValue<int>(  "HWWSelector.muCut.nTrackerHits");// = 10
	_muCut_NPixelHits    = _config.getValue<int>(  "HWWSelector.muCut.nPixelHits");// = 0
	_muCut_NChi2         = _config.getValue<int>(  "HWWSelector.muCut.nChi2");// = 10
	_muCut_relPtRes      = _config.getValue<float>("HWWSelector.muCut.relPtResolution");// = 0.1
	_muCut_combIsoOverPt = _config.getValue<float>("HWWSelector.muCut.combIso");// = 0.15

	_muSoftCut_Pt		 = _config.getValue<float>("HWWSelector.muSoftCut.Pt");
	_muSoftCut_HighPt	 = _config.getValue<float>("HWWSelector.muSoftCut.HighPt");
	_muSoftCut_NotIso    = _config.getValue<float>("HWWSelector.muSoftCut.NotIso");

	// config from file ?

	std::vector<std::string> hltPaths_el = _config.getVector<std::string>("HWWSelector.hltPaths.el");
	std::vector<std::string> hltPaths_mu = _config.getVector<std::string>("HWWSelector.hltPaths.mu");

	std::vector<std::string>::iterator hltIt;
	for (hltIt = hltPaths_el.begin(); hltIt != hltPaths_el.end(); ++hltIt)
		_hlt.add("el",*hltIt);

	for (hltIt = hltPaths_mu.begin(); hltIt != hltPaths_mu.end(); ++hltIt)
		_hlt.add("mu",*hltIt);

//	_hlt.add("el","HLT_Ele10_LW_L1R");
//	_hlt.add("el","HLT_Ele15_SW_L1R");
//	_hlt.add("el","HLT_Ele15_SW_CaloEleId_L1R");
//	_hlt.add("el","HLT_Ele17_SW_CaloEleId_L1R");
//	_hlt.add("el","HLT_Ele17_SW_TightEleId_L1R");
//	_hlt.add("el","HLT_Ele17_SW_TighterEleIdIsol_L1R_v2");
//	_hlt.add("el","HLT_Ele17_SW_TighterEleIdIsol_L1R_v3");
//	_hlt.add("mu","HLT_Mu9");
//	_hlt.add("mu","HLT_Mu15_v1");

	if ( _hltMode == "el_mu") {
		_hlt.set("el",ETHZHltChecker::kMatch);
		_hlt.set("mu",ETHZHltChecker::kMatch);
	} else if ( _hltMode == "el" ) {
		_hlt.set("el",ETHZHltChecker::kMatch);
	} else if ( _hltMode == "mu_not_el" ) {
		_hlt.set("mu",ETHZHltChecker::kMatch);
		_hlt.set("el",ETHZHltChecker::kReject);
	} else {
		THROW_RUNTIME("hltMode "<< _hltMode << " not defined");
	}

	_hlt.print();
//	_hltActiveNames.clear();
//	_hltActiveNames.push_back("HLT_Ele10_LW_L1R");
//	_hltActiveNames.push_back("HLT_Ele15_SW_L1R");
//	_hltActiveNames.push_back("HLT_Ele15_SW_CaloEleId_L1R");
//	_hltActiveNames.push_back("HLT_Ele17_SW_CaloEleId_L1R");
//	_hltActiveNames.push_back("HLT_Ele17_SW_TightEleId_L1R");
//	_hltActiveNames.push_back("HLT_Ele17_SW_TighterEleIdIsol_L1R_v2");
//	_hltActiveNames.push_back("HLT_Ele17_SW_TighterEleIdIsol_L1R_v3");
//	_hltActiveNames.push_back("HLT_Mu9");
//	_hltActiveNames.push_back("HLT_Mu15_v1");

}

//_____________________________________________________________________________
HWWSelectorB::~HWWSelectorB() {

}

//_____________________________________________________________________________
void HWWSelectorB::Book() {


	std::map<int,std::string> entriesLabels;
	entriesLabels[0] = "processedEntries";
	entriesLabels[1] = "selectedEntries";
	_hEntries = makeLabelHistogram("entries","HWWS selection entries",entriesLabels);

	Debug(0) << "Adding the selected objects" << std::endl;
	fSkimmedTree->Branch("ev","HWWEvent", &_diLepEvent);

	// counting histogram
	std::map<int,std::string> labels;


	labels[kLLBinAll]	   = "All events";
	labels[kLLBinHLT]      = "HLT";
	labels[kLLBinVertex]   = "Good Vertex";
	labels[kLLBinDilepton] = "l^{+}l^{-}";
	labels[kLLBinEtaPt]    = "EtaPt";
	labels[kLLBinIp]   	   = "Impact Parameter";
	labels[kLLBinIso]      = "Isolation";
	labels[kLLBinId]       = "Id";
	labels[kLLBinNoConv]   = "No Conversion";
	labels[kLLBinExtraLep] = "Extra lepton";

	_llCounters = makeLabelHistogram("llCounters","HWW selection",labels);
	_eeCounters = makeLabelHistogram("eeCounters","HWW selection - ee",labels);
	_emCounters = makeLabelHistogram("emCounters","HWW selection - em",labels);
	_mmCounters = makeLabelHistogram("mmCounters","HWW selection - mm",labels);

	std::map<int,std::string> ctrlLabels;
	ctrlLabels[kLepTagAll]		 = "All";
	ctrlLabels[kLepTagEta]       = "Eta";
	ctrlLabels[kLepTagPt]        = "Pt";
	ctrlLabels[kLepTagD0]        = "d0";
	ctrlLabels[kLepTagDz]        = "dz";
	ctrlLabels[kLepTagIsolation] = "Iso";
	ctrlLabels[kLepTagId]        = "Id";
	ctrlLabels[kLepTagNoConv]    = "Conversion Veto";

	fSkimmedFile->mkdir("ctrlHistograms")->cd();

	_elTightCtrl = makeLabelHistogram("elTightCtrl","Tight electrons",ctrlLabels);
	_elLooseCtrl = makeLabelHistogram("elLooseCtrl","Loose (extra) electrons",ctrlLabels);
	_muGoodCtrl  = makeLabelHistogram("muGoodCtrl" ,"Good muons",ctrlLabels);
	_muExtraCtrl = makeLabelHistogram("muExtraCtrl","Extra muons",ctrlLabels);

}

//_____________________________________________________________________________
TH1F* HWWSelectorB::makeLabelHistogram( const std::string& name, const std::string& title, std::map<int,std::string> labels) {
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
void HWWSelectorB::BeginJob() {
	readWorkingPoints( _wpFile );
	_hlt.connect(this->getChain(), _runInfoName);
}

//_____________________________________________________________________________
void HWWSelectorB::Process(Long64_t iEvent) {
	this->getEntry(iEvent);

	Debug(3) << "--"<< iEvent << "-----------------------------------------------" << std::endl;
	// make sure the previous event is cleared
	clear();

	if ( !selectAndClean() ) return;
	assembleNtuple();

	fSkimmedTree->Fill();
	++_nSelectedEvents;

}

//_____________________________________________________________________________
void HWWSelectorB::EndJob() {
	_llCounters->SetEntries(_llCounters->GetBinContent(1));
	_eeCounters->SetEntries(_eeCounters->GetBinContent(1));
	_emCounters->SetEntries(_emCounters->GetBinContent(1));
	_mmCounters->SetEntries(_mmCounters->GetBinContent(1));


	Debug(0) << "--- Job completed " << _nEvents << " processed " << _nSelectedEvents << " selected"<< std::endl;

	// add the number of processed events
	_hEntries->Fill("processedEntries",(double)_nEvents);
	_hEntries->Fill("selectedEntries",(double)_nSelectedEvents);

}

//_____________________________________________________________________________
Bool_t HWWSelectorB::Notify() {
	ETHZNtupleSelector::Notify();
	_hlt.updateIds();
    return kTRUE;

}

//_____________________________________________________________________________
void HWWSelectorB::readWorkingPoints( const std::string& path ) {

	std::cout << "Reading Working points from file " << path << std::endl;

	ifstream wpFile(path.c_str(), ifstream::in);
	if ( !wpFile.is_open() ) {
		THROW_RUNTIME(std::string("File ") + path + " not found");
	}

	std::string line;
	while( wpFile.good() ) {
		getline(wpFile, line);
		// remove trailing and leading spaces

		std::stringstream ss(line);
		std::string dummy;

		ss >> dummy;
		if ( dummy.empty() || dummy[0]=='#') continue;

		if ( dummy.length() != 1 )
			THROW_RUNTIME("Corrupted wp file: " + dummy + " is supposed to be 1 char long.");

		WorkingPoint p;
		switch (dummy[0]) {
		case 'B':
		case 'b':
			// Barrel
			p.partition = kBarrel;
			break;
		case 'E':
		case 'e':
			// Endcaps
			p.partition = kEndcap;
			break;
		default:
			std::cout << "Corrupted line\n" << line<< std::endl;
			continue;
		}

		ss >> p.efficiency >> p.See >> p.dPhi >> p.dEta>>p.HoE >> p.tkIso >> p.ecalIso >> p.hcalIso >> p.combIso>> p.missHits>> p.dist>> p.cot;

		p.print();

		_elWorkingPoints.push_back(p);
	}
}

//_____________________________________________________________________________
HWWSelectorB::WorkingPoint HWWSelectorB::getWorkingPoint(unsigned short part, int eff) {
	std::vector<WorkingPoint>::iterator it;
	for ( it=_elWorkingPoints.begin(); it != _elWorkingPoints.end(); ++it) {
		if ( (*it).partition == part && (*it).efficiency == eff)
			return *it;
	}

	std::stringstream msg;
	msg << "Working point " << part << "(" << eff << ") not found";
	THROW_RUNTIME(msg.str());

}

//_____________________________________________________________________________
void HWWSelectorB::clear() {

	_muTagged.clear();
	_elTagged.clear();

	_selectedPairs.clear();

	_selectedEls.clear();
	_selectedMus.clear();
	_softMus.clear();

//	_selectedJets.clear();
	_selectedPFJets.clear();

	_btaggedJets.clear();

}

//_____________________________________________________________________________
bool HWWSelectorB::selectAndClean() {
	//
	// loop over electrons and mus.
	// proceed only if there are 2 leptons (both tight and loose)



	Debug(3) << "- NtupleLeptons: " << getEvent()->getNEles()+getEvent()->getNMus() << '\n'
			<< "  NtupleMuons: " << getEvent()->getNMus() << '\n'
			<< "  NtupleElectrons: " <<getEvent()->getNEles() << std::endl;

	// check the HLT flags
	if ( !matchDataHLT() ) return false;

	if ( !hasGoodVertex() ) return false;

	// select electrons
	tagElectrons();

	// select good mus
	tagMuons();

	// fill some control histograms
	fillCtrlHistograms();

	countPairs();

	if ( !checkExtraLeptons() )
		return false;

	findSoftMus();

	// then clean the jets up
	cleanJets();
	return true;
}

//_____________________________________________________________________________
bool HWWSelectorB::matchDataHLT() {

    _llCounters->Fill(kLLBinAll);
    _eeCounters->Fill(kLLBinAll);
    _emCounters->Fill(kLLBinAll);
    _mmCounters->Fill(kLLBinAll);

    // GenMET is -1000 if it's a data file
    bool isData = ( getEvent()->getGenMET()  < -999.);
    bool match = !isData || _hlt.match( getEvent()->getHLTResults() );

	if ( match ) {
	    _llCounters->Fill(kLLBinHLT);
	    _eeCounters->Fill(kLLBinHLT);
	    _emCounters->Fill(kLLBinHLT);
	    _mmCounters->Fill(kLLBinHLT);
	}
//	return (trigger || !isData);
	return match;
}

//_____________________________________________________________________________
bool HWWSelectorB::hasGoodVertex() {
	//TODO move to config file

//	std::cout << "vrtxGood: " << PrimVtxGood << "\n"
//			<< "vrtxFake: " << PrimVtxIsFake << std::endl;
	ETHZEvent* ev = getEvent();
	bool goodVrtx = (ev->getPrimVtxNdof() >= _vrtxCut_nDof ) &&
	(ev->getPrimVtxGood() == 0 ) &&
	(ev->getPrimVtxIsFake() != 1) &&
	(TMath::Abs(ev->getPrimVtxRho() < _vrtxCut_rho )) &&
	(TMath::Abs(ev->getPrimVtxz()) < _vrtxCut_z );

	if ( goodVrtx ) {
		_llCounters->Fill(kLLBinVertex);
		_eeCounters->Fill(kLLBinVertex);
		_emCounters->Fill(kLLBinVertex);
		_mmCounters->Fill(kLLBinVertex);
	}

	return goodVrtx;
}

//_____________________________________________________________________________
void HWWSelectorB::electronIsoId( LepCandidate::elBitSet& tags, int idx, int eff ) {
	// identify tight electron

	ETHZEvent* ev = getEvent();
	float eta = ev->getElSCEta(idx);

	// apply the correction for the endcaps
	float dPhi = ev->getElDeltaPhiSuperClusterAtVtx(idx);
	float dEta = ev->getElDeltaEtaSuperClusterAtVtx(idx);

	float See       = ev->getElSigmaIetaIeta(idx);
	float HoE       = ev->getElHcalOverEcal(idx);
	float trkIso    = ev->getElDR03TkSumPt(idx);
	float ecalIso   = ev->getElDR03EcalRecHitSumEt(idx);
	float hcalIso   = ev->getElDR03HcalTowerSumEt(idx);
	float combIso_B = (trkIso + TMath::Max(0., ecalIso - 1.) + hcalIso) / ev->getElPt(idx);
	float combIso_E = (trkIso + ecalIso + hcalIso) / ev->getElPt(idx);
	float combIso   = 0;

	unsigned short p;
	if ( TMath::Abs(eta) <= _elCut_EtaSCEbEe ) {
		// barrel
		p = kBarrel;
		combIso = combIso_B;
	} else if ( TMath::Abs(eta) > _elCut_EtaSCEbEe ) {
		p = kEndcap;
		combIso = combIso_E;
	} else {
		//std::cout << "Candidate out of acceptance region" << std::endl;
		//return kOutOfAcc;
		return;
	}

	WorkingPoint wp = getWorkingPoint(p, eff );

    // conversion: the electron is a conversion
	// if |dist| < distCut and |delta cot(theta)| < cotCut
	// or
	// missingHist > hitsCut
	tags[kElTagDist] = (TMath::Abs(ev->getElConvPartnerTrkDist(idx)) < wp.dist);
	tags[kElTagCot]  = (TMath::Abs(ev->getElConvPartnerTrkDCot(idx)) < wp.cot);
	tags[kElTagHits] = (ev->getElNumberOfMissingInnerHits(idx) > wp.missHits);

	tags[kElTagSee]     = ( See < wp.See);
	tags[kElTagDphi]    = ( TMath::Abs(dPhi) < wp.dPhi);
	tags[kElTagDeta]    = ( TMath::Abs(dEta) < wp.dEta);
	tags[kElTagHoE]     = ( HoE  < wp.HoE);
	tags[kElTagCombIso] = ( combIso < wp.combIso);
	//std::cout << "elIdWord[" << i << "," << eta << ","<< _reader->ElPt[i] << "]: [" << wp.See << "][" << elIdWord.to_string() << "] See: " << See << ", dPhi: "<< dPhi << ", dEta: " << dEta << ", HoE: " << HoE << ", Comb: " << combIso << std::endl;

	return;

}

//_____________________________________________________________________________
void HWWSelectorB::tagElectrons() {

	ETHZEvent* ev = getEvent();
	_elTagged.clear();

	//loop over els
	for( int i(0);i < ev->getNEles(); ++i) {

		ElCandicate theEl(i);
		theEl.charge = ev->getElCharge(i);

		// first tag the tight word
		theEl.tightTags[kElTagEta] = (TMath::Abs( ev->getElEta(i) ) < _etaMaxEE);

		// interaction point
		theEl.tightTags[kElTagD0PV] = ( TMath::Abs(ev->getElD0PV(i)) < _lepCut_D0PV);
		theEl.tightTags[kElTagDzPV] = ( TMath::Abs(ev->getElDzPV(i)) < _lepCut_DzPV);

		// drop electrons with pT < _leptonPtCut
		theEl.tightTags[kElTagPt] = ( ev->getElPt(i) > _lepCut_leadingPt );

		electronIsoId(theEl.tightTags, theEl.idx, _elCut_TightWorkingPoint );

		// it's duplicate, I know
		theEl.looseTags[kElTagEta] = (TMath::Abs( ev->getElEta(i) ) < _etaMaxEE);

		// interaction point
		theEl.looseTags[kElTagD0PV] = ( TMath::Abs(ev->getElD0PV(i)) < _lepCut_D0PV);
		theEl.looseTags[kElTagDzPV] = ( TMath::Abs(ev->getElDzPV(i)) < _lepCut_DzPV);

		// drop electrons with pT < _leptonPtCut
		theEl.looseTags[kElTagPt] = ( ev->getElPt(i) > _lepCut_trailingPt );

		electronIsoId(theEl.looseTags, theEl.idx, _elCut_LooseWorkingPoint );

		_elTagged.push_back(theEl);

		Debug(5) << "- elTightTags: " << theEl.tightTags.to_string() << "\n"
				<<"  elLooseTags: " << theEl.looseTags.to_string() << std::endl;

		if ( theEl.isGood() && !theEl.isExtra()) {
			float trkIso    = ev->getElDR03TkSumPt(i);
			float ecalIso   = ev->getElDR03EcalRecHitSumEt(i);
			float hcalIso   = ev->getElDR03HcalTowerSumEt(i);
			float combIso_B = (trkIso + TMath::Max(0., ecalIso - 1.) + hcalIso) / ev->getElPt(i);
			float combIso_E = (trkIso + ecalIso + hcalIso) / ev->getElPt(i);
			THROW_RUNTIME("something fishy cIso: eta:" << ev->getElEta(i) << " b:" << combIso_B << " e:" << combIso_E);
		}

	}
}

//_____________________________________________________________________________
void HWWSelectorB::tagMuons() {
	// muon id cuts
	// isolation = (ev->getMuIso03SumPt(i) + ev->getMuIso03EmEt(i) + ev->getMuIso03HadEt(i) ) / ev->getMuPt(i) < 0.15
	// isGlobalMu
	// ev->getMuNChi2(i) < 10
	// ev->getMuNMuHits(i) > 0
	// ev->getMuNTkHits(i) > 10

	ETHZEvent* ev = getEvent();
	_muTagged.clear();
	// loop on mus
	for (int i=0; i < ev->getNMus(); ++i) {
		// reject mus with eta > _etaMaxMu
		// and pT < 10 GeV

		MuCandidate theMu(i);
		theMu.charge = ev->getMuCharge(i);
		LepCandidate::muBitSet& tags = theMu.tags;

		// to check
		tags[kMuTagEta] = (TMath::Abs( ev->getMuEta(i) ) < _etaMaxMu);

		// drop mus with pT < _leptonPtCut
		tags[kMuTagPt] = (  ev->getMuPt(i) > _lepCut_leadingPt );

		// check if the mu can be an extra
		tags[kMuTagExtraPt] = ( ev->getMuPt(i) > _lepCut_trailingPt );

		// interaction point
		tags[kMuTagD0PV] = ( TMath::Abs(ev->getMuD0PV(i)) < _lepCut_D0PV);
		tags[kMuTagDzPV] = ( TMath::Abs(ev->getMuDzPV(i)) < _lepCut_DzPV);

		// isolation, where does it come from?
		double combIso = (ev->getMuIso03SumPt(i) + ev->getMuIso03EmEt(i) + ev->getMuIso03HadEt(i) )/ ev->getMuPt(i);

		// the track is identified as a global muon
		// chi2/ndof of the global muon fit < 10
		// number of valid muon-detector hits used in the global fit > 0
		// Number of hits in the tracker track, Nhits, > 10.

		tags[kMuTagIsGlobal] = ( ev->getMuIsGlobalMuon(i)==1 );
		tags[kMuTagIsTracker]= ( ev->getMuIsTrackerMuon(i)==1 );
		tags[kMuTagNMuHits]  = ( ev->getMuNMuHits(i) > _muCut_NMuHist);
		tags[kMuTagNMatches] = ( ev->getMuNMatches(i) > _muCut_NMuMatches);
		tags[kMuTagNTkHits]  = ( ev->getMuNTkHits(i) > _muCut_NTrackerHits);
		tags[kMuTagNPxHits]  = ( ev->getMuNPxHits(i) > _muCut_NPixelHits);
		tags[kMuTagNChi2]    = ( ev->getMuNChi2(i) < _muCut_NChi2);
		tags[kMuTagRelPtRes] = ( ev->getMuPtE(i)/ev->getMuPt(i) < _muCut_relPtRes);
		tags[kMuTagCombIso]  = ( combIso < _muCut_combIsoOverPt );


		// additional soft muon tags
		tags[kMuTagSoftPt] = ( ev->getMuPt(i) > _muSoftCut_Pt );
		tags[kMuTagSoftHighPt] = ( ev->getMuPt(i) < _muSoftCut_HighPt);
		tags[kMuTagIsTMLastStationAngTight] = ( ev->getMuIsTMLastStationAngTight(i)==1 );
		tags[kMuTagNotIso] = ( combIso > _muSoftCut_NotIso );

		_muTagged.push_back(theMu);
		Debug(5) << "- muTags: " <<  theMu.tags.to_string() << std::endl;

	}
}

//_____________________________________________________________________________
void HWWSelectorB::findSoftMus() {

	_softMus.clear();

	std::set<unsigned int> softs;
	std::vector<MuCandidate>::iterator itMu;
	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu)
		softs.insert(itMu->idx);

	std::ostream_iterator< unsigned int > output( Debug(3), " " );
	Debug(3) << "- softs mus    '" ;
	std::copy( softs.begin(), softs.end(), output );
	Debug(3) << "'" << std::endl;
	Debug(3) << "- selected mus '" ;
	std::copy( softs.begin(), softs.end(), output );
	Debug(3) << "'" << std::endl;
	// remove those who are muons
	std::set_difference(softs.begin(), softs.end(),_selectedMus.begin(),_selectedMus.end(), std::inserter(_softMus,_softMus.end()));
	Debug(3) << "- softs clean  '" ;
	std::copy( _softMus.begin(), _softMus.end(), output );
	Debug(3) << "'" << std::endl;
}

//_____________________________________________________________________________
void HWWSelectorB::fillCtrlHistograms() {
	std::vector<ElCandicate>::iterator itEl;
	for( itEl = _elTagged.begin(); itEl!=_elTagged.end(); ++itEl) {
		_elTightCtrl->Fill(kLepTagAll);

		if ( !itEl->tightTags[kElTagEta] ) continue;
		_elTightCtrl->Fill(kLepTagEta);

		if ( !itEl->tightTags[kElTagPt] ) continue;
		_elTightCtrl->Fill(kLepTagPt);

		if ( !itEl->tightTags[kElTagD0PV] ) continue;
		_elTightCtrl->Fill(kLepTagD0);

		if ( !itEl->tightTags[kElTagDzPV] ) continue;
		_elTightCtrl->Fill(kLepTagDz);

		if ( !itEl->isIso() ) continue;
		_elTightCtrl->Fill(kLepTagIsolation);

		if ( !itEl->isId() ) continue;
		_elTightCtrl->Fill(kLepTagId);

		if ( !itEl->isNoConv() ) continue;
		_elTightCtrl->Fill(kLepTagNoConv);
	}

	//std::vector<ElCandicate>::iterator it;
	for( itEl = _elTagged.begin(); itEl!=_elTagged.end(); ++itEl) {
		_elLooseCtrl->Fill(kLepTagAll);

		if ( !itEl->looseTags[kElTagEta] ) continue;
		_elLooseCtrl->Fill(kLepTagEta);

		if ( !itEl->looseTags[kElTagPt] ) continue;
		_elLooseCtrl->Fill(kLepTagPt);

		if ( !itEl->looseTags[kElTagD0PV] ) continue;
		_elLooseCtrl->Fill(kLepTagD0);

		if ( !itEl->looseTags[kElTagDzPV] ) continue;
		_elLooseCtrl->Fill(kLepTagDz);

		if ( !itEl->isLooseIso() ) continue;
		_elLooseCtrl->Fill(kLepTagIsolation);

		if ( !itEl->isLooseId() ) continue;
		_elLooseCtrl->Fill(kLepTagId);

		if ( !itEl->isLooseNoConv() ) continue;
		_elLooseCtrl->Fill(kLepTagNoConv);
	}

	std::vector<MuCandidate>::iterator itMu;
	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu) {
		_muGoodCtrl->Fill(kLepTagAll);

		if ( !itMu->tags[kMuTagEta]  ) continue;
		_muGoodCtrl->Fill(kLepTagEta);

		if ( !itMu->tags[kMuTagPt]  ) continue;
		_muGoodCtrl->Fill(kLepTagPt);

		if ( !itMu->tags[kMuTagD0PV]  ) continue;
		_muGoodCtrl->Fill(kLepTagD0);

		if ( !itMu->tags[kMuTagDzPV]  ) continue;
		_muGoodCtrl->Fill(kLepTagDz);

		if ( !itMu->isIso() ) continue;
		_muGoodCtrl->Fill(kLepTagIsolation);

		if ( !itMu->isId()  ) continue;
		_muGoodCtrl->Fill(kLepTagId);

		if ( !itMu->isNoConv() ) continue;
		_muGoodCtrl->Fill(kLepTagNoConv);
	}

	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu) {
		_muExtraCtrl->Fill(kLepTagAll);

		if ( !itMu->tags[kMuTagEta]  ) continue;
		_muExtraCtrl->Fill(kLepTagEta);

		if ( !itMu->tags[kMuTagExtraPt]  ) continue;
		_muExtraCtrl->Fill(kLepTagPt);

		if ( !itMu->tags[kMuTagD0PV]  ) continue;
		_muExtraCtrl->Fill(kLepTagD0);

		if ( !itMu->tags[kMuTagDzPV]  ) continue;
		_muExtraCtrl->Fill(kLepTagDz);

		if ( !itMu->isIso() ) continue;
		_muExtraCtrl->Fill(kLepTagIsolation);

		if ( !itMu->isId()  ) continue;
		_muExtraCtrl->Fill(kLepTagId);

		if ( !itMu->isNoConv() ) continue;
		_muExtraCtrl->Fill(kLepTagNoConv);
	}
}

//_____________________________________________________________________________
void HWWSelectorB::countPairs() {

	_selectedPairs.clear();
	_selectedEls.clear();
	_selectedMus.clear();

	// put all leptons in a temporay container
	std::vector<LepCandidate*> allTags;

	std::vector<ElCandicate>::iterator itEl;
	for( itEl = _elTagged.begin(); itEl != _elTagged.end(); ++itEl)
		allTags.push_back(&(*itEl));

	std::vector<MuCandidate>::iterator itMu;
	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu)
		allTags.push_back(&(*itMu));

	Debug(4) << "  - nLepToPair: " << allTags.size() << "   nEl: " << _elTagged.size() <<" " <<getEvent()->getNEles()
			<< "   nMu: " << _muTagged.size() << " " <<getEvent()->getNMus() << std::endl;

	// make all the opposite sign pairs
	std::vector<LepPair> oppChargePairs;

	for( unsigned int i(0); i<allTags.size(); ++i)
		for( unsigned int j(i+1); j<allTags.size(); ++j) {
			LepPair p( allTags[i], allTags[j]);
			Debug(3) << "i:" <<  i << " j:" << j
					<< " opp " << p.isOpposite() << std::endl;
			if ( p.isOpposite() )
				oppChargePairs.push_back(p);
		}


	if ( oppChargePairs.size() == 0 ) {
		Debug(3) << "- No pairs found" << std::endl;
		return;
	}

	// go through the pairs
	std::vector<LepPair>::iterator iP;
	std::vector<unsigned int> eeCounts(kLLBinLast);
	std::vector<unsigned int> emCounts(kLLBinLast);
	std::vector<unsigned int> mmCounts(kLLBinLast);
	std::vector<unsigned int> llCounts(kLLBinLast);

	// loop over the pairs and count the final states
	for( iP = oppChargePairs.begin(); iP != oppChargePairs.end(); ++iP ) {

		//
		Debug(3) << "pair final state " << iP->finalState()
				<< "   A: " << (int)iP->_lA->type
				<< "   B: " << (int)iP->_lB->type
				<< std::endl;

		std::vector<unsigned int>* counts(0x0);
		switch (iP->finalState()) {
			case LepPair::kEE_t:
				counts = &eeCounts;
				break;
			case LepPair::kEM_t:
				counts = &emCounts;
				break;
			case LepPair::kMM_t:
				counts = &mmCounts;
				break;
			default:
				THROW_RUNTIME("Found lepton pair with weird final state code: " << iP->finalState());

		}

		// apply selection criteria
		(*counts)[kLLBinDilepton]++;

		if ( !iP->isPtEta() ) continue;
		(*counts)[kLLBinEtaPt]++;

		if ( !iP->isVertex() ) continue;
		(*counts)[kLLBinIp]++;

		if ( !iP->isIso() ) continue;
		(*counts)[kLLBinIso]++;

		if ( !iP->isId() ) continue;
		(*counts)[kLLBinId]++;

		if ( !iP->isNoConv() ) continue;
		(*counts)[kLLBinNoConv]++;

		// mark the leptons to be saved
		_selectedPairs.push_back(*iP);
	}

	//
	std::stringstream see, sem, smm, sll;

	for( unsigned int i(1); i<llCounts.size()-1; ++i ){
		see << eeCounts[i] << ",";
		sem << emCounts[i] << ",";
		smm << mmCounts[i] << ",";

		if ( eeCounts[i] ||  emCounts[i] || mmCounts[i] )
			llCounts[i]++;

		sll << llCounts[i] << ",";
	}

	Debug(3) << "ee: " << see.str() << '\n'
		     << "em: " << sem.str() << '\n'
		     << "mm: " << smm.str() << '\n'
		     << "ll: " << sll.str()  << std::endl;

	Debug(3) << "N selected pairs: " << _selectedPairs.size() << std::endl;


	fillCounts( _llCounters, llCounts);
	fillCounts( _eeCounters, eeCounts);
	fillCounts( _emCounters, emCounts);
	fillCounts( _mmCounters, mmCounts);

	for( iP = _selectedPairs.begin(); iP != _selectedPairs.end(); ++iP ) {
		for ( int i(0); i<2; ++i){
			LepCandidate* l = (*iP)[i];
			if (l->type == LepCandidate::kEl_t)
				_selectedEls.insert(l->idx);
			else if (l->type == LepCandidate::kMu_t)
				_selectedMus.insert(l->idx);
			else
				THROW_RUNTIME("Lepton type not recognized t:" << l->type << " idx:" << l->idx);
		}
	}

	Debug(3) << "Selected _reader->Els: "  << _selectedEls.size() << '\n'
			 << "Selected _reader->Mus: "  << _selectedMus.size() << std::endl;

}

//_____________________________________________________________________________
void HWWSelectorB::fillCounts( TH1F* h, const std::vector<unsigned int>& counts) {

	if ( counts[kLLBinDilepton] ) h->Fill(kLLBinDilepton);
	if ( counts[kLLBinEtaPt] )    h->Fill(kLLBinEtaPt);
	if ( counts[kLLBinIp] )	  	  h->Fill(kLLBinIp);
	if ( counts[kLLBinIso] )      h->Fill(kLLBinIso);
	if ( counts[kLLBinId] )       h->Fill(kLLBinId);
	if ( counts[kLLBinNoConv] )   h->Fill(kLLBinNoConv);

}

//_____________________________________________________________________________
bool HWWSelectorB::checkExtraLeptons() {

	// no pairs, no fun
	if( _selectedPairs.size() != 1 ) return false;

	// put here all the electrons
	std::set<unsigned int> allEls, allMus;

	// start from the selected ones
	allEls = _selectedEls;
	allMus = _selectedMus;

	// test printout
	std::set<unsigned int>::iterator it;
	Debug(4) << " - allEls(1): ";
	for( it = allEls.begin(); it != allEls.end(); ++it)
		Debug(4) << *it << ",";
	Debug(4) << std::endl;
	Debug(4) << " - allMus(1): ";
	for( it = allMus.begin(); it != allMus.end(); ++it)
		Debug(4) << *it << ",";
	Debug(4) << std::endl;
	// end test printout

	std::vector<ElCandicate>::iterator itEl;
	for ( itEl = _elTagged.begin(); itEl != _elTagged.end(); ++itEl)
		if ( itEl->isExtra() ) {
			allEls.insert(itEl->idx);
			Debug(5) << "Adding extra el " << itEl->idx << std::endl;
		}

	std::vector<MuCandidate>::iterator itMu;
	for ( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu) {
		if ( itMu->isExtra() ) {
			allMus.insert(itMu->idx);
			Debug(5) << "Adding extra mu " << itMu->idx << std::endl;
		}
	}

	Debug(4) << " - allEls(2): ";
	for( it = allEls.begin(); it != allEls.end(); ++it)
		Debug(4) << *it << ",";
	Debug(4) << std::endl;
	Debug(4) << " - allMus(2): ";
	for( it = allMus.begin(); it != allMus.end(); ++it)
		Debug(4) << *it << ",";
	Debug(4) << std::endl;

	Debug(3) << "- N (good+extra) leptons: " << (allEls.size()+allMus.size()) << std::endl;
	if ( allEls.size()+allMus.size() != 2 )
		return false;

	// find the final state histogram
	TH1F* counters;
	LepPair &p = _selectedPairs[0];
	switch (p.finalState()){
	case LepPair::kEE_t:
		counters = _eeCounters;
		break;
	case LepPair::kEM_t:
		counters = _emCounters;
		break;
	case LepPair::kMM_t:
		counters = _mmCounters;
		break;
	default:
		THROW_RUNTIME("Unidentified lepton pair: finalState = " << p.finalState());
	}

	counters->Fill(kLLBinExtraLep);
	_llCounters->Fill(kLLBinExtraLep);

	return true;
}

//_____________________________________________________________________________
void HWWSelectorB::assembleNtuple() {

	ETHZEvent* ev = getEvent();

	// clear the ntuple
	_diLepEvent->Clear();

	// fill the run parameters
	_diLepEvent->Run          = ev->getRun();
	_diLepEvent->Event        = ev->getEvent();
	_diLepEvent->LumiSection  = ev->getLumiSection();

    // primary vertexes
	_diLepEvent->PrimVtxGood  = ev->getPrimVtxGood();
	_diLepEvent->PrimVtxx     = ev->getPrimVtxx();
	_diLepEvent->PrimVtxy     = ev->getPrimVtxy();
	_diLepEvent->PrimVtxz     = ev->getPrimVtxz();
	_diLepEvent->NVrtx        = ev->getNVrtx();

	_diLepEvent->TCMET		  = ev->getTCMET();
	_diLepEvent->TCMETphi     = ev->getTCMETphi();
	_diLepEvent->PFMET        = ev->getPFMET();
	_diLepEvent->PFMETphi     = ev->getPFMETphi();
//	_diLepEvent->SumEt        = ev->getSumEt();
//	_diLepEvent->MuCorrMET    = ev->getMuCorrMET();
//	_diLepEvent->MuCorrMETphi = ev->getMuCorrMETphi();

	_diLepEvent->HasSoftMus   = _softMus.size() > 0;
//	_diLepEvent->HasBTaggedJets = _btaggedJets.size() > 0;

	_diLepEvent->NEles        = _selectedEls.size();

	_diLepEvent->NMus         = _selectedMus.size();

//	_diLepEvent->NJets        = _selectedJets.size();

	_diLepEvent->PFNJets      = _selectedPFJets.size();

	_diLepEvent->Els.resize(_diLepEvent->NEles);
	std::set<unsigned int>::iterator itEl = _selectedEls.begin();
	for( int i(0); i < _diLepEvent->NEles ; ++i) {
		unsigned int k = *itEl;
		HWWElectron &e = _diLepEvent->Els[i];
		e.P.SetXYZT(ev->getElPx(k), ev->getElPy(k), ev->getElPz(k), ev->getElE(k));
		e.Charge 					= ev->getElCharge(k);
		e.SigmaIetaIeta				= ev->getElSigmaIetaIeta(k);
		e.CaloEnergy 				= ev->getElCaloEnergy(k);
		e.DR03TkSumPt 				= ev->getElDR03TkSumPt(k);
		e.DR04EcalRecHitSumEt		= ev->getElDR04EcalRecHitSumEt(k);
		e.DR04HcalTowerSumEt 		= ev->getElDR04HcalTowerSumEt(k);
		e.NumberOfMissingInnerHits 	= ev->getElNumberOfMissingInnerHits(k);
		e.DeltaPhiSuperClusterAtVtx	= ev->getElDeltaPhiSuperClusterAtVtx(k);
		e.DeltaEtaSuperClusterAtVtx	= ev->getElDeltaEtaSuperClusterAtVtx(k);
		e.D0PV 						= ev->getElD0PV(k);
		e.DzPV 						= ev->getElDzPV(k);

		++itEl;
	}
	if ( itEl != _selectedEls.end() )
		THROW_RUNTIME("Not all electrons were copied?");

	_diLepEvent->Mus.resize(_diLepEvent->NMus);
	std::set<unsigned int>::iterator itMu = _selectedMus.begin();
    for( int i(0); i < _diLepEvent->NMus; ++i ) {
		unsigned int k = *itMu;
		HWWMuon &u = _diLepEvent->Mus[i];

		u.P.SetXYZT(ev->getMuPx(k), ev->getMuPy(k), ev->getMuPz(k), ev->getMuE(k) );
		u.Charge                   = ev->getMuCharge(k);
		u.Iso03SumPt               = ev->getMuIso03SumPt(k);
		u.Iso03EmEt                = ev->getMuIso03EmEt(k);
		u.Iso03HadEt               = ev->getMuIso03HadEt(k);
		u.NMuHits                  = ev->getMuNMuHits(k);
		u.NTkHits                  = ev->getMuNTkHits(k);
		u.NChi2                    = ev->getMuNChi2(k);
		u.IsGlobalMuon             = ev->getMuIsGlobalMuon(k);
		u.IsTrackerMuon            = ev->getMuIsTrackerMuon(k);
		u.IsTMLastStationAngTight  = ev->getMuIsTMLastStationAngTight(k);
		u.D0PV                     = ev->getMuD0PV(k);
		u.DzPV                     = ev->getMuDzPV(k);

		++itMu;
	}
	if ( itMu != _selectedMus.end() )
		THROW_RUNTIME("Not all muons were copied?");

//	_diLepEvent->Jets.resize(_diLepEvent->NJets);
//	std::set<unsigned int>::iterator itJ = _selectedJets.begin();
//	for( int i(0); i <_diLepEvent->NJets; ++i) {
//		int k = *itJ;
//		HWWJet& j = _diLepEvent->Jets[i];
//
//		j.P.SetXYZT( ev->getJPx(k), ev->getJPy(k), ev->getJPz(k), ev->getJE(k) );
//		j.EMfrac         = ev->getJEMfrac(k);
//		j.NConstituents  = ev->getJNConstituents(k);
//		j.ID_HPD         = ev->getJID_HPD(k);
//		j.ID_RBX         = ev->getJID_RBX(k);
//		j.ID_n90Hits     = ev->getJID_n90Hits(k);
//		j.ID_resEMF      = ev->getJID_resEMF(k);
//		j.ID_HCALTow     = ev->getJID_HCALTow(k);
//		j.ID_ECALTow     = ev->getJID_ECALTow(k);
//
//		++itJ;
//	}
//	if ( itJ != _selectedJets.end() )
//		THROW_RUNTIME("Not all jets were copied?");

	_diLepEvent->PFJets.resize(_diLepEvent->PFNJets);
	std::set<unsigned int>::iterator itPFJ = _selectedPFJets.begin();
	for( int i(0); i < _diLepEvent->PFNJets; ++i) {
		int k = *itPFJ;
		HWWPFJet& pfj = _diLepEvent->PFJets[i];

		pfj.P.SetXYZT(ev->getPFJPx(k), ev->getPFJPy(k), ev->getPFJPz(k), ev->getPFJE(k));
		pfj.ChHadfrac       = ev->getPFJChHadfrac(k);
		pfj.NeuHadfrac      = ev->getPFJNeuHadfrac(k);
		pfj.ChEmfrac        = ev->getPFJChEmfrac(k);
		pfj.NeuEmfrac       = ev->getPFJNeuEmfrac(k);
		pfj.NConstituents   = ev->getPFJNConstituents(k);

		++itPFJ;
	}
	if ( itPFJ != _selectedPFJets.end() )
		THROW_RUNTIME("Not all pfJets were copied?");


}

//_____________________________________________________________________________
void HWWSelectorB::cleanJets() {
	// so far so good, let's clean the jets up

	ETHZEvent* ev = getEvent();
//	_selectedJets.clear();
//	_btaggedJets.clear();
     	// loop on jets
//	for ( int i=0; i<ev->getNJets(); ++i) {
//
//		TVector3 pJet( ev->getJPx(i), ev->getJPy(i), ev->getJPz(i));
//		std::set<unsigned int>::iterator it;
//
//		bool match = false;
//		// try to match the jet with an electron
//		for( it=_selectedEls.begin();
//				it != _selectedEls.end(); ++it) {
//			TVector3 pEl(ev->getElPx(*it), ev->getElPy(*it), ev->getElPz(*it));
//
//			//what is the 0.3 cut?
//			match |= ( TMath::Abs(pJet.DeltaR(pEl)) < _jetCut_Dr );
//
//		}
//
//		for( it=_selectedMus.begin();
//				it != _selectedMus.end(); ++it) {
//			TVector3 pMu(ev->getMuPx(*it), ev->getMuPy(*it), ev->getMuPz(*it));
//			//what is the 0.3 cut?
//			match |= ( TMath::Abs(pJet.DeltaR(pMu)) < _jetCut_Dr );
//		}
//
//		if ( match ) continue;
//
//		// jet ptcut
//		if ( ev->getJPt(i) > _jetCut_Pt && ev->getJEta(i) < _jetCut_Eta )
//			_selectedJets.insert(i);
//
//	}

	_selectedPFJets.clear();
	// loop on pf jets now
	for ( int i=0; i<ev->getPFNJets(); ++i) {


		TVector3 pPFJet( ev->getPFJPx(i), ev->getPFJPy(i), ev->getPFJPz(i));
		std::set<unsigned int>::iterator it;

		bool match = false;
		// try to match the jet with an electron
		for( it=_selectedEls.begin();
				it != _selectedEls.end(); ++it) {
			TVector3 pEl(ev->getElPx(*it), ev->getElPy(*it), ev->getElPz(*it));
			//what is the 0.3 cut?
			match |= ( TMath::Abs(pPFJet.DeltaR(pEl)) < _jetCut_Dr );
		}

		for( it=_selectedMus.begin();
				it != _selectedMus.end(); ++it) {
			TVector3 pMu(ev->getMuPx(*it), ev->getMuPy(*it), ev->getMuPz(*it));

			//what is the 0.3 cut?
			match |= ( TMath::Abs(pPFJet.DeltaR(pMu)) < _jetCut_Dr );
		}

		if ( match ) continue;

		// jet ptcut
		if ( ev->getPFJPt(i) > _jetCut_Pt  && ev->getPFJEta(i) < _jetCut_Eta )
			_selectedPFJets.insert(i);
		// or check for btagged jets
		else if ( ev->getPFJbTagProbTkCntHighEff(i) > _jetCut_BtagProb )
			_btaggedJets.insert(i);

	}

}
