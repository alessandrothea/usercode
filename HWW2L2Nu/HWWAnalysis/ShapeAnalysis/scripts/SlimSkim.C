#include "TTree.h"
#include "TFile.h"
#include <iostream>
#include <TTreeFormula.h>
#include <TString.h>
#include <TMath.h>

using namespace std;

int SlimSkim(const char* selection, const char* input, const char* output) {

    TFile* inputFile = TFile::Open(input);
    if ( !inputFile || !inputFile->IsOpen() ) {
        cout << "Failed to open " << input << endl;
        return -1;
    }

    TString treeName = "latino";
    TTree* oldtree = (TTree*)inputFile->Get(treeName);
    if ( !oldtree ) {
        cout << "Tree " << treeName << " not found in " << input << endl;
        return -1;
    }

    TTreeFormula cut("skim",selection,oldtree);

    TFile* outputFile = TFile::Open(output,"recreate"); 
    TTree* newtree = oldtree->CloneTree(0);

    Long64_t entries = oldtree->GetEntries();
    cout << "Input events = "<< entries << endl;
    cout << "Selection  " << selection << endl;
    Long64_t counter = 0;
    for ( Long64_t i(0); i<entries; ++i) {
        oldtree->GetEntry(i);
        Double_t val = cut.EvalInstance();

        if ( i==0 || ( TMath::FloorNint(i*100/(double)entries) == TMath::CeilNint( (i-1)*100/(double)entries) )) {
            if ( i!=0 ) cout << '\r';
            int barLen = 100;
            int progress = TMath::Nint(i*barLen/(double)entries);
            string bar(progress, '=');
            bar[progress-1] = '>';
            bar.resize(barLen,' ');

            cout << " |" << bar << " " << TMath::Nint((i+1)*100/(double)entries) << "% i = " << i << flush;
        }
        if (val == 0.) continue;
        
        newtree->Fill();
        ++counter;
    }
    cout << endl;
    cout << "Output events = "<< counter << endl;

    outputFile->Write();
    outputFile->Close();

    delete outputFile;
    delete inputFile;

    return counter;

}
