void checkCuts() {

    gSystem->Load("lib/libHWWNtuple.so");

    TChain chain("hwwSkim");

    chain.AddFile("../ntuples/H130.root");


    HWWEvent* ev = new HWWEvent();

    chain.SetBranchAddress("ev", &ev);

    std::cout << ev << std::endl;
    chain.GetEntry(0);

    TH1F* eeMass = new TH1F("eeMass", "eeMass", 100, 10., 200.);
    TH1F* uuMass = new TH1F("uuMass", "uuMass", 100, 10., 200.);
    for( Long64_t i(0); i < chain.GetEntriesFast(); ++i) {
    	chain.GetEntry(i);
    	if ( ev->NEles ==2 ) {
    		Float_t mass = (ev->Els[0].P+ev->Els[1].P).Mag();
//    		std::cout << mass << std::endl;
    		eeMass->Fill(mass);
    	}

        if( ev->NMus == 2 ) {
    		Float_t mass = (ev->Mus[0].MuP+ev->Mus[1].MuP).Mag();
    		uuMass->Fill(mass);

        }
    }
    TCanvas* canvas = new TCanvas("c1","c1", 400, 600);
    canvas->Divide(1,2);

    canvas->cd(1);
    eeMass->Draw();
    canvas->cd(2);
    uuMass->Draw();
}
