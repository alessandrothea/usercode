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
#include "HWWAnalysis/DataFormats/interface/HWWNtuple.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Utils/interface/StringObjectFunction.h"

#include "HWWAnalysis/Misc/interface/Tools.h"
#include "HWWAnalysis/CutBasedAnalyzer/interface/PsetReader.h"
#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include <Reflex/Object.h>
#include <TSystem.h>
#include <TChain.h>
#include <boost/shared_ptr.hpp>
#include <boost/format.hpp>
#include <boost/dynamic_bitset.hpp>
#include <boost/multi_array.hpp>

//_____________________________________________________________________________
struct Variable {
    Variable(const std::string& str, const std::string& formula ) : name(str),functor(formula) {}
    std::string name;
    StringObjectFunction<HWWNtuple> functor;
    int bins;
    double min;
    double max;

    double value( const HWWNtuple& nt ) { _last = functor(nt); return _last; }
    double last() { return _last; }
    private:
    double _last;
};

typedef boost::shared_ptr<Variable> VarPtr;
typedef std::vector<VarPtr>         VarVector;

//_____________________________________________________________________________
struct Cut {
    Cut( const std::string& nm, const std::string& cut  ) : name(nm), selector(cut) {}
    std::string name;
    StringCutObjectSelector<HWWNtuple> selector;

    bool select( const HWWNtuple& nt) { return selector(nt); }
};

typedef boost::shared_ptr<Cut>  CutPtr;
typedef std::vector<CutPtr>     CutVector;

//_____________________________________________________________________________
struct Channel {

    typedef std::vector< std::vector< std::pair<VarPtr, TH1D*> > > HMatrix;

    Channel( const std::string& nm, const std::string& selection ) : name(nm), selector( selection ), yield(0x0) {}
    std::string name;
    StringCutObjectSelector<HWWNtuple> selector;
    bool matches( const HWWNtuple& nt ) { return selector(nt); }

    HMatrix histograms;
    TH1D* yield;
};

typedef std::vector<Channel> ChVector;

int main( int argc, char **argv ) {

    // load framework libraries
    gSystem->Load( "libFWCoreFWLite" );
    AutoLibraryLoader::enable();
    
    PsetReader reader("process");

    edm::ParameterSet config = reader.read( argc, argv );
//     std::cout << config << std::endl;


    std::vector<std::string> inputFiles = config.getParameter<std::vector<std::string> >("inputFiles");
    std::string outputFile = config.getParameter<std::string>("outputFile");

    TChain c("hwwAnalysis");

    std::vector<std::string>::iterator it;
    for ( it = inputFiles.begin(); it != inputFiles.end(); ++it )
        c.Add(it->c_str());


    /*  _____              __ _                      
    // /  __ \            / _(_)                     
    // | /  \/ ___  _ __ | |_ _  __ _ _   _ _ __ ___ 
    // | |    / _ \| '_ \|  _| |/ _` | | | | '__/ _ \
    // | \__/\ (_) | | | | | | | (_| | |_| | | |  __/
    //  \____/\___/|_| |_|_| |_|\__, |\__,_|_|  \___|
    //                           __/ |               
    //                          |___/                
    */     

    // create the variables and cuts to monitor
    edm::VParameterSet  chPars = config.getParameter<edm::VParameterSet>("channels");
    edm::VParameterSet cutPars = config.getParameter<edm::VParameterSet>("cuts");
    edm::VParameterSet varPars = config.getParameter<edm::VParameterSet>("variables");

    edm::VParameterSet::iterator itPset;

    std::cout << " -parse cuts---" << std::endl;
    CutVector cutflow; 

    for( itPset = cutPars.begin(); itPset != cutPars.end(); ++itPset) {
        std::string name = itPset->getParameter<std::string>("name");
        std::string cut   = itPset->getParameter<std::string>("cut");
        CutPtr theCut( new Cut(name,cut) );
        cutflow.push_back( theCut );
    }


    std::cout << " -parse variables---" << std::endl;
    VarVector varpool;
    for( itPset = varPars.begin(); itPset != varPars.end(); ++itPset) {
        std::string name  = itPset->getParameter<std::string>("name");
        std::string formula  = itPset->getParameter<std::string>("formula");
        VarPtr var( new Variable(name,formula) );
        
        var->bins  =  itPset->getParameter<int>("bins");
        var->min   =  itPset->getParameter<double>("min");
        var->max   =  itPset->getParameter<double>("max");
        varpool.push_back( var ); 
    }


    fwlite::TFileService fs(outputFile);

    
    CutVector::iterator cut;
    VarVector::iterator var;
    
    std::cout << " -build channels---" << std::endl;
    ChVector channels;
    for( itPset = chPars.begin(); itPset != chPars.end(); ++itPset ) {
        std::string name      = itPset->getParameter<std::string>("name");
        std::string selection = itPset->getParameter<std::string>("selection");
        
        Channel ch(name,selection);
        ch.histograms.resize(cutflow.size());
        for( size_t i(0); i<ch.histograms.size(); ++i) ch.histograms[i].resize(varpool.size() );

        TFileDirectory dir0 = fs.mkdir(name);

        ch.yield = dir0.make<TH1D>("yield","yield",cutflow.size(),0.,cutflow.size());
        ch.yield->Sumw2();
        for( size_t k(0); k<cutflow.size(); ++k ) {
            ch.yield->GetXaxis()->SetBinLabel(k+1,cutflow[k]->name.c_str());
        }

        unsigned short j;
        for ( j= 0, var = varpool.begin(); var != varpool.end(); ++var, ++j ) {
            TFileDirectory d = dir0.mkdir((*var)->name);
            unsigned short k;
            for( k = 0, cut = cutflow.begin(); cut != cutflow.end(); ++cut, ++k) {
                boost::format fmtName("%02d_%s_%s");
                fmtName % k % (*var)->name % (*cut)->name;
                boost::format fmtTitle("%s after %s");
                fmtTitle % (*var)->name % (*cut)->name;
                TH1D* h = d.make<TH1D>(fmtName.str().c_str(), fmtTitle.str().c_str(), (*var)->bins, (*var)->min, (*var)->max);
                h->Sumw2();
                // histograms are stored as cut,variable
                ch.histograms[k][j] = std::make_pair((*var),h);
            }
        }

        channels.push_back(ch);
        
    }

    std::cout << " -------------------" << std::endl;

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
    
    std::cout << " - " << c.GetEntries() << " entries found" << std::endl;

    Long64_t nEntries = c.GetEntriesFast();
//     nEntries = 10;
    

    Long64_t selected = 0;
    double weighted = 0.;
    boost::dynamic_bitset<> cutBits(cutflow.size());
    ChVector::iterator chan;
    for ( Long64_t i(0); i<nEntries; ++i) {

        cutBits.reset();
        c.GetEntry(i);

        bool eventAccepted = false;
        for ( chan = channels.begin(); chan != channels.end(); ++chan ) {

            if ( ! chan->matches(*nt) ) continue;
            unsigned short k;
            bool accepted = true;
            for( k= 0,cut = cutflow.begin(); cut != cutflow.end(); ++cut, ++k) {
                cutBits.set( k, (*cut)->select(*nt) );

                accepted &= cutBits.test(k);
                //             std::string dummy;
                //             boost::to_string(cutBits,dummy);
                //             std::cout << k <<" '" << dummy << "' " << accepted << "/" << cutBits.test(k) << std::endl;
                //             if ( !(*cut)->select(*nt) ) accepted = true;
                if ( accepted ){ 
                    std::vector<std::pair<VarPtr,TH1D*> >::iterator iHist;
                    for ( iHist = chan->histograms[k].begin(); iHist != chan->histograms[k].end(); ++iHist ) {
                        iHist->second->Fill( iHist->first->value(*nt)*nt->weight );
                    }
                    chan->yield->Fill(k, nt->weight);
                }
            }
            if ( !accepted ) continue;

            eventAccepted |= accepted;
        }

        if ( !eventAccepted ) continue;
        
        selected++;
        weighted += nt->weight;


    }
    
    std::cout << " Finish: selected entries " << selected << " weighted " << weighted << std::endl; 
    typedef boost::multi_array<std::string, 2> table;
    table summary(boost::extents[channels.size()+1][cutflow.size()+1]);

    std::vector<size_t> lens(channels.size()+1, 0);
    
    for( size_t k(0); k<cutflow.size(); ++k) {
        summary[0][k+1] = cutflow[k]->name;
        lens[0] = std::max(lens[0],summary[0][k+1].length());
    }

    size_t i,j;
    for ( i=0,chan = channels.begin(); chan != channels.end(); ++i, ++chan ) {
//         std::cout << "-" << chan->name << "-cutflow-------------" << std::endl;
        summary[i+1][0] = chan->name;
        lens[i+1] = summary[i+1][0].length();

        for( size_t k(0); k<cutflow.size(); ++k) {
//             std::cout << " - " << cutflow[k]->name << " = " << chan->yield->GetBinContent(k+1) << std::endl;
            summary[i+1][k+1] = Form("%.2f",chan->yield->GetBinContent(k+1) );
            lens[i+1] = std::max(lens[i+1],summary[i+1][k+1].length());
        }
    }

    std::stringstream ss;
    for( j=0; j<summary.shape()[1]; ++j) {
        for( i=0; i<summary.shape()[0]; ++i ) {
            ss.width( lens[i] );
            ss << std::internal << summary[i][j] << " | ";
        }
        ss << std::endl;
    }

    std::cout << ss.str() << std::endl;

	return 0;
}
