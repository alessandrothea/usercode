// -*- C++ -*-
//
// Package:    DileptonSelector
// Class:      DileptonSelector
// 

#include <HWWAnalysis/DileptonSelector/interface/DileptonSelector.h>
#include <HWWAnalysis/DileptonSelector/interface/EventProxy.h>
#include <HWWAnalysis/DileptonSelector/interface/HWWCandidates.h>
#include <HWWAnalysis/DileptonSelector/interface/HltObjMatcher.h>
#include <HWWAnalysis/Misc/interface/Tools.h>
#include <CommonTools/UtilAlgos/interface/TFileService.h>
#include <DataFormats/PatCandidates/interface/Electron.h>
#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/VertexReco/interface/Vertex.h>
#include <FWCore/ServiceRegistry/interface/Service.h>
#include <SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h>
#include <Math/VectorUtil.h>
#include <vector>
#include <fstream>

const double DileptonSelector::_etaMaxTrk=2.4000;
const double DileptonSelector::_etaMaxEB=1.4442;
const double DileptonSelector::_etaMinEE=1.5660;
const double DileptonSelector::_etaMaxEE=2.5000;
const double DileptonSelector::_etaMaxMu=2.4000;


//_____________________________________________________________________________
void DileptonSelector::VBTFWorkingPoint::print() {
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
        << combIso << '\t'
        << missHits << '\t'
        << dist << '\t'
        << cot << '\t'
        << std::endl;
}

//_____________________________________________________________________________
void DileptonSelector::LHWorkingPoint::print() {
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
        << lh0brem << '\t'
        << lh1brem << "   "
        << combIso << '\t'
        << missHits << '\t'
        << dist << '\t'
        << cot << '\t'
        << std::endl;
}

//______________________________________________________________________________
//
// constructors and destructor
//
DileptonSelector::DileptonSelector(const edm::ParameterSet& iConfig) : _nEvents(0), _nSelectedEvents(0),
    _tree(0x0), _diLepEvent(0x0)
{
    //now do what ever initialization is needed
    // configuration
    _debugLvl       = iConfig.getUntrackedParameter<int>("debugLevel");
    _puFactors      = iConfig.getParameter<std::vector<double> >("pileupFactors");


    // src tags
    if( iConfig.existsAs<edm::InputTag>("ptWeightSrc") ) {
        _ptWeightSrc = iConfig.getParameter<edm::InputTag> ("ptWeightSrc");
    }

    _puInfoSrc      = iConfig.getParameter<edm::InputTag>("puInfoSrc");
    _vertexSrc      = iConfig.getParameter<edm::InputTag>("vertexSrc");
    _electronSrc    = iConfig.getParameter<edm::InputTag>("electronSrc");
    _muonSrc        = iConfig.getParameter<edm::InputTag>("muonSrc");
    _jetSrc         = iConfig.getParameter<edm::InputTag>("jetSrc");
    _tcMetSrc       = iConfig.getParameter<edm::InputTag>("tcMetSrc");
    _pfMetSrc       = iConfig.getParameter<edm::InputTag>("pfMetSrc");
    _chMetSrc       = iConfig.getParameter<edm::InputTag>("chMetSrc");

    const edm::ParameterSet& vrtxCuts = iConfig.getParameterSet("vrtxCuts");
    _vrtxCut_nDof = vrtxCuts.getParameter<double>("nDof"); // 4.
    _vrtxCut_rho  = vrtxCuts.getParameter<double>("rho"); // 2.
    _vrtxCut_z    = vrtxCuts.getParameter<double>("z"); // 24.


    const edm::ParameterSet& lepCuts = iConfig.getParameterSet("lepCuts");
    _lepCut_extraPt       = lepCuts.getParameter<double>("extraPt");

    const edm::ParameterSet& elCuts = iConfig.getParameterSet("elCuts");
    _elCut_TightWorkingPoint = elCuts.getParameter<int>( "tightWorkingPoint");
    _elCut_LooseWorkingPoint = elCuts.getParameter<int>( "looseWorkingPoint");
    _elCut_leadingPt         = elCuts.getParameter<double>("leadingPt");
    _elCut_trailingPt        = elCuts.getParameter<double>("trailingPt");
    _elCut_ip3D              = elCuts.getParameter<double>( "ip3D" );

    const edm::ParameterSet& muCuts = iConfig.getParameterSet("muCuts");
    _muCut_leadingPt         = muCuts.getParameter<double>("leadingPt");
    _muCut_trailingPt        = muCuts.getParameter<double>("trailingPt");
    _muCut_NMuHits		     = muCuts.getParameter<int>("nMuHits");
    _muCut_NMuMatches	     = muCuts.getParameter<int>("nMuMatches");
    _muCut_NTrackerHits	     = muCuts.getParameter<int>("nTrackerHits");
    _muCut_NPixelHits	     = muCuts.getParameter<int>("nPixelHits");
    _muCut_NChi2		     = muCuts.getParameter<double>("nChi2");
    _muCut_relPtRes		     = muCuts.getParameter<double>("relPtResolution");
    _muCut_combIsoOverPt     = muCuts.getParameter<double>("combIso");
    _muCut_ip2D              = muCuts.getParameter<double>( "ip2D" );
    _muCut_dZPrimaryVertex   = muCuts.getParameter<double>( "dZPrimaryVertex" );

    const edm::ParameterSet& muSoftCuts = iConfig.getParameterSet("muSoftCuts");
    _muSoftCut_Pt		= muSoftCuts.getParameter<double>("Pt");
    _muSoftCut_HighPt	= muSoftCuts.getParameter<double>("HighPt");
    _muSoftCut_NotIso	= muSoftCuts.getParameter<double>("NotIso");

    const edm::ParameterSet& jetCuts = iConfig.getParameterSet("jetCuts");
    _jetCut_Pt	    	= jetCuts.getParameter<double>("Pt");
    _jetCut_Dr	    	= jetCuts.getParameter<double>("Dr");
    _jetCut_Eta	    	= jetCuts.getParameter<double>("Eta");
    _jetCut_BtagProb	= jetCuts.getParameter<double>("BtagProb");

    _jetCut_neutralEmFrac  =  jetCuts.getParameter<double>("neutralEmFrac");
    _jetCut_neutralHadFrac =  jetCuts.getParameter<double>("neutralHadFrac");
    _jetCut_multiplicity   =  jetCuts.getParameter<int>("multiplicity");
    _jetCut_chargedEmFrac  =  jetCuts.getParameter<double>("chargedEmFrac");
    _jetCut_chargedHadFrac =  jetCuts.getParameter<double>("chargedHadFrac");
    _jetCut_chargedMulti   =  jetCuts.getParameter<int>("chargedMulti");

    Debug(0) << "- lepCuts " << lepCuts.toString() << std::endl;
    Debug(0) << "- elCuts " << elCuts.toString() << std::endl;
    Debug(0) << "- muCuts " << muCuts.toString() << std::endl;
    Debug(0) << "- softMuCuts " << muSoftCuts.toString() << std::endl;
    Debug(0) << "- jetCuts " << jetCuts.toString() << std::endl;

    std::string dataType = iConfig.getParameter<std::string>("dataType");
    _hltMatcher = new HltObjMatcher(dataType);
    Debug(0) << "Data type is " << _hltMatcher->dataLabel() << " isData " << _hltMatcher->isData() << std::endl;
    
//     const edm::ParameterSet& hltPaths = iConfig.getParameterSet("hltPaths");
//     std::vector<std::string> hltSingleEl = hltPaths.getParameter<std::vector<std::string> >("singleEl"); 
//     std::vector<std::string> hltSingleMu = hltPaths.getParameter<std::vector<std::string> >("singleMu"); 

    loadVBFTId( iConfig.getParameter<edm::VParameterSet>("elCutBasedId") );
    loadLikelihoodId( iConfig.getParameter<edm::VParameterSet>("elLikelihood") );
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

    // set the labels
    proxy._puInfoTag    = this->_puInfoSrc; 
    proxy._vertexTag    = this->_vertexSrc;
    proxy._electronTag  = this->_electronSrc;
    proxy._muonTag      = this->_muonSrc;
    proxy._jetTag       = this->_jetSrc;
    proxy._tcMetTag     = this->_tcMetSrc;
    proxy._pfMetTag     = this->_pfMetSrc;
    proxy._chMetTag     = this->_chMetSrc;

    proxy.connect();





    Debug(3) << "--"<< iEvent.id().event() << "-----------------------------------------------" << std::endl;
    // make sure the previous event is cleared
    clear();

    // pileup info and set eventWeights
    calculateWeight( iEvent );

    _hltMatcher->setTriggerResults( iEvent );

    _nEvents += this->weight();

    if ( !selectAndClean() ) return;
    assembleEvent();

//     _nSelectedEvents++;
    _nSelectedEvents += this->weight();
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
DileptonSelector::calculateWeight( const edm::Event& iEvent ) {
    // FIXME: should it know whether it's data or not?

    

    if ( iEvent.isRealData() ) {
        _eventWeight = 1.;
        // fill some additional histograms
        _puNVertexes->Fill( getEvent()->getNVrtx(), this->weight() );
    } else {

        int nPU = getEvent()->getNPileUp();
        if ( nPU < 0 )
            THROW_RUNTIME(" nPU = " << nPU << " what's going on?!?");
        if ( nPU > (int)_puFactors.size() )
            THROW_RUNTIME("Simulated Pu [" << nPU <<"] larger than available puFactors");

        _eventWeight = _puFactors[ nPU ];
        _puNInteractions->Fill( nPU, this->weight() );
        _puNInteractionsUnweighted->Fill( nPU );
        _puNVertexes->Fill( getEvent()->getNVrtx(), this->weight() );
    }

    if ( !(_ptWeightSrc == edm::InputTag()) ) {
        edm::Handle<double> ptWeightHandle;
        iEvent.getByLabel(_ptWeightSrc, ptWeightHandle);
        
        _eventWeight *= *ptWeightHandle;
        
    }
        

}


//______________________________________________________________________________
void
DileptonSelector::loadLikelihoodId( const std::vector<edm::ParameterSet>& points ) {

	Debug(0) << "Reading Likelihood Working points " << std::endl;

    std::vector<edm::ParameterSet>::const_iterator iP;
    for( iP = points.begin(); iP != points.end(); ++iP ) {
        std::string dummy = iP->getParameter<std::string>("partition");

		if ( dummy.length() != 1 )
			THROW_RUNTIME("Corrupted working point: " + dummy + " is supposed to be 1 char long.");

		LHWorkingPoint p;
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

        p.efficiency = iP->getParameter<int>("eff");
        p.lh0brem    = iP->getParameter<double>("likelihood0");
        p.lh1brem    = iP->getParameter<double>("likelihood1");
        p.combIso    = iP->getParameter<double>("combIso");
        p.missHits   = iP->getParameter<double>("hits");
        p.dist       = iP->getParameter<double>("dist");
        p.cot        = iP->getParameter<double>("cot");

		p.print();

		_elLHWorkingPoints.push_back(p);
    }

}
    
//______________________________________________________________________________
void
DileptonSelector::loadVBFTId( const std::vector<edm::ParameterSet>& points ) {

	Debug(0) << "Reading LikelihoodID Working points " << std::endl;

    std::vector<edm::ParameterSet>::const_iterator iP;
    for( iP = points.begin(); iP != points.end(); ++iP ) {
        std::string dummy = iP->getParameter<std::string>("partition");

		if ( dummy.length() != 1 )
			THROW_RUNTIME("Corrupted working point: " + dummy + " is supposed to be 1 char long.");

		VBTFWorkingPoint p;
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

        p.efficiency = iP->getParameter<int>("eff");
        p.See        = iP->getParameter<double>("see");
        p.dPhi       = iP->getParameter<double>("dphi");
        p.dEta       = iP->getParameter<double>("deta");
        p.HoE        = iP->getParameter<double>("hoe");
        p.combIso    = iP->getParameter<double>("combIso");
        p.missHits   = iP->getParameter<double>("hits");
        p.dist       = iP->getParameter<double>("dist");
        p.cot        = iP->getParameter<double>("cot");

		p.print();

		_elVBTFWorkingPoints.push_back(p);
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


	labels[kLLBinAll]	    = "All events";
//     labels[kLLBinVertex]   = "Good Vertex";
	labels[kLLBinDilepton]  = "l^{+}l^{-}";
	labels[kLLBinEtaPt]     = "EtaPt";
	labels[kLLBinIp]   	    = "Impact Parameter";
	labels[kLLBinIso]       = "Isolation";
	labels[kLLBinId]        = "Id";
	labels[kLLBinNoConv]    = "No Conversion";
	labels[kLLBinExtraLep]  = "Extra lepton";
	labels[kLLBinHltBits]   = "HLT Bits";
	labels[kLLBinHltObject] = "HLT Objects";

	_llCounters = makeLabelHistogram(here,"llCounters","HWW selection",labels);
	_eeCounters = makeLabelHistogram(here,"eeCounters","HWW selection - ee",labels);
	_emCounters = makeLabelHistogram(here,"emCounters","HWW selection - em",labels);
	_meCounters = makeLabelHistogram(here,"meCounters","HWW selection - me",labels);
	_mmCounters = makeLabelHistogram(here,"mmCounters","HWW selection - mm",labels);

	std::map<int,std::string> ctrlLabels;
	ctrlLabels[kLepTagAll]		 = "All";
	ctrlLabels[kLepTagEta]       = "Eta";
	ctrlLabels[kLepTagPt]        = "Pt";
	ctrlLabels[kLepTagIsolation] = "Iso";
	ctrlLabels[kLepTagId]        = "Id";
	ctrlLabels[kLepTagIp]        = "Ip";
	ctrlLabels[kLepTagNoConv]    = "Conversion Veto";


    TFileDirectory sldir = fs->mkdir("singleLepton");

	_elTightCtrl = makeLabelHistogram(&sldir, "elTightCtrl","Tight electrons",ctrlLabels);
	_elLooseCtrl = makeLabelHistogram(&sldir, "elLooseCtrl","Loose (extra) electrons",ctrlLabels);
	_muGoodCtrl  = makeLabelHistogram(&sldir, "muGoodCtrl" ,"Good muons",ctrlLabels);
	_muExtraCtrl = makeLabelHistogram(&sldir, "muExtraCtrl","Extra muons",ctrlLabels);


    TFileDirectory puDir = fs->mkdir("puInfo");
    unsigned int maxPu = 30;
    _puNInteractions           = puDir.make<TH1D>("nPuInterations","# interactions",maxPu,0,maxPu);
    _puNInteractionsUnweighted = puDir.make<TH1D>("nPuInterationsUnweighted","# interactions",maxPu,0,maxPu);
    _puNVertexes               = puDir.make<TH1D>("nVertexes","# vertex",maxPu,0,maxPu);

    TFileDirectory elVarsDir = fs->mkdir("electronVars");
    makeElectronHistograms( &elVarsDir, _electronHistograms);
    TFileDirectory muVarsDir = fs->mkdir("muonVars");
    TFileDirectory jetVarsDir = fs->mkdir("jetsVars");

    _jetBTagProbTkCntHighEff = jetVarsDir.make<TH1D>("jetBTagProbTkCntHighEff","B-tag prob above jet cut",100,-10, 10);



}


//______________________________________________________________________________
void DileptonSelector::makeElectronHistograms( TFileDirectory* fd, std::vector<TH1D*>& histograms ) {

    histograms.assign(kElTagSize,0x0);


    histograms[kElTagLeadingPt]     = fd->make<TH1D>("pt",     "p_{T}",200, 0, 200);
    histograms[kElTagEta]           = fd->make<TH1D>("eta",    "#eta",100, 0, 5);
    histograms[kElTagIp3D]          = fd->make<TH1D>("ip3D",   "ip3D", 100,-0.05,0.05);
    histograms[kElTagSee]           = fd->make<TH1D>("see",    "Sigma #eta#eta",100, 0, 0.1);
    histograms[kElTagDeta]          = fd->make<TH1D>("dEta",   "#Delta#eta",100, 0, 0.2);
    histograms[kElTagDphi]          = fd->make<TH1D>("dPhi",   "#Delta#phi",100, -0.02, 0.02);
    histograms[kElTagCombIso]       = fd->make<TH1D>("combIso","Combined relative iso (VBTF)",100, 0, 2);
    histograms[kElTagCot]           = fd->make<TH1D>("cot","cotg", 100, 0, 0.05);
    histograms[kElTagDist]          = fd->make<TH1D>("dist","dist", 100, 0, 0.05);
    histograms[kElTagHits]          = fd->make<TH1D>("hits","hits", 10,0,10);
    histograms[kElTagLH_Likelihood] = fd->make<TH1D>("likelihood","Likelihood",100,-5,5);
}

//_____________________________________________________________________________
TH1D* DileptonSelector::makeLabelHistogram( TFileDirectory* fd, const std::string& name, const std::string& title, std::map<int,std::string> labels) {
	int xmin = labels.begin()->first;
	int xmax = labels.begin()->first;

	std::map<int, std::string>::iterator it;
	for( it = labels.begin(); it != labels.end(); ++it ) {
		xmin = it->first < xmin ? it->first : xmin;
		xmax = it->first > xmax ? it->first : xmax;
	}

	++xmax;
	int nbins = xmax-xmin;

	TH1D* h = fd->make<TH1D>(name.c_str(), title.c_str(), nbins, xmin, xmax);
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
DileptonSelector::VBTFWorkingPoint DileptonSelector::getVBTFWorkingPoint(unsigned short part, int eff) {
	std::vector<VBTFWorkingPoint>::iterator it;
	for ( it=_elVBTFWorkingPoints.begin(); it != _elVBTFWorkingPoints.end(); ++it) {
		if ( (*it).partition == part && (*it).efficiency == eff)
			return *it;
	}

	std::stringstream msg;
	msg << "Working point " << part << "(" << eff << ") not found";
	THROW_RUNTIME(msg.str());

}

//_____________________________________________________________________________
DileptonSelector::LHWorkingPoint DileptonSelector::getLHWorkingPoint(unsigned short part, int eff) {
	std::vector<LHWorkingPoint>::iterator it;
	for ( it=_elLHWorkingPoints.begin(); it != _elLHWorkingPoints.end(); ++it) {
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

    _eventWeight = 1.;
    _nPileUp     = 0;

    _btag_combinedSecondaryVertex.clear();
    _btag_combinedSecondaryVertexMVA.clear();
    _btag_simpleSecondaryVertexHighEff.clear();
    _btag_simpleSecondaryVertexHighPur.clear();
    _btag_jetBProbability.clear();
    _btag_jetProbability.clear();
    _btag_trackCountingHighEff.clear();
    _btag_trackCountingHighPur.clear();
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
    // move this somewhere else
    _llCounters->Fill(kLLBinAll, this->weight() );
    _eeCounters->Fill(kLLBinAll, this->weight() );
    _emCounters->Fill(kLLBinAll, this->weight() );
    _meCounters->Fill(kLLBinAll, this->weight() );
    _mmCounters->Fill(kLLBinAll, this->weight() );

	// check the HLT flags
//     if ( !pasGoodVertex() ) return false;

	// select electrons
	tagElectrons();

	// select good mus
	tagMuons();

	// fill some control histograms
	fillCtrlHistograms();

	countPairs();

	if ( !checkExtraLeptons() )
		return false;

    if ( !matchHlt() ) return false;


	findSoftMus();

	// then clean the jets up
	cleanJets();
	return true;
}

//_____________________________________________________________________________
bool DileptonSelector::matchHlt() {


    LepPair& pair = _selectedPairs.front();
    bool match  = false;
    match = _hltMatcher->matchesBits(pair); 

    if ( !match ) return false; //LATINOS_V2

    _llCounters->Fill(kLLBinHltBits, this->weight() );

    switch( pair.finalState() ) {
        case LepPair::kEE_t:
            _eeCounters->Fill(kLLBinHltBits, this->weight() );
            break;
        case LepPair::kEM_t:
            _emCounters->Fill(kLLBinHltBits, this->weight() );
            break;
        case LepPair::kME_t:
            _meCounters->Fill(kLLBinHltBits, this->weight() );
            break;
        case LepPair::kMM_t:
            _mmCounters->Fill(kLLBinHltBits, this->weight() );
            break;
    }

    match = _hltMatcher->matchesObject(pair);

    if ( !match ) return false; //LATINOS_V2     

    _llCounters->Fill(kLLBinHltObject, this->weight() );

    switch( pair.finalState() ) {
        case LepPair::kEE_t:
            _eeCounters->Fill(kLLBinHltObject, this->weight() );
            break;
        case LepPair::kEM_t:
            _emCounters->Fill(kLLBinHltObject, this->weight() );
            break;
        case LepPair::kME_t:
            _meCounters->Fill(kLLBinHltObject, this->weight() );
            break;
        case LepPair::kMM_t:
            _mmCounters->Fill(kLLBinHltObject, this->weight() );
            break;
    }

    return match;
}

//_____________________________________________________________________________
// bool DileptonSelector::hasGoodVertex() {
	//TODO move to config file

//     EventProxy* ev = getEvent();
//     bool goodVrtx = (ev->getPrimVtxNdof() >= _vrtxCut_nDof ) &&
//     (ev->getPrimVtxGood() == 0 ) &&
//     (ev->getPrimVtxIsFake() != 1) &&
//     (TMath::Abs(ev->getPrimVtxRho() < _vrtxCut_rho )) &&
//     (TMath::Abs(ev->getPrimVtxz()) < _vrtxCut_z );

//     //FIXME
//     goodVrtx = true;
//     if ( goodVrtx ) {
//         _llCounters->Fill(kLLBinVertex, this->weight() );
//         _eeCounters->Fill(kLLBinVertex, this->weight() );
//         _emCounters->Fill(kLLBinVertex, this->weight() );
//         _meCounters->Fill(kLLBinVertex, this->weight() );
//         _mmCounters->Fill(kLLBinVertex, this->weight() );
//     }

//     return goodVrtx;
// }

//_____________________________________________________________________________
void DileptonSelector::electronIsoId( ElCandicate &theEl, LepCandidate::elBitSet& tags, int eff ) {
	// identify tight electron

    unsigned int i = theEl.idx;
	EventProxy* ev = getEvent();



	// apply the correction for the endcaps
	float dPhi = ev->getElDeltaPhiSuperClusterAtVtx(i);
	float dEta = ev->getElDeltaEtaSuperClusterAtVtx(i);

	float See       = ev->getElSigmaIetaIeta(i);
	float HoE       = ev->getElHcalOverEcal(i);
	float trkIso    = ev->getElDR03TkSumPt(i);
	float ecalIso   = ev->getElDR03EcalRecHitSumEt(i);
//     float hcalIso   = theEl.el()->userFloat("hcalFull")
    float hcalIso   = ev->getElDR03HcalFull(i);
	float rho       = ev->getElRho(i);
    float puCorr    = rho*TMath::Pi()*0.3*0.3;
	float combIso_B = (trkIso + TMath::Max(0., ecalIso - 1.) + hcalIso - puCorr) / ev->getElPt(i);
	float combIso_E = (trkIso + ecalIso + hcalIso - puCorr ) / ev->getElPt(i);
	float combIso   = 0;

	unsigned short p;
    if ( theEl.el()->isEB() ) {
		// barrel
		p = kBarrel;
		combIso = combIso_B;
    } else {
        p = kEndcap;
        combIso = combIso_E;
    }

	VBTFWorkingPoint vbtfWp = getVBTFWorkingPoint(p, eff );
	LHWorkingPoint lhWp = getLHWorkingPoint(p, eff );

    // conversion: the electron is a conversion
	// if |dist| < distCut and |delta cot(theta)| < cotCut
	// or
	// missingHist > hitsCut
	tags[kElTagDist] = (TMath::Abs(ev->getElConvPartnerTrkDist(i)) > vbtfWp.dist);
	tags[kElTagCot]  = (TMath::Abs(ev->getElConvPartnerTrkDCot(i)) > vbtfWp.cot);
	tags[kElTagHits] = (ev->getElNumberOfMissingInnerHits(i) == vbtfWp.missHits);

	tags[kElTagSee]     = ( See < vbtfWp.See);
	tags[kElTagDphi]    = ( TMath::Abs(dPhi) < vbtfWp.dPhi);
	tags[kElTagDeta]    = ( TMath::Abs(dEta) < vbtfWp.dEta);
	tags[kElTagHoE]     = ( HoE  < vbtfWp.HoE);
	tags[kElTagCombIso] = ( combIso < vbtfWp.combIso);
    
    
    double likelihood = theEl.el()->electronID("egammaIDLikelihood");
    // likelihood id
    tags[kElTagLH_Likelihood] =   
        ( theEl.el()->numberOfBrems() == 0 && likelihood > lhWp.lh0brem ) 
        || ( theEl.el()->numberOfBrems() > 0 && likelihood > lhWp.lh1brem );
	tags[kElTagLH_CombIso] = ( combIso < lhWp.combIso);

	tags[kElTagLH_Dist] = (TMath::Abs(ev->getElConvPartnerTrkDist(i)) > lhWp.dist);
	tags[kElTagLH_Cot]  = (TMath::Abs(ev->getElConvPartnerTrkDCot(i)) > lhWp.cot);
	tags[kElTagLH_Hits] = (ev->getElNumberOfMissingInnerHits(i) == lhWp.missHits);

    _electronHistograms[kElTagSee]->Fill( See, this->weight() );
    _electronHistograms[kElTagDeta]->Fill( dEta, this->weight() );
    _electronHistograms[kElTagDphi]->Fill( dPhi, this->weight() );
    _electronHistograms[kElTagCombIso]->Fill( combIso, this->weight() );
    _electronHistograms[kElTagDist]->Fill( ev->getElConvPartnerTrkDist(i), this->weight() );
    _electronHistograms[kElTagCot]->Fill( ev->getElConvPartnerTrkDCot(i), this->weight() );
    _electronHistograms[kElTagHits]->Fill( ev->getElNumberOfMissingInnerHits(i), this->weight() );
    _electronHistograms[kElTagLH_Likelihood]->Fill( likelihood, this->weight() );

	return;

}

//_____________________________________________________________________________
void DileptonSelector::tagElectrons() {

	EventProxy* ev = getEvent();
	_elTagged.clear();

	//loop over els
	for( int i(0);i < ev->getNEles(); ++i) {

		ElCandicate theEl(i);
        theEl.candidate = &(ev->getElectrons()[i]);

        double ip3D = theEl.el()->userFloat("ip2");

        _electronHistograms[kElTagEta]->Fill( ev->getElEta(i), this->weight() );
        _electronHistograms[kElTagLeadingPt]->Fill( ev->getElPt(i), this->weight() );
        _electronHistograms[kElTagIp3D]->Fill( TMath::Abs(ip3D), this->weight() );

		// first tag the tight word
		theEl.tightTags[kElTagEta] = (TMath::Abs( ev->getElEta(i) ) < _etaMaxEE);

		// interaction point
        theEl.tightTags[kElTagIp3D] = ( TMath::Abs(ip3D) < _elCut_ip3D);

		// drop electrons with pT < _leptonPtCut
		theEl.tightTags[kElTagLeadingPt]    = ( ev->getElPt(i) > _elCut_leadingPt );
		theEl.tightTags[kElTagTrailingPt]   = ( ev->getElPt(i) > _elCut_trailingPt );
		theEl.tightTags[kElTagExtraPt]      = ( ev->getElPt(i) > _lepCut_extraPt );

		electronIsoId(theEl, theEl.tightTags, _elCut_TightWorkingPoint );

		// it's duplicate, I know
		theEl.looseTags[kElTagEta] = (TMath::Abs( ev->getElEta(i) ) < _etaMaxEE);

		// interaction point
        theEl.looseTags[kElTagIp3D] = ( TMath::Abs(ip3D) < _elCut_ip3D);

		// drop electrons with pT < _leptonPtCut
		theEl.looseTags[kElTagLeadingPt] = ( ev->getElPt(i) > _elCut_leadingPt );
		theEl.looseTags[kElTagTrailingPt] = ( ev->getElPt(i) > _elCut_trailingPt );
		theEl.looseTags[kElTagExtraPt] = ( ev->getElPt(i) > _lepCut_extraPt );

		electronIsoId(theEl, theEl.looseTags, _elCut_LooseWorkingPoint );

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
                    << "\n - tightW: " << theEl.tightTags.to_string() << "\n - looseW: " <<  theEl.looseTags.to_string() );
		}

        // fill some histograms

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
		theMu.candidate = &(ev->getMuons()[i]);

        double ip2D = theMu.mu()->userFloat("tip2");
        double dzPV = theMu.mu()->userFloat("dzPV");

		LepCandidate::muBitSet& tags = theMu.tags;

		// to check
		tags[kMuTagEta] = (TMath::Abs( ev->getMuEta(i) ) < _etaMaxMu);

		// drop mus with pT < _leptonPtCut
		tags[kMuTagLeadingPt]  = ( ev->getMuPt(i) > _muCut_leadingPt );
		tags[kMuTagTrailingPt] = ( ev->getMuPt(i) > _muCut_trailingPt );
		tags[kMuTagExtraPt]    = ( ev->getMuPt(i) > _lepCut_extraPt );

		// interaction point
        tags[kMuTagIp2D] = ( TMath::Abs(ip2D) < _muCut_ip2D);
        tags[kMuTagDzPV] = ( TMath::Abs(dzPV) < _muCut_dZPrimaryVertex);

		// isolation, where does it come from?
        float rho       = ev->getMuRho(i);
        float puCorr    = rho*TMath::Pi()*0.3*0.3;
		double combIso = (ev->getMuIso03SumPt(i) + ev->getMuIso03EmEt(i) + ev->getMuIso03HadEt(i) - puCorr )/ ev->getMuPt(i);

		// the track is identified as a global muon
		// chi2/ndof of the global muon fit < 10
		// number of valid muon-detector hits used in the global fit > 0
		// Number of hits in the tracker track, Nhits, > 10.

        // pattuplified
        tags[kMuTagIsGlobal] = theMu.mu()->isGlobalMuon() ;
        tags[kMuTagNChi2]    = theMu.mu()->isGlobalMuon()
            && (theMu.mu()->globalTrack()->normalizedChi2() < _muCut_NChi2);
        tags[kMuTagNMuHits]  = theMu.mu()->isGlobalMuon()
            && (theMu.mu()->globalTrack()->hitPattern().numberOfValidMuonHits() > _muCut_NMuHits);
        tags[kMuTagNMatches] = ( theMu.mu()->numberOfMatches() > _muCut_NMuMatches);

        tags[kMuTagIsTracker] = ( theMu.mu()->isTrackerMuon() );

        tags[kMuTagIsTMLastStationAngTight] = theMu.mu()->muonID("TMLastStationTight");
        tags[kMuTagNTkHits]  = ( theMu.mu()->innerTrack()->found() > _muCut_NTrackerHits);
        tags[kMuTagNPxHits]  = ( theMu.mu()->innerTrack()->hitPattern().numberOfValidPixelHits() > _muCut_NPixelHits);
        tags[kMuTagRelPtRes] = ( TMath::Abs(theMu.mu()->track()->ptError()/theMu.mu()->pt()) < _muCut_relPtRes);

        tags[kMuTagCombIso]  = ( combIso < _muCut_combIsoOverPt );


		// additional soft muon tags
		tags[kMuTagSoftPt] = ( ev->getMuPt(i) > _muSoftCut_Pt );
		tags[kMuTagSoftHighPt] = ( ev->getMuPt(i) < _muSoftCut_HighPt);
		tags[kMuTagNotIso] = ( combIso > _muSoftCut_NotIso );

        
//         const pat::Muon* mu = theMu.mu();
//         bool id = (( (mu->isGlobalMuon()
//                         && mu->globalTrack()->normalizedChi2() <10
//                         && mu->globalTrack()->hitPattern().numberOfValidMuonHits() > 0
//                         && mu->numberOfMatches() > 1 ) 
//                     || ( mu->isTrackerMuon() 
//                         && mu->muonID("TMLastStationTight")) ) 
//                 && mu->innerTrack()->found() >10 
//                 && mu->innerTrack()->hitPattern().numberOfValidPixelHits() > 0 
//                 && fabs(mu->track()->ptError() / mu->pt()) < 0.10 );

//         if ( id != theMu.isId() ) {
//             std::cout << "chi2 " << _muCut_NChi2 
//             << " muHits " << _nuCut_NMuHits
//             << " matches" << _muCut_NMuMatches;
// //             std::string word = "765432109876543210";
//             std::string word = theMu.tags.to_string(); 
//             //             THROW_RUNTIME(
//             std::cout <<"Maputtanazza!!! " << id << " - " << theMu.isId() << " % "
//                 << word.substr(kMuTagSize-14,3) << "|" << word.substr(kMuTagSize-11,2) << "|" << word.substr(kMuTagSize-9,4)  <<  "|" << word.substr(kMuTagSize-5,5) << "// " << word<< std::endl; 
//         }
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
	// remove those which are muons
	std::set_difference(softs.begin(), softs.end(),_selectedMus.begin(),_selectedMus.end(), std::inserter(_softMus,_softMus.end()));
	Debug(3) << "- softs clean  '" ;
	std::copy( _softMus.begin(), _softMus.end(), output );
	Debug(3) << "'" << std::endl;
}

//______________________________________________________________________________
bool DileptonSelector::jetLooseId( const pat::Jet& jet ) {

    int multiplicity = jet.neutralMultiplicity () + jet.chargedMultiplicity ();

    bool looseId = false;

    looseId =
        jet.neutralEmEnergyFraction() < _jetCut_neutralEmFrac 
        && jet.neutralHadronEnergyFraction() < _jetCut_neutralHadFrac
        && multiplicity > _jetCut_multiplicity;

    if ( TMath::Abs(jet.eta()) < _etaMaxTrk ) {
        looseId &= 
            jet.chargedHadronEnergyFraction() > _jetCut_chargedHadFrac 
            && jet.chargedMultiplicity() > _jetCut_chargedMulti
            && jet.chargedEmEnergyFraction() < _jetCut_chargedEmFrac;
    }

    return looseId;
}


//_____________________________________________________________________________
void DileptonSelector::fillCtrlHistograms() {
	std::vector<ElCandicate>::iterator itEl;
	for( itEl = _elTagged.begin(); itEl!=_elTagged.end(); ++itEl) {
		_elTightCtrl->Fill(kLepTagAll, this->weight());

		if ( !itEl->tightTags[kElTagEta] ) continue;
		_elTightCtrl->Fill(kLepTagEta, this->weight());

		if ( !itEl->tightTags[kElTagLeadingPt] ) continue;
		_elTightCtrl->Fill(kLepTagPt, this->weight());

		if ( !itEl->isIso() ) continue;
		_elTightCtrl->Fill(kLepTagIsolation, this->weight());

		if ( !itEl->isId() ) continue;
		_elTightCtrl->Fill(kLepTagId, this->weight());

        if ( !itEl->tightTags[kElTagIp3D] ) continue;
        _elTightCtrl->Fill(kLepTagIp, this->weight());

		if ( !itEl->isNoConv() ) continue;
		_elTightCtrl->Fill(kLepTagNoConv, this->weight());
	}

	//std::vector<ElCandicate>::iterator it;
	for( itEl = _elTagged.begin(); itEl!=_elTagged.end(); ++itEl) {
		_elLooseCtrl->Fill(kLepTagAll, this->weight());

		if ( !itEl->looseTags[kElTagEta] ) continue;
		_elLooseCtrl->Fill(kLepTagEta, this->weight());

		if ( !itEl->looseTags[kElTagLeadingPt] ) continue;
		_elLooseCtrl->Fill(kLepTagPt, this->weight());

		if ( !itEl->isLooseIso() ) continue;
		_elLooseCtrl->Fill(kLepTagIsolation, this->weight());

		if ( !itEl->isLooseId() ) continue;
		_elLooseCtrl->Fill(kLepTagId, this->weight());

        if ( !itEl->looseTags[kElTagIp3D] ) continue;
        _elLooseCtrl->Fill(kLepTagIp, this->weight());

		if ( !itEl->isLooseNoConv() ) continue;
		_elLooseCtrl->Fill(kLepTagNoConv, this->weight());
	}

	std::vector<MuCandidate>::iterator itMu;
	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu) {
		_muGoodCtrl->Fill(kLepTagAll, this->weight());

		if ( !itMu->tags[kMuTagEta]  ) continue;
		_muGoodCtrl->Fill(kLepTagEta, this->weight());

		if ( !itMu->tags[kMuTagLeadingPt]  ) continue;
		_muGoodCtrl->Fill(kLepTagPt, this->weight());

		if ( !itMu->isIso() ) continue;
		_muGoodCtrl->Fill(kLepTagIsolation, this->weight());

		if ( !itMu->isId()  ) continue;
		_muGoodCtrl->Fill(kLepTagId, this->weight());

		if ( !itMu->tags[kMuTagIp2D] ||  !itMu->tags[kMuTagDzPV] ) continue;
		_muGoodCtrl->Fill(kLepTagIp, this->weight());

		if ( !itMu->isNoConv() ) continue;
		_muGoodCtrl->Fill(kLepTagNoConv, this->weight());
	}

	for( itMu = _muTagged.begin(); itMu != _muTagged.end(); ++itMu) {
		_muExtraCtrl->Fill(kLepTagAll, this->weight());

		if ( !itMu->tags[kMuTagEta]  ) continue;
		_muExtraCtrl->Fill(kLepTagEta, this->weight());

		if ( !itMu->tags[kMuTagExtraPt]  ) continue;
		_muExtraCtrl->Fill(kLepTagPt, this->weight());

		if ( !itMu->isIso() ) continue;
		_muExtraCtrl->Fill(kLepTagIsolation, this->weight());

		if ( !itMu->isId()  ) continue;
		_muExtraCtrl->Fill(kLepTagId, this->weight());

		if ( !itMu->tags[kMuTagIp2D] || !itMu->tags[kMuTagDzPV]   ) continue;
		_muExtraCtrl->Fill(kLepTagIp, this->weight());

		if ( !itMu->isNoConv() ) continue;
		_muExtraCtrl->Fill(kLepTagNoConv, this->weight());
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

	Debug(4) << "  - nLepToPair: " << allTags.size() 
            << "   nEl: " << _elTagged.size() <<" " <<getEvent()->getNEles()
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
    
        // hlt matching pair
//         if( !_hltMatcher->matchesBits( *iP ) ) continue;
//         (*counts)[kLLBinHltBits]++;

//         // hlt matching objects
//         if( !_hltMatcher->matchesObject( *iP ) ) continue;
//         (*counts)[kLLBinHltObject]++;

		if ( !iP->isPtEta() ) continue;
		(*counts)[kLLBinEtaPt]++;

		if ( !iP->isId() ) continue;
		(*counts)[kLLBinId]++;

		if ( !iP->isIso() ) continue;
		(*counts)[kLLBinIso]++;

		if ( !iP->isNoConv() ) continue;
		(*counts)[kLLBinNoConv]++;

		if ( !iP->isIp() ) continue;
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
void DileptonSelector::fillCounts( TH1D* h, const std::vector<unsigned int>& counts) {

	if ( counts[kLLBinDilepton] != 0 )  h->Fill(kLLBinDilepton, this->weight());
//     if ( counts[kLLBinHltBits] != 0 )   h->Fill(kLLBinHltBits, this->weight());
//     if ( counts[kLLBinHltObject] != 0 ) h->Fill(kLLBinHltObject, this->weight());
	if ( counts[kLLBinEtaPt] != 0 )     h->Fill(kLLBinEtaPt, this->weight());
	if ( counts[kLLBinId] != 0 )        h->Fill(kLLBinId, this->weight());
	if ( counts[kLLBinIso] != 0 )       h->Fill(kLLBinIso, this->weight());
	if ( counts[kLLBinNoConv] != 0 )    h->Fill(kLLBinNoConv, this->weight());
	if ( counts[kLLBinIp] != 0 )	    h->Fill(kLLBinIp, this->weight());

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
	TH1D* counters;
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

	counters->Fill(kLLBinExtraLep, this->weight());
	_llCounters->Fill(kLLBinExtraLep, this->weight());


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
	_diLepEvent->Weight       = this->weight();

    // primary vertexes
	_diLepEvent->PrimVtxGood  = ev->getPrimVtxGood();
	_diLepEvent->PrimVtxx     = ev->getPrimVtxx();
	_diLepEvent->PrimVtxy     = ev->getPrimVtxy();
	_diLepEvent->PrimVtxz     = ev->getPrimVtxz();
    _diLepEvent->NVrtx        = ev->getNVrtx();
    _diLepEvent->NPileUp      = ev->getNPileUp(); 

    const reco::MET&   tcMet = ev->getTCMET();
    const reco::PFMET& pfMet = ev->getPFMET();
    const reco::PFMET& chargedMet = ev->getChargedMET();

    math::XYZTLorentzVector p4;
    p4 = tcMet.p4();
    _diLepEvent->TCMet.SetXYZT(p4.px(), p4.py(), p4.pz(), p4.e());

    p4 = pfMet.p4();
    _diLepEvent->PFMet.SetXYZT(p4.px(), p4.py(), p4.pz(), p4.e());

    p4 = chargedMet.p4();
    _diLepEvent->ChargedMet.SetXYZT(p4.px(), p4.py(), p4.pz(), p4.e());

	_diLepEvent->NSoftMus         = _softMus.size();
	_diLepEvent->NBTaggedJets     = _btaggedJets.size();

	_diLepEvent->NEles              = _selectedEls.size();

	_diLepEvent->NMus               = _selectedMus.size();

	_diLepEvent->PFNJets            = _selectedPFJets.size();

	_diLepEvent->Els.resize(_diLepEvent->NEles);
	std::set<unsigned int>::iterator itEl = _selectedEls.begin();
	for( int i(0); i < _diLepEvent->NEles ; ++i) {
		unsigned int k = *itEl;
        HWWElectron &el = _diLepEvent->Els[i];
        //TODO use the candidate list istead of getElectrons
        // put all the variables used by the selection (same for the muons)
        
        math::XYZTLorentzVector p4  = ev->getElectrons()[k].p4();
        el.P.SetXYZT(p4.px(), p4.py(), p4.pz(), p4.e());

		el.Charge 					    = ev->getElCharge(k);
		el.SigmaIetaIeta		        = ev->getElSigmaIetaIeta(k);
		el.CaloEnergy 				    = ev->getElCaloEnergy(k);
		el.DR03TkSumPt 				    = ev->getElDR03TkSumPt(k);
		el.DR04EcalRecHitSumEt		    = ev->getElDR04EcalRecHitSumEt(k);
		el.DR04HcalTowerSumEt 		    = ev->getElDR04HcalTowerSumEt(k);
		el.NumberOfMissingInnerHits 	= ev->getElNumberOfMissingInnerHits(k);
		el.DeltaPhiSuperClusterAtVtx	= ev->getElDeltaPhiSuperClusterAtVtx(k);
		el.DeltaEtaSuperClusterAtVtx	= ev->getElDeltaEtaSuperClusterAtVtx(k);
		el.D0PV 						= ev->getElD0PV(k);
		el.DzPV 						= ev->getElDzPV(k);

		++itEl;
	}
	if ( itEl != _selectedEls.end() )
		THROW_RUNTIME("Not all electrons were copied?");

	_diLepEvent->Mus.resize(_diLepEvent->NMus);
	std::set<unsigned int>::iterator itMu = _selectedMus.begin();
    for( int i(0); i < _diLepEvent->NMus; ++i ) {
		unsigned int k = *itMu;
		HWWMuon &mu = _diLepEvent->Mus[i];


        math::XYZTLorentzVector p4  = ev->getMuons()[k].p4();
        mu.P.SetXYZT(p4.px(), p4.py(), p4.pz(), p4.e());

		mu.P.SetXYZT(ev->getMuPx(k), ev->getMuPy(k), ev->getMuPz(k), ev->getMuE(k) );
		mu.Charge                   = ev->getMuCharge(k);
		mu.Iso03SumPt               = ev->getMuIso03SumPt(k);
		mu.Iso03EmEt                = ev->getMuIso03EmEt(k);
		mu.Iso03HadEt               = ev->getMuIso03HadEt(k);
		mu.NMuHits                  = ev->getMuNMuHits(k);
		mu.NTkHits                  = ev->getMuNTkHits(k);
		mu.NChi2                    = ev->getMuNChi2(k);
		mu.IsGlobalMuon             = ev->getMuIsGlobalMuon(k);
		mu.IsTrackerMuon            = ev->getMuIsTrackerMuon(k);
		mu.IsTMLastStationAngTight  = ev->getMuIsTMLastStationAngTight(k);
		mu.D0PV                     = ev->getMuD0PV(k);
		mu.DzPV                     = ev->getMuDzPV(k);

		++itMu;
	}
	if ( itMu != _selectedMus.end() )
		THROW_RUNTIME("Not all muons were copied?");

	_diLepEvent->PFJets.resize(_diLepEvent->PFNJets);
	std::set<unsigned int>::iterator itPFJ = _selectedPFJets.begin();
	for( int i(0); i < _diLepEvent->PFNJets; ++i) {
		int k = *itPFJ;
		HWWPFJet& pfj = _diLepEvent->PFJets[i];
        math::XYZTLorentzVector p4  = ev->getPFJets()[k].p4();
        pfj.P.SetXYZT(p4.px(), p4.py(), p4.pz(), p4.e());

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

    _diLepEvent->BTaggers.CombSecVrtx           = minMax(_btag_combinedSecondaryVertex);
    _diLepEvent->BTaggers.CombSecVrtxMVA        = minMax(_btag_combinedSecondaryVertexMVA);
    _diLepEvent->BTaggers.SimpleSecVrtxHighEff  = minMax(_btag_simpleSecondaryVertexHighEff);
    _diLepEvent->BTaggers.SimpleSecVrtxHighPur  = minMax(_btag_simpleSecondaryVertexHighPur);
    _diLepEvent->BTaggers.JetBProb              = minMax(_btag_jetBProbability);
    _diLepEvent->BTaggers.JetProb               = minMax(_btag_jetProbability);
    _diLepEvent->BTaggers.TkCntHighEff          = minMax(_btag_trackCountingHighEff);
    _diLepEvent->BTaggers.TkCntHighPur          = minMax(_btag_trackCountingHighPur);
}

//_____________________________________________________________________________
void DileptonSelector::cleanJets() {
	// so far so good, let's clean the jets up

	EventProxy* ev = getEvent();

	_selectedPFJets.clear();
    _btag_combinedSecondaryVertex.clear();
    _btag_combinedSecondaryVertexMVA.clear();
    _btag_simpleSecondaryVertexHighEff.clear();
    _btag_simpleSecondaryVertexHighPur.clear();
    _btag_jetBProbability.clear();
    _btag_jetProbability.clear();
    _btag_trackCountingHighEff.clear();
    _btag_trackCountingHighPur.clear();
	// loop on pf jets now
	for ( int i=0; i<ev->getPFNJets(); ++i) {

        const math::XYZTLorentzVector& pJet = ev->getPFJets()[i].p4();
		std::set<unsigned int>::iterator it;

		bool match = false;
		// try to match the jet with an electron
		for( it=_selectedEls.begin();
				it != _selectedEls.end(); ++it) {

            const math::XYZTLorentzVector& pEl = ev->getElectrons()[*it].p4();
            match |= ( TMath::Abs(ROOT::Math::VectorUtil::DeltaR(pJet,pEl)) < _jetCut_Dr );
		}

		for( it=_selectedMus.begin();
				it != _selectedMus.end(); ++it) {
            const math::XYZTLorentzVector& pMu = ev->getMuons()[*it].p4();
            match |= ( TMath::Abs(ROOT::Math::VectorUtil::DeltaR(pJet,pMu)) < _jetCut_Dr );
		}

		if ( match ) continue;
        
        
        const pat::Jet& jet = ev->getPFJets()[i];

        double btagProb = jet.bDiscriminator("trackCountingHighEffBJetTags");
        
        // the jets must be identified
        if ( !jetLooseId( jet ) ) continue;

        
        _jetBTagProbTkCntHighEff->Fill( btagProb, this->weight());

        // store the btag probability
        _btag_combinedSecondaryVertex.push_back(jet.bDiscriminator("combinedSecondaryVertexBJetTags"));
        _btag_combinedSecondaryVertexMVA.push_back(jet.bDiscriminator("combinedSecondaryVertexMVABJetTags"));
        _btag_simpleSecondaryVertexHighEff.push_back(jet.bDiscriminator("simpleSecondaryVertexHighEffBJetTags"));
        _btag_simpleSecondaryVertexHighPur.push_back(jet.bDiscriminator("simpleSecondaryVertexHighPurBJetTags"));
        _btag_jetBProbability.push_back(jet.bDiscriminator("jetBProbabilityBJetTags"));
        _btag_jetProbability.push_back(jet.bDiscriminator("jetProbabilityBJetTags"));
        _btag_trackCountingHighEff.push_back(jet.bDiscriminator("trackCountingHighEffBJetTags"));
        _btag_trackCountingHighPur.push_back(jet.bDiscriminator("trackCountingHighPurBJetTags"));

        // check for btagged jets (any jet in the event)
        if ( btagProb > _jetCut_BtagProb )
            _btaggedJets.insert(i);

        // jet ptcut
        if ( jet.pt() > _jetCut_Pt  && TMath::Abs(jet.eta()) < _jetCut_Eta ) {
            _selectedPFJets.insert(i);
            continue;
        }
	}

}


//define this as a plug-in
DEFINE_FWK_MODULE(DileptonSelector);
