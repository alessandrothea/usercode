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

//_____________________________________________________________________________
HWWSelectorB::LepCandidate* HWWSelectorB::LepPair::operator [](unsigned int i){
	switch (i) {
	case 0:
		return _lA;
	case 1:
		return _lB;
	default:
		THROW_RUNTIME("index out of bound i="<< i)
	}
}
//_____________________________________________________________________________
bool HWWSelectorB::MuCandidate::isPtEta(){
	return (tags[kMuTagPt] && tags[kMuTagEta]);
}

//_____________________________________________________________________________
bool HWWSelectorB::MuCandidate::isVertex() {
	return (tags[kMuTagD0PV] && tags[kMuTagDzPV] );
}

//_____________________________________________________________________________
bool HWWSelectorB::MuCandidate::isId() {
	return ( tags[kMuTagIsGlobal] &&
				tags[kMuTagIsTracker] &&
				tags[kMuTagNMuHits] &&
				tags[kMuTagNMatches] &&
				tags[kMuTagNTkHits] &&
				tags[kMuTagNPxHits] &&
				tags[kMuTagNChi2] &&
				tags[kMuTagRelPtRes]
			);
}

//_____________________________________________________________________________
bool HWWSelectorB::MuCandidate::isIso() {
	return tags[kMuTagCombIso];
}

//_____________________________________________________________________________
bool HWWSelectorB::MuCandidate::isExtra() {
	return (tags[kMuTagPt] && tags[kMuTagExtraPt])
		&& this->isVertex()
		&& this->isId()
		&& this->isIso();
}

//_____________________________________________________________________________
bool HWWSelectorB::MuCandidate::isGood() {
	return this->isPtEta()
		&& this->isVertex()
		&& this->isId()
		&& this->isIso();
}

//_____________________________________________________________________________
bool HWWSelectorB::MuCandidate::isSoft() {
	return ( tags[kMuTagEta] &&
			tags[kMuTagSoftPt] &&
			tags[kMuTagIsTracker] &&
			tags[kMuTagIsTMLastStationAngTight] &&
			tags[kMuTagNTkHits] &&
			tags[kMuTagD0PV] &&
			( !tags[kMuTagSoftHighPt] || tags[kMuTagSoftHighPt] && tags[kMuTagNotIso] )
		);

}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isPtEta() {
	return (tightTags[kElTagPt] && tightTags[kElTagEta]);
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isVertex() {
	return (tightTags[kElTagD0PV] && tightTags[kElTagDzPV] );
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isIso() {
	return tightTags[kElTagCombIso];
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isId() {
	return tightTags[kElTagSee] && tightTags[kElTagDphi] && tightTags[kElTagDeta] && tightTags[kElTagHoE];
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isNoConv() {
	// !conversion
	return !( ( tightTags[kElTagDist] && tightTags[kElTagCot] ) || tightTags[kElTagHits]);
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isLooseIso() {
	return looseTags[kElTagCombIso];
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isLooseId() {
	return looseTags[kElTagSee] && looseTags[kElTagDphi] && looseTags[kElTagDeta] && looseTags[kElTagHoE];
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isLooseNoConv() {
	// !conversion
	return !( ( looseTags[kElTagDist] && looseTags[kElTagCot] ) || looseTags[kElTagHits]);
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isGood() {
	return this->isPtEta()
		&& this->isVertex()
		&& this->isIso()
		&& this->isId()
		&& this->isNoConv();
}

//_____________________________________________________________________________
bool HWWSelectorB::ElCandicate::isExtra() {
	return
			// ptEta
			(looseTags[kElTagPt] && looseTags[kElTagEta])
			// vertex
			&& (looseTags[kElTagD0PV] && looseTags[kElTagDzPV] )
			// iso
			&& isLooseIso()
			// id
            && isLooseId()
            // no conversion
            && isLooseNoConv();
}

//_____________________________________________________________________________
HWWSelectorB::HWWSelectorB( int argc, char** argv ) : ETHZNtupleSelector( argc, argv ),
		_nSelectedEvents(0), _llCounters(0x0), _eeCounters(0x0), _emCounters(0x0), _mmCounters(0x0){

	_event = new HWWEvent();

	std::cout <<  fChain->GetName() << "   "<< fChain->GetTree() << std::endl;

	_hltMode		  = _config.getValue<std::string>("HWWSelector.hltMode","el_mu");
	_runInfoName      = _config.getValue<std::string>("HWWSelector.runInfoName");

	_elCut_TightWorkingPoint = _config.getValue<int>( "HWWSelector.elTightWorkingPoint");
	_elCut_LooseWorkingPoint = _config.getValue<int>( "HWWSelector.elLooseWorkingPoint");
	_elCut_EtaSCEbEe     = _config.getValue<float>("HWWSelector.elCut.etaSCEbEe"); // 1.479

	_wpFile				 = _config.getValue<std::string>( "HWWSelector.elWorkingPointFile");

	_lepCut_Pt			 = _config.getValue<float>("HWWSelector.lepCut.Pt"); // = 20.
	_lepCut_D0PV		 = _config.getValue<float>("HWWSelector.lepCut.d0PrimaryVertex");// = 0.2
	_lepCut_DzPV		 = _config.getValue<float>("HWWSelector.lepCut.dZPrimaryVertex");// = 10.
	_lepCut_extraPt 	 = _config.getValue<float>("HWWSelector.lepCut.extraPt"); // =10.

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
	_hlt.add("el","HLT_Ele10_LW_L1R");
	_hlt.add("el","HLT_Ele15_SW_L1R");
	_hlt.add("el","HLT_Ele15_SW_CaloEleId_L1R");
	_hlt.add("el","HLT_Ele17_SW_CaloEleId_L1R");
	_hlt.add("el","HLT_Ele17_SW_TightEleId_L1R");
	_hlt.add("el","HLT_Ele17_SW_TighterEleIdIsol_L1R_v2");
	_hlt.add("el","HLT_Ele17_SW_TighterEleIdIsol_L1R_v3");
	_hlt.add("mu","HLT_Mu9");
	_hlt.add("mu","HLT_Mu15_v1");

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
	fSkimmedTree->Branch("ev","HWWEvent", &_event);

	// counting histogram
	std::map<int,std::string> labels;


	labels[kLLBinAll]	   = "All events";
	labels[kLLBinHLT]      = "HLT";
	labels[kLLBinDilepton] = "l^{+}l^{-}";
	labels[kLLBinEtaPt]    = "EtaPt";
	labels[kLLBinVertex]   = "Vertex";
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
	_hlt.connect(fChain, _runInfoName);
}

//_____________________________________________________________________________
void HWWSelectorB::Process(Long64_t iEvent) {
	GetEntry(iEvent);

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

//	Debug(0) << "Chain " << fChain << " New file opened " << fChain->GetCurrentFile() << std::endl;
	_hlt.updateIds();
//
//	if (  fChain->GetCurrentFile() ) {
//		_hltAllNames.clear();
//
//		std::vector<std::string>*names = 0;
//		TTree* runInfo = (TTree*)(fChain->GetCurrentFile()->Get(_runInfoName.c_str()));
//		runInfo->SetBranchAddress("HLTNames",&names);
//		runInfo->GetEntry(0);
//		_hltAllNames = *names;
//	}
//
//
//	_hltIdx.clear();
//
//	std::vector<std::string>::iterator it;
//	for( unsigned int i(0); i < _hltAllNames.size(); ++i)
//		for( it = _hltActiveNames.begin(); it != _hltActiveNames.end(); ++it)
//			if ( _hltAllNames[i] == *it ) {
//				_hltIdx.push_back(i);
//				break;
//			}

//	for( int i(0); i<_hltIdx.size(); ++i)
//		Debug(1) << i << "   " << _hltNames[_hltIdx[i]] << "   " << _hltIdx[i] << std::endl;

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

	//-old stuff----
	_selectedEls.clear();
	_selectedMus.clear();
	_softMus.clear();

	_selectedJets.clear();
	_selectedPFJets.clear();

	_btaggedJets.clear();

}

//_____________________________________________________________________________
bool HWWSelectorB::selectAndClean() {
	//
	// loop over electrons and mus.
	// proceed only if there are 2 leptons (both tight and loose)



	Debug(3) << "- NtupleLeptons: " << NEles+NMus << '\n'
			<< "  NtupleMuons: " << NMus << '\n'
			<< "  NtupleElectrons: " << NEles << std::endl;

	// check the HLT flags
	if ( !matchDataHLT() ) return false;

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
    bool isData = ( GenMET  < -999.);
    bool match = !isData || _hlt.match( HLTResults );

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
HWWSelectorB::elBitSet HWWSelectorB::electronIsoId( elBitSet& tags, int idx, int eff ) {
	// identify tight electron

	float eta = ElSCEta[idx];

	// apply the correction for the endcaps
	float dPhi = ElDeltaPhiSuperClusterAtVtx[idx];
	float dEta = ElDeltaEtaSuperClusterAtVtx[idx];

	float See       = ElSigmaIetaIeta[idx];
	float HoE       = ElHcalOverEcal[idx];
	float trkIso    = ElDR03TkSumPt[idx];
	float ecalIso   = ElDR03EcalRecHitSumEt[idx];
	float hcalIso   = ElDR03HcalTowerSumEt[idx];
	float combIso_B = (trkIso + TMath::Max(0., ecalIso - 1.) + hcalIso) / ElPt[idx];
	float combIso_E = (trkIso + ecalIso + hcalIso) / ElPt[idx];
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
		return false;
	}

	WorkingPoint wp = getWorkingPoint(p, eff );

    // conversion: the electron is a conversion
	// if |dist| < distCut and |delta cot(theta)| < cotCut
	// or
	// missingHist > hitsCut
	tags[kElTagDist] = (TMath::Abs(ElConvPartnerTrkDist[idx]) < wp.dist);
	tags[kElTagCot]  = (TMath::Abs(ElConvPartnerTrkDCot[idx]) < wp.cot);
	tags[kElTagHits] = (ElNumberOfMissingInnerHits[idx] > wp.missHits);

	tags[kElTagSee]     = ( See < wp.See);
	tags[kElTagDphi]    = ( TMath::Abs(dPhi) < wp.dPhi);
	tags[kElTagDeta]    = ( TMath::Abs(dEta) < wp.dEta);
	tags[kElTagHoE]     = ( HoE  < wp.HoE);
	tags[kElTagCombIso] = ( combIso < wp.combIso);
	//std::cout << "elIdWord[" << i << "," << eta << ","<< ElPt[i] << "]: [" << wp.See << "][" << elIdWord.to_string() << "] See: " << See << ", dPhi: "<< dPhi << ", dEta: " << dEta << ", HoE: " << HoE << ", Comb: " << combIso << std::endl;

	return tags;

}

//_____________________________________________________________________________
void HWWSelectorB::tagElectrons() {

	_elTagged.clear();

	//loop over els
	for( int i(0); i<NEles; ++i) {

		ElCandicate theEl(i);
		theEl.charge = ElCharge[i];

		// first tag the tight word
		theEl.tightTags[kElTagEta] = (TMath::Abs( ElEta[i] ) < _etaMaxEE);

		// interaction point
		theEl.tightTags[kElTagD0PV] = ( TMath::Abs(ElD0PV[i]) < _lepCut_D0PV);
		theEl.tightTags[kElTagDzPV] = ( TMath::Abs(ElDzPV[i]) < _lepCut_DzPV);

		// drop electrons with pT < _leptonPtCut
		theEl.tightTags[kElTagPt] = ( ElPt[i] > _lepCut_Pt );

		electronIsoId(theEl.tightTags, theEl.idx, _elCut_TightWorkingPoint );

		// it's duplicate, I know
		theEl.looseTags[kElTagEta] = (TMath::Abs( ElEta[i] ) < _etaMaxEE);

		// interaction point
		theEl.looseTags[kElTagD0PV] = ( TMath::Abs(ElD0PV[i]) < _lepCut_D0PV);
		theEl.looseTags[kElTagDzPV] = ( TMath::Abs(ElDzPV[i]) < _lepCut_DzPV);

		// drop electrons with pT < _leptonPtCut
		theEl.looseTags[kElTagPt] = ( ElPt[i] > _lepCut_extraPt );

		electronIsoId(theEl.looseTags, theEl.idx, _elCut_LooseWorkingPoint );

		_elTagged.push_back(theEl);

		Debug(5) << "- elTightTags: " << theEl.tightTags.to_string() << "\n"
				<<"  elLooseTags: " << theEl.looseTags.to_string() << std::endl;

		if ( theEl.isGood() && !theEl.isExtra()) {
			float trkIso    = ElDR03TkSumPt[i];
			float ecalIso   = ElDR03EcalRecHitSumEt[i];
			float hcalIso   = ElDR03HcalTowerSumEt[i];
			float combIso_B = (trkIso + TMath::Max(0., ecalIso - 1.) + hcalIso) / ElPt[i];
			float combIso_E = (trkIso + ecalIso + hcalIso) / ElPt[i];
			THROW_RUNTIME("something fishy cIso: eta:" << ElEta[i] << " b:" << combIso_B << " e:" << combIso_E);
		}

	}
}

//_____________________________________________________________________________
void HWWSelectorB::tagMuons() {
	// muon id cuts
	// isolation = (MuIso03SumPt[i] + MuIso03EmEt[i] + MuIso03HadEt[i] ) / MuPt[i] < 0.15
	// isGlobalMu
	// MuNChi2[i] < 10
	// MuNMuHits[i] > 0
	// MuNTkHits[i] > 10

	_muTagged.clear();
	// loop on mus
	for (int i=0; i<NMus; ++i) {
		// reject mus with eta > _etaMaxMu
		// and pT < 10 GeV

		MuCandidate theMu(i);
		theMu.charge = MuCharge[i];
		muBitSet& tags = theMu.tags;

		// to check
		tags[kMuTagEta] = (TMath::Abs( MuEta[i] ) < _etaMaxMu);

		// drop mus with pT < _leptonPtCut
		tags[kMuTagPt] = (  MuPt[i] > _lepCut_Pt );

		// check if the mu can be an extra
		tags[kMuTagExtraPt] = ( MuPt[i] > _lepCut_extraPt );

		// interaction point
		tags[kMuTagD0PV] = ( TMath::Abs(MuD0PV[i]) < _lepCut_D0PV);
		tags[kMuTagDzPV] = ( TMath::Abs(MuDzPV[i]) < _lepCut_DzPV);

		// isolation, where does it come from?
		double combIso = (MuIso03SumPt[i] + MuIso03EmEt[i] + MuIso03HadEt[i] )/ MuPt[i];

		// the track is identified as a global muon
		// chi2/ndof of the global muon fit < 10
		// number of valid muon-detector hits used in the global fit > 0
		// Number of hits in the tracker track, Nhits, > 10.

		tags[kMuTagIsGlobal] = ( MuIsGlobalMuon[i]==1 );
		tags[kMuTagIsTracker]= ( MuIsTrackerMuon[i]==1 );
		tags[kMuTagNMuHits]  = ( MuNMuHits[i] > _muCut_NMuHist);
		tags[kMuTagNMatches] = ( MuNMatches[i] > _muCut_NMuMatches);
		tags[kMuTagNTkHits]  = ( MuNTkHits[i] > _muCut_NTrackerHits);
		tags[kMuTagNPxHits]  = ( MuNPxHits[i] > _muCut_NPixelHits);
		tags[kMuTagNChi2]    = ( MuNChi2[i] < _muCut_NChi2);
		tags[kMuTagRelPtRes] = ( MuPtE[i]/MuPt[i] < _muCut_relPtRes);
		tags[kMuTagCombIso]  = ( combIso < _muCut_combIsoOverPt );


		// additional soft muon tags
		tags[kMuTagSoftPt] = ( MuPt[i] > _muSoftCut_Pt );
		tags[kMuTagSoftHighPt] = ( MuPt[i] < _muSoftCut_HighPt);
		tags[kMuTagIsTMLastStationAngTight] = ( MuIsTMLastStationAngTight[i]==1 );
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

	Debug(4) << "  - nLepToPair: " << allTags.size() << "   nEl: " << _elTagged.size() <<" " << NEles
			<< "   nMu: " << _muTagged.size() << " " << NMus << std::endl;

	// make all the opposite sign pairs
	std::vector<LepPair> oppChargePairs;

	for( int i(0); i<allTags.size(); ++i)
		for( int j(i+1); j<allTags.size(); ++j) {
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
		(*counts)[kLLBinVertex]++;

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

	for( int i(1); i<llCounts.size()-1; ++i ){
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

	Debug(3) << "Selected Els: "  << _selectedEls.size() << '\n'
			 << "Selected Mus: "  << _selectedMus.size() << std::endl;

}

//_____________________________________________________________________________
void HWWSelectorB::fillCounts( TH1F* h, const std::vector<unsigned int>& counts) {

	if ( counts[kLLBinDilepton] ) h->Fill(kLLBinDilepton);
	if ( counts[kLLBinEtaPt] )    h->Fill(kLLBinEtaPt);
	if ( counts[kLLBinVertex] )	  h->Fill(kLLBinVertex);
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
};

//_____________________________________________________________________________
void HWWSelectorB::assembleNtuple() {
	// clear the ntuple
	_event->Clear();

	// fill the run parameters
	_event->Run          = Run;
	_event->Event        = Event;
	_event->LumiSection  = LumiSection;

    // primary vertexes
	_event->PrimVtxGood  = PrimVtxGood;
	_event->PrimVtxx     = PrimVtxx;
	_event->PrimVtxy     = PrimVtxy;
	_event->PrimVtxz     = PrimVtxz;
	_event->NVrtx        = NVrtx;

	_event->TCMET		 = TCMET;
	_event->TCMETphi	 = TCMETphi;
	_event->PFMET        = PFMET;
	_event->PFMETphi     = PFMETphi;
	_event->SumEt        = SumEt;
	_event->MuCorrMET    = MuCorrMET;
	_event->MuCorrMETphi = MuCorrMETphi;

	_event->HasSoftMus   = _softMus.size() > 0;
	_event->HasBTaggedJets = _btaggedJets.size() > 0;

	_event->NEles        = _selectedEls.size();

	_event->NMus         = _selectedMus.size();

	_event->NJets        = _selectedJets.size();

	_event->PFNJets      = _selectedPFJets.size();

	_event->Els.resize(_event->NEles);
	std::set<unsigned int>::iterator itEl = _selectedEls.begin();
	for( unsigned int i(0); i < _event->NEles ; ++i) {
		unsigned int k = *itEl;
		HWWElectron &e = _event->Els[i];
		e.P.SetXYZT(ElPx[k], ElPy[k], ElPz[k], ElE[k]);
		e.Charge 					= ElCharge[k];
		e.SigmaIetaIeta				= ElSigmaIetaIeta[k];
		e.CaloEnergy 				= ElCaloEnergy[k];
		e.DR03TkSumPt 				= ElDR03TkSumPt[k];
		e.DR04EcalRecHitSumEt		= ElDR04EcalRecHitSumEt[k];
		e.DR04HcalTowerSumEt 		= ElDR04HcalTowerSumEt[k];
		e.NumberOfMissingInnerHits 	= ElNumberOfMissingInnerHits[k];
		e.DeltaPhiSuperClusterAtVtx	= ElDeltaPhiSuperClusterAtVtx[k];
		e.DeltaEtaSuperClusterAtVtx	= ElDeltaEtaSuperClusterAtVtx[k];
		e.D0PV 						= ElD0PV[k];
		e.DzPV 						= ElDzPV[k];

		++itEl;
	}
	if ( itEl != _selectedEls.end() )
		THROW_RUNTIME("Not all electrons were copied?");

	_event->Mus.resize(_event->NMus);
	std::set<unsigned int>::iterator itMu = _selectedMus.begin();
    for( unsigned int i(0); i < _event->NMus; ++i ) {
		unsigned int k = *itMu;
		HWWMuon &u = _event->Mus[i];

		u.P.SetXYZT(MuPx[k], MuPy[k], MuPz[k], MuE[k] );
		u.Charge                   = MuCharge[k];
		u.Iso03SumPt               = MuIso03SumPt[k];
		u.Iso03EmEt                = MuIso03EmEt[k];
		u.Iso03HadEt               = MuIso03HadEt[k];
		u.NMuHits                  = MuNMuHits[k];
		u.NTkHits                  = MuNTkHits[k];
		u.NChi2                    = MuNChi2[k];
		u.IsGlobalMuon             = MuIsGlobalMuon[k];
		u.IsTrackerMuon            = MuIsTrackerMuon[k];
		u.IsTMLastStationAngTight  = MuIsTMLastStationAngTight[k];
		u.D0PV                     = MuD0PV[k];
		u.DzPV                     = MuDzPV[k];

		++itMu;
	}
	if ( itMu != _selectedMus.end() )
		THROW_RUNTIME("Not all muons were copied?");

	_event->Jets.resize(_event->NJets);
	std::set<unsigned int>::iterator itJ = _selectedJets.begin();
	for( int i(0); i <_event->NJets; ++i) {
		int k = *itJ;
		HWWJet& j = _event->Jets[i];

		j.P.SetXYZT( JPx[k], JPy[k], JPz[k], JE[k] );
		j.EMfrac         = JEMfrac[k];
		j.NConstituents  = JNConstituents[k];
		j.ID_HPD         = JID_HPD[k];
		j.ID_RBX         = JID_RBX[k];
		j.ID_n90Hits     = JID_n90Hits[k];
		j.ID_resEMF      = JID_resEMF[k];
		j.ID_HCALTow     = JID_HCALTow[k];
		j.ID_ECALTow     = JID_ECALTow[k];

		++itJ;
	}
	if ( itJ != _selectedJets.end() )
		THROW_RUNTIME("Not all jets were copied?");

	_event->PFJets.resize(_event->PFNJets);
	std::set<unsigned int>::iterator itPFJ = _selectedPFJets.begin();
	for( int i(0); i < _event->PFNJets; ++i) {
		int k = *itPFJ;
		HWWPFJet& pfj = _event->PFJets[i];

		pfj.P.SetXYZT(PFJPx[k], PFJPy[k], PFJPz[k], PFJE[k]);
		pfj.ChHadfrac       = PFJChHadfrac[k];
		pfj.NeuHadfrac      = PFJNeuHadfrac[k];
		pfj.ChEmfrac        = PFJChEmfrac[k];
		pfj.NeuEmfrac       = PFJNeuEmfrac[k];
		pfj.NConstituents   = PFJNConstituents[k];

		++itPFJ;
	}
	if ( itPFJ != _selectedPFJets.end() )
		THROW_RUNTIME("Not all pfJets were copied?");


}

//_____________________________________________________________________________
void HWWSelectorB::cleanJets() {
	// so far so good, let's clean the jets up
	_selectedJets.clear();
	_btaggedJets.clear();
     	// loop on jets
	for ( int i=0; i<NJets; ++i) {

		TVector3 pJet( JPx[i], JPy[i], JPz[i]);
		std::set<unsigned int>::iterator it;

		bool match = false;
		// try to match the jet with an electron
		for( it=_selectedEls.begin();
				it != _selectedEls.end(); ++it) {
			TVector3 pEl(ElPx[*it], ElPy[*it], ElPz[*it]);

			//what is the 0.3 cut?
			match |= ( TMath::Abs(pJet.DeltaR(pEl)) < _jetCut_Dr );

		}

		for( it=_selectedMus.begin();
				it != _selectedMus.end(); ++it) {
			TVector3 pMu(MuPx[*it], MuPy[*it], MuPz[*it]);
			//what is the 0.3 cut?
			match |= ( TMath::Abs(pJet.DeltaR(pMu)) < _jetCut_Dr );
		}

		if ( match ) continue;

		// jet ptcut
		if ( JPt[i] > _jetCut_Pt && JEta[i] < _jetCut_Eta )
			_selectedJets.insert(i);
		// or check for btagged jets
		else if ( JbTagProbTkCntHighEff[i] > _jetCut_BtagProb )
				_btaggedJets.insert(i);


	}

	_selectedPFJets.clear();
	// loop on pf jets now
	for ( int i=0; i<PFNJets; ++i) {


		TVector3 pPFJet( PFJPx[i], PFJPy[i], PFJPz[i]);
		std::set<unsigned int>::iterator it;

		bool match = false;
		// try to match the jet with an electron
		for( it=_selectedEls.begin();
				it != _selectedEls.end(); ++it) {
			TVector3 pEl(ElPx[*it], ElPy[*it], ElPz[*it]);
			//what is the 0.3 cut?
			match |= ( TMath::Abs(pPFJet.DeltaR(pEl)) < _jetCut_Dr );
		}

		for( it=_selectedMus.begin();
				it != _selectedMus.end(); ++it) {
			TVector3 pMu(MuPx[*it], MuPy[*it], MuPz[*it]);

			//what is the 0.3 cut?
			match |= ( TMath::Abs(pPFJet.DeltaR(pMu)) < _jetCut_Dr );
		}

		// jet ptcut
		if ( match || PFJPt[i] < _jetCut_Pt  && PFJEta[i] < _jetCut_Eta ) continue;

		_selectedPFJets.insert(i);
	}

}
