/*JPx[k],
 * HWWSelector.cpp
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#include "HWWSelector.h"
#include <iostream>
#include <stdexcept>
#include <fstream>
#include <sstream>
#include <bitset>
#include <TVector3.h>
#include <TStopwatch.h>
#include <TH1F.h>
#include "Tools.h"

const float HWWSelector::_etaMaxEB=1.4442;
const float HWWSelector::_etaMinEE=1.5660;
const float HWWSelector::_etaMaxEE=2.5000;
const float HWWSelector::_etaMaxMu=2.4000;

//_____________________________________________________________________________
void HWWSelector::WorkingPoint::print() {
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
			<< hits << '\t'
			<< dist << '\t'
			<< cot << '\t'
			<< std::endl;
}

//_____________________________________________________________________________
HWWSelector::HWWSelector( int argc, char** argv ) : ETHZNtupleSelector(argc,argv),
	_elTightWorkingPoint(0), _elLooseWorkingPoint(0), _nSelectedEvents(0), _event(0x0),
	_elTightCounters(0x0), _elLooseCounters(0x0), _muCounters(0x0), _counters(0x0) {
	// TODO Auto-generated constructor stub

	_event = new HWWEvent();
	std::cout <<  fChain->GetName() << "   "<< fChain->GetTree() << std::endl;

	_elTightWorkingPoint = _config.getValue<int>( "HWWSelector.elTightWorkingPoint");
	_elLooseWorkingPoint = _config.getValue<int>( "HWWSelector.elLooseWorkingPoint");
	_leptonPtCut 		 = _config.getValue<float>( "HWWSelector.leptonPtCut");
	_jetPtCut	 		 = _config.getValue<float>( "HWWSelector.jetPtCut");
	_jetDrCut			 = _config.getValue<float>( "HWWSelector.jetDrCut");
	_wpFile				 = _config.getValue<std::string>( "HWWSelector.elWorkingPointFile");
}

//_____________________________________________________________________________
HWWSelector::~HWWSelector() {
	// TODO Auto-generated destructor stub
}

//_____________________________________________________________________________
void HWWSelector::clear() {
	_elLooseCandidates.clear();
	_elTightCandidates.clear();
	_muCandidates.clear();
	_softMuCandidates.clear();

	_elLooseBits.clear();
	_elTightBits.clear();
	_muBits.clear();
}

//_____________________________________________________________________________
void HWWSelector::Book() {
	std::cout << "Adding the selected objects" << std::endl;
	fSkimmedTree->Branch("ev","HWWEvent", &_event);

	std::vector<std::string> labels;

	labels.push_back("no cuts");
	labels.push_back("2 leptons");
	labels.push_back(Form("#eta < %.1f",_etaMaxEE));
	labels.push_back(Form("p_{T} > %.0f GeV", _leptonPtCut));
	labels.push_back("Id");
	labels.push_back("Isolation");
	labels.push_back("Conversion Veto");
	labels.push_back("3rd Lepton Veto");

	_counters = new TH1F("Counters","HWW selection req. n_{lep} > 2",labels.size(),1,labels.size()+1);

	TAxis* ax = _counters->GetXaxis();
	for ( int i = 0; i < labels.size(); ++i){
		ax->SetBinLabel(i+1,labels[i].c_str());
	}

	std::vector<std::string> elLabels, muLabels;

	elLabels.push_back("no cuts");
	elLabels.push_back(Form("#eta < %.1f",_etaMaxEE));
	elLabels.push_back(Form("p_{T} > %.0f GeV", _leptonPtCut));
	elLabels.push_back("Isolation");
	elLabels.push_back("Identification");
	elLabels.push_back("Conversion Veto");

	_elTightCounters = new TH1F("ElTightCounters","Tight electrons counters",elLabels.size(),1,elLabels.size()+1);
	_elLooseCounters = new TH1F("ElLooseCounters","Loose electrons counters",elLabels.size(),1,elLabels.size()+1);

	TAxis* axTight = _elTightCounters->GetXaxis();
	TAxis* axLoose = _elLooseCounters->GetXaxis();
	for ( int i = 0; i < elLabels.size(); ++i){
			axTight->SetBinLabel(i+1,elLabels[i].c_str());
			axLoose->SetBinLabel(i+1,elLabels[i].c_str());
		}

	muLabels.push_back("no cuts");
	muLabels.push_back(Form("#eta < %.1f",_etaMaxEE));
	muLabels.push_back(Form("p_{T} > %.0f GeV", _leptonPtCut));
	muLabels.push_back("Isolation");
	muLabels.push_back("Identification");

	_muCounters = new TH1F("MuCounters","Muon counters",muLabels.size(),1,muLabels.size()+1);
	TAxis* axMus = _muCounters->GetXaxis();
	for ( int i = 0; i < muLabels.size(); ++i){
		axMus->SetBinLabel(i+1,muLabels[i].c_str());
	}

}

//_____________________________________________________________________________
void HWWSelector::BeginJob() {

	readWorkingPoints( _wpFile );
	// attach the entuple to the tree

}
//_____________________________________________________________________________
void HWWSelector::EndJob() {
	std::cout << "--- Job completed " << _nEvents << " processed " << _nSelectedEvents << " selected"<< std::endl;
}

//_____________________________________________________________________________
void HWWSelector::Process( Long64_t iEvent ) {


	GetEntry(iEvent);

	// make sure the previous event is cleared
	clear();

	if ( !selectAndClean() ) return;
	assembleNtuple();

	fSkimmedTree->Fill();
	++_nSelectedEvents;

//	_counters->SetBinContent(1,fChain->GetEntriesFast());
//	_counters->SetBinContent(kSelected,_nSelectedEvents);
}


//_____________________________________________________________________________
bool HWWSelector::selectAndClean() {
	//
	// loop over electrons and mus.
	// proceed only if there are 2 leptons (both tight and loose)

	// ok, if there are not even 2 leptons we don't bother
	//if ( NEles + NMus < 2 ) return false;
	// select good electrons
	tagElectrons();

	// select good mus
	tagMuons();

	count();

	std::cout << '(' << NEles << ',' << NMus << '|' << _elTightCandidates.size() << ',' << _elLooseCandidates.size() << ',' <<  _muCandidates.size()
			<< '|'  << _elTightCandidates.size()+_muCandidates.size() << ',' << _elLooseCandidates.size()+_muCandidates.size()
			<< '|'<< _softMuCandidates.size() <<')' << std::endl;

	// accept only events with 2 good candidates and only 2 loose candidates
	if ( (_elTightCandidates.size()+_muCandidates.size()) != 2 ||
			(_elLooseCandidates.size()+_muCandidates.size()) != 2 ) {
		// 3rd lepton veto
		return false;
	}

	// then clean the jets up
	cleanJets();
	return true;
}
//_____________________________________________________________________________
void HWWSelector::tagElectrons() {
	_elTightCandidates.clear();
	_elLooseCandidates.clear();

	// loop over electrons
	// start from the highest pt
	for(unsigned int i=0; i<NEles; ++i) {

		elBitSet word, ptEtaWord, idWord;
		// reject electrons with eta>2.5
		ptEtaWord.set(kElEta,TMath::Abs( ElEta[i] ) < _etaMaxEE);

		if ( !ptEtaWord[kElEta] ) {
			// add the word to both the loose and tight selection for book keeping purposes
			_elTightBits.push_back( std::make_pair(i,ptEtaWord) );
			_elLooseBits.push_back( std::make_pair(i,ptEtaWord) );
			continue;
		}

		// drop electrons with pT < _leptonPtCut
		ptEtaWord.set(kElPt, ElPt[i] > _leptonPtCut);
		//		std::cout << "elPt[" << i << "] = " << ElPt[i] << "   " <<	_leptonPtCut << std::endl;

		idWord =  electronID(_elTightWorkingPoint, i);
		word = ptEtaWord | idWord;
		_elTightBits.push_back(std::make_pair(i, word) );

		idWord = electronID(_elLooseWorkingPoint, i);
		word = ptEtaWord | idWord;
		_elLooseBits.push_back(std::make_pair(i,word));
	}

	if ( _elTightBits.size() != NEles || _elLooseBits.size() != NEles )
		THROW_RUNTIME("Something's wrong, because NEles = "<< NEles << " - Ntight = " << _elTightBits.size() << " - Nloose = " << _elLooseBits.size() );

}
//_____________________________________________________________________________
void HWWSelector::tagMuons() {
	// muon id cuts
	// isolation = (MuIso03SumPt[i] + MuIso03EmEt[i] + MuIso03HadEt[i] ) / MuPt[i] < 0.15
	// isGlobalMu
	// MuNChi2[i] < 10
	// MuNMuHits[i] > 0
	// MuNTkHits[i] > 10

	_muCandidates.clear();
	// loop on mus
	for (int i=0; i<NMus; ++i) {
		// reject mus with eta > _etaMaxMu
		// and pT < 10 GeV

		muBitSet word;

		word.set( kMuEta, TMath::Abs( MuEta[i] ) < _etaMaxEE);

		// drop mus with pT < _leptonPtCut
		word.set( kMuPt, MuPt[i] > _leptonPtCut );

		// isolation, where does it come from?
		double isolation  = (MuIso03SumPt[i] + MuIso03EmEt[i] + MuIso03HadEt[i] ) / MuPt[i];
		word.set( kMuIso, isolation < 0.15 );

		// the track is identified as a global muon
		// chi2/ndof of the global muon fit < 10
		// number of valid muon-detector hits used in the global fit > 0
		// Number of hits in the tracker track, Nhits, > 10.

		word.set( kMuIsGlobal, MuIsGlobalMuon[i]==1 );
		word.set( kMuNChi2, MuNChi2[i] < 10);
		word.set( kMuNMuHits, MuNMuHits[i] > 0);
		word.set( kMuNTkHits, MuNTkHits[i] > 10);

		word.set( kMuSoftPt, MuPt[i] > 3 );
		word.set( kMuIsTracker, MuIsTrackerMuon[i]==1 );
		word.set( kMuIsTMLastStationAngTight, MuIsTMLastStationAngTight[i]==1 );
		word.set( kMuD0PV, TMath::Abs(MuD0PV[i]) < 0.2);

		bool id = ( word[kMuIsGlobal] &&
					word[kMuNChi2] &&
					word[kMuNMuHits] &&
					word[kMuNTkHits] );

		word.set(kMuId,id);

		bool soft = ( word[kMuEta] &&
				word[kMuSoftPt] && !word[kMuPt] &&
				word[kMuIsTracker] &&
				word[kMuIsTMLastStationAngTight] &&
				word[kMuNTkHits] &&
				word[kMuD0PV] );

		word.set( kMuSoft, soft );

		//TODO: Soft muon check?

		_muBits.push_back(std::make_pair(i,word));
	}
}

//_____________________________________________________________________________
void HWWSelector::count() {

	std::vector<unsigned int> cT = countElectrons(_elTightBits, _elTightCandidates);
	std::vector<unsigned int> cL = countElectrons(_elLooseBits, _elLooseCandidates);

	for ( int i(0); i<cT.size(); ++i) {
		_elTightCounters->Fill(i+1,cT[i]);
		_elLooseCounters->Fill(i+1,cL[i]);
	}

	std::vector<unsigned int> cMu = countMuons(_muBits, _muCandidates);
	for ( int i(0); i<cMu.size(); ++i)
		_muCounters->Fill(i+1,cMu[i]);

	std::vector<unsigned int> cSoftMu = countSoftMuons(_muBits, _softMuCandidates);

	// all events/no cuts
	_counters->Fill(1);

	// just 2 leptons
	if ( cT[0]+cMu[0] >= 2 ) _counters->Fill(2);

	// 2 leptons with eta < 2.5
	if ( cT[1]+cMu[1] >= 2 ) _counters->Fill(3);

	// 2 leptons with pT > leptonCut
	if ( cT[2]+cMu[2] >= 2 ) _counters->Fill(4);

	// 2 leptons identified
	if ( cT[3]+cMu[3] >= 2 ) _counters->Fill(5);

	// 2 leptons isolated
	if ( cT[4]+cMu[4] >= 2 ) _counters->Fill(6);

	// conversion veto
	if ( cT[5]+cMu[4] >= 2 ) _counters->Fill(7);

	// 3rd lepton veto
	if ( cT[5]+cMu[4] == 2 && cL[5]+cMu[4] == 2) _counters->Fill(8);
}

//_____________________________________________________________________________
std::vector<unsigned int> HWWSelector::countElectrons( const wordVector& bits, std::vector<unsigned int>& candidates) {
	// Counts the electron candidates and stores the indexes in the candidates vector.
	//

	std::vector< std::pair<unsigned int, elBitSet> >::const_iterator iEl;
	std::vector<unsigned int> c(6,0);
	for ( iEl = bits.begin(); iEl != bits.end(); ++iEl ) {

		const elBitSet& wEl = iEl->second;
		++c[0];

		if ( wEl.test(kElEta) )	++c[1]; else continue;

		if ( wEl.test(kElPt) ) 	++c[2]; else continue;

		if ( wEl.test(kElId) ) 	++c[3]; else continue;

		if ( wEl.test(kElIso) ) ++c[4]; else continue;

		if ( wEl.test(kElNoConv) ) ++c[5]; else continue;

		candidates.push_back(iEl->first);
	}

	return c;
}

//_____________________________________________________________________________
std::vector<unsigned int> HWWSelector::countMuons( const wordVector& bits, std::vector<unsigned int>& candidates) {
	wordVector::const_iterator iMu;
	std::vector<unsigned int> c(5,0);
	for ( iMu = bits.begin(); iMu != bits.end(); ++iMu ) {

		const muBitSet& wMu = iMu->second;
		++c[0];

		if ( wMu.test(kMuEta) ) ++c[1]; else continue;

		if ( wMu.test(kMuPt) )  ++c[2]; else continue;

		if ( wMu.test(kMuIso) ) ++c[3]; else continue;

		if ( wMu.test(kMuId) )  ++c[4]; else continue;

		candidates.push_back(iMu->first);
	}
	return c;
}

//_____________________________________________________________________________
std::vector<unsigned int> HWWSelector::countSoftMuons( const wordVector& bits, std::vector<unsigned int>& candidates ) {
	wordVector::const_iterator iMu;
	std::vector<unsigned int> c(3,0);
	for ( iMu = bits.begin(); iMu != bits.end(); ++iMu ) {
		const muBitSet& wMu = iMu->second;
		++c[0];

		if ( wMu.test(kMuEta) ) ++c[1]; else continue;

		if ( wMu.test(kMuSoft) ) ++c[2]; else continue;

		candidates.push_back(iMu->first);
	}

	return c;
}

//_____________________________________________________________________________
void HWWSelector::cleanJets() {
	// so far so good, let's clean the jets up
	_jetCandidates.clear();
	// loop on jets
	for ( int i=0; i<NJets; ++i) {

		// jet ptcut
		if ( JPt[i] < _jetPtCut ) continue;

		TVector3 pJet( JPx[i], JPy[i], JPz[i]);
		std::vector<unsigned int>::iterator it;

		bool match = false;
		// try to match the jet with an electron
		for( it=_elTightCandidates.begin();
				it != _elTightCandidates.end(); ++it) {
			TVector3 pEl(ElPx[*it], ElPy[*it], ElPz[*it]);

			//what is the 0.3 cut?
			match &= ( TMath::Abs(pJet.DeltaR(pEl)) < _jetDrCut );

		}

		for( it=_muCandidates.begin();
				it != _muCandidates.end(); ++it) {
			TVector3 pMu(MuPx[*it], MuPy[*it], MuPz[*it]);
			//what is the 0.3 cut?
			match &= ( TMath::Abs(pJet.DeltaR(pMu)) < 0.3 );
		}

		if ( !match ) _jetCandidates.push_back(i);
	}

	_pfJetCandidates.clear();
	// loop on pf jets now
	for ( int i=0; i<PFNJets; ++i) {

		// jet ptcut
		if ( PFJPt[i] < _jetPtCut ) continue;

		TVector3 pPFJet( PFJPx[i], PFJPy[i], PFJPz[i]);
		std::vector<unsigned int>::iterator it;

		bool match = false;
		// try to match the jet with an electron
		for( it=_elTightCandidates.begin();
				it != _elTightCandidates.end(); ++it) {
			TVector3 pEl(ElPx[*it], ElPy[*it], ElPz[*it]);
			//what is the 0.3 cut?
			match &= ( TMath::Abs(pPFJet.DeltaR(pEl)) < _jetDrCut );
		}

		for( it=_muCandidates.begin();
				it != _muCandidates.end(); ++it) {
			TVector3 pMu(MuPx[*it], MuPy[*it], MuPz[*it]);

			//what is the 0.3 cut?
			match &= ( TMath::Abs(pPFJet.DeltaR(pMu)) < 0.3 );
		}

		if ( !match ) _pfJetCandidates.push_back(i);
	}

}

//_____________________________________________________________________________
void HWWSelector::readWorkingPoints( const std::string& path ) {

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

		ss >> p.efficiency >> p.See >> p.dPhi >> p.dEta>>p.HoE >> p.tkIso >> p.ecalIso >> p.hcalIso >> p.combIso>> p.hits>> p.dist>> p.cot;

		p.print();

		_elWorkingPoints.push_back(p);
	}
}

//_____________________________________________________________________________
HWWSelector::WorkingPoint HWWSelector::getWorkingPoint(unsigned short part, int eff) {
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
HWWSelector::elBitSet HWWSelector::electronID( int eff, int i ) {
	// identify tight electron
	// requires
	// ElSCEta
	// ElDeltaPhiSuperClusterAtVtx
	// ElDeltaEtaSuperClusterAtVtx
	// ElSigmaIetaIeta
	// ElHcalOverEcal
	// ElDR03TkSumPt
	// ElDR03EcalRecHitSumEt
	// ElDR03HcalTowerSumEt
	// ElConvPartnerTrkDist
	// ElConvPartnerTrkDCot
	// ElNumberOfMissingInnerHits

	float eta = ElSCEta[i];

	// apply the correction for the endcaps
	float dPhi = ElDeltaPhiSuperClusterAtVtx[i];
	float dEta = ElDeltaEtaSuperClusterAtVtx[i];

	float See  = ElSigmaIetaIeta[i];
	float HoE  = ElHcalOverEcal[i];
	float trkIso  = ElDR03TkSumPt[i];
	float ecalIso = ElDR03EcalRecHitSumEt[i];
	float hcalIso = ElDR03HcalTowerSumEt[i];
	float combIso_B = (trkIso + TMath::Max(0., ecalIso - 1.) + hcalIso) / ElPt[i];
	float combIso_E = (trkIso + ecalIso + hcalIso) / ElPt[i];
	float combIso = 0;

	unsigned short p;
	if ( TMath::Abs(eta) <= _etaMaxEB ) {
		// barrel
		p = kBarrel;
		combIso = combIso_B;
	} else if ( TMath::Abs(eta) >= _etaMinEE ) {
		p = kEndcap;
		combIso = combIso_E;
	} else {
		//std::cout << "Candidate out of acceptance region" << std::endl;
		//return kOutOfAcc;
		return false;
	}

	WorkingPoint wp = getWorkingPoint(p, eff );

	elBitSet word;
    // conversion
	word.set(kElDist,TMath::Abs(ElConvPartnerTrkDist[i]) < wp.dist);
	word.set(kElCot, TMath::Abs(ElConvPartnerTrkDCot[i]) < wp.cot);
	word.set(kElHits,ElNumberOfMissingInnerHits[i] > wp.hits);

	word.set(kElSee, See < wp.See);
	word.set(kElDphi, TMath::Abs(dPhi) < wp.dPhi);
	word.set(kElDeta, TMath::Abs(dEta) < wp.dEta);
	word.set(kElHoE, HoE  < wp.HoE);
	word.set(kElCombIso, combIso < wp.combIso);
	//std::cout << "elIdWord[" << i << "," << eta << ","<< ElPt[i] << "]: [" << wp.See << "][" << elIdWord.to_string() << "] See: " << See << ", dPhi: "<< dPhi << ", dEta: " << dEta << ", HoE: " << HoE << ", Comb: " << combIso << std::endl;

	word[kElNoConv] = !(( word[kElDist] && word[kElCot] ) || word[kElHits]);
	word[kElIso] = word[kElCombIso];
	word[kElId] = word[kElSee] && word[kElDphi] && word[kElDeta] && word[kElHoE];

	return word;


}

//_____________________________________________________________________________
void HWWSelector::assembleNtuple() {
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

	_event->PFMET        = PFMET;
	_event->PFMETphi     = PFMETphi;
	_event->SumEt        = SumEt;
	_event->MuCorrMET    = MuCorrMET;
	_event->MuCorrMETphi = MuCorrMETphi;

	_event->NEles        = NEles;
	_event->NMus         = NMus;
	_event->NJets        = NJets;
	_event->PFNJets      = PFNJets;

	_event->HasSoftMus   = _softMuCandidates.size() > 0;

	_event->NEles        = _elTightCandidates.size();

	_event->NMus         = _muCandidates.size();

	_event->NJets        = _jetCandidates.size();

	_event->PFNJets      = _pfJetCandidates.size();

	for( int i(0); i < _event->NEles ; ++i) {
		int k = _elTightCandidates[i];
		_event->Els.resize(i+1);
		HWWElectron &e = _event->Els[i];
		e.ElP.SetXYZT(ElPx[k], ElPy[k], ElPz[k], ElE[k]);
		e.ElCharge 						= ElCharge[k];
		e.ElSigmaIetaIeta				= ElSigmaIetaIeta[k];
		e.ElCaloEnergy 					= ElCaloEnergy[k];
		e.ElDR03TkSumPt 				= ElDR03TkSumPt[k];
		e.ElDR04EcalRecHitSumEt			= ElDR04EcalRecHitSumEt[k];
		e.ElDR04HcalTowerSumEt 			= ElDR04HcalTowerSumEt[k];
		e.ElNumberOfMissingInnerHits 	= ElNumberOfMissingInnerHits[k];
		e.ElDeltaPhiSuperClusterAtVtx	= ElDeltaPhiSuperClusterAtVtx[k];
		e.ElDeltaEtaSuperClusterAtVtx	= ElDeltaEtaSuperClusterAtVtx[k];
		e.ElD0PV 						= ElD0PV[k];
		e.ElDzPV 						= ElDzPV[k];

//		std::cout << e.ElP.Eta()-ElEta[k] << std::endl;
	}

	for( int i(0); i < _event->NMus; ++i ) {
		int k = _muCandidates[i];
		_event->Mus.resize(i+1);
		HWWMuon &u = _event->Mus[i];

		u.MuP.SetXYZT(MuPx[k], MuPy[k], MuPz[k], MuE[k] );
		u.MuCharge                   = MuCharge[k];
		u.MuIso03SumPt               = MuIso03SumPt[k];
		u.MuIso03EmEt                = MuIso03EmEt[k];
		u.MuIso03HadEt               = MuIso03HadEt[k];
		u.MuNMuHits                  = MuNMuHits[k];
		u.MuNTkHits                  = MuNTkHits[k];
		u.MuNChi2                    = MuNChi2[k];
		u.MuIsGlobalMuon             = MuIsGlobalMuon[k];
		u.MuIsTrackerMuon            = MuIsTrackerMuon[k];
		u.MuIsTMLastStationAngTight  = MuIsTMLastStationAngTight[k];
		u.MuD0PV                     = MuD0PV[k];
		u.MuDzPV                     = MuDzPV[k];
	}

	for( int i(0); i <_event->NJets; ++i) {
		int k = _jetCandidates[i];
		_event->Jets.resize(i+1);
		HWWJet& j = _event->Jets[i];

		j.JP.SetXYZT( JPx[k], JPy[k], JPz[k], JE[k] );
		j.JEMfrac         = JEMfrac[k];
		j.JNConstituents  = JNConstituents[k];
		j.JID_HPD         = JID_HPD[k];
		j.JID_RBX         = JID_RBX[k];
		j.JID_n90Hits     = JID_n90Hits[k];
		j.JID_resEMF      = JID_resEMF[k];
		j.JID_HCALTow     = JID_HCALTow[k];
		j.JID_ECALTow     = JID_ECALTow[k];
	}

	_event->PFNJets = _pfJetCandidates.size();
	for( int i(0); i < _event->PFNJets; ++i) {
		int k = _pfJetCandidates[i];

		_event->PFJets.resize(i+1);
		HWWPFJet& pfj = _event->PFJets[i];

		pfj.PFJP.SetXYZT(PFJPx[k], PFJPy[k], PFJPz[k], PFJE[k]);
		pfj.PFJChHadfrac       = PFJChHadfrac[k];
		pfj.PFJNeuHadfrac      = PFJNeuHadfrac[k];
		pfj.PFJChEmfrac        = PFJChEmfrac[k];
		pfj.PFJNeuEmfrac       = PFJNeuEmfrac[k];
		pfj.PFJNConstituents   = PFJNConstituents[k];
	}

}
