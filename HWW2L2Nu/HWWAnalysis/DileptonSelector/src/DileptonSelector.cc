// -*- C++ -*-
//
// Package:    DileptonSelector
// Class:      DileptonSelector
// 

#include <HWWAnalysis/DileptonSelector/interface/DileptonSelector.h>
#include <HWWAnalysis/DileptonSelector/interface/HWWCandidates.h>
#include <HWWAnalysis/DileptonSelector/interface/EventProxy.h>
#include <HWWAnalysis/DileptonSelector/interface/Tools.h>
#include <CommonTools/UtilAlgos/interface/TFileService.h>
#include <DataFormats/PatCandidates/interface/Electron.h>
#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/VertexReco/interface/Vertex.h>
#include <FWCore/ServiceRegistry/interface/Service.h>
#include <SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h>
#include <vector>
#include <fstream>

const double DileptonSelector::_etaMaxEB=1.4442;
const double DileptonSelector::_etaMinEE=1.5660;
const double DileptonSelector::_etaMaxEE=2.5000;
const double DileptonSelector::_etaMaxMu=2.4000;


//_____________________________________________________________________________
void DileptonSelector::WorkingPoint::print() {
    char p(0);
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
//         << tkIso << '\t'
//         << ecalIso << '\t'
//         << hcalIso << '\t'
        << combIso << '\t'
        << missHits << '\t'
        << dist << '\t'
        << cot << '\t'
        << std::endl;
}

//
// constructors and destructor
//
DileptonSelector::DileptonSelector(const edm::ParameterSet& iConfig) : _nEvents(0), _nSelectedEvents(0),
    _tree(0x0), _diLepEvent(0x0)
{
    //now do what ever initialization is needed
    // configuration
    _debugLvl = iConfig.getUntrackedParameter<int>("debugLevel");
    _wpFile = iConfig.getUntrackedParameter<std::string>("elWorkingPointsFile");
    _puFactors = iConfig.getParameter<std::vector<double> >("pileupFactors");

    const edm::ParameterSet& vrtxCuts = iConfig.getParameterSet("vrtxCuts");
    _vrtxCut_nDof = vrtxCuts.getParameter<double>("nDof"); // 4.
    _vrtxCut_rho  = vrtxCuts.getParameter<double>("rho"); // 2.
    _vrtxCut_z    = vrtxCuts.getParameter<double>("z"); // 24.


    const edm::ParameterSet& lepCuts = iConfig.getParameterSet("lepCuts");
    _lepCut_leadingPt   = lepCuts.getParameter<double>("leadingPt");
    _lepCut_trailingPt  = lepCuts.getParameter<double>("trailingPt");
    _lepCut_D0PV        = lepCuts.getParameter<double>("d0PrimaryVertex");
    _lepCut_DzPV        = lepCuts.getParameter<double>("dZPrimaryVertex") ;

    const edm::ParameterSet& elCuts = iConfig.getParameterSet("elCuts");
    _elCut_TightWorkingPoint = elCuts.getParameter<int>( "tightWorkingPoint");
    _elCut_LooseWorkingPoint = elCuts.getParameter<int>( "looseWorkingPoint");
    _elCut_EtaSCEbEe         = elCuts.getParameter<double>("etaSCEbEe"); // 1.479

    const edm::ParameterSet& muCuts = iConfig.getParameterSet("muCuts");
    _muCut_NMuHist		 = muCuts.getParameter<int>("nMuHits");
    _muCut_NMuMatches	 = muCuts.getParameter<int>("nMuMatches");
    _muCut_NTrackerHits	 = muCuts.getParameter<int>("nTrackerHits");
    _muCut_NPixelHits	 = muCuts.getParameter<int>("nPixelHits");
    _muCut_NChi2		 = muCuts.getParameter<double>("nChi2");
    _muCut_relPtRes		 = muCuts.getParameter<double>("relPtResolution");
    _muCut_combIsoOverPt = muCuts.getParameter<double>("combIso");

    const edm::ParameterSet& muSoftCuts = iConfig.getParameterSet("muSoftCuts");
    _muSoftCut_Pt		= muSoftCuts.getParameter<double>("Pt");
    _muSoftCut_HighPt	= muSoftCuts.getParameter<double>("HighPt");
    _muSoftCut_NotIso	= muSoftCuts.getParameter<double>("NotIso");

    const edm::ParameterSet& jetCuts = iConfig.getParameterSet("jetCuts");
    _jetCut_Pt	    	= jetCuts.getParameter<double>("Pt");
    _jetCut_Dr	    	= jetCuts.getParameter<double>("Dr");
    _jetCut_Eta	    	= jetCuts.getParameter<double>("Eta");
    _jetCut_BtagProb	= jetCuts.getParameter<double>("BtagProb");

    Debug(0) << "- lepCuts " << lepCuts.toString() << std::endl;
    Debug(0) << "- elCuts " << elCuts.toString() << std::endl;
    Debug(0) << "- muCuts " << muCuts.toString() << std::endl;
    Debug(0) << "- softMuCuts " << muSoftCuts.toString() << std::endl;
    Debug(0) << "- jetCuts " << jetCuts.toString() << std::endl;

    const edm::ParameterSet& hltPaths = iConfig.getParameterSet("hltPaths");
    std::vector<std::string> elhlt = hltPaths.getParameter<std::vector<std::string> >("el"); 
    std::vector<std::string> muhlt = hltPaths.getParameter<std::vector<std::string> >("mu"); 

    loadWorkingPoints( iConfig.getParameter<edm::VParameterSet>("elWorkingPoints") );
    book();

    // tmp check
//     _debugFile.open("debugDilepton.txt");
}


DileptonSelector::~DileptonSelector()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
DileptonSelector::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;



    //    _nEvents++;
    EventProxy proxy(iEvent, iSetup);
    _eventProxy = &proxy;

    Debug(3) << "--"<< iEvent.id().event() << "-----------------------------------------------" << std::endl;
    // make sure the previous event is cleared
    clear();

    // pileup info and set eventWeights
    checkPileUp( iEvent );

    _nEvents += _eventWeight;

    if ( !selectAndClean() ) return;
    assembleEvent();

//     _nSelectedEvents++;
    _nSelectedEvents += _eventWeight;
    _tree->Fill();

    _eventProxy = 0x0;
}



// ------------ method called once each job just before starting event loop  ------------
void 
DileptonSelector::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
DileptonSelector::endJob() 
{

	_llCounters->SetEntries(_llCounters->GetBinContent(1));
	_eeCounters->SetEntries(_eeCounters->GetBinContent(1));
	_emCounters->SetEntries(_emCounters->GetBinContent(1));
	_meCounters->SetEntries(_meCounters->GetBinContent(1));
	_mmCounters->SetEntries(_mmCounters->GetBinContent(1));


	Debug(0) << "--- Job completed " << _nEvents << " processed " << _nSelectedEvents << " selected"<< std::endl;

	// add the number of processed events
	_hEntries->Fill("processedEntries",(double)_nEvents);
	_hEntries->Fill("selectedEntries",(double)_nSelectedEvents);

    // tmp
//     _debugFile.close();
}

// ------------ method called when starting to processes a run  ------------
void 
DileptonSelector::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
DileptonSelector::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
DileptonSelector::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
DileptonSelector::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
DileptonSelector::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//______________________________________________________________________________
void
DileptonSelector::checkPileUp( const edm::Event& iEvent ) {
    bool found = false;
    try {
        edm::Handle<std::vector<PileupSummaryInfo> > puInfo;
        iEvent.getByLabel("addPileupInfo", puInfo);

        std::vector<PileupSummaryInfo>::const_iterator puIt;
        // search for in-time pu and to the weight
        for(puIt = puInfo->begin(); puIt != puInfo->end(); ++puIt) {

            //        std::cout << " Pileup Information: bunchXing, nvtx: " << puIt->getBunchCrossing() << " " << puIt->getPU_NumInteractions() << std::endl;
            // in time pu
            if ( puIt->getBunchCrossing() == 0 ) {
                if ( (size_t)puIt->getPU_NumInteractions() > _puFactors.size() )
                    THROW_RUNTIME("Simulated Pu [" << puIt->getPU_NumInteractions() <<"] larger than available puFactors");
                _eventWeight = _puFactors[ puIt->getPU_NumInteractions() ];
                _puNInteractions->Fill( puIt->getPU_NumInteractions(), _eventWeight );
                _puNInteractionsUnweighted->Fill( puIt->getPU_NumInteractions() );
                found = true;
                break;
            } 
        }

    } catch ( cms::Exception &e ) {
        std::cout << "Pu not found: DATA!" << std::endl;
        _eventWeight = 1;
    }

    if ( !found ) THROW_RUNTIME(
            "Event " <<  getEvent()->getEvent() << " didn't find the in time pileup info"
            );

    // fill some additional histograms
    _puNVertexes->Fill( getEvent()->getNVrtx(), _eventWeight );
}


//______________________________________________________________________________
void
DileptonSelector::loadWorkingPoints( const std::vector<edm::ParameterSet>& points ) {

	Debug(0) << "Reading Working points " << std::endl;

    std::vector<edm::ParameterSet>::const_iterator iP;
    for( iP = points.begin(); iP != points.end(); ++iP ) {
        std::string dummy = iP->getParameter<std::string>("partition");

		if ( dummy.length() != 1 )
			THROW_RUNTIME("Corrupted working point: " + dummy + " is supposed to be 1 char long.");

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
			THROW_RUNTIME("Corrupted entry\n" << iP->dump());
		}

        p.efficiency = iP->getParameter<double>("eff");
        p.See        = iP->getParameter<double>("see");
        p.dPhi       = iP->getParameter<double>("dphi");
        p.dEta       = iP->getParameter<double>("deta");
        p.HoE        = iP->getParameter<double>("hoe");
//         p.tkIso      = iP->getParameter<double>("tkIso");
//         p.ecalIso    = iP->getParameter<double>("ecalIso");
//         p.hcalIso    = iP->getParameter<double>("hcalIso");
        p.combIso    = iP->getParameter<double>("combIso");
        p.missHits   = iP->getParameter<double>("hits");
        p.dist       = iP->getParameter<double>("dist");
        p.cot        = iP->getParameter<double>("cot");

		p.print();

		_elWorkingPoints.push_back(p);
    }

    
}

// ----------- code shared starts here

// ----------- FIXME limited changes from the standalone version
//_____________________________________________________________________________
void DileptonSelector::book() {

	Debug(0) << "Adding the selected objects" << std::endl;
    edm::Service<TFileService> fs;
    TFileDirectory* here = fs.operator->();
    _tree = fs->make<TTree>("hwwSkim","skim");
    _tree->Branch("ev","HWWEvent", &_diLepEvent);
    
	std::map<int,std::string> entriesLabels;
	entriesLabels[0] = "processedEntries";
	entriesLabels[1] = "selectedEntries";
	_hEntries = makeLabelHistogram(here,"entries","HWWS selection entries",entriesLabels);


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

	_llCounters = makeLabelHistogram(here,"llCounters","HWW selection",labels);
	_eeCounters = makeLabelHistogram(here,"eeCounters","HWW selection - ee",labels);
	_emCounters = makeLabelHistogram(here,"emCounters","HWW selection - em",labels);
	_meCounters = makeLabelHistogram(here,"meCounters","HWW selection - me",labels);
	_mmCounters = makeLabelHistogram(here,"mmCounters","HWW selection - mm",labels);

	std::map<int,std::string> ctrlLabels;
	ctrlLabels[kLepTagAll]		 = "All";
	ctrlLabels[kLepTagEta]       = "Eta";
	ctrlLabels[kLepTagPt]        = "Pt";
	ctrlLabels[kLepTagD0]        = "d0";
	ctrlLabels[kLepTagDz]        = "dz";
	ctrlLabels[kLepTagIsolation] = "Iso";
	ctrlLabels[kLepTagId]        = "Id";
	ctrlLabels[kLepTagNoConv]    = "Conversion Veto";


    TFileDirectory sldir = fs->mkdir("singleLepton");

	_elTightCtrl = makeLabelHistogram(&sldir, "elTightCtrl","Tight electrons",ctrlLabels);
	_elLooseCtrl = makeLabelHistogram(&sldir, "elLooseCtrl","Loose (extra) electrons",ctrlLabels);
	_muGoodCtrl  = makeLabelHistogram(&sldir, "muGoodCtrl" ,"Good muons",ctrlLabels);
	_muExtraCtrl = makeLabelHistogram(&sldir, "muExtraCtrl","Extra muons",ctrlLabels);


    TFileDirectory puDir = fs->mkdir("puInfo");
    unsigned int maxPu = 30;
    _puNInteractions           = puDir.make<TH1F>("nPuInterations","# interactions",maxPu,0,maxPu);
    _puNInteractionsUnweighted = puDir.make<TH1F>("nPuInterationsUnweighted","# interactions",maxPu,0,maxPu);
    _puNVertexes               = puDir.make<TH1F>("nVertexes","# vertex",maxPu,0,maxPu);

    TFileDirectory elVarsDir = fs->mkdir("electronVars");
    makeElectronHistograms( &elVarsDir, _electronHistograms);
    TFileDirectory muVarsDir = fs->mkdir("muonVars");
    TFileDirectory jetVarsDir = fs->mkdir("jetsVars");

    _jetBTagProbTkCntHighEff = jetVarsDir.make<TH1F>("jetBTagProbTkCntHighEff","B-tag prob above jet cut",100,0, 10);



}


//______________________________________________________________________________
void DileptonSelector::makeElectronHistograms( TFileDirectory* fd, std::vector<TH1F*>& histograms ) {

    histograms.assign(kElCutsSize,0x0);


    histograms[kElPt]       = fd->make<TH1F>("pt",     "p_{T}",200, 0, 200);
    histograms[kElEta]      = fd->make<TH1F>("eta",    "#eta",100, 0, 5);
    histograms[kElD0]       = fd->make<TH1F>("d0",     "d0", 100,-0.05,0.05);
    histograms[kElDz]       = fd->make<TH1F>("dz",     "dz", 100,-2,2);
    histograms[kElSee]      = fd->make<TH1F>("see",    "Sigma #eta#eta",100, 0, 0.1);
    histograms[kElDeta]     = fd->make<TH1F>("dEta",   "#Delta#eta",100, 0, 0.2);
    histograms[kElDphi]     = fd->make<TH1F>("dPhi",   "#Delta#phi",100, -0.02, 0.02);
    histograms[kElCombIso]  = fd->make<TH1F>("combIso","Combined relative iso",100, 0, 2);
}

//_____________________________________________________________________________
TH1F* DileptonSelector::makeLabelHistogram( TFileDirectory* fd, const std::string& name, const std::string& title, std::map<int,std::string> labels) {
	int xmin = labels.begin()->first;
	int xmax = labels.begin()->first;

	std::map<int, std::string>::iterator it;
	for( it = labels.begin(); it != labels.end(); ++it ) {
		xmin = it->first < xmin ? it->first : xmin;
		xmax = it->first > xmax ? it->first : xmax;
	}

	++xmax;
	int nbins = xmax-xmin;

	TH1F* h = fd->make<TH1F>(name.c_str(), title.c_str(), nbins, xmin, xmax);
	for( it = labels.begin(); it != labels.end(); ++it ) {
		int bin = h->GetXaxis()->FindBin(it->first);
		h->GetXaxis()->SetBinLabel(bin, it->second.c_str());
	}

	return h;

}


// FIXME basically no changes from here on
//_____________________________________________________________________________
std::ostream& DileptonSelector::Debug(int level) {
	static std::ostream rc(std::clog.rdbuf());
	rc.rdbuf(level <= _debugLvl ? std::clog.rdbuf() : 0);
	return rc;
}


//_____________________________________________________________________________
void DileptonSelector::readWorkingPoints( const std::string& path ) {

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

//         ss >> p.efficiency >> p.See >> p.dPhi >> p.dEta>>p.HoE >> p.tkIso >> p.ecalIso >> p.hcalIso >> p.combIso>> p.missHits>> p.dist>> p.cot;
		ss >> 
            p.efficiency >> 
            p.See >> 
            p.dPhi >> 
            p.dEta>>
            p.HoE >> 
//             p.tkIso >> 
//             p.ecalIso >> 
//             p.hcalIso >> 
            p.combIso >>
            p.missHits >> 
            p.dist >> 
            p.cot;

		p.print();

		_elWorkingPoints.push_back(p);
	}
}

//_____________________________________________________________________________
DileptonSelector::WorkingPoint DileptonSelector::getWorkingPoint(unsigned short part, int eff) {
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
void DileptonSelector::clear() {

	_muTagged.clear();
	_elTagged.clear();

	_selectedPairs.clear();

	_selectedEls.clear();
	_selectedMus.clear();
	_softMus.clear();

	_selectedPFJets.clear();

	_btaggedJets.clear();

}

//_____________________________________________________________________________
bool DileptonSelector::selectAndClean() {
	//
	// loop over electrons and mus.
	// proceed only if there are 2 leptons (both tight and loose)



	Debug(3) << "- NtupleLeptons: " << getEvent()->getNEles()+getEvent()->getNMus() << '\n'
			<< "  NtupleMuons: " << getEvent()->getNMus() << '\n'
			<< "  NtupleElectrons: " <<getEvent()->getNEles() << std::endl;

//     _hlt.updateIds( getEvent()->getRun());

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
bool DileptonSelector::matchDataHLT() {

    _llCounters->Fill(kLLBinAll, _eventWeight );
    _eeCounters->Fill(kLLBinAll, _eventWeight );
    _emCounters->Fill(kLLBinAll, _eventWeight );
    _meCounters->Fill(kLLBinAll, _eventWeight );
    _mmCounters->Fill(kLLBinAll, _eventWeight );

    // GenMET is -1000 if it's a data file
//     bool isData = ( getEvent()->getGenMET()  < -999.);
//     bool match = !isData || _hlt.match( getEvent()->getHLTResults() );
//
    bool match = true;

	if ( match ) {
	    _llCounters->Fill(kLLBinHLT, _eventWeight );
	    _eeCounters->Fill(kLLBinHLT, _eventWeight );
	    _emCounters->Fill(kLLBinHLT, _eventWeight );
	    _meCounters->Fill(kLLBinHLT, _eventWeight );
	    _mmCounters->Fill(kLLBinHLT, _eventWeight );
	}
//	return (trigger || !isData);
	return match;
}

//_____________________________________________________________________________
bool DileptonSelector::hasGoodVertex() {
	//TODO move to config file

//	std::cout << "vrtxGood: " << PrimVtxGood << "\n"
//			<< "vrtxFake: " << PrimVtxIsFake << std::endl;
	EventProxy* ev = getEvent();
	bool goodVrtx = (ev->getPrimVtxNdof() >= _vrtxCut_nDof ) &&
	(ev->getPrimVtxGood() == 0 ) &&
	(ev->getPrimVtxIsFake() != 1) &&
	(TMath::Abs(ev->getPrimVtxRho() < _vrtxCut_rho )) &&
	(TMath::Abs(ev->getPrimVtxz()) < _vrtxCut_z );

    //FIXME
    goodVrtx = true;
	if ( goodVrtx ) {
		_llCounters->Fill(kLLBinVertex, _eventWeight );
		_eeCounters->Fill(kLLBinVertex, _eventWeight );
		_emCounters->Fill(kLLBinVertex, _eventWeight );
		_meCounters->Fill(kLLBinVertex, _eventWeight );
		_mmCounters->Fill(kLLBinVertex, _eventWeight );
	}

	return goodVrtx;
}

//_____________________________________________________________________________
void DileptonSelector::electronIsoId( LepCandidate::elBitSet& tags, int idx, int eff ) {
	// identify tight electron

	EventProxy* ev = getEvent();
	float scEta = ev->getElSCEta(idx);

	// apply the correction for the endcaps
	float dPhi = ev->getElDeltaPhiSuperClusterAtVtx(idx);
	float dEta = ev->getElDeltaEtaSuperClusterAtVtx(idx);

	float See       = ev->getElSigmaIetaIeta(idx);
	float HoE       = ev->getElHcalOverEcal(idx);
	float trkIso    = ev->getElDR03TkSumPt(idx);
	float ecalIso   = ev->getElDR03EcalRecHitSumEt(idx);
    float hcalIso   = ev->getElDR03HcalTowerSumEt(idx);
//     float hcalIso   = ev->getElDR03HcalFull(idx);
	float rho       = ev->getElRho(idx);
    float puCorr    = rho*TMath::Pi()*0.3*0.3;
	float combIso_B = (trkIso + TMath::Max(0., ecalIso - 1.) + hcalIso - puCorr) / ev->getElPt(idx);
	float combIso_E = (trkIso + ecalIso + hcalIso - puCorr ) / ev->getElPt(idx);
	float combIso   = 0;

	unsigned short p;
	if ( TMath::Abs(scEta) <= _elCut_EtaSCEbEe ) {
		// barrel
		p = kBarrel;
		combIso = combIso_B;
	} else if ( TMath::Abs(scEta) > _elCut_EtaSCEbEe ) {
		p = kEndcap;
		combIso = combIso_E;
	} else {
		//std::cout << "Candidate out of acceptance region" << std::endl;
		//return kOutOfAcc;
		return;
	}

//     Debug(3) << "scEta " << TMath::Abs(scEta) << " combIso " << combIso << " isEb " << ev->getElIsEb(idx) << std::endl;

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

    _electronHistograms[kElSee]->Fill( See, _eventWeight );
    _electronHistograms[kElDeta]->Fill( dEta, _eventWeight );
    _electronHistograms[kElDphi]->Fill( dPhi, _eventWeight );
    _electronHistograms[kElCombIso]->Fill( combIso, _eventWeight );
	return;

}

//_____________________________________________________________________________
void DileptonSelector::tagElectrons() {

	EventProxy* ev = getEvent();
	_elTagged.clear();

	//loop over els
	for( int i(0);i < ev->getNEles(); ++i) {

		ElCandicate theEl(i);
		theEl.charge = ev->getElCharge(i);
		theEl.pt     = ev->getElPt(i);

        _electronHistograms[kElEta]->Fill( ev->getElEta(i), _eventWeight );
        _electronHistograms[kElPt]->Fill( ev->getElPt(i), _eventWeight );
        _electronHistograms[kElD0]->Fill( ev->getElD0PV(i), _eventWeight );
        _electronHistograms[kElDz]->Fill( ev->getElDzPV(i), _eventWeight );

		// first tag the tight word
		theEl.tightTags[kElTagEta] = (TMath::Abs( ev->getElEta(i) ) < _etaMaxEE);

		// interaction point
		theEl.tightTags[kElTagD0PV] = ( TMath::Abs(ev->getElD0PV(i)) < _lepCut_D0PV);
		theEl.tightTags[kElTagDzPV] = ( TMath::Abs(ev->getElDzPV(i)) < _lepCut_DzPV);

		// drop electrons with pT < _leptonPtCut
		theEl.tightTags[kElTagLeadingPt] = ( ev->getElPt(i) > _lepCut_leadingPt );
		theEl.tightTags[kElTagTrailingPt] = ( ev->getElPt(i) > _lepCut_trailingPt );

		electronIsoId(theEl.tightTags, theEl.idx, _elCut_TightWorkingPoint );

		// it's duplicate, I know
		theEl.looseTags[kElTagEta] = (TMath::Abs( ev->getElEta(i) ) < _etaMaxEE);

		// interaction point
		theEl.looseTags[kElTagD0PV] = ( TMath::Abs(ev->getElD0PV(i)) < _lepCut_D0PV);
		theEl.looseTags[kElTagDzPV] = ( TMath::Abs(ev->getElDzPV(i)) < _lepCut_DzPV);

		// drop electrons with pT < _leptonPtCut
		theEl.looseTags[kElTagLeadingPt] = ( ev->getElPt(i) > _lepCut_leadingPt );
		theEl.looseTags[kElTagTrailingPt] = ( ev->getElPt(i) > _lepCut_trailingPt );

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
			THROW_RUNTIME("something fishy cIso: eta:" << ev->getElEta(i) << " b:" << combIso_B << " e:" << combIso_E
                    << " tightW: " << theEl.tightTags.to_string() << " - looseW: " <<  theEl.looseTags.to_string() );
		}

	}
}

//_____________________________________________________________________________
void DileptonSelector::tagMuons() {
	// muon id cuts
	// isolation = (ev->getMuIso03SumPt(i) + ev->getMuIso03EmEt(i) + ev->getMuIso03HadEt(i) ) / ev->getMuPt(i) < 0.15
	// isGlobalMu
	// ev->getMuNChi2(i) < 10
	// ev->getMuNMuHits(i) > 0
	// ev->getMuNTkHits(i) > 10

	EventProxy* ev = getEvent();
	_muTagged.clear();
	// loop on mus
	for (int i=0; i < ev->getNMus(); ++i) {
		// reject mus with eta > _etaMaxMu
		// and pT < 10 GeV

		MuCandidate theMu(i);
		theMu.charge = ev->getMuCharge(i);
		theMu.pt     = ev->getMuPt(i);

		LepCandidate::muBitSet& tags = theMu.tags;

		// to check
		tags[kMuTagEta] = (TMath::Abs( ev->getMuEta(i) ) < _etaMaxMu);

		// drop mus with pT < _leptonPtCut
		tags[kMuTagLeadingPt] = (  ev->getMuPt(i) > _lepCut_leadingPt );

		// check if the mu can be an extra
		tags[kMuTagTrailingPt] = ( ev->getMuPt(i) > _lepCut_trailingPt );

		// interaction point
		tags[kMuTagD0PV] = ( TMath::Abs(ev->getMuD0PV(i)) < _lepCut_D0PV);
		tags[kMuTagDzPV] = ( TMath::Abs(ev->getMuDzPV(i)) < _lepCut_DzPV);

		// isolation, where does it come from?
        float rho       = ev->getMuRho(i);
        float puCorr    = rho*TMath::Pi()*0.3*0.3;
		double combIso = (ev->getMuIso03SumPt(i) + ev->getMuIso03EmEt(i) + ev->getMuIso03HadEt(i) - puCorr )/ ev->getMuPt(i);

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
		tags[kMuTagRelPtRes] = ( TMath::Abs(ev->getMuPtE(i)/ev->getMuPt(i)) < _muCut_relPtRes);
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
void DileptonSelector::findSoftMus() {

	_softMus.clear();

	std::set<unsigned int> softs;
	std::vector<MuCandidate>::iterator itMu;
	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu)
        if ( itMu->isSoft() )
            softs.insert(itMu->idx);

	std::ostream_iterator< unsigned int > output( Debug(3), " " );
	Debug(3) << "- softs mus    '" ;
	std::copy( softs.begin(), softs.end(), output );
	Debug(3) << "'" << std::endl;
	Debug(3) << "- selected mus '" ;
	std::copy( _selectedMus.begin(), _selectedMus.end(), output );
	Debug(3) << "'" << std::endl;
	// remove those who are muons
	std::set_difference(softs.begin(), softs.end(),_selectedMus.begin(),_selectedMus.end(), std::inserter(_softMus,_softMus.end()));
	Debug(3) << "- softs clean  '" ;
	std::copy( _softMus.begin(), _softMus.end(), output );
	Debug(3) << "'" << std::endl;
}

//_____________________________________________________________________________
void DileptonSelector::fillCtrlHistograms() {
	std::vector<ElCandicate>::iterator itEl;
	for( itEl = _elTagged.begin(); itEl!=_elTagged.end(); ++itEl) {
		_elTightCtrl->Fill(kLepTagAll, _eventWeight);

		if ( !itEl->tightTags[kElTagEta] ) continue;
		_elTightCtrl->Fill(kLepTagEta, _eventWeight);

		if ( !itEl->tightTags[kElTagLeadingPt] ) continue;
		_elTightCtrl->Fill(kLepTagPt, _eventWeight);

		if ( !itEl->tightTags[kElTagD0PV] ) continue;
		_elTightCtrl->Fill(kLepTagD0, _eventWeight);

		if ( !itEl->tightTags[kElTagDzPV] ) continue;
		_elTightCtrl->Fill(kLepTagDz, _eventWeight);

		if ( !itEl->isIso() ) continue;
		_elTightCtrl->Fill(kLepTagIsolation, _eventWeight);

		if ( !itEl->isId() ) continue;
		_elTightCtrl->Fill(kLepTagId, _eventWeight);

		if ( !itEl->isNoConv() ) continue;
		_elTightCtrl->Fill(kLepTagNoConv, _eventWeight);
	}

	//std::vector<ElCandicate>::iterator it;
	for( itEl = _elTagged.begin(); itEl!=_elTagged.end(); ++itEl) {
		_elLooseCtrl->Fill(kLepTagAll, _eventWeight);

		if ( !itEl->looseTags[kElTagEta] ) continue;
		_elLooseCtrl->Fill(kLepTagEta, _eventWeight);

		if ( !itEl->looseTags[kElTagLeadingPt] ) continue;
		_elLooseCtrl->Fill(kLepTagPt, _eventWeight);

		if ( !itEl->looseTags[kElTagD0PV] ) continue;
		_elLooseCtrl->Fill(kLepTagD0, _eventWeight);

		if ( !itEl->looseTags[kElTagDzPV] ) continue;
		_elLooseCtrl->Fill(kLepTagDz, _eventWeight);

		if ( !itEl->isLooseIso() ) continue;
		_elLooseCtrl->Fill(kLepTagIsolation, _eventWeight);

		if ( !itEl->isLooseId() ) continue;
		_elLooseCtrl->Fill(kLepTagId, _eventWeight);

		if ( !itEl->isLooseNoConv() ) continue;
		_elLooseCtrl->Fill(kLepTagNoConv, _eventWeight);
	}

	std::vector<MuCandidate>::iterator itMu;
	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu) {
		_muGoodCtrl->Fill(kLepTagAll, _eventWeight);

		if ( !itMu->tags[kMuTagEta]  ) continue;
		_muGoodCtrl->Fill(kLepTagEta, _eventWeight);

		if ( !itMu->tags[kMuTagLeadingPt]  ) continue;
		_muGoodCtrl->Fill(kLepTagPt, _eventWeight);

		if ( !itMu->tags[kMuTagD0PV]  ) continue;
		_muGoodCtrl->Fill(kLepTagD0, _eventWeight);

		if ( !itMu->tags[kMuTagDzPV]  ) continue;
		_muGoodCtrl->Fill(kLepTagDz, _eventWeight);

		if ( !itMu->isIso() ) continue;
		_muGoodCtrl->Fill(kLepTagIsolation, _eventWeight);

		if ( !itMu->isId()  ) continue;
		_muGoodCtrl->Fill(kLepTagId, _eventWeight);

		if ( !itMu->isNoConv() ) continue;
		_muGoodCtrl->Fill(kLepTagNoConv, _eventWeight);
	}

	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu) {
		_muExtraCtrl->Fill(kLepTagAll, _eventWeight);

		if ( !itMu->tags[kMuTagEta]  ) continue;
		_muExtraCtrl->Fill(kLepTagEta, _eventWeight);

		if ( !itMu->tags[kMuTagTrailingPt]  ) continue;
		_muExtraCtrl->Fill(kLepTagPt, _eventWeight);

		if ( !itMu->tags[kMuTagD0PV]  ) continue;
		_muExtraCtrl->Fill(kLepTagD0, _eventWeight);

		if ( !itMu->tags[kMuTagDzPV]  ) continue;
		_muExtraCtrl->Fill(kLepTagDz, _eventWeight);

		if ( !itMu->isIso() ) continue;
		_muExtraCtrl->Fill(kLepTagIsolation, _eventWeight);

		if ( !itMu->isId()  ) continue;
		_muExtraCtrl->Fill(kLepTagId, _eventWeight);

		if ( !itMu->isNoConv() ) continue;
		_muExtraCtrl->Fill(kLepTagNoConv, _eventWeight);
	}
}

//_____________________________________________________________________________
void DileptonSelector::countPairs() {

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
	std::vector<unsigned int> meCounts(kLLBinLast);
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
			case LepPair::kME_t:
				counts = &meCounts;
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

		if ( !iP->isId() ) continue;
		(*counts)[kLLBinId]++;

		if ( !iP->isIso() ) continue;
		(*counts)[kLLBinIso]++;

		if ( !iP->isNoConv() ) continue;
		(*counts)[kLLBinNoConv]++;

		if ( !iP->isVertex() ) continue;
		(*counts)[kLLBinIp]++;

		// mark the leptons to be saved
		_selectedPairs.push_back(*iP);
	}

	//
	std::stringstream see, sem, sme, smm, sll;

	for( unsigned int i(1); i<llCounts.size()-1; ++i ){
		see << eeCounts[i] << ",";
		sem << emCounts[i] << ",";
		sme << meCounts[i] << ",";
		smm << mmCounts[i] << ",";

		if ( eeCounts[i] || emCounts[i] || meCounts[i] || mmCounts[i] )
			llCounts[i]++;

		sll << llCounts[i] << ",";
	}

	Debug(3) << "ee: " << see.str() << '\n'
		     << "em: " << sem.str() << '\n'
		     << "me: " << sme.str() << '\n'
		     << "mm: " << smm.str() << '\n'
		     << "ll: " << sll.str()  << std::endl;

	Debug(3) << "N selected pairs: " << _selectedPairs.size() << std::endl;

	fillCounts( _llCounters, llCounts);
	fillCounts( _eeCounters, eeCounts);
	fillCounts( _emCounters, emCounts);
	fillCounts( _meCounters, meCounts);
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
void DileptonSelector::fillCounts( TH1F* h, const std::vector<unsigned int>& counts) {

	if ( counts[kLLBinDilepton] != 0 ) h->Fill(kLLBinDilepton, _eventWeight);
	if ( counts[kLLBinEtaPt] != 0 )    h->Fill(kLLBinEtaPt, _eventWeight);
	if ( counts[kLLBinIp] != 0 )	   h->Fill(kLLBinIp, _eventWeight);
	if ( counts[kLLBinIso] != 0 )      h->Fill(kLLBinIso, _eventWeight);
	if ( counts[kLLBinId] != 0 )       h->Fill(kLLBinId, _eventWeight);
	if ( counts[kLLBinNoConv] != 0 )   h->Fill(kLLBinNoConv, _eventWeight);

}

//_____________________________________________________________________________
bool DileptonSelector::checkExtraLeptons() {

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
	case LepPair::kME_t:
		counters = _meCounters;
		break;
	case LepPair::kMM_t:
		counters = _mmCounters;
		break;
	default:
		THROW_RUNTIME("Unidentified lepton pair: finalState = " << p.finalState());
	}

	counters->Fill(kLLBinExtraLep, _eventWeight);
	_llCounters->Fill(kLLBinExtraLep, _eventWeight);


//     if (p.finalState()==LepPair::kEE_t)
//         //FIXME
//         _debugFile << getEvent()->getEvent() << std::endl;
    

	return true;
}

//_____________________________________________________________________________
void DileptonSelector::assembleEvent() {

	EventProxy* ev = getEvent();

	// clear the ntuple
	_diLepEvent->Clear();

	// fill the run parameters
	_diLepEvent->Run          = ev->getRun();
	_diLepEvent->Event        = ev->getEvent();
	_diLepEvent->LumiSection  = ev->getLumiSection();
	_diLepEvent->Weight       = _eventWeight;

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

	_diLepEvent->HasSoftMus   = _softMus.size() > 0;
	_diLepEvent->HasBTaggedJets = _btaggedJets.size() > 0;

	_diLepEvent->NEles        = _selectedEls.size();

	_diLepEvent->NMus         = _selectedMus.size();

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
        pfj.BTagProbTkCntHighEff = ev->getPFJbTagProbTkCntHighEff(k);

		++itPFJ;
	}
	if ( itPFJ != _selectedPFJets.end() )
		THROW_RUNTIME("Not all pfJets were copied?");


}

//_____________________________________________________________________________
void DileptonSelector::cleanJets() {
	// so far so good, let's clean the jets up

	EventProxy* ev = getEvent();

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
			match |= ( TMath::Abs(pPFJet.DeltaR(pEl)) < _jetCut_Dr );
		}

		for( it=_selectedMus.begin();
				it != _selectedMus.end(); ++it) {
			TVector3 pMu(ev->getMuPx(*it), ev->getMuPy(*it), ev->getMuPz(*it));

			match |= ( TMath::Abs(pPFJet.DeltaR(pMu)) < _jetCut_Dr );
		}

		if ( match ) continue;
        
		// jet ptcut
		if ( ev->getPFJPt(i) > _jetCut_Pt  && ev->getPFJEta(i) < _jetCut_Eta ) {
			_selectedPFJets.insert(i);
        }
        
        _jetBTagProbTkCntHighEff->Fill(ev->getPFJbTagProbTkCntHighEff(i), _eventWeight);

		// or check for btagged jets
		if ( ev->getPFJbTagProbTkCntHighEff(i) > _jetCut_BtagProb )
			_btaggedJets.insert(i);

	}

}


//define this as a plug-in
DEFINE_FWK_MODULE(DileptonSelector);
