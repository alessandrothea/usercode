/*
 * HWWAnalyzer.cc
 *
 *  Created on: Dec 14, 2010
 *      Author: ale
 */

#include "HWWAnalysis/CutBasedAnalyzer/interface/HWWAnalyzer.h"
#include "HWWAnalysis/Misc/interface/Tools.h"
#include "HWWAnalysis/CutBasedAnalyzer/interface/Razor.h"
#include "HWWAnalysis/DataFormats/interface/HWWEvent.h"
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"
#include <TChain.h>
#include <TFile.h>
#include <TVector3.h>
#include <TLorentzVector.h>
#include <stdexcept>
#include <algorithm>
#include <fstream>
#include <TH1D.h>
#include <THashList.h>
#include <TH2D.h>


const double HWWAnalyzer::_Z0Mass = 9.11869999999999976e+01;

//_____________________________________________________________________________
void HWWAnalyzer::HiggsCutSet::print() {
        std::cout << hMass << '\t'
                << minPtHard << '\t'
                << minPtSoft << '\t'
                << maxMll << '\t'
                << maxDphi << '\t'
                << minR << '\t'
                << maxR << '\t'
                << std::endl;
}

//_____________________________________________________________________________
HWWAnalyzer::HWWAnalyzer(int argc, char** argv) : UserAnalyzer(argc,argv), _nthMask(kCutsSize),
        _hEntries(0x0), _analysisTree(0x0), _event(0x0), _ntuple(0x0) {

    _analysisTreeName = _config.getValue<std::string>("HWWAnalyzer.analysisTreeName");

    _higgsMass        = _config.getValue<int>("HWWAnalyzer.higgsMass");

    _cutFile          = _config.getValue<std::string>("HWWAnalyzer.cutFile");
    _minMet           = _config.getValue<double>("HWWAnalyzer.minMet");
    _minMll           = _config.getValue<double>("HWWAnalyzer.minMll");
    _zVetoWidth       = _config.getValue<double>("HWWAnalyzer.zVetoWidth");

    _minProjMetEM     = _config.getValue<double>("HWWAnalyzer.minProjMetEM");
    _minProjMetLL     = _config.getValue<double>("HWWAnalyzer.minProjMetLL");

    _histLabels = _config.getVector<std::string>("HWWAnalyzer.copyHistograms");

    //std::copy(_histLabels.begin(), _histLabels.end(), output);

    readHiggsCutSet( _cutFile );

    _theCuts = getHiggsCutSet( _higgsMass );

    // initialize the bitmask
    higgsBitWord dummy( (1 << kCutsSize )-1);
    dummy.set(0,0).set(1,0);
    _theMask = dummy;

    // initialize the n-1 masks
    for( int k=2; k<kCutsSize; ++k) {
        _nthMask[k] = _theMask;
        _nthMask[k].set(k,false);
//         std::cout << _nthMask[k].to_string() << std::endl;
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

    
    bookHistogramSet(_llHistograms, "ll");
    bookHistogramSet(_eeHistograms, "ee");
    bookHistogramSet(_emHistograms, "em");
    bookHistogramSet(_meHistograms, "me");
    bookHistogramSet(_mmHistograms, "mm");

    _output->mkdir("jetVeto")->cd();
    _jetN      = new TH1D("jetN",    "n_{jets} (pre-veto)", 20, 0, 20);
    _jetPt     = new TH1D("jetPt",   "Jet Pt (pre-veto)",   100, 0, 1000);
    _jetEta    = new TH1D("jetEta",  "Jet Eta (pre-veto)",  100, -5, 5);

    _output->mkdir("bTags")->cd();
    _btagCombinedSecondaryVertex        = new TH1D("combinedSecondaryVertex","combinedSecondaryVertex",2000,-10,10);
    _btagCombinedSecondaryVertexMVA     = new TH1D("combinedSecondaryVertexMVA","combinedSecondaryVertexMVA",2000,-10,10);
    _btagSimpleSecondaryVertexHighEff   = new TH1D("simpleSecondaryVertexHighEff","simpleSecondaryVertexHighEff",2000,-10,10);
    _btagSimpleSecondaryVertexHighPur   = new TH1D("simpleSecondaryVertexHighPur","simpleSecondaryVertexHighPur",2000,-10,10);
    _btagJetBProbability                = new TH1D("jetBProbability","jetBProbability",400,0,10);
    _btagJetProbability                 = new TH1D("jetProbability","jetProbability",400,0,10);
    _btagTrackCountingHighEff           = new TH1D("tkCountingHighEff","tkCountingHighEff",2000,-100,100);
    _btagTrackCountingHighPur           = new TH1D("tkCountingHighPur","tkCountingHighPur",2000,-100,100);

    _output->mkdir("pileUp")->cd();
    _nVrtx     = new TH1D("nVrtx",   "n_{vrtx}", 20, 1, 21);
    _llJetNVsNvrtx = makeNjetsNvrtx("llNjetsNvrtx");
    _eeJetNVsNvrtx = makeNjetsNvrtx("eeNjetsNvrtx", "ee - ");
    _emJetNVsNvrtx = makeNjetsNvrtx("emNjetsNvrtx", "em - ");
    _meJetNVsNvrtx = makeNjetsNvrtx("meNjetsNvrtx", "me - ");
    _mmJetNVsNvrtx = makeNjetsNvrtx("mmNjetsNvrtx", "mm - ");

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
        TH1D* entries = (TH1D*)_chain->GetCurrentFile()->Get((_folder+"/entries").c_str());
        if ( !entries )
            std::cout << "Warning: Preselection entries not found" << std::endl;
        else
            _hEntries->Add(entries);

        std::vector<std::string>::iterator it;
        for( it = _histLabels.begin(); it!=_histLabels.end();it++) {
            TH1D* h = (TH1D*)_chain->GetCurrentFile()->Get( (_folder+'/'+*it).c_str());
            if ( !h ) {
                std::cout << "Warning: histogram "<< *it << " not found" << std::endl;
                continue;
            }

            if ( _hists.find(*it) == _hists.end() ) {
                _hists[*it] = (TH1D*)h->Clone();
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
void HWWAnalyzer::bookDiHistograms( std::vector<TH1D*>& histograms , const std::string& nPrefix, const std::string& lPrefix ){

    // all numbers to 0, just to be sure;
    histograms.assign(kDiSize,0x0);

    histograms[kDiPfMet]            = new TH1D((nPrefix+"PfMet").c_str(),             (lPrefix+"PfMET").c_str(), 200, 0, 200);
    histograms[kDiTcMet]            = new TH1D((nPrefix+"TcMet").c_str(),             (lPrefix+"TcMET").c_str(), 200, 0, 200);
    histograms[kDiChargedMet]       = new TH1D((nPrefix+"ChargedMet").c_str(),        (lPrefix+"ChargedMET").c_str(), 200, 0, 200);
    histograms[kDiProjPfMet]        = new TH1D((nPrefix+"ProjPfMet").c_str(),         (lPrefix+"Projected PfMET").c_str(), 200, 0, 200);
    histograms[kDiProjTcMet]        = new TH1D((nPrefix+"ProjTcMet").c_str(),         (lPrefix+"Projected TcMET").c_str(), 200, 0, 200);
    histograms[kDiProjChargedMet]   = new TH1D((nPrefix+"ProjChargedMet").c_str(),    (lPrefix+"Projected ChargedMET").c_str(), 200, 0, 200);
    histograms[kDiLeadPt]           = new TH1D((nPrefix+"LeadingPt").c_str(),         (lPrefix+"p^{lead}").c_str(), 200, 0, 200);
    histograms[kDiTrailPt]          = new TH1D((nPrefix+"TrailingPt").c_str(),        (lPrefix+"p^{trail}").c_str(), 200, 0, 200);
    histograms[kDiMll]              = new TH1D((nPrefix+"Mll").c_str(),               (lPrefix+"m^{ll}").c_str(),   300, 0,  300);
    histograms[kDiDeltaPhi]         = new TH1D((nPrefix+"DeltaPhi").c_str(),          (lPrefix+"#Delta#Phi_{ll}").c_str(), 180, 0, 180.);
    histograms[kDiGammaMRStar]      = new TH1D((nPrefix+"GammaMRstar").c_str(),       (lPrefix+"#gammaMR^{*}").c_str(), 100, 0, 200.);
    
}

//_____________________________________________________________________________
void HWWAnalyzer::bookExtraHistograms(std::vector<TH1D*>& histograms, const std::string& nPrefix, const std::string& lPrefix) {
    
    // all numbers to 0, just to be sure;
    histograms.assign(kExtraSize,0x0);

    histograms[kExtraDeltaPhi]      = new TH1D((nPrefix+"DeltaPhi").c_str(),     (lPrefix+"#Delta#Phi_{ll}").c_str(), 180, 0, 180.);
    Double_t edges[] = {0., 45., 60., 90., 135., 150., 180. };
    histograms[kExtraDeltaPhiBands] = new TH1D((nPrefix+"DeltaPhiBands").c_str(), (lPrefix+"#Delta#Phi_{ll} Bands").c_str(), 6, edges);
    
}

//_____________________________________________________________________________
void HWWAnalyzer::bookCutHistograms( std::vector<TH1D*>& histograms , const std::string& nPrefix, const std::string& lPrefix ) {

    // all numbers to 0, just to be sure;
    histograms.assign(kCutsSize,0x0);

    histograms[kMinMet]     = new TH1D(("01_"+nPrefix+"MinMet").c_str(),     (lPrefix+"min #slash E_{T}").c_str(),        100, 0, 100);
    histograms[kMinMll]     = new TH1D(("02_"+nPrefix+"MinMll").c_str(),     (lPrefix+"m^{ll}_{min}").c_str(),    300, 0, 300);
    histograms[kZveto]      = new TH1D(("03_"+nPrefix+"Zveto").c_str(),      (lPrefix+"Z veto").c_str(),          300, 0, 300);
    histograms[kProjMet]    = new TH1D(("04_"+nPrefix+"MinProjMet").c_str(), (lPrefix+"Proj #slash E_{T}").c_str(),   100, 0, 100);
    histograms[kJetVeto]    = new TH1D(("05_"+nPrefix+"JetVeto").c_str(),    (lPrefix+"n_{jets} = 0").c_str(),     15, 0, 15);
    histograms[kSoftMuon]   = new TH1D(("06_"+nPrefix+"SoftMuon").c_str(),   (lPrefix+"No Soft #mu").c_str(),      10, 0,10);
    histograms[kTopVeto]    = new TH1D(("07_"+nPrefix+"TopVeto").c_str(),    (lPrefix+"Top Veto").c_str(),         10, 0,10);
    histograms[kMaxMll]     = new TH1D(("08_"+nPrefix+"MaxMll").c_str(),     (lPrefix+"m^{ll}_{max}").c_str(),    300, 0,  300);
    histograms[kLeadPtMin]  = new TH1D(("09_"+nPrefix+"MinLeadPt").c_str(),  (lPrefix+"p^{lead}_{min}").c_str(),  100, 0, 3.*_theCuts.minPtHard);
    histograms[kTrailPtMin] = new TH1D(("10_"+nPrefix+"MinTrailPt").c_str(), (lPrefix+"p^{trail}_{min}").c_str(),  100, 0, 3.*_theCuts.minPtSoft);
    histograms[kDeltaPhi]   = new TH1D(("11_"+nPrefix+"DeltaPhi").c_str(),   (lPrefix+"#Delta#Phi_{ll}").c_str(), 180, 0, 180.);
    histograms[kRazor]      = new TH1D(("12_"+nPrefix+"Razor").c_str(),      (lPrefix+"2*#gammaMR^{*}/M_{higgs}").c_str(), 100, 0., 2.);

}

//______________________________________________________________________________
void HWWAnalyzer::bookHistogramSet( HistogramSet& set, const std::string& name ) {
    

    _output->cd();
    TDirectory* dir = _output->mkdir(name.c_str());
    dir->cd();

    std::map<int,std::string> labels;

    labels[kSkimmed] = "N_{l^{+}l^{-}}";
    labels[kMinMet]    = "min #slash E_{T}";
    labels[kMinMll]    = "m^{ll}_{min}";
    labels[kZveto]     = "Z veto";
    labels[kProjMet]   = "Proj#slash E_{T}";
    labels[kJetVeto]   = "n_{jets} == 0";
    labels[kSoftMuon]  = "No Soft #mu";
    labels[kTopVeto]   = "Top Veto";
    labels[kMaxMll]    = "m^{ll}_{max}";
    labels[kLeadPtMin] = "p^{lead}_{min}";
    labels[kTrailPtMin] = "p^{trail}_{min}";
    labels[kDeltaPhi]  = "#Delta#Phi_{ll}";
    labels[kRazor]     = "2#gamma^{*} MR^{*}/M_{higgs}";

    set.counters = makeLabelHistogram(name+"Counters",name+"Counters",labels);

    dir->mkdir("skim")->cd();
    bookDiHistograms( set.dileptons, name, name + " - ");
    dir->mkdir("cuts")->cd();
    bookCutHistograms( set.preCuts,  name+"Pre",  name+" PreCut - ");
    bookCutHistograms( set.postCuts, name+"Post", name+" PostCut - ");

    dir->mkdir("extra")->cd();
    bookExtraHistograms( set.extra, name, name + " - " );

    dir->mkdir("Nminus1")->cd();
    bookCutHistograms( set.nm1Cut, name+"Nm1", name+" N-1 Plot - " );
    
    // fill the matrix with null pointers
    set.cutByCut.resize(kLogSize);
    for ( size_t i(0); i <set.cutByCut.size(); ++i )
        set.cutByCut[i].assign(kCutsSize,0x0);


    dir->cd();

    // variables to track
    std::vector<std::string> vars;
    vars.resize(kLogSize);
    vars[kLogNJets]     = "nJets";
    vars[kLogNSoftMus]  = "nSoftMus";
    vars[kLogNBjets]    = "nBjets";
    vars[kLogMet]       = "met";
    vars[kLogProjMet]   = "projMet";
    vars[kLogMll]       = "mll";
    vars[kLogPtLead]    = "ptLead";
    vars[kLogPtTrail]   = "ptTrail";
    vars[kLogDphi]      = "dPhi";
    vars[kLogRazor]     = "Razor";


    std::vector<std::string>::iterator it;
    for ( it = vars.begin();it != vars.end(); ++it )
        dir->mkdir(it->c_str());

    // name tag for the cuts
    std::vector<std::string > cuts;
    cuts.resize(kCutsSize);
    cuts[kSkimmed]  = "skim";
    cuts[kMinMet]     = "minMet";
    cuts[kMinMll]     = "minMll";
    cuts[kZveto]      = "Zveto";
    cuts[kProjMet]    = "projMet";
    cuts[kJetVeto]    = "jVeto";
    cuts[kSoftMuon]   = "softMus";
    cuts[kTopVeto]    = "topVeto";
    cuts[kMaxMll]     = "maxMll";
    cuts[kLeadPtMin]  = "minPtLead";
    cuts[kTrailPtMin] = "minPtTrail";
    cuts[kDeltaPhi]   = "maxDphi";
    cuts[kRazor]      = "razor";

    for ( int k = kSkimmed; k<kCutsSize; ++k ) {
        // list of variables starts from 0
        for ( size_t i(0); i < vars.size(); ++i ){
            dir->cd(vars[i].c_str());
            std::string name  = Form("%02d_%s_%s",k,vars[i].c_str(),cuts[k].c_str());
            std::string title = Form("%s after %s",vars[i].c_str(),cuts[k].c_str());
            set.cutByCut[i][k] = makeVarHistogram( i, name, title);
            
        }
    }


}

//______________________________________________________________________________
TH1D* HWWAnalyzer::makeVarHistogram( int code, const std::string& name, const std::string& title ) {
    TH1D* histogram = 0x0;
    switch ( code ) {
        case kLogNJets:
        case kLogNSoftMus:
        case kLogNBjets:
            histogram = new TH1D(name.c_str(), title.c_str(),10,0,10);
            histogram->SetXTitle("N");
            break;

        case kLogMet:
        case kLogProjMet:
            histogram = new TH1D(name.c_str(), title.c_str(),100,0,100);
            histogram->SetXTitle("GeV");
            break;

        case kLogMll:
            histogram = new TH1D(name.c_str(), title.c_str(),300,0,300);
            histogram->SetXTitle("GeV");
            break;

        case kLogPtLead:
        case kLogPtTrail:
            histogram = new TH1D(name.c_str(), title.c_str(),200,0,200);
            histogram->SetXTitle("GeV");
            break;

        case kLogDphi:
            histogram = new TH1D(name.c_str(), title.c_str(),180,0,180);
            histogram->SetXTitle("deg");
            break;

        case kLogRazor:
            histogram = new TH1D(name.c_str(), title.c_str(),100,0,2);
            break;

        default:
            THROW_RUNTIME("Variable code " << code << " not supported");
    }
    return histogram;
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

        ss >> h.minPtHard >> h.minPtSoft >> h.maxMll >> h.maxDphi >> h.minR >> h.maxR;

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
void HWWAnalyzer::fillNtuple(){

    TLorentzVector pA, pB;
    Int_t cA(0), cB(0);
    double d0A(0), d0B(0);
    double dZA(0), dZB(0);
    unsigned short type = 0;

//  std::cout << "Neles " << _event->NEles << "   NMus " << _event->NMus << std::endl;

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
            type = kMuEl_t;
        }


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

        type = kMuMu_t;

        break;
    }

    // we work on the assumption A is the highet pT lepton, B is not. This is a watchdog
    if ( pB.Pt() > pA.Pt() ) {
        THROW_RUNTIME("A.Pt < B.Pt");
    }

    // 3 - invariant mass
    double mll = (pA+pB).Mag();

    TLorentzVector& pfMet4 = _event->PFMet;
    TLorentzVector& tcMet4 = _event->TCMet;
    TLorentzVector& chargedMet4 = _event->ChargedMet;

    // 4a pfMet
    double pfMet = pfMet4.Pt();
    // 4b - tcMet
    double tcMet = tcMet4.Pt();
    // 4c - chargedMet
    double chargedMet = chargedMet4.Pt();

    // 5 - projected MeT
    // 5a - projPfMet

    double pfMetDphi = TMath::Min(
            TMath::Abs(pfMet4.DeltaPhi( pA )),
            TMath::Abs(pfMet4.DeltaPhi( pB ))
            );

    double projPfMet = pfMet*(pfMetDphi < TMath::PiOver2() ? TMath::Sin(pfMetDphi) : 1.);

    // 5b - projTcMet

    double tcMetDphi = TMath::Min(
            TMath::Abs(tcMet4.DeltaPhi( pA )),
            TMath::Abs(tcMet4.DeltaPhi( pB ))
            );

    double projTcMet = tcMet*(tcMetDphi < TMath::PiOver2() ? TMath::Sin(tcMetDphi) : 1.);

    // 5c - projChargedMet
    double chargedMetDphi = TMath::Min(
            TMath::Abs(chargedMet4.DeltaPhi( pA )),
            TMath::Abs(chargedMet4.DeltaPhi( pB ))
            );

    double projChargedMet = chargedMet*(chargedMetDphi < TMath::PiOver2() ? TMath::Sin(chargedMetDphi) : 1.);

    // 6 - dPhiEE
    double dPhiLL = TMath::Abs(pA.DeltaPhi(pB));

    double dPhiLLJet = -TMath::TwoPi();
    // 7 1-jet case
    if ( _event->PFNJets == 1 ) {
        TLorentzVector pJet = _event->PFJets[0].P;
        TLorentzVector pLL  = pA+pB;
        dPhiLLJet           = TMath::Abs(pJet.DeltaPhi(pLL));
    }

    _ntuple->type = type;

    _ntuple->run           = _event->Run;
    _ntuple->lumiSection   = _event->LumiSection;
    _ntuple->event         = _event->Event;
    _ntuple->weight        = _event->Weight;

    _ntuple->nVrtx         = _event->NVrtx;
    _ntuple->nPileUp       = _event->NPileUp;

    _ntuple->cA            = cA;
    _ntuple->cB            = cB;

    _ntuple->pA.SetXYZT(pA.X(),pA.Y(),pA.Z(),pA.T());
    _ntuple->pB.SetXYZT(pB.X(),pB.Y(),pB.Z(),pB.T());
//     _ntuple->pB            = pB;
    
    _ntuple->d0A           = d0A;
    _ntuple->d0B           = d0B;

    _ntuple->dZA           = dZA;
    _ntuple->dZB           = dZB;

    _ntuple->mll           = mll;

    _ntuple->pfMet         = pfMet;
    _ntuple->tcMet         = tcMet;
    _ntuple->chargedMet    = chargedMet;


    _ntuple->pfMetDphi     = pfMetDphi;
    _ntuple->tcMetDphi     = tcMetDphi;
    _ntuple->chargedMetDphi = chargedMetDphi;

    _ntuple->projPfMet     = projPfMet;
    _ntuple->projTcMet     = projTcMet;
    _ntuple->projChargedMet  = projChargedMet;

    _ntuple->minProjMet    = TMath::Min(_ntuple->projPfMet, _ntuple->projChargedMet);

    _ntuple->met           = _ntuple->pfMet;
    _ntuple->projMet       = _ntuple->minProjMet;

    _ntuple->mrStar        = razor::MRstar(pA,pB);
    _ntuple->gammaMRstar   = razor::gammaMRstar(pA,pB);

    _ntuple->razor         = 2*_ntuple->gammaMRstar/(float)_higgsMass;


    _ntuple->dPhi          = dPhiLL;
    _ntuple->nJets         = _event->PFNJets;
    _ntuple->nSoftMus      = _event->NSoftMus;
    _ntuple->nBJets        = _event->NBTaggedJets;

    _ntuple->dPhillj       = dPhiLLJet;

}

//______________________________________________________________________________
void HWWAnalyzer::fillDiLeptons(std::vector<TH1D*>& dilep ) {
    dilep[kDiPfMet]->Fill(_ntuple->pfMet, getWeight() );
    dilep[kDiTcMet]->Fill(_ntuple->tcMet, getWeight() );
    dilep[kDiChargedMet]->Fill(_ntuple->tcMet, getWeight() );
    
    dilep[kDiProjPfMet]->Fill(_ntuple->projPfMet, getWeight() );
    dilep[kDiProjTcMet]->Fill(_ntuple->projTcMet, getWeight() );
    dilep[kDiProjChargedMet]->Fill(_ntuple->projTcMet, getWeight() );
    
    dilep[kDiLeadPt]->Fill(_ntuple->pA.Pt(), getWeight() );
    dilep[kDiTrailPt]->Fill(_ntuple->pB.Pt(), getWeight() );
    dilep[kDiMll]->Fill(_ntuple->mll, getWeight() );
    dilep[kDiDeltaPhi]->Fill(TMath::RadToDeg()*_ntuple->dPhi, getWeight() );
    dilep[kDiGammaMRStar]->Fill(_ntuple->gammaMRstar,getWeight());

}


//______________________________________________________________________________
void HWWAnalyzer::fillNminus1(std::vector<TH1D*>& nm1, higgsBitWord word ){

    if ( (word & _nthMask[kMinMet]) == _nthMask[kMinMet] )
        nm1[kMinMet]->Fill(_ntuple->met, getWeight() );

    if ( (word & _nthMask[kMinMll]) == _nthMask[kMinMll] )
        nm1[kMinMll]->Fill(_ntuple->mll, getWeight() );

    if ( (word & _nthMask[kZveto]) == _nthMask[kZveto] )
        nm1[kZveto]->Fill(_ntuple->mll, getWeight() );

    if ( (word & _nthMask[kProjMet]) == _nthMask[kProjMet] )
        nm1[kProjMet]->Fill( _ntuple->projMet , getWeight() );

    if ( (word & _nthMask[kJetVeto]) == _nthMask[kJetVeto] )
        nm1[kJetVeto]->Fill(_ntuple->nJets, getWeight() );

    if ( (word & _nthMask[kSoftMuon]) == _nthMask[kSoftMuon] )
        nm1[kSoftMuon]->Fill(_ntuple->nSoftMus, getWeight() );

    if ( (word & _nthMask[kTopVeto]) == _nthMask[kTopVeto] )
        nm1[kTopVeto]->Fill(_ntuple->nBJets, getWeight() );

    if ( (word & _nthMask[kLeadPtMin]) == _nthMask[kLeadPtMin] )
        nm1[kLeadPtMin]->Fill(_ntuple->pA.Pt(), getWeight() );

    if ( (word & _nthMask[kTrailPtMin]) == _nthMask[kTrailPtMin] )
        nm1[kTrailPtMin]->Fill(_ntuple->pB.Pt(), getWeight() );

    if ( (word & _nthMask[kMaxMll]) == _nthMask[kMaxMll] )
        nm1[kMaxMll]->Fill(_ntuple->mll, getWeight() );

    if ( (word & _nthMask[kDeltaPhi]) == _nthMask[kDeltaPhi] )
        nm1[kDeltaPhi]->Fill(TMath::RadToDeg()*_ntuple->dPhi, getWeight() );

    if ( (word & _nthMask[kRazor]) == _nthMask[kRazor] )
        nm1[kRazor]->Fill(_ntuple->razor, getWeight() );
    
}
    
//______________________________________________________________________________
void HWWAnalyzer::fillExtra(std::vector<TH1D*>& extra ) {
    
    if ( _ntuple->mll < 12. || _ntuple->mll > 60. ) return;
    if ( _ntuple->nJets != 0 ) return;
    if ( _ntuple->pB.Pt() < 30. ) return;
//     if ( _ntuple->pfMet < 30. ) return;

    extra[kExtraDeltaPhi]->Fill(_ntuple->dPhi*TMath::RadToDeg(), getWeight() );
    extra[kExtraDeltaPhiBands]->Fill(_ntuple->dPhi*TMath::RadToDeg(), getWeight() );

}

//______________________________________________________________________________
void HWWAnalyzer::fillVariables( HistogramSet* histograms, HCuts_t cutCode ) {

    histograms->cutByCut[kLogNJets][cutCode]->Fill( _ntuple->nJets, getWeight());

    histograms->cutByCut[kLogNSoftMus][cutCode]->Fill( _ntuple->nSoftMus, getWeight());

    histograms->cutByCut[kLogNBjets][cutCode]->Fill( _ntuple->nBJets, getWeight());

    histograms->cutByCut[kLogMet][cutCode]->Fill( _ntuple->met, getWeight());

    histograms->cutByCut[kLogProjMet][cutCode]->Fill( _ntuple->projMet, getWeight());

    histograms->cutByCut[kLogMll][cutCode]->Fill( _ntuple->mll, getWeight());

    histograms->cutByCut[kLogPtLead][cutCode]->Fill( _ntuple->pA.Pt(), getWeight());

    histograms->cutByCut[kLogPtTrail][cutCode]->Fill( _ntuple->pB.Pt(), getWeight());

    histograms->cutByCut[kLogDphi][cutCode]->Fill( _ntuple->dPhi*TMath::RadToDeg(), getWeight());

    histograms->cutByCut[kLogRazor][cutCode]->Fill( _ntuple->razor, getWeight());

}

//______________________________________________________________________________
void HWWAnalyzer::fillBtaggers() {
    // cmbSecVrtx
    std::vector<double>& cmbSecVrtx = _event->BTaggers.CombSecVrtx;
    if ( cmbSecVrtx.size() != 0 )
        _btagCombinedSecondaryVertex->Fill( *std::max_element(cmbSecVrtx.begin(),cmbSecVrtx.end()),getWeight() );

    // cmbSecVrtx
    std::vector<double>& cmbSecVrtxMVA = _event->BTaggers.CombSecVrtxMVA;
    if ( cmbSecVrtxMVA.size() != 0 )
        _btagCombinedSecondaryVertexMVA->Fill( *std::max_element(cmbSecVrtxMVA.begin(),cmbSecVrtxMVA.end()),getWeight() );

    // simpleSecVrtxHEff
    std::vector<double>& simpleSecVrtxHEff = _event->BTaggers.SimpleSecVrtxHighEff;
    if ( simpleSecVrtxHEff.size() != 0 )
        _btagSimpleSecondaryVertexHighEff->Fill( *std::max_element(simpleSecVrtxHEff.begin(),simpleSecVrtxHEff.end()),getWeight() );

    // simpleSecVrtxHPur
    std::vector<double>& simpleSecVrtxHPur = _event->BTaggers.SimpleSecVrtxHighPur;
    if ( simpleSecVrtxHPur.size() != 0 )
        _btagSimpleSecondaryVertexHighPur->Fill( *std::max_element(simpleSecVrtxHPur.begin(),simpleSecVrtxHPur.end()),getWeight() );

    // jetBProbability
    std::vector<double>& jetBProb = _event->BTaggers.JetBProb;
    if ( jetBProb.size() != 0 )
        _btagJetBProbability->Fill( *std::max_element(jetBProb.begin(),jetBProb.end()),getWeight() );

    // jetProb
    std::vector<double>& jetProb = _event->BTaggers.JetProb;
    if ( jetProb.size() != 0 )
        _btagJetProbability->Fill( *std::max_element(jetProb.begin(),jetProb.end()),getWeight() );

    // TrackCountingHighEff
    std::vector<double>& tkCntHEff = _event->BTaggers.TkCntHighEff;
    if ( tkCntHEff.size() != 0 )
        _btagTrackCountingHighEff->Fill( *std::max_element(tkCntHEff.begin(),tkCntHEff.end()),getWeight() );
    // TrackCountingHighPur
    std::vector<double>& tkCntHPur = _event->BTaggers.TkCntHighPur;
    if ( tkCntHPur.size() != 0 )
        _btagTrackCountingHighPur->Fill( *std::max_element(tkCntHPur.begin(),tkCntHPur.end()),getWeight() );
}

//_____________________________________________________________________________
void HWWAnalyzer::cutAndFill() {

    higgsBitWord word;

//     double met = _ntuple->tcMet;
//     double projMet = _ntuple->projTcMet;
//     double met = _ntuple->pfMet;
    

    bool isMixedFlavour = _ntuple->type == kElMu_t || _ntuple->type == kMuEl_t;

    word[kMinMet]     = ( _ntuple->met > _minMet );

    word[kMinMll]     = ( _ntuple->mll > _minMll);

    word[kZveto]      = ( isMixedFlavour || TMath::Abs(_ntuple->mll - _Z0Mass) > _zVetoWidth );

    float minProjMet  = isMixedFlavour ? _minProjMetEM : _minProjMetLL;
    word[kProjMet]    = ( _ntuple->projMet > minProjMet);

    word[kJetVeto]    = ( _ntuple->nJets == 0);

    word[kSoftMuon]   = ( _ntuple->nSoftMus == 0);

    word[kTopVeto]    = ( _ntuple->nBJets == 0 );

    word[kLeadPtMin]  = ( _ntuple->pA.Pt() > _theCuts.minPtHard);

    word[kTrailPtMin] = ( _ntuple->pB.Pt() > _theCuts.minPtSoft);

    //TODO check if maxMll applies to all the combinations
    word[kMaxMll]     = ( _ntuple->mll < _theCuts.maxMll);

    word[kDeltaPhi]   = ( _ntuple->dPhi < _theCuts.maxDphi*TMath::DegToRad() );

    word[kRazor]      = ( _ntuple->razor > _theCuts.minR && _ntuple->razor < _theCuts.maxR );

    _ntuple->tags     = word.to_ulong();


    HistogramSet* histograms;
    TH2D* nJnV;
    switch ( _ntuple->type ) {
    case kElEl_t:
        histograms = &_eeHistograms;
        nJnV     = _eeJetNVsNvrtx;
        break;
    case kElMu_t:
        histograms = &_emHistograms;
        nJnV     = _emJetNVsNvrtx;
        break;
    case kMuEl_t:
        histograms = &_meHistograms;
        nJnV     = _meJetNVsNvrtx;
        break;

    case kMuMu_t:
        histograms = &_mmHistograms;
        nJnV     = _mmJetNVsNvrtx;
        break;
    default:
        THROW_RUNTIME("Wrong event type : " << _ntuple->type );
    };


    fillDiLeptons( histograms->dileptons );
    fillExtra( histograms->extra );
    fillNminus1( histograms->nm1Cut, word );

    _nVrtx->Fill(_event->NVrtx, getWeight() );

    //-----------
    //-----------

    histograms->counters->Fill(kSkimmed, getWeight() );

    fillVariables( histograms, kSkimmed);

    // min missing Et
    histograms->preCuts[kMinMet]->Fill(_ntuple->met, getWeight() );
    if ( !word[kMinMet] ) return;
    histograms->counters->Fill(kMinMet, getWeight() );
    histograms->postCuts[kMinMet]->Fill(_ntuple->met, getWeight() );

    fillVariables( histograms, kMinMet);

    // min invariant mass
    histograms->preCuts[kMinMll]->Fill(_ntuple->mll, getWeight() );
    if ( !word[kMinMll] ) return;
    histograms->counters->Fill(kMinMll, getWeight() );
    histograms->postCuts[kMinMll]->Fill(_ntuple->mll, getWeight() );

    fillVariables( histograms, kMinMll);

    // Z veto (m_ll-m_Z < 15 GeV)
    histograms->preCuts[kZveto]->Fill(_ntuple->mll, getWeight() );
    if ( !word[kZveto] ) return;
    histograms->counters->Fill(kZveto, getWeight() );
    histograms->postCuts[kZveto]->Fill(_ntuple->mll, getWeight() );
    
    fillVariables( histograms, kZveto);

    // proj Met (20 GeV for ee)
    histograms->preCuts[kProjMet]->Fill(_ntuple->projMet, getWeight() );
    if ( !word[kProjMet] ) return;
    histograms->counters->Fill(kProjMet, getWeight() );
    histograms->postCuts[kProjMet]->Fill(_ntuple->projMet, getWeight() );

    fillVariables( histograms, kProjMet);

    // pause here for jet pt and eta
    _jetN->Fill(_event->PFJets.size(), getWeight() );
    for ( unsigned int i(0); i<_event->PFJets.size(); ++i) {
        _jetPt->Fill(_event->PFJets[i].P.Pt(), getWeight() );
        _jetEta->Fill(_event->PFJets[i].P.Eta(), getWeight() );
    }

    nJnV->Fill(_event->NVrtx, _event->PFJets.size(), getWeight() );

    // njets == 0
    histograms->preCuts[kJetVeto]->Fill(_ntuple->nJets, getWeight() );
    if ( !word[kJetVeto] ) return;
    histograms->counters->Fill(kJetVeto, getWeight() );
    histograms->postCuts[kJetVeto]->Fill(_ntuple->nJets, getWeight() );

    fillVariables( histograms, kJetVeto);

    // soft muon
    histograms->preCuts[kSoftMuon]->Fill(_ntuple->nSoftMus, getWeight() );
    if ( !word[kSoftMuon] ) return;
    histograms->counters->Fill(kSoftMuon, getWeight() );
    histograms->postCuts[kSoftMuon]->Fill(_ntuple->nSoftMus, getWeight() );

    fillVariables( histograms, kSoftMuon);

    fillBtaggers();

    // top veto
    histograms->preCuts[kTopVeto]->Fill(_ntuple->nBJets, getWeight() );
    if ( !word[kTopVeto] ) return;
    histograms->counters->Fill(kTopVeto, getWeight() );
    histograms->postCuts[kTopVeto]->Fill(_ntuple->nBJets, getWeight() );

    fillVariables( histograms, kTopVeto);

    // Mll_max
    histograms->preCuts[kMaxMll]->Fill(_ntuple->mll, getWeight() );
    if ( !word[kMaxMll] ) return;
    histograms->counters->Fill(kMaxMll, getWeight() );
    histograms->postCuts[kMaxMll]->Fill(_ntuple->mll, getWeight() );

    fillVariables( histograms, kMaxMll);

    // hard pt cut
    histograms->preCuts[kLeadPtMin]->Fill(_ntuple->pA.Pt(), getWeight() );
    if ( !word[kLeadPtMin] ) return;
    histograms->counters->Fill(kLeadPtMin, getWeight() );
    histograms->postCuts[kLeadPtMin]->Fill(_ntuple->pA.Pt(), getWeight() );

    fillVariables( histograms, kLeadPtMin);

    // soft pt cut
    histograms->preCuts[kTrailPtMin]->Fill(_ntuple->pB.Pt(), getWeight() );
    if ( !word[kTrailPtMin] ) return;
    histograms->counters->Fill(kTrailPtMin, getWeight() );
    histograms->postCuts[kTrailPtMin]->Fill(_ntuple->pB.Pt(), getWeight() );

    fillVariables( histograms, kTrailPtMin);

    // delta phi
    histograms->preCuts[kDeltaPhi]->Fill(TMath::RadToDeg()*_ntuple->dPhi, getWeight() );
    if ( !word[kDeltaPhi] ) return;
    histograms->counters->Fill(kDeltaPhi, getWeight() );
    histograms->postCuts[kDeltaPhi]->Fill(TMath::RadToDeg()*_ntuple->dPhi, getWeight() );

    fillVariables( histograms, kDeltaPhi);

    // razor [not used]
    histograms->preCuts[kRazor]->Fill(_ntuple->razor, getWeight() );
    if ( !word[kRazor] ) return;
    histograms->counters->Fill(kRazor, getWeight() );
    histograms->postCuts[kRazor]->Fill(_ntuple->razor, getWeight() );

    fillVariables( histograms, kRazor);

    _ntuple->selected = true;


}

//_____________________________________________________________________________
void HWWAnalyzer::Process( Long64_t iEvent ) {
//  std::cout << iEvent <<  std::endl;
    _chain->GetEntry(iEvent);

    _ntuple->clear();
//     _btaggedJets.clear();
//     _selectedJets.clear();

//     sortJets();

    if ( _event->NEles + _event->NMus != 2 )
        THROW_RUNTIME("Wrong number of leptons in the event: NEles = " << _event->NEles << " NMus = " << _event->NMus  );

    fillNtuple();
    cutAndFill();

    _analysisTree->Fill();
}

//_____________________________________________________________________________
void HWWAnalyzer::EndJob() {

    _eeHistograms.counters->SetEntries(_eeHistograms.counters->GetBinContent(1));
    _emHistograms.counters->SetEntries(_emHistograms.counters->GetBinContent(1));
    _meHistograms.counters->SetEntries(_meHistograms.counters->GetBinContent(1));
    _mmHistograms.counters->SetEntries(_mmHistograms.counters->GetBinContent(1));

    _llHistograms.counters->Add(_eeHistograms.counters);
    _llHistograms.counters->Add(_emHistograms.counters);
    _llHistograms.counters->Add(_meHistograms.counters);
    _llHistograms.counters->Add(_mmHistograms.counters);

    for ( unsigned int k(0); k < _llHistograms.dileptons.size(); ++k ) {
        _llHistograms.dileptons[k]->Add(_eeHistograms.dileptons[k]);
        _llHistograms.dileptons[k]->Add(_emHistograms.dileptons[k]);
        _llHistograms.dileptons[k]->Add(_meHistograms.dileptons[k]);
        _llHistograms.dileptons[k]->Add(_mmHistograms.dileptons[k]);

    }

    // pre cuts
    for ( unsigned int k(0); k<_llHistograms.preCuts.size(); ++k ) {
        if( !_llHistograms.preCuts[k] ) continue;
        _llHistograms.preCuts[k]->Add( _eeHistograms.preCuts[k]);
        _llHistograms.preCuts[k]->Add( _emHistograms.preCuts[k]);
        _llHistograms.preCuts[k]->Add( _meHistograms.preCuts[k]);
        _llHistograms.preCuts[k]->Add( _mmHistograms.preCuts[k]);
    }

    // post cuts
    for ( unsigned int k(0); k<_llHistograms.postCuts.size(); ++k ) {
        if( !_llHistograms.postCuts[k] ) continue;
        _llHistograms.postCuts[k]->Add( _eeHistograms.postCuts[k]);
        _llHistograms.postCuts[k]->Add( _emHistograms.postCuts[k]);
        _llHistograms.postCuts[k]->Add( _meHistograms.postCuts[k]); //TODO
        _llHistograms.postCuts[k]->Add( _mmHistograms.postCuts[k]);
    }

    // extra histograms
    for ( unsigned int k(0); k < _llHistograms.extra.size(); ++k ) {
        if( !_llHistograms.extra[k] ) continue;
        _llHistograms.extra[k]->Add(_eeHistograms.extra[k]);
        _llHistograms.extra[k]->Add(_emHistograms.extra[k]);
        _llHistograms.extra[k]->Add(_meHistograms.extra[k]);
        _llHistograms.extra[k]->Add(_mmHistograms.extra[k]);

    }

    for ( unsigned int k(0); k<_llHistograms.nm1Cut.size(); ++k) {
        if (!_llHistograms.nm1Cut[k] ) continue;
        _llHistograms.nm1Cut[k]->Add(_eeHistograms.nm1Cut[k]);
        _llHistograms.nm1Cut[k]->Add(_emHistograms.nm1Cut[k]);
        _llHistograms.nm1Cut[k]->Add(_meHistograms.nm1Cut[k]);
        _llHistograms.nm1Cut[k]->Add(_mmHistograms.nm1Cut[k]);
    }
    

    // cutByCut
    for( size_t i(0); i<_llHistograms.cutByCut.size(); ++i)
        for( size_t k(0); k<_llHistograms.cutByCut[i].size(); ++k) {
            if ( !_llHistograms.cutByCut[i][k] ) continue;
            _llHistograms.cutByCut[i][k]->Add(_eeHistograms.cutByCut[i][k]);
            _llHistograms.cutByCut[i][k]->Add(_emHistograms.cutByCut[i][k]);
            _llHistograms.cutByCut[i][k]->Add(_meHistograms.cutByCut[i][k]);
            _llHistograms.cutByCut[i][k]->Add(_mmHistograms.cutByCut[i][k]);
        }
    

    _llJetNVsNvrtx->Add(_eeJetNVsNvrtx);
    _llJetNVsNvrtx->Add(_emJetNVsNvrtx);
    _llJetNVsNvrtx->Add(_meJetNVsNvrtx); //TODO
    _llJetNVsNvrtx->Add(_mmJetNVsNvrtx);

    _output->mkdir("lepSelection")->cd();
    std::map<std::string,TH1D*>::iterator it;
    for( it = _hists.begin(); it!=_hists.end();it++) {
        it->second->Write();
    }

    _output->mkdir("fullSelection")->cd();


    glueCounters(_eeHistograms.counters);
    glueCounters(_emHistograms.counters);
    glueCounters(_meHistograms.counters);
    glueCounters(_mmHistograms.counters);
    glueCounters(_llHistograms.counters);

}

//_____________________________________________________________________________
TH2D* HWWAnalyzer::makeNjetsNvrtx( const std::string& name, const std::string& prefix  ) {
    int nJets(20), nVrtx(20);
    TH2D* h2 = new TH2D(name.c_str(),(prefix+"n_{jets} vs .n_{vrtx}").c_str(),
            nVrtx, 1, nVrtx+1, nJets, 0, nJets);
    h2->GetXaxis()->SetTitle("n_{vrtx}");
    h2->GetYaxis()->SetTitle("n_{jets} p_{T} > 25 GeV");
    return h2;
}

//_____________________________________________________________________________
TH1D* HWWAnalyzer::makeLabelHistogram( const std::string& name, const std::string& title, std::map<int,std::string> labels) {
    int xmin = labels.begin()->first;
    int xmax = labels.begin()->first;

    std::map<int, std::string>::iterator it;
    for( it = labels.begin(); it != labels.end(); ++it ) {
        xmin = it->first < xmin ? it->first : xmin;
        xmax = it->first > xmax ? it->first : xmax;
    }

    ++xmax;
    int nbins = xmax-xmin;

    TH1D* h = new TH1D(name.c_str(), title.c_str(), nbins, xmin, xmax);
    for( it = labels.begin(); it != labels.end(); ++it ) {
        int bin = h->GetXaxis()->FindBin(it->first);
        h->GetXaxis()->SetBinLabel(bin, it->second.c_str());
    }

    return h;

}
//_____________________________________________________________________________
TH1D* HWWAnalyzer::glueCounters(TH1D* counters) {

    std::string name = counters->GetName();
    std::map<std::string,TH1D*>::iterator it = _hists.find(name);
    if ( it == _hists.end() ) return 0x0;
    TH1D* cntPreSel = it->second;


    // make a copy
    std::string clone_name = counters->GetName();
    clone_name += "_copy";
    bool add = TDirectory::AddDirectoryStatus();
    TDirectory::AddDirectory(kFALSE);
    TH1D* cntCopy = dynamic_cast<TH1D*>(counters->Clone( clone_name.c_str() ));
    TDirectory::AddDirectory(add);

    int nBins    = cntCopy->GetNbinsX();
    int nBinsPre = cntPreSel->GetNbinsX();

    // check bin content
    double preSelectedEntries = cntPreSel->GetBinContent(nBinsPre);
    double processedEntries = cntCopy->GetBinContent(1);
    // define mismtch ad the ratio bewtween the difference and the preselected entries
    double mismatch = TMath::Abs( (preSelectedEntries- processedEntries) );

    if ( TMath::Abs(mismatch/(double)preSelectedEntries) > 1E-6 )
        std::cout << TermColors::kYellow << "Mismatch (" << name << ") = " << mismatch << " over " << preSelectedEntries << TermColors::kReset<< std::endl;
//     if ( TMath::Abs(mismatch/) > 1E-6 )
//         THROW_RUNTIME("Bin Content Mismatch: Wrong histogram?\n"
//                 << cntPreSel->GetName() << " (" << nBinsPre << ") : " 
//                 << cntPreSel->GetXaxis()->GetBinLabel(nBinsPre) << "=" << preSelectedEntries << "\n"
//                 << cntCopy->GetName() << " (" << nBins << ") : " 
//                 << cntCopy->GetXaxis()->GetBinLabel(1) << "="<< processedEntries);

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
    TH1D* hNew = new TH1D(cntPreSel->GetName(),cntPreSel->GetTitle(),nBinsNew,xmin,xmax);

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
