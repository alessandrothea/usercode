
#include <TMultiGraph.h>
#include <TGraph.h>
#include <TGraphAsymmErrors.h>
#include <TAxis.h>
#include <TLine.h>
#include <TLegend.h>
#include <TText.h>
#include <TLatex.h>
#include <TCanvas.h>
#include <TSystem.h>

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <iomanip>

//#include "tdrstyle.C"

void PlotLimit ( string LimitFile , string LimTitle , bool DoObsLim , bool DoExpLim ) {

    //   setTDRStyle();

    vector<float> vMass           ;
    vector<float> vObsLimit       ; 
    vector<float> vMeanExpLimit   ; 
    vector<float> vMedianExpLimit ; 
    vector<float> vExpLim68Down   ; 
    vector<float> vExpLim68Up     ; 
    vector<float> vExpLim95Down   ; 
    vector<float> vExpLim95Up     ;

    ifstream indata;
    indata.open(LimitFile.c_str());
    if(!indata) { // file couldn't be opened
        cerr << "Error: file could not be opened" << endl;
        return;
    }
    while ( !indata.eof() ) { // keep reading until end-of-file
        float Mass           ;
        float ObsLimit       ; 
        float MeanExpLimit   ; 
        float MedianExpLimit ; 
        float ExpLim68Down   ; 
        float ExpLim68Up     ; 
        float ExpLim95Down   ; 
        float ExpLim95Up     ;

        //     indata >> Mass >> ObsLimit >> MeanExpLimit >> MedianExpLimit >> ExpLim95Down >> ExpLim68Up >> ExpLim68Down >> ExpLim95Up ;
        indata >> Mass >> ObsLimit >> MeanExpLimit >> MedianExpLimit >> ExpLim68Down >> ExpLim68Up >> ExpLim95Down >> ExpLim95Up ;


/*         cout << "- " << Mass << " " << ObsLimit  << " " << MeanExpLimit  << " " << MedianExpLimit <<" "<< ExpLim68Down <<" "<< ExpLim68Up <<" "<< ExpLim95Down <<" "<< ExpLim95Up << endl; */




        vMass           .push_back(Mass           );
        vObsLimit       .push_back(ObsLimit       ); 
        vMeanExpLimit   .push_back(MeanExpLimit   ); 
        vMedianExpLimit .push_back(MedianExpLimit ); 
        vExpLim68Down   .push_back(ExpLim68Down   ); 
        vExpLim68Up     .push_back(ExpLim68Up     ); 
        vExpLim95Down   .push_back(ExpLim95Down   ); 
        vExpLim95Up     .push_back(ExpLim95Up     );
    }

    TCanvas* cLimit = new TCanvas();

    cLimit->cd();

    float x1 = vMass.at(0) - 5. ;
    float x2 = vMass.at(vMass.size()-1) + 5. ; 

    TMultiGraph* pool = new TMultiGraph("Limit", "Limit");
    // Expected Limit
    TGraph* ExpLim = NULL ;
    TGraphAsymmErrors* ExpBand68 = NULL ;
    TGraphAsymmErrors* ExpBand95 = NULL ;
    if ( DoExpLim ) {
        float x[100];
        float ex[100];
        float y[100];
        float yu68[100];
        float yd68[100];
        float yu95[100];
        float yd95[100]; 
        for ( int i = 0 ; i < (signed) vMass.size() ; ++i ) {
/*             cout << i << endl; */
            x[i]  = vMass.at(i) ;
            ex[i] = 0 ;
            y[i]  = vMedianExpLimit.at(i) ;
            yu68[i] = vExpLim68Up.at(i) ; 
            yd68[i] = vExpLim68Down.at(i) ;
            yu95[i] = vExpLim95Up.at(i) ; 
            yd95[i] = vExpLim95Down.at(i) ;

            cout << yu95[i] << " "<<yu68[i] << " * " << y[i] << " * " << yd68[i] << " "  << yd95[i] << endl;

            yu68[i] = vExpLim68Up.at(i) - y[i]; 
            yd68[i] = y[i] - vExpLim68Down.at(i) ;
            yu95[i] = vExpLim95Up.at(i) - y[i] ; 
            yd95[i] = y[i] - vExpLim95Down.at(i) ;

            cout << yu95[i] << " "<<yu68[i] << " * " << y[i] << " * " << yd68[i] << " "  << yd95[i] << endl;

        }
        ExpBand95 = new TGraphAsymmErrors((signed) vMass.size(),x,y,ex,ex,yd95,yu95);
        ExpBand95->SetName("expBand95");
        ExpBand95->SetFillColor(90); 
        pool->Add(ExpBand95,"3");
        /*     ExpBand95->DrawClone("A3"); */
        ExpBand68 = new TGraphAsymmErrors((signed) vMass.size(),x,y,ex,ex,yd68,yu68);
        ExpBand68->SetName("expBand68");
        ExpBand68->SetFillColor(211); 
        pool->Add(ExpBand68,"3");
        /*     ExpBand68->DrawClone("3"); */

        ExpLim = new TGraph((signed) vMass.size(),x,y);    
        ExpLim->SetName("expLimit");
        ExpLim->SetLineWidth(2);
        ExpLim->SetLineStyle(2);
        /*     ExpLim->DrawClone("l"); */
        pool->Add(ExpLim,"l");

        pool->Draw("a");
        cLimit->Update();
        pool->GetYaxis()->SetRangeUser(0.,10);
        pool->GetXaxis()->SetRangeUser(x1,x2);
        pool->SetTitle();
        pool->GetXaxis()->SetTitle("Higgs mass [GeV/c^{2}]");
        pool->GetYaxis()->SetTitle("95% Limit on #sigma/#sigma_{SM} ");

    }


    // Observed Limit
    TGraph* ObsLim = NULL ;
    if ( DoObsLim ) {
        float x[100];
        float y[100];    
        for ( int i = 0 ; i < (signed) vMass.size() ; ++i ) { x[i] = vMass.at(i) ; y[i] = vObsLimit.at(i) ; }
        ObsLim = new TGraph((signed) vMass.size(),x,y);
        ObsLim->SetMarkerColor(kBlack);
        ObsLim->SetLineWidth(2);
        ObsLim->SetLineColor(kBlack);
        //ObsLim->SetLineStyle(2);
        ObsLim->SetMarkerStyle(kFullCircle);
        /*     if   (DoExpLim) ObsLim->DrawClone("lp"); */
        pool->Add(ObsLim,"lp");
        if   (!DoExpLim) {
            pool->Draw();
            pool->GetYaxis()->SetRangeUser(0.,10); 
            pool->GetXaxis()->SetRangeUser(x1,x2);
            pool->GetXaxis()->SetTitle("Higgs mass [GeV/c^{2}]");
            pool->GetYaxis()->SetTitle("95% CL Limit on #sigma/#sigma_{SM} ");
        }
    }

    TGraph* theLine = new TGraph(2);
    theLine->SetPoint(0,1,1);
    theLine->SetPoint(1,1000,1);
    theLine->SetLineColor(kRed);
    theLine->SetLineWidth(2);
    theLine->Draw("L");

    /*   TLine *l = new TLine(x1,1,x2,1); */
    /*   l->SetLineWidth(2); */
    /*   l->SetLineColor(kBlack); */
    /* |+   l->SetBit(kLineNDC); +| */
    /*   l->Draw("same"); */

    TText* title = new TText(.5,.94,LimTitle.c_str());
    title->SetTextSize(.04);
    title->SetNDC(1);
    title->Draw("same");

    TText* CMS = new TText(.15,.85,"CMS Preliminary");
    CMS ->SetTextSize(.05);
    CMS ->SetNDC(1);
    CMS ->Draw("same");

    TLatex* Lumi = new TLatex(.15,.81,"Lumi = 4.6 fb^{-1} ");
    Lumi ->SetTextSize(.03);
    Lumi ->SetNDC(1);
    Lumi ->Draw("same");

    TLegend* leg = NULL ;  
    leg = new TLegend(0.5,0.67,0.78,0.8,"");
    leg->AddEntry(ExpLim,   "95% CL exclusion: median","l");
    leg->AddEntry(ExpBand68,"95% CL exclusion: 68% band","f");
    leg->AddEntry(ExpBand95,"95% CL exclusion: 95% band","f");
    if ( DoObsLim ) {
        leg->AddEntry(ObsLim,"Observed","lp");
    }
    leg->SetTextSize(.03);
    leg->SetFillStyle(0);
    leg->SetBorderSize(0);
    leg->SetShadowColor(0);
    leg->SetFillColor(0);
    leg->Draw("same");


    TAxis* xax = pool->GetXaxis();
/*     TAxis* yax = pool->GetYaxis(); */

    string plotDir = "plots";
    string baseFigName = plotDir +"/"+ LimTitle;

    gSystem->mkdir(plotDir.c_str(),kTRUE);
    cLimit->SaveAs((baseFigName+".pdf").c_str()) ;
    cLimit->SaveAs((baseFigName+".png").c_str()) ;
    gPad->WaitPrimitive();

    xax->SetRangeUser(110.,160.);
    cLimit->Modified();
    cLimit->Update();
    cLimit->SaveAs((baseFigName+"_lowmass.pdf").c_str()) ;
    cLimit->SaveAs((baseFigName+"_lowmass.png").c_str()) ;

/*     xax->UnZoom(); */
/*     yax->SetRangeUser(0.1,yax->GetXmax()); */


/*     cLimit->SetLogy(); */
/*     cLimit->Modified(); */
/*     cLimit->Update(); */
/*     cLimit->SaveAs((baseFigName+"_log.pdf").c_str()) ; */
/*     cLimit->SaveAs((baseFigName+"_log.png").c_str()) ; */

/*     xax->SetRangeUser(100.,300.); */
/*     cLimit->Modified(); */
/*     cLimit->Update(); */
/*     cLimit->SaveAs((baseFigName+"_lowmass_log.pdf").c_str()) ; */
/*     cLimit->SaveAs((baseFigName+"_lowmass_log.png").c_str()) ; */
/*     cLimit->SetLogy(kFALSE); */

    ofstream txttable((baseFigName+".txt").c_str());
    if ( !txttable.is_open() ) {
        cout << "Couldn't open " <<  baseFigName+".txt" << endl;
    }
    txttable << "" << endl;
/*     txttable.precision(2); */
    txttable.fill(' ');
    txttable 
            << setw(6) << "Mass"
            << setw(8) << "Obs"
            << setw(8) << "Median"
            << setw(14) << "Exp 68\%" << setw(6) << " "
            << setw(14) << "Exp 95\%" << setw(6) << " "
            << endl;

    for ( int i = 0 ; i < (signed) vMass.size() ; ++i ) {
        txttable  
            << setw(6) << vMass.at(i)
            << setw(8) << setprecision(3) << vObsLimit.at(i)
            << setw(8) << vMedianExpLimit.at(i)
            << "   [" << setw(6) <<  vExpLim68Down.at(i) << ',' << setw(6)<< vExpLim68Up.at(i) << "]   "
            << "   [" << setw(6) <<  vExpLim95Down.at(i) << ',' << setw(6)<< vExpLim95Up.at(i) << "]   " << endl;

    }
    txttable.close();

    return;
}
