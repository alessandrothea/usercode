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
#include "TGraph.h"
#endif

#include <iostream>
#include <algorithm>
#include <utility>


float xPos[] = {0.0,0.0,0.0,0.0,1.3,1.3,1.3,1.3,2.3,3.0,3.3,0.0,1.3,2.3,3.3,0.0,1.3,2.3,3.3}; 
float yOff[] = {  0,  1,  2,  3,  0,  1,  2,  3,  3,  3,  3,  4,  4,  4,  4,  5,  5,  5,  5};

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
Float_t GetMaximumIncludingErrors(TH1F* h)
{
    Float_t maxWithErrors = 0;

    for (Int_t i=1; i<=h->GetNbinsX(); i++) {

        Float_t binHeight = h->GetBinContent(i) + h->GetBinError(i);

        if (binHeight > maxWithErrors) maxWithErrors = binHeight;
    }

    return maxWithErrors;
}





class PlotVHqqHggH {

    public: 
        PlotVHqqHggH() { 
            _data = 0; 
            _breakdown = false; 
            _nbins=-1;
	    _low=-1;
	    _high=-1;
            _labelFont        = 42;
            _legendTextSize   = 0.04;
            _xoffset          = 0.20;
            _yoffset          = 0.06;
	    _globalYoffset    = 0.80;
            _labelOffset      = 0.015;
            _axisLabelSize    = 0.050;
            _titleOffset      = 1.6;
	    _blindSx          = -999;
	    _blindDx          = -999;   
	    _blindBinSx       = 0;
	    _blindBinDx       = 0;
	    _addSignal        = 1;
            _addSignalOnBackground = 0;
            _mergeSignal      = 0;
            _cutSx            = -999;
	    _cutDx            = -999;
            _mass             = -1;
        }
        
        ///---- data
        
        void setDataHist (TH1F * h)         {
	 if (!_data) {
	  _data          = (TH1F*) h->Clone();        
          _data -> SetLineWidth (2);
          _data -> SetMarkerSize (1);
          _data -> SetLineColor (kBlack);
          _data -> SetMarkerColor (kBlack);
	 }
	 else {
	  TH1F* temp_data = (TH1F*) h->Clone();        
	  _data -> Add(temp_data);        
	 }
// 	 int nBin = _data->GetNbinsX();	 
	 double integral;
	 double error;
	 integral = h->IntegralAndError(-1,-1, error);
	 std::cout << " samp = " << "DATA" << " yield = " << integral << " +/- " << error << std::endl;
	 std::cout << " ~~~~~~~~~~~~~~~~~~~~~~~~~~" << std::endl;
	} 
	
	                                                   
       ///---- background
       
       void set_vectTHBkg (std::vector<TH1F*>& vh) {
        std::cout << " BkgSize = " << vh.size() << std::endl;
	for (unsigned int iBkg = 0; iBkg<vh.size(); iBkg++) {
         std::cout << " vh.at(" << iBkg << ") = " << vh.at(iBkg) << std::endl;
         std::cout << " _vectTHBkg.size() = " << _vectTHBkg.size() << std::endl;
	 _vectTHBkg.push_back(vh.at(iBkg));
	 double integral;
	 double error;
	 integral = vh.at(iBkg)->IntegralAndError(-1,-1, error);
	 std::cout << " samp = " << "bkg[" << iBkg << "] ::" << " yield = " << integral << " +/- " << error << std::endl;
	 std::cout << " ~~~~~~~~~~~~~~~~~~~~~~~~~~" << std::endl;
	}
       }
	
	void set_vectNameBkg (std::vector<std::string>& vh) { 
         std::cout << " ~~~~ name ~~~~" << std::endl;
	 for (unsigned int iBkg = 0; iBkg<vh.size(); iBkg++) {
	 _vectNameBkg.push_back(vh.at(iBkg));
         std::cout << " name.at(" << iBkg <<" :: " << vh.size() << ") = " << (vh.at(iBkg)) << std::endl;
	}
	std::cout << " ~~~~ name (end) ~~~~" << std::endl;
        }

	void set_vectColourBkg (std::vector<int>& vh) { 
	 for (unsigned int iBkg = 0; iBkg<vh.size(); iBkg++) {
	 _vectColourBkg.push_back(vh.at(iBkg));
	}
       }
       
       void set_vectSystBkg (std::vector<double>& vh) { 
	for (unsigned int iBkg = 0; iBkg<vh.size(); iBkg++) {
	 _vectSystBkg.push_back(vh.at(iBkg));
	}
       }

       void set_vectScaleBkg (std::vector<double>& vh) { 
        for (unsigned int iBkg = 0; iBkg<vh.size(); iBkg++) {
         _vectScaleBkg.push_back(vh.at(iBkg));
        }
       }
              
       void set_vectNormalizationBkg (std::vector<double>& vh) { 
        for (unsigned int iBkg = 0; iBkg<vh.size(); iBkg++) {
         _vectNormalizationBkg.push_back(vh.at(iBkg));
        }
       }
                    
       
       ///---- signal

       void set_vectTHSig (std::vector<TH1F*>& vh) { 
	for (unsigned int iSig = 0; iSig<vh.size(); iSig++) {
	 _vectTHSig.push_back(vh.at(iSig));
	 double integral;
	 double error;
	 integral = vh.at(iSig)->IntegralAndError(-1,-1, error);
	 std::cout << " samp = " << "sig[" << iSig << "] ::" << " yield = " << integral << " +/- " << error << std::endl;
	 std::cout << " ~~~~~~~~~~~~~~~~~~~~~~~~~~" << std::endl;
	}
       }
	
	void set_vectNameSig (std::vector<std::string>& vh) { 
	 for (unsigned int iSig = 0; iSig<vh.size(); iSig++) {
	 _vectNameSig.push_back(vh.at(iSig));
	}
       }

	void set_vectColourSig (std::vector<int>& vh) { 
	 for (unsigned int iSig = 0; iSig<vh.size(); iSig++) {
	 _vectColourSig.push_back(vh.at(iSig));
	}
       }
       
       void set_vectSystSig (std::vector<double>& vh) { 
	for (unsigned int iSig = 0; iSig<vh.size(); iSig++) {
	 _vectSystSig.push_back(vh.at(iSig));
	}
       }

       void set_vectScaleSig (std::vector<double>& vh) { 
        for (unsigned int iSig = 0; iSig<vh.size(); iSig++) {
         _vectScaleSig.push_back(vh.at(iSig));
        }
       }
       
       void set_vectNormalizationSig (std::vector<double>& vh) { 
        for (unsigned int iSig = 0; iSig<vh.size(); iSig++) {
         _vectNormalizationSig.push_back(vh.at(iSig));
        }
       }
       

       //---- stack signal = 1, no stack signal = 0
       void set_addSignal (int addSignal) {
        _addSignal = addSignal;
	std::cout << " addSignal = " << _addSignal << std::endl;
       }

       //---- stack signal over the background = 1, no stack signal over the background = 0
       void set_addSignalOnBackground (int addSignalOnBackground) {
        _addSignalOnBackground = addSignalOnBackground;
        std::cout << " addSignalOnBackground = " << _addSignalOnBackground << std::endl;
       }
       
       //---- merge signal in one unique histogram:  merge = 1, no merge = 0
       void set_mergeSignal (int mergeSignal) {
        _mergeSignal = mergeSignal;
        std::cout << " mergeSignal = " << _mergeSignal << std::endl;
       }
         
       //---- blind bins
       void setBlindBinSx(int blindBinSx) {
	_blindBinSx = blindBinSx;
       }

       void setBlindBinDx(int blindBinDx) {
	_blindBinDx = blindBinDx;
       }

       void setBlindSx(double blindSx) {
	_blindSx = blindSx;
       }

       void setBlindDx(double blindDx) {
	_blindDx = blindDx;
       }

       //---- cuts
       void setCutSx(double cutSx, std::string what) {
	_cutSx = cutSx;
	if (what == ">") _cutSxSign = 1;
	if (what == "<") _cutSxSign = -1;
       }
       
       void setCutDx(double cutDx, std::string what) {
	_cutDx = cutDx;
	if (what == ">") _cutDxSign = 1;
	if (what == "<") _cutDxSign = -1;
       }
       
       //---- prepare histos and stacks                                                   
       void prepare () {
	std::cout << " prepare ... " << std::endl;

        //---- in case there is a scale factor to be applied ...
        if (_vectScaleBkg.size() != 0) {
         for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
          std::cout << " iBkg = " << iBkg << " :: " << _vectTHBkg.size() << std::endl;
          int nbin = _vectTHBkg.at(iBkg) -> GetNbinsX();
          for (int iBin = 0; iBin < nbin; iBin++) {
           double err_before = _vectTHBkg.at(iBkg) -> GetBinError(iBin+1);
           double value = _vectTHBkg.at(iBkg) -> GetBinContent(iBin+1);
           double scale = _vectScaleBkg.at(iBkg);
           double err_after = scale * err_before;
           double value_after = scale * value;
           _vectTHBkg.at(iBkg) -> SetBinError   (iBin+1, err_after);
           _vectTHBkg.at(iBkg) -> SetBinContent (iBin+1, value_after);
          }
         }
        }
        
        if (_vectScaleSig.size() != 0) {
         for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
          std::cout << " iSig = " << iSig << " :: " << _vectTHSig.size() << std::endl;
          int nbin = _vectTHSig.at(iSig) -> GetNbinsX();
          for (int iBin = 0; iBin < nbin; iBin++) {
           double err_before = _vectTHSig.at(iSig) -> GetBinError(iBin+1);
           double value = _vectTHSig.at(iSig) -> GetBinContent(iBin+1);
           double scale = _vectScaleSig.at(iSig);
           double err_after = scale*err_before;
           double value_after = scale * value;
           _vectTHSig.at(iSig) -> SetBinError   (iBin+1, err_after);
           _vectTHSig.at(iSig) -> SetBinContent (iBin+1, value_after);
          }
         }
        }
        
        //---- in case the normalization of the background must be changed ...
        if (_vectNormalizationBkg.size() != 0) {
         std::cout << "normalize Bkg" << std::endl;
         for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
          int nbin = _vectTHBkg.at(iBkg) -> GetNbinsX();
          double normalization = _vectNormalizationBkg.at(iBkg);
          if (normalization >= 0) {
           double integral = _vectTHBkg.at(iBkg)->Integral();
           double scale;
           if (integral != 0) scale = normalization/integral;
           else scale = 1.;
           
           for (int iBin = 0; iBin < nbin; iBin++) {
            double err_before = _vectTHBkg.at(iBkg) -> GetBinError(iBin+1);
            double value = _vectTHBkg.at(iBkg) -> GetBinContent(iBin+1);
            double err_after = scale * err_before;
            double value_after = scale * value;
            _vectTHBkg.at(iBkg) -> SetBinError   (iBin+1, err_after);
            _vectTHBkg.at(iBkg) -> SetBinContent (iBin+1, value_after);
           }
          }
         }
        }
        
        if (_vectNormalizationSig.size() != 0) {
         std::cout << "normalize Sig" << std::endl;
         for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
          int nbin = _vectTHSig.at(iSig) -> GetNbinsX();
          double normalization = _vectNormalizationSig.at(iSig);
          if (normalization >= 0) {
           double integral = _vectTHSig.at(iSig)->Integral();
           double scale;
           if (integral != 0) scale = normalization/integral;
           else scale = 1.;
           
           for (int iBin = 0; iBin < nbin; iBin++) {
            double err_before = _vectTHSig.at(iSig) -> GetBinError(iBin+1);
            double value = _vectTHSig.at(iSig) -> GetBinContent(iBin+1);
            double err_after = scale * err_before;
            double value_after = scale * value;
            _vectTHSig.at(iSig) -> SetBinError   (iBin+1, err_after);
            _vectTHSig.at(iSig) -> SetBinContent (iBin+1, value_after);
           }
          }
         }
        }        
        
        //---- in case there are systematic errors to be added ...
        
	if (_vectSystBkg.size() != 0) {
         std::cout << " ~~~~~~~~~ after systematics addition ~~~~~~~~~~~~~" << std::endl;
	 for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
	  int nbin = _vectTHBkg.at(iBkg) -> GetNbinsX();
	  for (int iBin = 0; iBin < nbin; iBin++) {
	   double err_before = _vectTHBkg.at(iBkg) -> GetBinError(iBin+1);
	   double value = _vectTHBkg.at(iBkg) -> GetBinContent(iBin+1);
	   double syst = _vectSystBkg.at(iBkg);
	   double err_after = sqrt(err_before*err_before + syst*value*syst*value);
	   _vectTHBkg.at(iBkg) -> SetBinError(iBin+1, err_after);
	  }
	  
	  double error;
          double integral = _vectTHBkg.at(iBkg)->IntegralAndError(-1,-1, error);
          std::cout << " samp = " << "bkg[" << iBkg << "] ::" << " yield = " << integral << " +/- " << error << std::endl;
          std::cout << " ~~~~~~~~~~~~~~~~~~~~~~~~~~" << std::endl;          
	 }
	}
	
	if (_vectSystSig.size() != 0) {
	 for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
	  int nbin = _vectTHSig.at(iSig) -> GetNbinsX();
	  for (int iBin = 0; iBin < nbin; iBin++) {
	   double err_before = _vectTHSig.at(iSig) -> GetBinError(iBin+1);
	   double value = _vectTHSig.at(iSig) -> GetBinContent(iBin+1);
	   double syst = _vectSystSig.at(iSig);
	   double err_after = sqrt(err_before*err_before + syst*value*syst*value);
	   _vectTHSig.at(iSig) -> SetBinError(iBin+1, err_after);
	  }
	 }
	}


	//---- prepare style for signal histograms (in case of drawing  over background
        for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
         _vectTHSig.at(iSig) -> SetFillStyle(1001);
         _vectTHSig.at(iSig) -> SetLineColor(_vectColourSig.at(iSig));
         _vectTHSig.at(iSig) -> SetLineWidth(3);
        }


        //---- add signal histograms
        for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
         std::cout << " nbin(" << iSig << ") = " << _vectTHSig.at (iSig)->GetNbinsX() << std::endl;
         _vectTHstackSig.push_back ((TH1F*) _vectTHSig.at (iSig) -> Clone() );
         if (iSig != 0 && _addSignal) { 
          _vectTHstackSig.at (iSig) -> Add ( _vectTHstackSig.at (iSig-1) ) ;
         }
        }  
        
	//---- prepare style for signal histograms
	for (unsigned int iSig = 0; iSig<_vectTHstackSig.size(); iSig++) {
         _vectTHstackSig.at(iSig) -> SetFillStyle(0);
         _vectTHstackSig.at(iSig) -> SetLineColor(_vectColourSig.at(iSig));
         _vectTHstackSig.at(iSig) -> SetLineWidth(3);
        }
        
        //---- blind only if there is data histogram
        if (_data) {
         int nBin = _data -> GetNbinsX();
         double binWidth = _data -> GetBinWidth(1);
         double min_binWidth = _data -> GetBinLowEdge(1);
         double max_binWidth = _data -> GetBinLowEdge(nBin + 1);
         
         std::cout << " blindBinSx = " << _blindBinSx << " :: nBin = " << nBin << std::endl;
         std::cout << " blindBinDx = " << _blindBinDx << " :: nBin = " << nBin << std::endl;
         
         if (_blindSx != -999 && _blindBinSx==0) {
          if (binWidth != 0) _blindBinSx = ceil((_blindSx-min_binWidth) / binWidth);
         }
         
         if (_blindDx != -999 && _blindBinDx==0) {
          if (binWidth != 0) _blindBinDx = ceil((max_binWidth-_blindDx) / binWidth);
         }
         
         std::cout << " blindSx    = " << _blindSx << " :: (" << min_binWidth << " , " << max_binWidth << ") :: " << binWidth << std::endl;
         std::cout << " blindDx    = " << _blindDx << " :: (" << min_binWidth << " , " << max_binWidth << ") :: " << binWidth << std::endl;
         std::cout << " blindBinSx = " << _blindBinSx << " :: nBin = " << nBin << std::endl;
         std::cout << " blindBinDx = " << _blindBinDx << " :: nBin = " << nBin << std::endl;
         
         for (int iBin=(nBin-_blindBinDx); iBin < nBin; iBin++) {
          _data -> SetBinContent(iBin+1,0);
          _data -> SetBinError(iBin+1,0);
         }
         for (int iBin=0; iBin < _blindBinSx; iBin++) {
          _data -> SetBinContent(iBin+1,0);
          _data -> SetBinError(iBin+1,0);
         }
        }
       } 


       void Draw(const int &rebin=1,const bool &div=false) {
            Draw(new TCanvas(),rebin,div);
        }

        void Draw(TCanvas *c1, const int &rebin=1, const bool &div=false) {
// 	    std::cout << " Ora disegno ! " << std::endl;
// 	    std::cout << " rebin = " << rebin << std::endl; 
	   int rebin2 = rebin; //---> just not to have warning :)
	   rebin2+=0; 
            
            gStyle->SetOptStat(0);
            c1->cd();
            c1->Clear();

            TPad *pad1;
            if(div) {
                pad1 = new TPad("pad1","pad1",0,1-0.614609572,1,1);
                pad1->SetTopMargin(0.0983606557);
                pad1->SetBottomMargin(0.025);
            } else {
	        _globalYoffset = 0.85;
                pad1 = new TPad("pad1","pad1",0,0,1,1);
            }
            pad1->Draw();
            pad1->cd();

// 	    std::cout << " GetStack" << std::endl;
            THStack *hstack = GetStack(c1->GetLogy());
// 	    std::cout << " GetData" << std::endl;
	    TH1F *data   = GetDataHist();
	    
            if (c1->GetLogy()) gPad->SetLogy();
            if (div) hstack->GetHistogram()->SetLabelSize(0.00,"X");
            if (div) hstack->GetHistogram()->SetLabelSize(0.06,"Y");
            if (div) hstack->GetHistogram()->SetTitleSize(0.06,"XY");
            hstack->Draw("hist");
//             std::cout << " Disegnato lo stack! " << std::endl;

            for (unsigned int iSig = 0; iSig<_vectTHstackSig.size(); iSig++) {
             if (_mergeSignal == 0 ||  iSig == (_vectTHstackSig.size()-1)) {
              if (_mergeSignal == 1) {
               _vectTHstackSig.at(iSig) -> SetLineColor (kRed);
              }
              _vectTHstackSig.at(iSig) -> Draw("hist,same");
             }
            }
            
            if (data)     data->Draw("ep,same");
            DrawLabels();
            pad1->GetFrame()->DrawClone();

	    TH1F *summed = GetSummedMCHist();
	    summed->SetFillStyle(3335);
	    summed->SetFillColor(kBlack);
	    summed->SetMarkerSize(0);
	    summed->Draw("sameE2");

	    
	    _max = hstack->GetMaximum() * 1.1;
	    if (_data && _data->GetMaximum() * 1.1 > _max) _max = _data->GetMaximum() * 1.1;

	    _maxLog = hstack->GetMaximum() * 1.05;
	    if (_data && _data->GetMaximum() * 1.05 > _maxLog) _maxLog = _data->GetMaximum() * 1.05;
	    
	    _min = 0;
	    if (hstack->GetMinimum() > 0) _minLog = hstack->GetMinimum() / 10.;
	    else _minLog = 0.0001;
	    if (_vectTHstackSig.size() != 0 && _vectTHstackSig.at(0) -> GetMinimum() / 10. < _minLog && _vectTHstackSig.at(0) -> GetMinimum() > 0) _minLog = _vectTHstackSig.at(0)->GetMinimum() / 10.;
	    
	    
             if (_blindBinDx != 0 && _data) {
	     double xblind    = data->GetBinLowEdge(data->GetNbinsX() - _blindBinDx + 1);
	     double xblindmax = data->GetBinLowEdge(data->GetNbinsX() + 1);
	     
	     double maxy ;
	     double miny ;
	     
	     if (c1->GetLogy()) {
	      maxy = _maxLog;
	      miny = _minLog;
	     }
	     else {
	      maxy = _max;
	      miny = _min;
	     }
	     
	     
	     Double_t x[2], y[2], x2[2];
	     Int_t n = 2;
	     for (Int_t i=0;i<n;i++) {
	      x[i] = xblind ;
	      x2[i]= xblindmax; 
	     }
	      
	     y[0] = miny;
	     y[1] = maxy*10.; 
	     
	     TGraph* grBlind = new TGraph(2*n);
	     grBlind->SetPoint(0,x2[0],y[0]); 
	     grBlind->SetPoint(1,x2[0],y[1]); 
	     grBlind->SetPoint(2,x [0],y[1]); 
	     grBlind->SetPoint(3,x [0],y[0]); 
	     grBlind->SetFillColor(kBlue);
	     grBlind->SetLineColor( 0);
	     grBlind->SetFillStyle(3003);
	     grBlind->Draw("f");
	    }
	    
	    if (_blindBinSx != 0 && data) {
	     double xblind    = data->GetBinLowEdge(_blindBinSx + 1);
	     double xblindmin = data->GetBinLowEdge(1);
	     
	     double maxy ;
	     double miny ;
	     
	     if (c1->GetLogy()) {
	      maxy = _maxLog;
	      miny = _minLog;
	     }
	     else {
	      maxy = _max;
	      miny = _min;
	     }
	     
	     
	     Double_t x[2], y[2], x2[2];
	     Int_t n = 2;
	     for (Int_t i=0;i<n;i++) {
	      x[i] = xblind ;
	      x2[i]= xblindmin; 
	     }
	     y[0] = miny;
	     y[1] = maxy*10.;	    
	     
	     TGraph* grBlind = new TGraph(2*n);
	     grBlind->SetPoint(0,x2[0],y[0]); 
	     grBlind->SetPoint(1,x2[0],y[1]); 
	     grBlind->SetPoint(2,x [0],y[1]); 
	     grBlind->SetPoint(3,x [0],y[0]); 
	     grBlind->SetFillColor(kBlue);
	     grBlind->SetLineColor( 0);
	     grBlind->SetFillStyle(3003);
	     grBlind->Draw("f");
	    }
	    
	    
	    ///---- Cuts ----
	    
	    Double_t XRange = 0;
	    if      ( _vectTHstackSig.size() > 0 ) XRange = _vectTHstackSig.at(0)->GetBinLowEdge(_vectTHstackSig.at(0)->GetNbinsX()) - _vectTHstackSig.at(0)->GetBinLowEdge(1);
	    else if ( _vectTHBkg.size() > 0      ) XRange = _vectTHBkg.at(0)->GetBinLowEdge(_vectTHBkg.at(0)->GetNbinsX()) - _vectTHBkg.at(0)->GetBinLowEdge(1);
	    else if ( _data ) XRange = _data -> GetBinLowEdge(_data->GetNbinsX()) - _data->GetBinLowEdge(1);
	    
	    ///---- ---- cutSx ----
	    if (_cutSx != -999) {     
	     Double_t x[2], y[2], x2[2];
	     Int_t n = 2;
	     for (Int_t i=0;i<n;i++) {
	      x[i] = _cutSx ;
	      if ( _cutSxSign == 1  ) x2[i]= _cutSx - 0.05*( XRange ) ; 
	      if ( _cutSxSign == -1 ) x2[i]= _cutSx + 0.05*( XRange ) ; 
	     }
	     if (c1->GetLogy()) {
	      y[0] = _minLog;
	      y[1] = _maxLog;
	     } else {
	      y[0] = _min;
	      y[1] = _max;
	     }
	     
	     TGraph* gr = new TGraph(n,x,y);
	     gr->SetLineWidth(2);
	     gr->SetLineColor(kRed);
	     gr->Draw("");
	     
	     TGraph* grF = new TGraph(2*n);
	     grF->SetPoint(0,x2[0],y[0]); 
	     grF->SetPoint(1,x2[0],y[1]); 
	     grF->SetPoint(2,x [0],y[1]); 
	     grF->SetPoint(3,x [0],y[0]); 
	     grF->SetFillColor(kRed);
	     grF->SetLineColor( 0);
	     grF->SetFillStyle(3005);
	     grF->Draw("f");
	    }
	    
	    ///---- ---- cutDx ----
	    if (_cutDx != -999) {
	     
	     Double_t x[2], y[2], x2[2];
	     Int_t n = 2;
	     for (Int_t i=0;i<n;i++) {
	      x[i] = _cutDx ;
	      if ( _cutDxSign == 1  ) x2[i]= _cutDx - 0.05*( XRange ) ; 
	      if ( _cutDxSign == -1 ) x2[i]= _cutDx + 0.05*( XRange ) ; 
	     }
	     if (c1->GetLogy()) {
	      y[0] = _minLog;
	      y[1] = _maxLog;
	     } else {
	      y[0] = _min;
	      y[1] = _max;
	     }
	     
	     TGraph* gr = new TGraph(n,x,y);
	     gr->SetLineWidth(2);
	     gr->SetLineColor(kRed);
	     gr->Draw("");
	     
	     TGraph* grF = new TGraph(2*n);
	     grF->SetPoint(0,x2[0],y[0]); 
	     grF->SetPoint(1,x2[0],y[1]); 
	     grF->SetPoint(2,x [0],y[1]); 
	     grF->SetPoint(3,x [0],y[0]); 
	     grF->SetFillColor(kRed);
	     grF->SetLineColor( 0);
	     grF->SetFillStyle(3005);
	     grF->Draw("f");
	    }
	    
	    
	    
	    
	    
	    
	    
            if (div) {

//                 TH1F *summed = GetSummedMCHist();

                TH1F *rdat = (TH1F*)data->Clone("rdat");   
                if(gROOT->FindObject("rref")) gROOT->FindObject("rref")->Delete();
                TH1F *rref = new TH1F("rref","rref",
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

// 		rref->GetYaxis()->SetRangeUser(TMath::Max(0.,1.-absmax), absmax+1.);
// 		rref->GetYaxis()->SetRangeUser(TMath::Max(0.,1.-absmax), TMath::Min(10.,absmax+1.));
                rref->GetYaxis()->SetRangeUser(0., 3.);
//                 rref->GetYaxis()->SetRangeUser(0., 5.);
                
                //                 AxisFonts(rref->GetYaxis(), "y", "ratio");
                AxisFonts(rref->GetXaxis(), "x", hstack->GetXaxis()->GetTitle());
                rref->GetYaxis()->SetTitle("data / sim");
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
                pad2->GetFrame()->DrawClone();
            }
            
            ///---- write to screen numbers ----
            
            TObjArray* histos = hstack->GetStack () ;
	    Int_t number = histos->GetEntries();
	    TH1F* last = (TH1F*) histos->At (number-1) ;
	    double toterror;
	    double tot;
// 	    int totnumbers;
	    std::cout << " ~~~~~~ " << std::endl;	   
// 	    totnumbers = last->Integral();
	    tot = last->IntegralAndError(-1,-1, toterror);
	    std::cout << " totMC   = " << tot << " +/- " << toterror << std::endl;

	    for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
	     tot = _vectTHSig.at(iSig) -> IntegralAndError(-1,-1, toterror);     
	     std::cout << " totMC signal " << _vectNameSig.at(iSig) << " = " << tot << " +/- " << toterror << std::endl;
	    }
	  
	    if(div) {
	     tot = data->IntegralAndError(-1,-1, toterror);
	     std::cout << " totDATA = " << tot << " +/- " << toterror << std::endl;
	    }
        }


        TH1F* GetDataHist() { 
        
            if(_data) _data->SetLineColor  (kBlack);
            if(_data) _data->SetMarkerStyle(kFullCircle);
            return _data; 
        }

        TH1F *GetSummedMCHist() {
         
         if ( _nbins == -1 && _vectTHBkg.size() != 0) {
          _nbins  = _vectTHBkg.at(0)->GetNbinsX();
          _low    = _vectTHBkg.at(0)->GetXaxis()->GetBinLowEdge(1);
          _high   = _vectTHBkg.at(0)->GetBinLowEdge(_nbins+1);
         }
         
         if(gROOT->FindObject("hMC")) gROOT->FindObject("hMC")->Delete();
                                                        TH1F* hMC = new TH1F("hMC","hMC",_nbins,_low,_high);
         hMC->Sumw2();
         for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
          hMC->Add(_vectTHBkg.at(iBkg));
         }
         if (_addSignalOnBackground) {
          //---- prepare style for signal histograms -> dot-line if also superimposed
          for (unsigned int iSig = 0; iSig<_vectTHstackSig.size(); iSig++) {
           _vectTHstackSig.at(iSig) -> SetLineStyle(2);
          }
          for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
           hMC->Add(_vectTHSig.at (iSig));
          }             
         }
         
         return hMC;   
        }
        
        THStack* GetStack(bool isLog) {
            THStack* hstack = new THStack();
//             float binWidth = 0;
	    for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
	     _vectTHBkg.at (iBkg) -> SetLineColor( _vectColourBkg.at (iBkg) );
	     _vectTHBkg.at (iBkg) -> SetFillColor( _vectColourBkg.at (iBkg) );
	     _vectTHBkg.at (iBkg) -> SetFillStyle(1001);
// 	     binWidth = _vectTHBkg.at (iBkg) -> GetBinWidth(1);
	     hstack->Add(_vectTHBkg.at (iBkg));
	    }
	    
	    if (_addSignalOnBackground) {
             //---- prepare style for signal histograms -> dot-line if also superimposed
             for (unsigned int iSig = 0; iSig<_vectTHstackSig.size(); iSig++) {
              _vectTHstackSig.at(iSig) -> SetLineStyle(2);
             }
             
             for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
              _vectTHSig.at (iSig) -> SetLineColor( _vectColourSig.at (iSig) );
              _vectTHSig.at (iSig) -> SetFillColor( _vectColourSig.at (iSig) );
              _vectTHSig.at (iSig) -> SetFillStyle(3003);
              if (_mergeSignal == 0) {
               hstack->Add(_vectTHSig.at (iSig));
              }
             }             
             
             if (_mergeSignal == 1) {
              for (unsigned int iSig = 0; iSig<_vectTHstackSig.size(); iSig++) {
               if (iSig == (_vectTHstackSig.size() -1 ) ){
//                 _vectTHstackSig.at (iSig) -> SetLineColor( _vectColourSig.at (iSig) );
//                 _vectTHstackSig.at (iSig) -> SetFillColor( _vectColourSig.at (iSig) );
//                 _vectTHstackSig.at (iSig) -> SetFillStyle(3003);
                TH1F* tempHist = (TH1F*) _vectTHstackSig.at (iSig)->Clone("allSignal");
                tempHist -> SetFillStyle(1001);
                tempHist -> SetLineColor(kRed);
                tempHist -> SetLineStyle(1);
                tempHist -> SetLineWidth(3);
                hstack->Add(tempHist);
               }
              }             
             }
            }
	    
            hstack->Draw("GOFF");

            Float_t theMax = hstack->GetMaximum();
            Float_t theMin;
	    if (hstack->GetMinimum() >= 0 ) theMin = hstack->GetMinimum();
	    else theMin = 0.0001;

	    if (_vectTHstackSig.size() != 0) {
	     if (_vectTHstackSig.at(_vectTHstackSig.size()-1)->GetMaximum() > theMax) theMax = _vectTHstackSig.at(_vectTHstackSig.size()-1)->GetMaximum();
	     if (_vectTHstackSig.at(_vectTHstackSig.size()-1)->GetMinimum() < theMin) theMin = _vectTHstackSig.at(_vectTHstackSig.size()-1)->GetMinimum();	     
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
		    THStackAxisFonts(hstack, "y", "entries");
//                     THStackAxisFonts(hstack, "y", TString::Format("entries / %.0f %s", binWidth,_units.Data()));
                }
            }
            return hstack;
         }

        void setMass(const float &m) { _mass = m; }
        void setLumi(const float &l) { _lumi = l; }
        void setLabel(const TString &s) { _xLabel = s; }
        void setUnits(const TString &s) { _units = s; }
        void setBreakdown(const bool &b = true) { _breakdown = b; }
        void addLabel(const std::string &s) {
	    _extraLabel = new TString (s);
//             _extraLabel = new TLatex(0.707, 0.726, TString(s));
//             _extraLabel->SetNDC();
//             _extraLabel->SetTextAlign(32);
//             _extraLabel->SetTextFont(42);
//             _extraLabel->SetTextSize(_legendTextSize*0.9);
        }

    private: 
        int GetSampCount() {	 
	 int sampCount = _vectTHBkg.size();
	 sampCount += _vectTHstackSig.size();
	 if  (_data) sampCount++;
	 
	 return sampCount;
        }

        void DrawLabels() {

            // total mess to get it nice, should be redone
            size_t j=0;

            float *pos,*off;
            int sampCount = GetSampCount();
            if(sampCount == 12 || sampCount == 15) { pos = xPosA; off = yOffA; }
            else if(sampCount == 11 )              { pos = xPosB; off = yOffB; }
            else                                   { pos = xPos;  off = yOff;  }
            float x0=0.22; float wx=0.19;
            if(_data        ) { 
	     DrawLegend(x0+pos[j]*wx, _globalYoffset - off[j]*_yoffset, _data,                  " data",                "lp");
	     j++; 
	    }
	    for (unsigned int iSig = 0; iSig<_vectTHstackSig.size(); iSig++) {
             if (_mergeSignal == 0 ||  iSig == (_vectTHstackSig.size()-1)) {
              if (_mergeSignal == 1) {
               TString name4Legend;
               if (_mass == -1) {
                name4Legend = Form ("Higgs");
               }
               else {
                name4Legend = Form ("Higgs %d GeV", _mass);
               }
               DrawLegend(x0+pos[1]*wx, _globalYoffset - off[1]*_yoffset, _vectTHstackSig.at(iSig)         , name4Legend.Data() ,           "l" );
              }
              else {
               DrawLegend(x0+pos[j]*wx, _globalYoffset - off[j]*_yoffset, _vectTHstackSig.at(iSig)         , _vectNameSig.at(iSig) ,           "l" );
              }
             }
	     j++;
	    }
	    for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
	     DrawLegend(x0+pos[j]*wx, _globalYoffset - off[j]*_yoffset, _vectTHBkg.at(iBkg)         , _vectNameBkg.at(iBkg) ,           "f" );
	     j++; 
	    }
	    
            TLatex* luminosity;
            if(_extraLabel) {
	     luminosity = new TLatex(0.670, 0.781, TString::Format("#splitline{CMS preliminary}{#splitline{     L = %.1f fb^{-1}}{%s}}",_lumi,_extraLabel->Data()));
	    }
	    else {
	     luminosity = new TLatex(0.670, 0.781, TString::Format("#splitline{CMS preliminary}{     L = %.1f fb^{-1}}",_lumi));
	    }
            luminosity->SetNDC();
            luminosity->SetTextAlign(12);
            luminosity->SetTextFont(42);
            luminosity->SetTextSize(_legendTextSize*0.95);
            luminosity->Draw("same");
// 	    if(_extraLabel) _extraLabel->Draw("same");
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
                TH1F*   hist,
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
        

        std::vector<TH1F*>       _vectTHBkg             ;
        std::vector<std::string> _vectNameBkg           ;
        std::vector<int>         _vectColourBkg         ;
        std::vector<double>      _vectSystBkg           ;
        std::vector<double>      _vectScaleBkg          ;
        std::vector<double>      _vectNormalizationBkg  ;
        
        std::vector<TH1F*>        _vectTHstackSig       ;
        std::vector<TH1F*>        _vectTHSig            ;
        std::vector<std::string> _vectNameSig           ;
        std::vector<int>         _vectColourSig         ;
        std::vector<double>      _vectSystSig           ;
        std::vector<double>      _vectScaleSig          ;
        std::vector<double>      _vectNormalizationSig  ;
        

        TH1F* _data;

        float    _lumi;
	
        TString  _xLabel;
        TString  _units;
//         TLatex * _extraLabel;
	TString * _extraLabel;
        bool     _breakdown;
        int      _nbins;
        float    _low;
        float    _high;
	
	float    _max;
	float    _min;
	float    _maxLog;
	float    _minLog;
	
        Int_t   _labelFont      ;
        Float_t _legendTextSize ;
        Float_t _xoffset        ;
        Float_t _yoffset        ;
	Float_t _globalYoffset  ;
	Float_t _labelOffset    ;
        Float_t _axisLabelSize  ;
        Float_t _titleOffset    ;
	
	int     _blindBinSx        ;
	int     _blindBinDx        ;
	double  _blindSx        ;
	double  _blindDx        ;
	
	double  _cutSx          ;
	double  _cutDx          ;
	int     _cutSxSign      ; // -1 = "<"       +1 = ">"
	int     _cutDxSign      ; // -1 = "<"       +1 = ">"
	
	int     _addSignal      ;
        int     _addSignalOnBackground      ;
        
        int     _mergeSignal    ;
        
        int     _mass           ;
        
};


