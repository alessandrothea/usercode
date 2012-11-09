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
#include "TPaveText.h"
#include "TGraphAsymmErrors.h"
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
Float_t GetMaximumIncludingErrors(TH1* h)
{
    Float_t maxWithErrors = 0;

    for (Int_t i=1; i<=h->GetNbinsX(); i++) {

        Float_t binHeight = h->GetBinContent(i) + h->GetBinError(i);

        if (binHeight > maxWithErrors) maxWithErrors = binHeight;
    }

    return maxWithErrors;
}

class MWLPlot {
    private:
        std::vector<TH1*> _hist;
        std::vector<std::pair<std::string,TH1*> > _autreHists;
        TH1* _data;
        TGraphAsymmErrors* _nuisances;

        //MWL
        float    _lumi;
        TString  _xLabel;
        TString  _units;
        TLatex * _extraLabel;
        bool     _breakdown;
        bool     _stackSignal;
        bool     _overlayNuisances;
        int      _mass;
        int      _nbins;
        double   _low;
        double   _high;
        Int_t   _labelFont      ;
        Float_t _legendTextSize ;
        Float_t _x0             ;
        Float_t _xoffset        ;
        Float_t _yoffset        ;
        Float_t _labelOffset    ;
        Float_t _axisLabelSize  ;
        Float_t _titleOffset    ;
        Float_t _ratioMin       ;
        Float_t _ratioMax       ;
        Float_t _leftMargin     ;
        Float_t _rightMargin    ;
        TPad *_pad1;
        TPad *_pad2;


    public: 
        MWLPlot() { 
            _hist.resize(nSamples,0); 
            _data             = 0;
            _stackSignal      = false;
            _breakdown        = false;
            _mass             = 0;
            _labelFont        = 42;
            _legendTextSize   = 0.04;
            _x0               = 0.22;
            _xoffset          = 0.25;
            _yoffset          = 0.06;
            _labelOffset      = 0.015;
/*             _axisLabelSize    = 0.050; */
            _axisLabelSize    = 40;
            _titleOffset      = 1.6;
            _leftMargin       = 0.18;
            _rightMargin      = 0.05;
            _extraLabel       = 0x0;
            _pad1             = 0x0;
            _pad2             = 0x0;
            _nuisances        = 0x0;
            _overlayNuisances = false;
            _nbins = _low = _high = -1;
            _ratioMin = _ratioMax = 0.;

        }

        void stretch( float s ) {
            _xoffset     /= s;
            _x0          /= s;
            _titleOffset /= s;
            _rightMargin /= s;
            _leftMargin  /= s;
        }

        void setRatioRange( Float_t min = 0.0, Float_t max = 0.0 ) { _ratioMin = min; _ratioMax = max;} 

        void setDataHist (TH1 * h)         { _data          = h;        } 
        void setHWWHist  (TH1 * h)         { setMCHist(iHWW  ,h);       } 
        void setWWHist   (TH1 * h)         { setMCHist(iWW   ,h);       } 
        void setZJetsHist(TH1 * h)         { setMCHist(iZJets,h);       } 
        void setTopHist  (TH1 * h)         { setMCHist(iTop  ,h);       } 
        void setVVHist   (TH1 * h)         { setMCHist(iVV   ,h);       } 
        void setWZHist   (TH1 * h)         { setMCHist(iWZ   ,h);       } 
        void setZZHist   (TH1 * h)         { setMCHist(iZZ   ,h);       } 
        void setFakesHist(TH1 * h)         { setMCHist(iFakes,h);       } 
        void setWJetsHist(TH1 * h)         { setMCHist(iWJets,h);       }
        void setNuisances(TGraphAsymmErrors* g, bool overlay=false)  { _nuisances = g; _overlayNuisances=overlay;}        

        void setMCHist   (const samp &s,        TH1 * h)  { 
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

        void setMCHist   (const std::string &s, TH1 * h)  { 
            if (sampByName(s) == Undefined) {
                _autreHists.push_back(make_pair(s,h));
            } else {
                setMCHist(sampByName(s),h);
            }
        } 

        void setMass(const int &m) {_mass=m;}

        void Draw(TCanvas *c1, int rebin=1, bool div=false) {

            gStyle->SetOptStat(0);
            c1->cd();
            c1->Clear();

            // adapt legend
            

			if ( div && !GetDataHist() )
				div = false;

            if(div) {
                _pad1 = new TPad("pad1","pad1",0,1-0.614609572,1,1);
                _pad1->SetTopMargin(0.0983606557);
                _pad1->SetBottomMargin(0.025);
            } else {
                _pad1 = new TPad("pad1","pad1",0,0,1,1);
            }
            _pad1->SetRightMargin(_rightMargin);
            _pad1->SetLeftMargin(_leftMargin);
            std::cout << "w:" << _pad1->GetAbsWNDC()*c1->GetWw() << " h:" << _pad1->GetAbsHNDC()*c1->GetWh()  << std::endl;
            _pad1->Draw();
            _pad1->cd();

/*             Float_t padw = _pad1->GetAbsWNDC()*c1->GetWw(); */
/*             Float_t padh = _pad1->GetAbsHNDC()*c1->GetWh(); */

/*             if ( padw > padh ) { */
/*                 _xoffset *= padh/padw; */
/*             } else if ( padw <  padh ) { */
/*                 _yoffset *= padw/padh; */
/*             } */

            RebinHists(rebin);
            THStack *hstack = GetStack(c1->GetLogy());
            TH1 *signal = GetSignalHist();
            TH1 *data   = GetDataHist();

            if(c1->GetLogy()) gPad->SetLogy();
            if(div) hstack->GetHistogram()->SetLabelSize(0.00,"X");
            if(div) hstack->GetHistogram()->SetLabelSize(0.06,"Y");
            if(div) hstack->GetHistogram()->SetTitleSize(0.06,"XY");
            hstack->Draw("hist");
            if(signal && !_stackSignal) signal->Draw("hist,same");
            if(data)     data->Draw("ep,same");
            if (_nuisances && _overlayNuisances ) {
                _nuisances->SetFillStyle(3153);
                _nuisances->Draw("2");
            }
            DrawLabels();
            //            _pad1->GetFrame()->DrawClone();

            if(div) {

                TH1 *summed = GetSummedMCHist();

                TH1 *rdat = (TH1*)data->Clone("rdat");   

                if(gROOT->FindObject("rref")) gROOT->FindObject("rref")->Delete();

				TH1 *rref = (TH1*)summed->Clone("rref");
				rref->SetTitle("rref");
				rref->Reset();

                for (int i = 1, n = rref->GetNbinsX(); i <= n+1; ++i) {
                    rref->SetBinContent(i,summed->GetBinContent(i));
                    rref->SetBinError(i,summed->GetBinError(i));
                }
                rref->SetTitle("");
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

                TGraphAsymmErrors *rnuis = 0x0; 
                if (_nuisances) {
                
                    if(gROOT->FindObject("rnuis")) gROOT->FindObject("rnuis")->Delete();

                    rnuis = (TGraphAsymmErrors*)_nuisances->Clone("rnuis");
                    rnuis->SetTitle("rnuis");

                    for( int i(0); i<rnuis->GetN(); ++i) {
                        double scale = summed->GetBinContent(i+1);
                        rnuis->GetY()[i]      /= scale;
                        rnuis->GetEYhigh()[i] /= scale;
                        rnuis->GetEYlow()[i]  /= scale;
                    }
                }
                c1->cd();
                _pad2 = new TPad("pad2","pad2",0,0,1,1-0.614609572);

                _pad2->SetTopMargin(0.0261437908);
                _pad2->SetBottomMargin(0.392156863);
                _pad2->SetRightMargin(_rightMargin);
                _pad2->SetLeftMargin(_leftMargin);
                _pad2->Draw();
                _pad2->cd();


/*                 TLine *line = new TLine(rref->GetXaxis()->GetXmin(), 1.0, rref->GetXaxis()->GetXmax(), 1.0); */
/*                 line->SetLineColor(kBlack); */
/*                 line->SetLineWidth(1); */
/*                 line->SetLineStyle(1); */

                if ( _ratioMin==0. && _ratioMax==0.)
                    rref->GetYaxis()->SetRangeUser(TMath::Max(0.,1.-absmax), absmax+1.);
                else
                    rref->GetYaxis()->SetRangeUser(_ratioMin,_ratioMax);
                AxisFonts(rref->GetXaxis(), "x", hstack->GetXaxis()->GetTitle());
                AxisFonts(rref->GetYaxis(), "y", "data/mc");
                rref->GetYaxis()->SetTitle("data/mc");
                rref->GetYaxis()->SetLabelSize(0.09);
                rref->GetYaxis()->SetTitleSize(0.09);
                rref->GetYaxis()->SetTitleOffset(_titleOffset*0.66);
                rref->GetXaxis()->SetLabelSize(0.09);
                rref->GetXaxis()->SetTitleSize(0.09);
                rref->GetXaxis()->SetTitleOffset(1.5);

                if (rnuis) {
                    rref->SetFillStyle(0);
                    rref->SetLineColor(0);
                    rref->SetLineWidth(0);
                    rref->Draw("hist");
                    rnuis->SetFillStyle(3153);
                    rnuis->SetFillColor(1);
                    rnuis->SetLineColor(2);
                    rnuis->SetMarkerColor(3);
                    rnuis->Draw("2");
/*                     rnuis->Draw("P"); */
                } else {
                    rref->Draw("E2"); 
                }
                rdat->SetMarkerStyle(20);
                rdat->Draw("E SAME p");
/*                 line->Draw("SAME");  */

                TLine line;
                line.SetLineColor(kBlack);
                line.SetLineWidth(1);
                line.SetLineStyle(1);
                line.DrawLine(rref->GetXaxis()->GetXmin(), 1.0, rref->GetXaxis()->GetXmax(), 1.0);
                line.SetLineStyle(7);
                line.DrawLine(rref->GetXaxis()->GetXmin(), 1.5, rref->GetXaxis()->GetXmax(), 1.5);
                line.DrawLine(rref->GetXaxis()->GetXmin(), 0.5, rref->GetXaxis()->GetXmax(), 0.5);
                c1->Update();
            }   
        } 

        TH1* GetDataHist() { 
        
            if(_data) _data->SetLineColor  (kBlack);
            if(_data) _data->SetMarkerStyle(kFullCircle);
            return _data; 
        }

        TH1 *GetSignalHist() {

            if( _hist[iHWW] ) {
                _hist[iHWW]->SetLineColor(sampleColor[iHWW]);
                _hist[iHWW]->SetLineWidth(3);
            }
            return _hist[iHWW];

        }

        //---
        TH1 *GetSummedMCHist() {

            if(gROOT->FindObject("hMC")) gROOT->FindObject("hMC")->Delete();

			TH1* hMC = 0x0;
			for (int i=0; i<nSamples; i++) if( _hist[i] && i != iHWW)
				hMC = (TH1*)_hist[i]->Clone("hMC");

			hMC->SetTitle("hMC");
			hMC->Reset();

            for (int i=0; i<nSamples; i++) if( _hist[i] && i != iHWW) hMC->Add(_hist[i]);
            for (size_t i=0; i<_autreHists.size(); i++)               hMC->Add(_autreHists[i].second);

			if ( _stackSignal )
				hMC->Add(GetSignalHist());

            return hMC;

        }

        //---
        THStack* GetStack(bool isLog) {
            THStack* hstack = new THStack("HWWStack","HWWStack");

            float binWidth = 0;
            for (int i=0; i<nSamples; i++) if( _hist[i] && i != iHWW) {

                _hist[i]->SetLineColor(1+sampleColor[i]);
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
            
            //
            if ( _stackSignal ) 
                hstack->Add(GetSignalHist());


            hstack->Draw("GOFF");
            hstack->SetTitle("");

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

        void setLumi(float l) { _lumi = l; }
        void setLabel(const TString &s) { _xLabel = s; }
        void setUnits(const TString &s) { _units = s; }
        void setBreakdown(bool b = true) { _breakdown = b; }
        void setStackSignal(bool b=true) { _stackSignal = b; }
        void addLabel(const std::string &s) {
            _extraLabel = new TLatex(0.707, 0.726, TString(s));
            _extraLabel->SetNDC();
            _extraLabel->SetTextAlign(32);
            _extraLabel->SetTextFont(42);
            _extraLabel->SetTextSize(_legendTextSize*0.9);
        }

		TPad* pad1() { return _pad1; }
		TPad* pad2() { return _pad2; }
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
            float x0=_x0; float wx=_xoffset;
            if(_data        ) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _data,                  " data",                "lp"); j++; }
            if(_hist[iHWW  ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iHWW  ]         , higgsLabel,             "l" ); j++; }
            if(_hist[iWW   ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iWW   ]         , " WW",                  "f" ); j++; }
            if(_hist[iZJets]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iZJets]         , " Z+jets",              "f" ); j++; }
            if(_hist[iTop  ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iTop  ]         , " top",                 "f" ); j++; }
            if(_hist[iVV   ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iVV   ]         , " WZ/ZZ",               "f" ); j++; }
            if(_hist[iWJets]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iWJets]         , " W+jets",              "f" ); j++; }
            if(_hist[iWZ   ]) { DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _hist[iWZ   ]         , " WZ",                  "f" ); j++; }
            for(size_t i=0;i<_autreHists.size();++i) {
                                DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _autreHists[i].second , _autreHists[i].first,   "f" ); j++; 
            }
            if (_nuisances && _overlayNuisances) {
                                DrawLegend(x0+pos[j]*wx, 0.80 - off[j]*_yoffset, _nuisances            , " syst #oplus stat",    "f" ); j++;
            }

            TLatex* preliminary = new TLatex(0.896, 0.830, "CMS Preliminary");
            preliminary->SetNDC();
            preliminary->SetTextAlign(32);
            preliminary->SetTextFont(42);
            preliminary->SetTextSize(_legendTextSize*0.95);
            preliminary->Draw("same");

            if ( _lumi ) {
                TLatex* luminosity = new TLatex(0.896, 0.781, TString::Format("L = %.1f fb^{-1}",_lumi));
                luminosity->SetNDC();
                luminosity->SetTextAlign(32);
                luminosity->SetTextFont(42);
                luminosity->SetTextSize(_legendTextSize*0.95);
                luminosity->Draw("same");
            }
            if(_extraLabel) _extraLabel->Draw("same");

            TPaveText* title = (TPaveText*)gPad->FindObject("title");
            if (title) {
                gPad->Modified();
                gPad->Update();
                title->SetFillStyle(0);
            }
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
                TObject* obj,
                TString label,
                TString option)
        {
            TLegend* legend = new TLegend(x1,
                    y1,
                    x1 + _xoffset,
                    y1 + _yoffset);
        
            legend->SetBorderSize(     0);
            legend->SetFillColor (     0);
            legend->SetFillStyle (     0);
            legend->SetTextAlign (    12);
            legend->SetTextFont  (_labelFont);
            legend->SetTextSize  (_legendTextSize);
        
            legend->AddEntry(obj, label.Data(), option.Data());
        
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

};
