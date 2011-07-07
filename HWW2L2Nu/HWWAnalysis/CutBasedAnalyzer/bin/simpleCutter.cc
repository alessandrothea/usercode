/*
 * runHWW.cc
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

#include <iostream>
#include <fstream>
#include <stdexcept>
#include <vector>
#include <algorithm>
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Utils/interface/StringObjectFunction.h"

#include "HWWAnalysis/Misc/interface/Tools.h"
#include "HWWAnalysis/CutBasedAnalyzer/interface/PsetReader.h"
#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "CommonTools/Utils/interface/TH1AddDirectorySentry.h"
#include <Reflex/Object.h>
#include <TMath.h>
#include <TSystem.h>
#include <TChain.h>
#include <TROOT.h>
#include <boost/shared_ptr.hpp>
#include <boost/format.hpp>
#include <boost/dynamic_bitset.hpp>
#include <boost/multi_array.hpp>


using namespace std;

struct BaseVariable {
    BaseVariable(const string& str, const string& formula ) : name(str),functor(formula) {}
    string name;
    StringObjectFunction<HWWNtuple> functor;

    double value( const HWWNtuple& nt ) { _last = functor(nt); return _last; }
    double last() { return _last; }
    private:
    double _last;

};

typedef boost::shared_ptr<BaseVariable> BaseVarPtr;
typedef vector<BaseVarPtr>         BaseVarVector;

//_____________________________________________________________________________
struct Variable : public BaseVariable {
    Variable(const string& str, const string& formula ) : BaseVariable(str,formula) {}
    string title;
    int bins;
    double min;
    double max;

};

typedef boost::shared_ptr<Variable> VarPtr;
typedef vector<VarPtr>         VarVector;

//_____________________________________________________________________________
struct Cut {
    Cut( const string& nm, const string& lbl, const string& cut  ) : name(nm), label(lbl), selector(cut) {}
    string name;
    string label;
    StringCutObjectSelector<HWWNtuple> selector;

    bool select( const HWWNtuple& nt) { return selector(nt); }
};

typedef boost::shared_ptr<Cut>  CutPtr;
typedef vector<CutPtr>     CutVector;

//_____________________________________________________________________________
struct Channel {

    typedef vector< pair<VarPtr, TH1D*> >  HVector;
    typedef vector< HVector > HMatrix;

    Channel( const string& nm, const string& selection ) : name(nm), selector( selection ), yield(0x0) {}
    string name;
    StringCutObjectSelector<HWWNtuple> selector;
    bool matches( const HWWNtuple& nt ) { return selector(nt); }

    HMatrix histograms;
    HMatrix nm1Histograms;
    TH1D* yield;
};

typedef vector<Channel> ChVector;


//______________________________________________________________________________
int main( int argc, char **argv ) {

    // load framework libraries
    gSystem->Load( "libFWCoreFWLite" );
    AutoLibraryLoader::enable();
    TH1::AddDirectory(false);
    
    PsetReader reader("process");

    edm::ParameterSet config = reader.read( argc, argv );
//     cout << config << endl;

    vector<string> inputFiles = config.getParameter<vector<string> >("inputFiles");
    string outputFile = config.getParameter<string>("outputFile");


    /*  _____              __ _                      
    // /  __ \            / _(_)                     
    // | /  \/ ___  _ __ | |_ _  __ _ _   _ _ __ ___ 
    // | |    / _ \| '_ \|  _| |/ _` | | | | '__/ _ \
    // | \__/\ (_) | | | | | | | (_| | |_| | | |  __/
    //  \____/\___/|_| |_|_| |_|\__, |\__,_|_|  \___|
    //                           __/ |               
    //                          |___/                
    */     


    bool doMonitor                  = config.getParameter<bool>("monitor");
    long long maxEvents             = config.getParameter<long long>("maxEvents");
    vector<string> copyHistograms   = config.getParameter<vector<string> >("copyObjects");
    bool useWeights                 = config.getParameter<bool>("useWeights");

    string treeName = config.getParameter<string>("treeName");
    // update
    TChain c(treeName.c_str());

    vector<string>::iterator iFileName;
    for ( iFileName = inputFiles.begin(); iFileName != inputFiles.end(); ++iFileName ) {
        c.Add(iFileName->c_str());
        cout << "Added " << *iFileName << endl;
    }
//     cout << "A " << inputFiles.size() << "   " << TH1::AddDirectoryStatus() << endl;

    // output
    fwlite::TFileService* fs = 0x0;
    fs = new fwlite::TFileService(outputFile);

    TObjArray buffer;
    {
//         cout << "B " << inputFiles.size() << endl;
        vector<boost::shared_ptr<TFile> >  files;
        // loop over files
        for( iFileName = inputFiles.begin(); iFileName != inputFiles.end(); ++iFileName ) {
//             cout << "C" << *iFileName << endl;
            TFile* filePtr = TFile::Open(iFileName->c_str());
            boost::shared_ptr<TFile> file(filePtr);
            gROOT->GetListOfFiles()->Remove(filePtr);
            files.push_back(file);
        }

        vector<boost::shared_ptr<TFile> >::iterator iFile;
        vector<string>::iterator iObj;
        for( iObj = copyHistograms.begin(); iObj != copyHistograms.end(); ++iObj ) {
            cout << " -cloning " << *iObj << "--" << endl;
            TH1* h = 0x0;
            for( iFile = files.begin(); iFile != files.end(); ++iFile ) {
                TH1* dummy = (TH1*)(*iFile)->Get(iObj->c_str());
                if ( !dummy ) THROW_RUNTIME("Histogram " << *iObj << " not found");

                if ( h == 0 ) {
                    h = dynamic_cast<TH1*>(dummy->Clone());
                } else {
                    h->Add(dummy);
                }

            }
            buffer.Add(h);
        }
    }

    //  long long reportEvery = config.getParameter<long long>("reportEvery");
    



    // create the variables and cuts to monitor
    edm::VParameterSet  chPars = config.getParameter<edm::VParameterSet>("channels");
    edm::VParameterSet cutPars = config.getParameter<edm::VParameterSet>("cuts");
    edm::VParameterSet varPars = config.getParameter<edm::VParameterSet>("variables");
    vector<string> monList = config.getParameter<vector<string> >("monitored");

    edm::VParameterSet::iterator itPset;
    


    cout << " -parse cuts---" << endl;
    CutVector cutflow; 

    for( itPset = cutPars.begin(); itPset != cutPars.end(); ++itPset) {
        string name  = itPset->getParameter<string>("name");
        string label = itPset->getParameter<string>("label");
        string cut   = itPset->getParameter<string>("cut");
        CutPtr theCut( new Cut(name,label,cut) );
        cutflow.push_back( theCut );
    }


    cout << " -parse variables---" << endl;

    VarVector varpool;
    for( itPset = varPars.begin(); itPset != varPars.end(); ++itPset) {
        string name  = itPset->getParameter<string>("name");
        string formula  = itPset->getParameter<string>("formula");
        VarPtr var( new Variable(name,formula) );
        
        var->bins  =  itPset->getParameter<int>("bins");
        var->min   =  itPset->getParameter<double>("min");
        var->max   =  itPset->getParameter<double>("max");
        if ( itPset->exists("title") ) {
            var->title =itPset->getParameter<string>("title");
        }
        varpool.push_back( var ); 
    }

    cout << " -monitored variables---" << endl;
    
    BaseVarVector monitored;
    vector<string>::iterator iMon;
    for ( iMon = monList.begin(); iMon != monList.end(); ++iMon ) {
       BaseVarPtr d( new BaseVariable( *iMon, *iMon) );
       monitored.push_back(d); 
    }
    
    CutVector::iterator cut;
    VarVector::iterator var;
    
    // if the output is defined...
    cout << " -build channels---" << endl;
    ChVector channels;
    for( itPset = chPars.begin(); itPset != chPars.end(); ++itPset ) {
        string name      = itPset->getParameter<string>("name");
        string selection = itPset->getParameter<string>("selection");
        
        Channel ch(name,selection);
        ch.histograms.resize(cutflow.size());
        for( size_t i(0); i<ch.histograms.size(); ++i) ch.histograms[i].resize(varpool.size() );
        ch.nm1Histograms.resize(cutflow.size());
        for( size_t i(0); i<ch.nm1Histograms.size(); ++i) ch.nm1Histograms[i].resize(varpool.size() );

        TFileDirectory dir0 = fs->mkdir(name);

        TFileDirectory dir1 = dir0.mkdir("cutflow");

        ch.yield = dir1.make<TH1D>("yield","yield",cutflow.size(),0.,cutflow.size());
        ch.yield->Sumw2();
        for( size_t k(0); k<cutflow.size(); ++k ) {
            ch.yield->GetXaxis()->SetBinLabel(k+1,cutflow[k]->name.c_str());
        }

        unsigned short j,k;
        for ( j= 0, var = varpool.begin(); var != varpool.end(); ++var, ++j ) {
            TFileDirectory d = dir1.mkdir((*var)->name);
            for( k = 0, cut = cutflow.begin(); cut != cutflow.end(); ++cut, ++k) {
                // create the cutflow histograms for each variable
                boost::format fmtName("%02d_%s_%s");
                fmtName % k % (*var)->name % (*cut)->name;
                TH1D* h = d.make<TH1D>(fmtName.str().c_str(), (*var)->title.c_str(), (*var)->bins, (*var)->min, (*var)->max);
                // add the postfix to the title
                boost::format fmtTitle("%s after %s");
                fmtTitle % (*var)->name % (*cut)->label;
                string newtitle = h->GetTitle();
                if ( newtitle.length() != 0 )
                    newtitle += " | ";
                newtitle += fmtTitle.str();
                h->SetTitle(newtitle.c_str());
                h->Sumw2();
                // histograms are stored as cut,variable
                ch.histograms[k][j] = make_pair((*var),h);
            }
        }

        TFileDirectory dir2 = dir0.mkdir("n-1");
        for( k = 0, cut = cutflow.begin(); cut != cutflow.end(); ++cut, ++k) {
            string dirname = (*cut)->name;
            replace(dirname.begin(),dirname.end(),' ','_');

            TFileDirectory d = dir2.mkdir(dirname);
            for ( j= 0, var = varpool.begin(); var != varpool.end(); ++var, ++j ) {
                boost::format fmtName("nm1_%s_%s");
                fmtName % (*cut)->name % (*var)->name ;
                TH1D* h = d.make<TH1D>(fmtName.str().c_str(), (*var)->title.c_str(), (*var)->bins, (*var)->min, (*var)->max);
                boost::format fmtTitle("( n-1 %s )");
                fmtTitle % (*cut)->label;
                string newtitle = h->GetTitle();
                if ( newtitle.length() != 0 )
                    newtitle += " | ";
                newtitle += fmtTitle.str();
                h->SetTitle(newtitle.c_str());
                h->Sumw2();
                // histograms are stored as cut,variable
                ch.nm1Histograms[k][j] = make_pair((*var),h);
            }
        }


        channels.push_back(ch);
        
    }

    cout << " -------------------" << endl;

    /*
    //  _                       
    // | |                      
    // | |     ___   ___  _ __  
    // | |    / _ \ / _ \| '_ \ 
    // | |___| (_) | (_) | |_) |
    // \_____/\___/ \___/| .__/ 
    //                   | |    
    //                   |_|    
    */     

    HWWNtuple* nt = 0x0;
    c.SetBranchAddress("nt",&nt);
    
    cout << " - " << c.GetEntries() << " entries found" << endl;

    Long64_t nEntries = c.GetEntriesFast();
    
    
    nEntries = min(nEntries,maxEvents != -1 ? maxEvents : nEntries );

    Long64_t selected = 0;
    double weighted = 0.;
    double weight = 1.;
    boost::dynamic_bitset<> cutBits(cutflow.size());
    boost::dynamic_bitset<> nm1Mask(cutflow.size());
    ChVector::iterator chan;
    BaseVarVector::iterator monVar;

    if ( doMonitor) {
        cout << "-- Monitored variables --";
        cout << "   ";
        for( monVar = monitored.begin(); monVar != monitored.end(); ++monVar) {
            cout << (*monVar)->name << '\t';
        }
        cout << endl;
    }
    cout << "-- Starting event loop --" << endl;

    string sep = " | ";
    if ( doMonitor ) {
        stringstream theStr;
        theStr << sep 
            << setw(10) << "i" << sep
            << setw(10) << "run" << sep
            << setw(10) << "ls" << sep
            << setw(10) << "event" << sep;
        for( monVar = monitored.begin(); monVar != monitored.end(); ++monVar) {
            theStr << setw(10) << (*monVar)->name << sep;
        }
        cout << theStr.str() << endl;
    }

    for ( Long64_t i(0); i<nEntries; ++i) {

        c.GetEntry(i);

        weight = useWeights ? nt->weight : 1.;

        if ( !doMonitor && (i==0 || ( TMath::FloorNint(i*100/(double)nEntries) == TMath::CeilNint( (i-1)*100/(double)nEntries) )) ) {
            if ( i!=0 ) cout << '\r';
            int barLen = 100;
            int progress = TMath::Nint(i*barLen/(double)nEntries);
            string bar(progress, '=');
            bar[progress-1] = '>';
            bar.resize(barLen,' ');

			cout << " |" << bar << " " << TMath::Nint((i+1)*100/(double)nEntries) << "% i = " << i << flush;
		}

        bool eventAccepted = false;
        for ( chan = channels.begin(); chan != channels.end(); ++chan ) {

            cutBits.reset();
            if ( ! chan->matches(*nt) ) continue;
            unsigned short k;
            bool accepted = true;
            for( k= 0,cut = cutflow.begin(); cut != cutflow.end(); ++cut, ++k) {
                cutBits.set( k, (*cut)->select(*nt) );

                accepted &= cutBits.test(k);
                if ( accepted ){ 
                    vector<pair<VarPtr,TH1D*> >::iterator iHist;
                    for ( iHist = chan->histograms[k].begin(); iHist != chan->histograms[k].end(); ++iHist ) {
                        if ( iHist->second ) iHist->second->Fill( iHist->first->value(*nt),weight );
                    }
                    chan->yield->Fill(k, weight);
                }
            }
            // re-loop for nm1 plots
            for( k = 0,cut = cutflow.begin(); cut != cutflow.end(); ++cut, ++k) {
                nm1Mask.reset();
                // set the kth bit for the kth 
                nm1Mask.set(k).flip();
                // if the selection == flipped cutbit
                if ( nm1Mask == ( nm1Mask & cutBits ) ) {
//                     cout << cutBits << " / " << nm1Mask << " / " <<  ( nm1Mask & cutBits ) << endl;
//                     cout << "N-1! " << (*cut)->name << endl;
                    // fill all the nm1 histogram associated with the cut
                    vector<pair<VarPtr,TH1D*> >::iterator iHist;
                    for ( iHist = chan->nm1Histograms[k].begin(); iHist != chan->nm1Histograms[k].end(); ++iHist ) {
                        if ( iHist->second ) iHist->second->Fill( iHist->first->value(*nt),weight );
                    }
                }
            }
            if ( !accepted ) continue;

            eventAccepted |= accepted;
        }

        if ( !eventAccepted ) continue;
        
        selected++;
        weighted += weight;
        if ( doMonitor ) {
            stringstream theStr;
            theStr << sep 
                << setw(10) << i << sep
                << setw(10) << nt->run << sep
                << setw(10) << nt->lumiSection << sep
                << setw(10) << nt->event << sep; 
            for( monVar = monitored.begin(); monVar != monitored.end(); ++monVar) {
                theStr << setw(10) << (*monVar)->value(*nt) << sep;
            }
            cout << theStr.str() << endl;
        }

    }
    
    cout << endl;
    cout << "-- Finish: selected entries " << selected << " weighted " << weighted << endl; 

    fs->cd();
    buffer.Write();


    // build the summary
    // typedef 2d multiarray of strings
    typedef boost::multi_array<string, 2> table;
    table summary(boost::extents[channels.size()+1][cutflow.size()+1]);
    
    // lengths
    vector<size_t> lens(channels.size()+1, 0);
    
    for( size_t k(0); k<cutflow.size(); ++k) {
        summary[0][k+1] = cutflow[k]->label;
        lens[0] = max(lens[0],summary[0][k+1].length());
    }

    // loop over the channels
    size_t i,j;
    for ( i=0,chan = channels.begin(); chan != channels.end(); ++i, ++chan ) {
        summary[i+1][0] = chan->name;
        lens[i+1] = summary[i+1][0].length();

        for( size_t k(0); k<cutflow.size(); ++k) {
//             cout << " - " << cutflow[k]->name << " = " << chan->yield->GetBinContent(k+1) << endl;
            summary[i+1][k+1] = Form("%.2f",chan->yield->GetBinContent(k+1) );
            lens[i+1] = max(lens[i+1],summary[i+1][k+1].length());
        }
    }

    stringstream ss;
    for( j=0; j<summary.shape()[1]; ++j) {
        for( i=0; i<summary.shape()[0]; ++i ) {
            ss.width( lens[i] );
            ss << internal << summary[i][j] << " | ";
        }
        ss << endl;
    }

    cout << ss.str() << endl;
    
    cout << "-- Cleanup" << endl;
    if (fs) delete fs;
	return 0;
}
