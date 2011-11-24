// Hard-coded things
//   static TString names[nsample+1]
//            = { "ggWW", "Vg", "WJet", "Top", "WW", "VV", "DYtau", "DY", "ggH", "vbfH", "Data" };
//   TString histdir = "./finalhisto/";
//   TString histPrefix = "histo_";
//   TString datadir = "./Scenario1/";
//            --> taken from CVS UserCode/emanuele/HiggsAnalysisTools/datacards/Oct21st2011/Scenario1/
//   TString oname = Form("hww-2.13fb.mH%s.%s_%dj_shape",
//           masses[im].Data(),channames[ichan].Data(), ijet);
//   TString fname = Form("histo_H%s_%djet_mllmtPreSel_%s.root",
//		     masses[im].Data(), ijet, channames[ichan].Data());
// 
// There are some other things regarding the systematics naming that depends on "names"
//
//////////////////////////////////////////////////////////////////////////////////////////////////

#include "TSystem.h"
#include "TStyle.h"
#include "TChain.h"
#include "TFile.h"
#include "THStack.h"
#include "TH2.h"
#include "TCanvas.h"
#include "TPad.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TLine.h"
#include "TMath.h"
#include "TSystem.h"

#include <iostream>
#include <fstream>
#include <vector>

using namespace std;

vector<TH1D*> gethistos(TFile *f, TString hname);
map<TString, map<TString,vector<TH1D*> > > getSystHistos( TFile *f, const TString& prefix );
void getsyst(TString cname, float mass, float &N, float &s, float &u);

// channels

static const int njet(2);

static const int nchannel(2);
static TString channames[nchannel] = { "sf", "of" };
static TString chanlabels[nchannel] = { "ee/mm", "em/me" };

// higgs mass hypotheses

static const int nmass(22);
static TString masses[nmass] = {"110","115","120","130","140","150","160","170","180","190",
    "200","210","220","230","250","300","350","400","450","500",
    "550","600"};
static int imasses[nmass] = {110,115,120,130,140,150,160,170,180,190,
    200,210,220,230,250,300,350,400,450,500,
    550,600};

/* static const int nmass(1); */
/* static TString masses[nmass] = {"130"}; */
/* static int imasses[nmass] = {130}; */

// background and signal processes

static const int nsample(10);
static TString names[nsample+1] 
= { "ggWW", "Vg", "WJet", "Top", "WW", "VV", "DYtau", "DY", "ggH", "vbfH", "Data" };
static int processes[nsample+1] 
= {      1,    2,      3,     4,    5,    6,    7,       8,     0,     -1,    100 };

// systematics 

// data-driven estimates
static const int nsyst_data(4);
static TString syst_dname[nsyst_data] = { "Top", "WW", "ggWW", "DY" };
// type of systematics, log-normal or multiplicatie-gamma
static TString syst_dtype[nsyst_data] = { "lnN", "lnN", "lnN", "gmM" };
// info from Twiki http://hepuser.ucsd.edu/twiki2/bin/view/Latinos/October21st
static int syst_dctrl[nsyst_data][njet] // N in control region used for WW-level estimates  
= { { 131, 491 }, { 350, 198 }, { 350, 198 }, { (79+108), (71+93) } }; 
static float syst_derr[nsyst_data][njet] // fractional error on estimates
= { { -1, -1 }, { -1, -1 }, { -1, -1 }, { 0.64, 0.52 } }; // except DY, take from datacards

// experimental systematics
static const float scale_WW[2] = { 0.95, 1.21 };
static const float eff_e    = 1.02;
static const float eff_m    = 1.02;
static const TString eff_proc(" Vg VV DYtau ggH vbfH "); // only for pure MC predictions
static const float p_scale_e = 1.02;
static const float p_scale_m = 1.01;
static const TString p_l_proc(" Vg VV DYtau ggH vbfH ");
static const float p_scale_j = 1.02;
static const TString p_j_proc(" Vg VV DYtau ggH vbfH ");
static const float fake_e   = 1.29; // take the average of ee/me
static const float fake_m   = 1.34; // take the average of mm/em
static const float fake_Vg  = 2.00;
static const float met      = 1.02;
// different values for 0-jet, 1-jet bins
static const TString met_proc(" Vg VV DYtau ggH vbfH ");
static const float QCDscale_VV[2] = { 1.04, 1.04 };
static const float QCDscale_Vg[2] = { 1.50, 0 }; // not for 1jet bin
static const float QCDscale_ggH[2] = { 1.11, 0 }; // not for 1jet bin
static const float QCDscale_ggH1in[2] = { 0.99, 1.55 };
static const float QCDscale_ggH2in[2] = { 0.  , 0.88 }; // not for 0jet bin
static const float QCDscale_ggH_ACEPT[2] = { 1.02, 1.02 };
static const float QCDscale_ggVV[2] = { 1.5, 1.5 }; 
static const float QCDscale_qqH[2] = { 1.01, 1.01 };
static const float QCDscale_qqH_ACEPT[2] = { 1.02, 1.02 };
static const float ueps     = 0.94;
static const TString ueps_proc(" ggH ");
static const float lumi     = 1.04;
static const TString lumi_proc(" Vg VV DYtau ggH vbfH ");
// sample dependent
static const float pdf_gg[2] = { 1.0, 1.08 };
static const TString pdf_gg_proc[2] = { "ggWW", "ggH" };
static const float pdf_qqbar[3] = { 1.0, 1.04, 1.02 };
static const TString pdf_qqbar_proc[3] = { "WW", "VV", "vbfH" };

// shape systematics
static TString syst_samples[] = { "Top", "VV", "WW", "ggWW","vbfH", "ggH" }; 
static TString syst_effect[]  = { "eff_l","met","p_res_e","p_scale_e","p_scale_j","p_scale_m"};

// take the same for all channels since e/m effects (sort of) average for of/sf 
// --> to be reconsidered when shape systematics are in place
void load_systematics(int ijet,
        vector<TString> &syst_fname, vector<TString> &syst_fproc, vector<float> &syst_fval) {

    // QCD scale
    syst_fname.push_back("CMS_QCDscale_WW_EXTRAP");
    syst_fproc.push_back(" WW ");
    syst_fval.push_back(scale_WW[ijet]);
    // lepton efficiency
    syst_fname.push_back("CMS_eff_e\t");
    syst_fproc.push_back(eff_proc); 
    syst_fval.push_back(eff_e);
    syst_fname.push_back("CMS_eff_m\t");
    syst_fproc.push_back(eff_proc); 
    syst_fval.push_back(eff_m);
    // fake lepton
    syst_fname.push_back("CMS_fake_e\t");
    syst_fproc.push_back(" WJet ");
    syst_fval.push_back(fake_e);
    syst_fname.push_back("CMS_fake_m\t");
    syst_fproc.push_back(" WJet ");
    syst_fval.push_back(fake_m);
    // fake from gamma
    if (!ijet) {
        syst_fname.push_back("CMS_fake_Vg\t");
        syst_fproc.push_back(" Vg ");
        syst_fval.push_back(fake_Vg);
    }
    // met
    syst_fname.push_back("CMS_met\t\t");
    syst_fproc.push_back(met_proc);
    syst_fval.push_back(met);
    // energy scale
    syst_fname.push_back("CMS_p_scale_e\t");
    syst_fproc.push_back(p_l_proc);
    syst_fval.push_back(p_scale_e);
    syst_fname.push_back("CMS_p_scale_m\t");
    syst_fproc.push_back(p_l_proc);
    syst_fval.push_back(p_scale_m);
    syst_fname.push_back("CMS_p_scale_j\t");
    syst_fproc.push_back(p_j_proc);
    syst_fval.push_back(p_scale_j);
    // QCD scale
    syst_fname.push_back("QCDscale_VV\t");
    syst_fproc.push_back(" VV ");
    syst_fval.push_back(QCDscale_VV[ijet]);
    syst_fname.push_back("QCDscale_Vg\t");
    syst_fproc.push_back(" Vg ");
    syst_fval.push_back(QCDscale_Vg[ijet]);
    if (!ijet) {
        syst_fname.push_back("QCDscale_ggH\t");
        syst_fproc.push_back("ggH");
        syst_fval.push_back(QCDscale_ggH[ijet]);
    }
    syst_fname.push_back("QCDscale_ggH1lin");
    syst_fproc.push_back(" ggH ");
    syst_fval.push_back(QCDscale_ggH1in[ijet]);
    if (ijet) {
        syst_fname.push_back("QCDscale_ggH2lin");
        syst_fproc.push_back(" ggH ");
        syst_fval.push_back(QCDscale_ggH2in[ijet]);
    } 
    syst_fname.push_back("QCDscale_ggH_ACEPT");
    syst_fproc.push_back(" ggH ");
    syst_fval.push_back(QCDscale_qqH_ACEPT[ijet]);
    syst_fname.push_back("QCDscale_qqH\t");
    syst_fproc.push_back("qqH");
    syst_fval.push_back(QCDscale_qqH[ijet]);
    syst_fname.push_back("QCDscale_qqH_ACEPT");
    syst_fproc.push_back(" ggH ");
    syst_fval.push_back(QCDscale_qqH_ACEPT[ijet]);
    // others
    syst_fname.push_back("UEPS\t\t");
    syst_fproc.push_back(ueps_proc);
    syst_fval.push_back(ueps);
    syst_fname.push_back("lumi\t\t");
    syst_fproc.push_back(lumi_proc);
    syst_fval.push_back(lumi);

    return;
}

// some formats in the card
static TString intro("## Shape (BDT) input card for H->WW analysis using 2.12/fb\n");
static TString header("imax 1 number of channels\njmax * number of background\nkmax * number of nuisance parameters\n");
static TString hline("------------------------------------------------------------------------------------------------------------------\n");

void make_datacards()
{

    TH2::SetDefaultSumw2(1);

    TString histdir = "./finalhisto/";
    TString dataCardDir = "./datacards/";
    TString histPrefix = "histo_";
    TString datadir = "./Scenario1/";

    gSystem->mkdir(dataCardDir,kTRUE);

    ofstream datacard;
/*     datacard.open(""); */

    for (int ijet=0; ijet<njet; ++ijet) {

        for (int ichan=0; ichan<nchannel; ++ichan) {

            for (int im=0; im<nmass; ++im) {
                //if (im!=3) continue;
                int mass = imasses[im];

                //
                // datacard datacard for limits
                //

                TString oname = Form("hww-2.13fb.mH%s.%s_%dj_shape", 
                        masses[im].Data(),channames[ichan].Data(), ijet);
                datacard.open((dataCardDir+oname+".txt").Data());
                // headers
                datacard << intro << header << hline;
                // channel
                TString binname = Form("%s_%dj", channames[ichan].Data(), ijet); 
                datacard << "bin\t\t" << binname << endl;

                //
                // datacard histos for limits
                //

                TString fname = Form("histo_H%s_%djet_mllmtPreSel_%s.root", 
                        masses[im].Data(), ijet, channames[ichan].Data());
                printf("get histos from file %s\n", (histdir+fname).Data());
                TFile *f = new TFile(histdir+fname,"READ");
                vector<TH1D*> histos = gethistos(f, histPrefix);
                // data
                float nd = histos[nsample]->Integral(0,histos[nsample]->GetNbinsX()+1);
                datacard << Form("observation\t%.0f\n", nd);
                // datacard file
                datacard << Form("shapes\t*\t* %s\thisto_$PROCESS histo_$PROCESS_$SYSTEMATIC\n", (oname+".root").Data());
                datacard << Form("shapes\tdata_obs\t* %s\thisto_%s\n", (oname+".root").Data(), names[nsample].Data());
                datacard << hline;
                // background and signal processes
                TString bin("bin\t\t\t\t\t");
                TString prol("process\t\t\t\t\t");
                TString pron("process\t\t\t\t\t");
                TString rate("rate\t\t\t\t\t");
                for (int i=0; i<histos.size()-1; ++i) {
                    if (channames[ichan] == "of" && names[i] == "DY" ) continue; 
                    //  printf("histo %d %.1f\n", i, ((TH1D*)histos[i])->GetEntries());
                    bin+=("\t"+binname);
                    prol+=("\t"+names[i]);
                    pron+=(Form("\t%d", processes[i]));
                    float np = histos[i]->Integral(0,histos[i]->GetNbinsX()+1);
                    if (ijet==1 && names[i]=="Vg") np = 0; // no Vg for 1-jet
                    rate+=(Form("\t%.3f", np));
                }
                datacard << bin << endl << prol << endl << pron << endl << rate << endl << hline;

                // 
                // systematics from experimental and theoretical aspects
                //

                // from list of flat systematics
                vector<TString> syst_fname;
                vector<TString> syst_fproc;
                vector<float>   syst_fval;
                load_systematics(ijet, syst_fname, syst_fproc, syst_fval);
                TString line("");
                for (unsigned int isyst=0; isyst<syst_fname.size(); ++isyst) {
                    line=syst_fname[isyst]+"\t\tlnN\t";
                    for (int is=0; is<nsample; ++is) {
                        if (channames[ichan] == "of" && names[is] == "DY" ) continue; 
                        if (syst_fproc[isyst].Contains(" "+names[is]+" ")) {
                            line+=Form("\t%.2f",syst_fval[isyst]);
                        } else {
                            line+="\t-";
                        }
                    }
                    datacard << line << endl;
                }

                // sample dependent values, pdf_gg
                line = "pdf_gg\t\t\t\tlnN\t";
                for (int is=0; is<nsample; ++is) {
                    if (channames[ichan] == "of" && names[is] == "DY" ) continue; 	
                    bool found(false);
                    for (int isyst=0; isyst<3; isyst++) {
                        if (pdf_gg_proc[isyst]==names[is]) {
                            line+=Form("\t%.2f",pdf_gg[isyst]);
                            found = true; break;
                        }
                    }
                    if (!found) { line+="\t-"; }
                }
                datacard << line << endl;

                // sample dependent values, pdf_qqbar
                line = "pdf_qqbar\t\t\tlnN\t";
                for (int is=0; is<nsample; ++is) {
                    if (channames[ichan] == "of" && names[is] == "DY" ) continue; 
                    bool found(false);
                    for (int isyst=0; isyst<3; isyst++) {
                        if (pdf_qqbar_proc[isyst]==names[is]) {
                            line+=Form("\t%.2f",pdf_qqbar[isyst]);
                            found = true; break;
                        } 
                    }
                    if (!found) { line+="\t-"; }
                }	
                datacard << line << endl;

                //
                // systematics related to data-driven estimates
                //

                TString chantemp1(channames[ichan]), chantemp2(channames[ichan]); 
                if (channames[ichan].Contains("of")) { chantemp1 = "em"; chantemp2 = "me"; }
                if (channames[ichan].Contains("sf")) { chantemp1 = "ee"; chantemp2 = "mm"; }

                for (int isyst=0; isyst<nsyst_data; ++isyst) {
                    if (channames[ichan] == "of" && syst_dname[isyst] == "DY" ) continue; 

                    //printf("data-driven systematics %d\n", isyst);

                    TString line1(""), line2("");
                    line1+=Form("CMS_hww_%s_%dj_extr\t\t%s\t", syst_dname[isyst].Data(), ijet, syst_dtype[isyst].Data());
                    line2+=Form("CMS_hww_%s_%dj_stat\t\t%s",   syst_dname[isyst].Data(), ijet, "gmN");

                    for (int is=0; is<nsample; ++is) {

                        if (channames[ichan] == "of" && names[is] == "DY" ) continue; 

                        //printf("adding systematics: %s\n", syst_dname[isyst].Data());

                        if (names[is]==syst_dname[isyst]) {


                            // temporary fix for mass points without d-d-estimates
                            int imass(mass);
                            if (mass<120) imass = 120; if (mass>200 && mass<250) imass = 200;

                            // N in signal region
                            float Ny = histos[is]->Integral(0, histos[is]->GetNbinsX()+1); 
                            // case1
                            float N1(Ny),s1(0),u1(0);
                            TString cname = Form(syst_dname[isyst]+"Card_"+chantemp1+"_%dj.txt", ijet);
                            getsyst(datadir+cname, imass, N1, s1, u1); 
                            // case2
                            float N2(Ny),s2(0),u2(0);
                            cname = Form(syst_dname[isyst]+"Card_"+chantemp2+"_%dj.txt", ijet);
                            getsyst(datadir+cname, imass, N2, s2, u2);
                            //printf("Nc %.0f %.0f s %.3f %.3f u %.3f %.3f\n", N1, N2, s1, s2, u1, u2);	
                            // lines in limit datacard card                          
                            // extr <type>  <empty> ....  1+u/s (lnN) or u/s (gmM)
                            // stat  gmN     Nc     ....  s                                                        
                            // BUT!! since there is no dd estimates at BDT-level, do a temporary patch 
                            // combine two sub-channels
                            float ratio = Ny/(s1*N1+s2*N2); // ratio of events in signal region (datacard / current) 
                            float Nc = syst_dctrl[isyst][ijet]; // currently extrapolating WW level estimates
                            float s =  Ny/Nc; // scale factor from control region
                            float u = s*0.5*(u1/s1+u2/s2); // average two uncertainties fractions
                            if (syst_dname[isyst]=="DY") syst_derr[isyst][ijet]; // only for DY, take from WW-level 
                            //printf(syst_dname[isyst]+"\tNy %.3f Nc %.0f s %.3f u %.3f ratio to MC %.3f\n", Ny, Nc, s, u, 1./ratio);
                            float extr = 1+u/s; // syst w.r.t. 1
                            if (syst_dtype[isyst].Contains("gm")) extr = u/s; // syst w.r.t. 0
                            line1+=Form("\t%.2f", extr);
                            line2+=Form("\t%.4f", s);
                            line2.ReplaceAll("gmN", Form("gmN\t%.0f",Nc));

                        } else {

                            line1+="\t-";
                            line2+="\t-";

                        }

                    } // nsample

                    datacard<< line1 << endl << line2 << endl;

                } // nsyst

                //
                // statistical uncertainty (just the total one, to be improved later)
                //

                for (int is=0; is<nsample; ++is) {

                    if (channames[ichan] == "of" && names[is] == "DY" ) continue;

                    TString lines("");
                    lines+=Form("CMS_hww%s_stat_%dj_%s_bin1\tlnN\t", channames[ichan].Data(), ijet, names[is].Data());

                    for (int js=0; js<nsample; ++js) {

                        if (channames[ichan] == "of" && names[js] == "DY" ) continue;

                        if (names[is]==names[js]) {
                            lines+=Form("\t%.3f",1.+(1./sqrt(histos[is]->GetEntries())));
                        } else {
                            lines+="\t-";
                        }
                    }

                    datacard << lines <<endl;
                }

                map<TString, map<TString,vector<TH1D*> > > shapeSyst = getSystHistos(f, histPrefix);

                map<TString, map<TString,vector<TH1D*> > >::iterator iSS, bSS=shapeSyst.begin(), eSS=shapeSyst.end();
                map<TString,vector<TH1D*> >::iterator iSam, eSam, bSam;

                for(iSS = bSS; iSS != eSS; ++iSS) {
                    int nTabs = 4-iSS->first.Length()/8;
/*                     cout << nTabs << endl;  */
                    datacard << iSS->first;
                    for ( ; nTabs > 0; --nTabs ) {  datacard << '\t'; }
                    datacard << "shape\t"; 
                    bSam = iSS->second.begin();
                    eSam = iSS->second.end();

                    for (int is=0; is<nsample; ++is) {
/*                         cout << "'" << names[is] << "'"; */
                        if ( channames[ichan] == "of" && names[is] == "DY" ) continue;
/*                         for (iSam = bSam; iSam != eSam; ++iSam ) { */
/*                             cout << "\t'" << iSam->first << "'"; */
/*                         } */
/*                         cout << endl; */
                        iSam = iSS->second.find(names[is]);
                        datacard << "\t" << (iSam != iSS->second.end() ? "1" : "-");
/*                         cout << names[is] << "  " << iSS->first << endl; */
                    }
                    datacard << endl;
                }

                datacard.close();
                for (unsigned int i=0; i<histos.size(); ++i) {
/*                     histos[i]->~TH1D(); */
                    delete histos[i];
                }
                f->Close(); 
/*                 f->~TFile(); */
                delete f;

            } // nmass

        } // nchannel

    } // njet

}

// returns a vector containing all the histograms corresponding to the nominam sample 
vector<TH1D*> gethistos(TFile *f, TString prefix) {

    vector<TH1D*> histos;

    for (int is=0; is<nsample+1; ++is) {
        TString histoname = prefix+names[is];
        //printf("looking for histo %s\n", histoname.Data());
        TH1D* h = (TH1D*)f->Get(histoname);
        if ( h == NULL )
            cout << "Warning: histogram" << histoname.Data() << "not found" << endl;
        histos.push_back( (TH1D*)h->Clone(histoname+"_temp") );    
    }
    printf("found %d histos\n", histos.size());

    return histos;

}

map<TString, map<TString,vector<TH1D*> > > getSystHistos( TFile *f, const TString& prefix ) {

    map<TString, map<TString,vector<TH1D*> > > m;
    int nSamples = sizeof(syst_samples)/sizeof(*syst_samples);
    int nSyst    = sizeof(syst_effect)/sizeof(*syst_effect);
    
    for ( int iSam=0; iSam < nSamples; ++ iSam) {
        for ( int iEff=0; iEff < nSyst; ++iEff ) {
            TString histoname = prefix+syst_samples[iSam]+"_"+syst_effect[iEff];
            TH1D* h;
            h = (TH1D*)f->Get(histoname+"Up");
            if ( h == NULL )
                cout << "Warning: histogram" << (histoname+"Up").Data() << "not found" << endl;
/*             cout << h->GetName() << "  " << h->GetTitle() << endl; */
            m[syst_effect[iEff]][syst_samples[iSam]].push_back( h ); 
            h = (TH1D*)f->Get(histoname+"Down");
            if ( h == NULL )
                cout << "Warning: histogram" << (histoname+"Down").Data() << "not found" << endl;
/*             cout << h->GetName() << "  " << h->GetTitle() << endl; */
            m[syst_effect[iEff]][syst_samples[iSam]].push_back( h ); 
        }
    }
/*     cout << nSamples << "  " << nSyst << endl; */

    return m;
    

}


void getsyst(TString cname, float mass, float &N, float &s, float &u) {

    ifstream card; card.open(cname.Data());
    if(!card) {
        printf("Did not find card %s\n", cname.Data());
        return;
    }
    while ( !card.eof() ) { 
        float HiggsMass(0);
        float NumEventsInCtrlRegion(0);
        float scaleToSignRegion(0);
        float uncertaintyOnScaleToSignRegion(0);
        card >> HiggsMass >> NumEventsInCtrlRegion >> scaleToSignRegion >> uncertaintyOnScaleToSignRegion;
        // notes from Emanuele
        // n in signal region = NumEventsInCtrlRegion * scaleToSignRegion
        // uncertainty on n   = NumEventsInCtrlRegion * uncertaintyOnScaleToSignRegion    
        // fractional uncertainty on n = uncertaintyOnScaleToSignRegion / scaleToSignRegion

        //printf("looking for mass point %.1f %.1f\n", mass, HiggsMass);
        if (fabs(HiggsMass-mass)<5) {
            s = scaleToSignRegion;
            N = NumEventsInCtrlRegion;
            u = uncertaintyOnScaleToSignRegion;
            //printf("Found mass point %.0f: %.3f %.3f %.3f\n", mass, N, s, u);
            return;
        }
    }
    printf("Did not find mass point %.0f\n", mass);
    return;

}
