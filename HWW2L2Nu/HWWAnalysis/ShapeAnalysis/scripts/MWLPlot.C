#include<vector>

#if !defined (__CINT__) || defined (__MAKECINT__)
#include "THStack.h"
#include "TGaxis.h"
#include "TH1F.h"
#include "TLatex.h"
#include "TPad.h"
#include "TCanvas.h"
#include "TAxis.h"
#include "TLegend.h"
#include "TFrame.h"
#include "TROOT.h"
#include "TStyle.h"
#endif

#include <iostream>
#include <algorithm>
#include <utility>

enum samp                       {  Undefined ,  iHWW ,  iWW    ,  iZJets ,  iTop   ,  iVV   ,  iWJets ,  iWZ    ,  iZZ   ,  iFakes ,  nSamples  };
const std::string sampNames[] = { "Undefined",  "HWW",  "WW"   ,  "ZJets",  "Top"  ,  "VV"  ,  "WJets",  "WZ"   ,  "ZZ"  ,  "Fakes", "nSamples" };
Color_t sampleColor[]         = { kWhite     , kRed+1, kAzure-9, kGreen+2, kYellow , kAzure-2, kGray+1, kAzure-2, kAzure-9, kGray+1,  kBlack    };

Color_t autreColors[]         = {kMagenta-9, kBlue-3, kSpring-9, kOrange-9, kRed-9, kViolet-9, kCyan-6, kGreen-6, kYellow-7, kOrange-6, kRed+3, kMagenta+2 }; 

std::string nameBySamp(samp a){
    if(int(a) < int(nSamples) && int(a)>0) return sampNames[int(a)];
    else                                   return "undefined";
}

samp sampByName(const std::string &name){
    int index = std::find(sampNames, sampNames+nSamples, name)-sampNames;
    if(index == nSamples) return Undefined; 
    return samp(index);
}


//              1 2 3 4 5 6 7 8 9 101112131415161718
//              1 2 3 4 5 6 7 8 9 10    1314  161718
float xPos[] = {0,0,0,1,1,1,0,1,2,3,0,1,2,3,0,1,2,3}; 
float yOff[] = {0,1,2,0,1,2,3,3,3,3,4,4,4,4,5,5,5,5};

//              1 2 3 4 5 6 7 8 9 101112131415161718
//                                    12    15
float xPosA[] = {0,0,0,1,1,1,0,1,2,0,1,2,0,1,2}; 
float yOffA[] = {0,1,2,0,1,2,3,3,3,4,4,4,5,5,5};

//              1 2 3 4 5 6 7 8 9 101112131415161718
//                                  11   
float xPosB[] = {0,0,0,1,1,1,0,1,0,1,2}; 
float yOffB[] = {0,1,2,0,1,2,3,3,4,4,4};



//------------------------------------------------------------------------------
// GetMaximumIncludingErrors
//------------------------------------------------------------------------------
Float_t GetMaximumIncludingErrors(TH1D* h)
{
    Float_t maxWithErrors = 0;

    for (Int_t i=1; i<=h->GetNbinsX(); i++) {

        Float_t binHeight = h->GetBinContent(i) + h->GetBinError(i);

        if (binHeight > maxWithErrors) maxWithErrors = binHeight;
    }

    return maxWithErrors;
}





class MWLPlot {

    public: 
        MWLPlot() { 
            _hist.resize(nSamples,0); 
            _data = 0; 
            _breakdown = false; 
            _mass = 0; 
            _nbins=_low=_high=-1;
            _labelFont        = 42;
            _legendTextSize   = 0.04;
            _xoffset          = 0.20;
            _yoffset          = 0.06;
            _labelOffset      = 0.015;
            _axisLabelSize    = 0.050;
            _titleOffset      = 1.6;
            _extraLabel       = 0x0;
        }

        void setDataHist (TH1D * h)                        { _data          = h;        } 
        void setHWWHist  (TH1D * h)                        { setMCHist(iHWW  ,h);       } 
        void setWWHist   (TH1D * h)                        { setMCHist(iWW   ,h);       } 
        void setZJetsHist(TH1D * h)                        { setMCHist(iZJets,h);       } 
        void setTopHist  (TH1D * h)                        { setMCHist(iTop  ,h);       } 
        void setVVHist   (TH1D * h)                        { setMCHist(iVV   ,h);       } 
        void setWZHist   (TH1D * h)                        { setMCHist(iWZ   ,h);       } 
        void setZZHist   (TH1D * h)                        { setMCHist(iZZ   ,h);       } 
        void setFakesHist(TH1D * h)                        { setMCHist(iFakes,h);       } 
        void setWJetsHist(TH1D * h)                        { setMCHist(iWJets,h);       }

        void setMCHist   (const samp &s,        TH1D * h)  { 
            if ( _nbins == -1 ) {
                _nbins  = h->GetNbinsX();
                _low    = h->GetXaxis()->GetBinLowEdge(1);
                _high   = h->GetBinLowEdge(h->GetNbinsX()+1);
            }
            if (h->GetNbinsX() != _nbins || fabs(h->GetXaxis()->GetBinLowEdge(1)-_low) > 0.001 || fabs(h->GetBinLowEdge(h->GetNbinsX()+1)-_high) > 0.001) {
                std::cout << "Warning, we have a bin mismatch problem" << std::endl;
            }
            _hist[s]       = h;        
        } 

        void setMCHist   (const std::string &s, TH1D * h)  { 
            if (sampByName(s) == Undefined) {
                _autreHists.push_back(make_pair(s,h));
            } else {
                setMCHist(sampByName(s),h);
            }
        } 

        void setMass(const int &m) {_mass=m;}

//         void Draw(const int &rebin=1,const bool &div=false) {

//             Draw(new TCanvas(),rebin,div);

//         }

        void Draw(TCanvas *c1, const int &rebin=1, const bool &div=false) {

            gStyle->SetOptStat(0);
            c1->cd();
            c1->Clear();

            TPad *pad1;
            if(div) {
                pad1 = new TPad("pad1","pad1",0,1-0.614609572,1,1);
                pad1->SetTopMargin(0.0983606557);
                pad1->SetBottomMargin(0.025);
            } else {
                pad1 = new TPad("pad1","pad1",0,0,1,1);
            }
            pad1->Draw();
            pad1->cd();

            RebinHists(rebin);
            THStack *hstack = GetStack(c1->GetLogy());
            TH1D *signal = GetSignalHist();
            TH1D *data   = GetDataHist();

            if(c1->GetLogy()) gPad->SetLogy();
            if(div) hstack->GetHistogram()->SetLabelSize(0.00,"X");
            if(div) hstack->GetHistogram()->SetLabelSize(0.06,"Y");
            if(div) hstack->GetHistogram()->SetTitleSize(0.06,"XY");
            hstack->Draw("hist");
            if(signal) signal->Draw("hist,same");
            if(data)     data->Draw("ep,same");
            DrawLabels();
            //            pad1->GetFrame()->DrawClone();

            if(div) {

                TH1D *summed = GetSummedMCHist();

                TH1D *rdat = (TH1D*)data->Clone("rdat");   
                if(gROOT->FindObject("rref")) gROOT->FindObject("rref")->Delete();
                TH1D *rref = new TH1D("rref","rref",
                    summed->GetNbinsX(),
                    summed->GetBinLowEdge(1),
                    summed->GetBinLowEdge(summed->GetNbinsX()+1)
                );
                for (int i = 1, n = rref->GetNbinsX(); i <= n+1; ++i) {
                    rref->SetBinContent(i,summed->GetBinContent(i));
                    rref->SetBinError(i,summed->GetBinError(i));
                }
                rref->SetTitle("");
                rref->SetLineWidth(0);
                rref->SetFillColor(kGray+1);
                rref->SetFillStyle(1001);
                double absmax = 0;
                for (int i = 0, n = rdat->GetNbinsX(); i <= n+1; ++i) {
                    double scale = rref->GetBinContent(i);
                    if (scale == 0) {
                        rdat->SetBinContent(i, 0);
                        rref->SetBinContent(i, 0);
                        rdat->SetBinError(i, 0);
                        rref->SetBinError(i, 0);
                    } else {
                        rdat->SetBinContent(i, rdat->GetBinContent(i)/scale);
                        rref->SetBinContent(i, rref->GetBinContent(i)/scale);
                        rdat->SetBinError(i, rdat->GetBinError(i)/scale);
                        rref->SetBinError(i, rref->GetBinError(i)/scale);
                        double mymax = TMath::Max(1.2*fabs(rdat->GetBinContent(i)-1)+1.4*rdat->GetBinError(i), 2.0*rref->GetBinError(i));
                        absmax = TMath::Max(mymax, absmax);
                    }
                }

                c1->cd();
                TPad *pad2 = new TPad("pad2","pad2",0,0,1,1-0.614609572);

                pad2->SetTopMargin(0.0261437908);
                pad2->SetBottomMargin(0.392156863);
                pad2->Draw();
                pad2->cd();

                TLine *line = new TLine(rref->GetXaxis()->GetXmin(), 1.0, rref->GetXaxis()->GetXmax(), 1.0);
                line->SetLineColor(kBlack);
                line->SetLineWidth(1);
                line->SetLineStyle(1);

                rref->GetYaxis()->SetRangeUser(TMath::Max(0.,1.-absmax), absmax+1.);
//                 AxisFonts(rref->GetYaxis(), "y", "ratio");
                AxisFonts(rref->GetXaxis(), "x", hstack->GetXaxis()->GetTitle());
                rref->GetYaxis()->SetTitle("data/mc");
                rref->GetYaxis()->SetLabelSize(0.09);
                rref->GetYaxis()->SetTitleSize(0.09);
                rref->GetYaxis()->SetTitleOffset(1.02);
                rref->GetXaxis()->SetLabelSize(0.09);
                rref->GetXaxis()->SetTitleSize(0.09);
                rref->GetXaxis()->SetTitleOffset(1.5);
                rref->Draw("E2"); 
                rdat->SetMarkerStyle(20);
                rdat->Draw("E SAME p");
                line->Draw("SAME"); 
                c1->Update();
/*                 pad2->GetFrame()->DrawClone(); */
            }

        }


        TH1D* GetDataHist() { 
        
            if(_data) _data->SetLineColor  (kBlack);
            if(_data) _data->SetMarkerStyle(kFullCircle);
            return _data; 
        }

        TH1D *GetSignalHist() {

            if( _hist[iHWW] ) {
                _hist[iHWW]->SetLineColor(sampleColor[iHWW]);
                _hist[iHWW]->SetLineWidth(3);
            }
            return _hist[iHWW];

        }

        TH1D *GetSummedMCHist() {

            if(gROOT->FindObject("hMC")) gROOT->FindObject("hMC")->Delete();
            TH1D* hMC = new TH1D("hMC","hMC",_nbins,_low,_high);
            hMC->Sumw2();

            for (int i=0; i<nSamples; i++) if( _hist[i] && i != iHWW) hMC->Add(_hist[i]);
            for (size_t i=0; i<_autreHists.size(); i++)               hMC->Add(_autreHists[i].second);

            return hMC;

        }

        THStack* GetStack(bool isLog) {
            THStack* hstack = new THStack();

            float binWidth = 0;
            for (int i=0; i<nSamples; i++) if( _hist[i] && i != iHWW) {

                _hist[i]->SetLineColor(sampleColor[i]);
                _hist[i]->SetFillColor(sampleColor[i]);
                _hist[i]->SetFillStyle(1001);
                binWidth = _hist[i]->GetBinWidth(1);

                hstack->Add(_hist[i]);
            }

            for (size_t i=0; i<_autreHists.size(); i++) {

                _autreHists[i].second->SetLineColor(autreColors[i]);
                _autreHists[i].second->SetFillColor(autreColors[i]);
                _autreHists[i].second->SetFillStyle(1001);

                hstack->Add(_autreHists[i].second);
            }


            hstack->Draw("GOFF");
            hstack->SetTitle("CMS preliminary");

            Float_t theMax = hstack->GetMaximum();
            Float_t theMin = hstack->GetMinimum();

            if (_hist[iHWW]) {
                if (_hist[iHWW]->GetMaximum() > theMax) theMax = _hist[iHWW]->GetMaximum();
                if (_hist[iHWW]->GetMinimum() < theMin) theMin = _hist[iHWW]->GetMinimum();
            }

            if (_data) {
                Float_t dataMax = GetMaximumIncludingErrors(_data);
                if (dataMax > theMax) theMax = dataMax;
            }

            int sampCount = GetSampCount();
            float scaleBy = 1.35 + 0.2*(sampCount>6) + 0.2*(sampCount>10) + 0.2*(sampCount>14);

            if (isLog) {
                theMin = theMin==0?0.1:theMin/10;
                hstack->SetMinimum(theMin);
                hstack->SetMaximum(pow(10,(log(theMax)/log(10)-log(theMin)/log(10)+1)*scaleBy+log(theMin)/log(10)-1));
            } else {
                hstack->SetMaximum(scaleBy * theMax);
            }

            if(_breakdown) {
                THStackAxisFonts(hstack, "y", "entries");
                hstack->GetHistogram()->LabelsOption("v");
            } else {
                THStackAxisFonts(hstack, "x", TString::Format("%s [%s]",_xLabel.Data(),_units.Data()));
                if(_units.Sizeof() == 1) {
                    THStackAxisFonts(hstack, "x", _xLabel.Data());
                    THStackAxisFonts(hstack, "y", "entries");
                } else {
                    THStackAxisFonts(hstack, "x", TString::Format("%s [%s]",_xLabel.Data(),_units.Data()));
                    THStackAxisFonts(hstack, "y", TString::Format("entries / %.0f %s", binWidth,_units.Data()));
                }
            }
            return hstack;
        }

        void setLumi(const float &l) { _lumi = l; }
        void setLabel(const TString &s) { _xLabel = s; }
        void setUnits(const TString &s) { _units = s; }
        void setBreakdown(const bool &b = true) { _breakdown = b; }
        void addLabel(const std::string &s) {
            _extraLabel = new TLatex(0.707, 0.726, TString(s));
            _extraLabel->SetNDC();
            _extraLabel->SetTextAlign(32);
            _extraLabel->SetTextFont(42);
            _extraLabel->SetTextSize(_legendTextSize*0.9);
        }

    private: 
        int GetSampCount() {
            int sampCount = 0;
            for (int i=0; i<nSamples; i++) if( _hist[i] ) sampCount++;
            for (size_t i=0; i<_autreHists.size(); i++)   sampCount++;
            if  (_data)                                   sampCount++;
            return sampCount;
        }


        void RebinHists(const int &rebin) {

            for (int i=0; i<nSamples; i++) if( _hist[i] )            _hist[i]->Rebin(rebin);
            for (size_t i=0; i<_autreHists.size(); i++) _autreHists[i].second->Rebin(rebin);
            if(_data) _data->Rebin(rebin);

        }


        void DrawLabels() {

            // total mess to get it nice, should be redone
            size_t j=0;
            TString higgsLabel = " HWW";
            if(_mass != 0) higgsLabel.Form(" m_{H}=%d",_mass);

            float *pos,*off;
            int sampCount = GetSampCount();
            if(sampCount == 12 || sampCount == 15) { pos = xPosA; off = yOffA; }
            else if(sampCount == 11 )              { pos = xPosB; off = yOffB; }
            else                                   { pos = xPos;  off = yOff;  }
            float x0=0.22; float wx=0.19;
            if(_data        ) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _data,                  " data",                "lp"); j++; }
            if(_hist[iHWW  ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iHWW  ]         , higgsLabel,             "l" ); j++; }
            if(_hist[iWW   ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iWW   ]         , " WW",                  "f" ); j++; }
            if(_hist[iZJets]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iZJets]         , " Z+jets",              "f" ); j++; }
            if(_hist[iTop  ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iTop  ]         , " top",                 "f" ); j++; }
            if(_hist[iVV   ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iVV   ]         , " WZ/ZZ",               "f" ); j++; }
            if(_hist[iWJets]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iWJets]         , " W+jets",              "f" ); j++; }
            if(_hist[iWZ   ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iWZ   ]         , " WZ",                  "f" ); j++; }
//             if(_hist[iZZ   ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iZZ   ]         , " ZZ",                  "f" ); j++; }
//             if(_hist[iFakes]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iFakes]         , " fakes",               "f" ); j++; }
            for(size_t i=0;i<_autreHists.size();++i) {
                                DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _autreHists[i].second , _autreHists[i].first,   "f" ); j++; 
            }

            TLatex* luminosity = new TLatex(0.896, 0.781, TString::Format("L = %.1f fb^{-1}",_lumi));
            luminosity->SetNDC();
            luminosity->SetTextAlign(32);
            luminosity->SetTextFont(42);
            luminosity->SetTextSize(_legendTextSize*0.95);
            luminosity->Draw("same");
            if(_extraLabel) _extraLabel->Draw("same");
        }

        //------------------------------------------------------------------------------
        // AxisFonts
        //------------------------------------------------------------------------------
        void AxisFonts(TAxis*  axis,
                       TString coordinate,
                TString title)
        {
            axis->SetLabelFont  (_labelFont  );
            axis->SetLabelOffset(_labelOffset);
            axis->SetLabelSize  (_axisLabelSize);
            axis->SetNdivisions (  505);
            axis->SetTitleFont  (_labelFont);
            axis->SetTitleOffset(  1.5);
            axis->SetTitleSize  (_axisLabelSize);
        
            if (coordinate == "y") axis->SetTitleOffset(_titleOffset);
        
            axis->SetTitle(title);
        }
        
        //------------------------------------------------------------------------------
        // DrawLegend
        //------------------------------------------------------------------------------
        void DrawLegend(Float_t x1,
                Float_t y1,
                TH1D*   hist,
                TString label,
                TString option)
        {
            TLegend* legend = new TLegend(x1,
                    y1,
                    x1 + _xoffset,
                    y1 + _yoffset);
        
            legend->SetBorderSize(     0);
            legend->SetFillColor (     0);
            legend->SetTextAlign (    12);
            legend->SetTextFont  (_labelFont);
            legend->SetTextSize  (_legendTextSize);
        
            legend->AddEntry(hist, label.Data(), option.Data());
        
            legend->Draw();
        }


        //------------------------------------------------------------------------------
        // THStackAxisFonts
        //------------------------------------------------------------------------------
        void THStackAxisFonts(THStack* h,
                TString  coordinate,
                TString  title)
        {
            TAxis* axis = NULL;
        
            if (coordinate.Contains("x")) axis = h->GetHistogram()->GetXaxis();
            if (coordinate.Contains("y")) axis = h->GetHistogram()->GetYaxis();
        
            AxisFonts(axis, coordinate, title);
        }
        

        std::vector<TH1D*> _hist;
        std::vector<std::pair<std::string,TH1D*> > _autreHists;
        TH1D* _data;

        //MWL
        float    _lumi;
        TString  _xLabel;
        TString  _units;
        TLatex * _extraLabel;
        bool     _breakdown;
        int      _mass;
        int      _nbins;
        float    _low;
        float    _high;
        Int_t   _labelFont      ;
        Float_t _legendTextSize ;
        Float_t _xoffset        ;
        Float_t _yoffset        ;
        Float_t _labelOffset    ;
        Float_t _axisLabelSize  ;
        Float_t _titleOffset    ;


};
