#include<vector>

#if !defined (__CINT__) || defined (__MAKECINT__)
#include "THStack.h"
#include "TGaxis.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TLatex.h"
#include "TPad.h"
#include "TCanvas.h"
#include "TAxis.h"
#include "TLegend.h"
#include "TFrame.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TGraph.h"
#include "TGraphAsymmErrors.h"
#include "TGraph2DErrors.h"
#include "TExec.h"
#include "TText.h"
#endif

#include <iostream>
#include <algorithm>
#include <utility>

#ifdef __MAKECINT__
#pragma link C++ class std::vector<TH1F*>;
#endif

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
            _doBandError      = false;
            _doLabelNumber    = false;
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
            //   int nBin = _data->GetNbinsX();  
            double integral;
            double error;
            integral = h->IntegralAndError(-1,-1, error);
            std::cout << " samp = " << "DATA" << " yield = " << integral << " +/- " << error << std::endl;
            std::cout << " ~~~~~~~~~~~~~~~~~~~~~~~~~~" << std::endl;
        } 


        void set_doLabelNumber (bool doLabelNumber) {
            _doLabelNumber = doLabelNumber;
        }


        void set_ErrorBand (TGraphAsymmErrors& grAE) {
            std::cout << " TGraphAsymmErrors:: Error band"  << std::endl;
            if (!_doBandError) {
                _BandError = (TGraphAsymmErrors*) grAE.Clone();
            }
            else {

                TGraphAsymmErrors* temp_BandError = new TGraphAsymmErrors ();

                int nBin =  _BandError->GetN();
                for (int iBin = 0; iBin < nBin; iBin ++) {
                    double X = (_BandError->GetX()) [iBin];
                    double Y = (_BandError->GetY()) [iBin];

                    double errXUp      = _BandError->GetErrorXhigh(iBin);
                    double errXDown    = _BandError->GetErrorXlow(iBin);
                    double errYUp      = _BandError->GetErrorYhigh(iBin);
                    double errYDown    = _BandError->GetErrorYlow(iBin);

                    /*           double X2 = (grAE.GetX()) [iBin]; */
                    double Y2 = (grAE.GetY()) [iBin];

                    /*           double errXUp2      = grAE.GetErrorXhigh(iBin); */
                    /*           double errXDown2    = grAE.GetErrorXlow(iBin); */
                    double errYUp2      = grAE.GetErrorYhigh(iBin);
                    double errYDown2    = grAE.GetErrorYlow(iBin);

                    double errXUpComb      = errXUp; // sqrt(errXUp2*errXUp2     + errXUp*errXUp);  --> on X no propagation!
                    double errXDownComb    = errXDown; // sqrt(errXDown2*errXDown2 + errXDown*errXDown);   --> on X no propagation!
                    double errYUpComb      = sqrt(errYUp2*errYUp2     + errYUp*errYUp);
                    double errYDownComb    = sqrt(errYDown2*errYDown2 + errYDown*errYDown);

                    std::cout << " iBin = " << iBin << " eY = " << errYDownComb << " - " << errYUpComb << " eX = " << errXDownComb << " - " << errXUpComb << std::endl;
                    std::cout << "                  Y = " << Y + Y2 << " = " << Y << " + " << Y2 << std::endl;

                    temp_BandError -> SetPoint      (iBin, X, Y + Y2);
                    temp_BandError -> SetPointError (iBin, errXDownComb, errXUpComb, errYDownComb, errYUpComb);

                }
                std::swap (_BandError,     temp_BandError) ;
            }
            _doBandError = true;
            std::cout << " grAE = " << &grAE << std::endl;
            std::cout << " done " << std::endl;
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




        //---- merge trees with the same name ----

        void mergeSamples() {

            //---- for the Background

            std::vector<TH1F*> vectTHBkg;          
            std::vector<int> vectColourBkg;        
            std::vector<std::string> vectNameBkg;  
            //         std::vector<double> vectNormalizationBkg; 
            //         std::vector<double> vectSystBkg;       
            //         std::vector<double> vectScaleBkg;      

            std::vector<double> vectFlagToKeepBkg; //---- 1=keep, 0=remove because it has been merged


            for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
                vectFlagToKeepBkg.push_back(1);
            }
            int iHistoToKeepBkg = 0;
            for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
                if (vectFlagToKeepBkg.at(iBkg) == 1) {
                    if (_vectTHBkg.size() != 0)            vectTHBkg.push_back     (_vectTHBkg.at(iBkg));
                    if (_vectColourBkg.size() != 0)        vectColourBkg.push_back (_vectColourBkg.at(iBkg));
                    if (_vectNameBkg.size() != 0)          vectNameBkg.push_back   (_vectNameBkg.at(iBkg));
                    //           if (_vectSystBkg.size() != 0)          vectSystBkg.push_back(_vectSystBkg.at(iBkg));          
                    //           if (_vectScaleBkg.size() != 0)         vectScaleBkg.push_back(_vectScaleBkg.at(iBkg));
                    //           if (_vectNormalizationBkg.size() != 0) vectNormalizationBkg.push_back(_vectNormalizationBkg.at(iBkg));

                    for (unsigned int jBkg = iBkg+1; jBkg<_vectTHBkg.size(); jBkg++) {
                        //            std::cout << " iBkg = " << iBkg << "::" << _vectTHBkg.size() << " jBkg = " << jBkg << std::endl;
                        if (_vectNameBkg.at(jBkg) == _vectNameBkg.at(iBkg)) {
                            vectTHBkg.at(iHistoToKeepBkg) -> Add (_vectTHBkg.at(jBkg));
                            vectFlagToKeepBkg.at(jBkg) = 0; //---- to be removed
                        }
                    }
                    iHistoToKeepBkg++;
                }
            }

            std::swap (_vectTHBkg,     vectTHBkg) ;
            std::swap (_vectColourBkg, vectColourBkg) ;
            std::swap (_vectNameBkg,   vectNameBkg) ;







            //---- for the Signal
            //---- there is an ad hoc function!
            //---- see set_mergeSignal
            //----
            //---- or you can use this method too!
            //---- for example to merge ggH 7 TeV and ggH 8 TeV only and
            //----  not all the signal samples together
            //----


            std::vector<TH1F*> vectTHSig;          
            std::vector<int> vectColourSig;        
            std::vector<std::string> vectNameSig;  

            std::vector<double> vectFlagToKeepSig; //---- 1=keep, 0=remove because it has been merged


            for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
                vectFlagToKeepSig.push_back(1);
            }
            int iHistoToKeepSig = 0;
            for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
                if (vectFlagToKeepSig.at(iSig) == 1) {
                    if (_vectTHSig.size() != 0)            vectTHSig.push_back     (_vectTHSig.at(iSig));
                    if (_vectColourSig.size() != 0)        vectColourSig.push_back (_vectColourSig.at(iSig));
                    if (_vectNameSig.size() != 0)          vectNameSig.push_back   (_vectNameSig.at(iSig));

                    for (unsigned int jSig = iSig+1; jSig<_vectTHSig.size(); jSig++) {
                        if (_vectNameSig.at(jSig) == _vectNameSig.at(iSig)) {
                            vectTHSig.at(iHistoToKeepSig) -> Add (_vectTHSig.at(jSig));
                            vectFlagToKeepSig.at(jSig) = 0; //---- to be removed
                        }
                    }
                    iHistoToKeepSig++;
                }
            }

            std::swap (_vectTHSig,     vectTHSig) ;
            std::swap (_vectColourSig, vectColourSig) ;
            std::swap (_vectNameSig,   vectNameSig) ;

            //---- prepare style for signal histograms (in case of drawing  over background
            //         for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
            //          _vectTHSig.at(iSig) -> SetFillStyle(1001);
            //          _vectTHSig.at(iSig) -> SetLineColor(_vectColourSig.at(iSig));
            //          _vectTHSig.at(iSig) -> SetLineWidth(3);
            //         }


            //---- add signal histograms
            _vectTHstackSig.clear(); //---->>> very important! Otherwise it crashes!!!
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


        //---- change bin ranges and axes to deal with variable bin width ----
        void set_vectEdges (std::vector<double>& vEdges) { 
            for (unsigned int iEdg = 0; iEdg<vEdges.size(); iEdg++) {
                _vEdges.push_back(vEdges.at(iEdg));
            }
        }





        //---- draw propaganda plot for discovery ----

        void DrawPropagandaPlot(const int &rebin,const int& numRolling=-1, TString nameX = "mth", double minX=0,  double maxX=0,  TString nameY = "mll", double minY=0,  double maxY=0, int subrangeX=-1, int subrangeY=-1) {
            DrawPropagandaPlot(new TCanvas(),rebin,numRolling,nameX,minX,maxX,nameY,minY,maxY, subrangeX, subrangeY);
        }

        void DrawPropagandaPlot(TCanvas *c1, const int &rebin,const int& numRolling=-1, TString nameX = "mth", double minX=0,  double maxX=0,  TString nameY = "mll", double minY=0,  double maxY=0, int subrangeX=-1, int subrangeY=-1) {
            int rebin2 = rebin; //---> just not to have warning :)
            rebin2+=0; 



            TH1F *summed = GetSummedMCHist();

            //         TH1F *bkgoffsetsummed = new TH1F("bkgoffsetsummed","background offset",summed->GetNbinsX(), summed->GetBinLowEdge(1), summed->GetBinLowEdge(summed->GetNbinsX()+1));

            int nbinX = summed->GetNbinsX()/numRolling;
            int nbinY = numRolling;

            if (numRolling == -1) {
                nbinX = 1;
                nbinY = 1;
            }

            TH2F *h_bkgoffsetsummed = new TH2F("h_bkgoffsetsummed","background offset",(int) nbinX, minX, maxX,(int) nbinY, minY, maxY);
            TH2F *h_bkgoffsetsummed_up = new TH2F("h_bkgoffsetsummed_up","background offset",(int) nbinX, minX, maxX,(int) nbinY, minY, maxY);
            TH2F *h_bkgoffsetsummed_do = new TH2F("h_bkgoffsetsummed_do","background offset",(int) nbinX, minX, maxX,(int) nbinY, minY, maxY);
            TH2F *h_dataoffsetsigma = new TH2F("h_dataoffsetsigma","data #sigma offset",(int) nbinX, minX, maxX,(int) nbinY, minY, maxY);
            TH2F *h_dataoffset      = new TH2F("h_dataoffset"     ,"data       offset",(int) nbinX, minX, maxX,(int) nbinY, minY, maxY);
            TH2F *h_signaloffset    = new TH2F("h_signaloffset"   ,"signal      offset",(int) nbinX, minX, maxX,(int) nbinY, minY, maxY);
            TH2F *h_dummy           = new TH2F("h_dummy"          ,""                  ,(int) nbinX, minX, maxX,(int) nbinY, minY, maxY);



            TH2F *h_dataoffset_zoom(0x0);
            TH2F *h_signaloffset_zoom(0x0);
            if (subrangeX!=-1 && subrangeY!=-1) {
                h_dataoffset_zoom   = new TH2F("h_dataoffset_zoom"     ,"data       offset", (int) subrangeX, minX, minX+(maxX-minX)/nbinX*subrangeX,(int) subrangeY, minY, minY+(maxY-minY)/nbinY*subrangeY);
                h_signaloffset_zoom = new TH2F("h_signaloffset_zoom"   ,"signal      offset",(int) subrangeX, minX, minX+(maxX-minX)/nbinX*subrangeX,(int) subrangeY, minY, minY+(maxY-minY)/nbinY*subrangeY);

                h_dataoffset_zoom -> SetMarkerSize(1);
                h_dataoffset_zoom -> SetMarkerStyle(20);
                h_dataoffset_zoom -> SetMarkerColor(kBlack);
                h_dataoffset_zoom -> SetLineWidth(2);
                h_dataoffset_zoom -> SetLineColor(kBlack);

                h_signaloffset_zoom -> SetMarkerSize(1);
                h_signaloffset_zoom -> SetMarkerStyle(20);
                h_signaloffset_zoom -> SetMarkerColor(kBlack);
                h_signaloffset_zoom -> SetLineWidth(2);
                h_signaloffset_zoom -> SetLineColor(kBlack);

                h_dataoffset_zoom->GetXaxis()->SetTitle(nameX);
                h_dataoffset_zoom->GetYaxis()->SetTitle(nameY);
                h_dataoffset_zoom->GetZaxis()->SetTitle("excess of events");
                h_dataoffset_zoom->SetTitle ("number of events over background");
                h_dataoffset_zoom->SetTitle ("");

                h_signaloffset_zoom->GetXaxis()->SetTitle(nameX);
                h_signaloffset_zoom->GetYaxis()->SetTitle(nameY);
                h_signaloffset_zoom->GetZaxis()->SetTitle("number of signal events");
                h_signaloffset_zoom->SetTitle ("number of signal events");
                h_signaloffset_zoom->SetTitle ("");

            }

            TGraph2DErrors *g_bkgoffsetsummed = new TGraph2DErrors();
            TGraph2DErrors *g_bkgoffsetsummed_error = new TGraph2DErrors();
            TGraph2DErrors *g_dataoffset      = new TGraph2DErrors();
            /*         TGraph2DErrors *g_dataoffsetsigma = new TGraph2DErrors(); */

            g_bkgoffsetsummed -> SetFillColor(kGreen);
            g_bkgoffsetsummed -> SetLineWidth(1);
            g_bkgoffsetsummed -> SetLineColor(kGreen);
            g_bkgoffsetsummed -> SetFillStyle(3001);
            g_bkgoffsetsummed -> SetMarkerSize(0);
            g_bkgoffsetsummed -> SetMarkerStyle(21);
            g_bkgoffsetsummed -> SetMarkerColor(kGreen);

            g_bkgoffsetsummed_error -> SetFillColor(kGreen);
            g_bkgoffsetsummed_error -> SetLineWidth(1);
            g_bkgoffsetsummed_error -> SetLineColor(kGreen);
            g_bkgoffsetsummed_error -> SetFillStyle(3001);
            g_bkgoffsetsummed_error -> SetMarkerSize(0);
            g_bkgoffsetsummed_error -> SetMarkerStyle(21);
            g_bkgoffsetsummed_error -> SetMarkerColor(kGreen);


            h_bkgoffsetsummed -> SetFillColor(kGreen);
            h_bkgoffsetsummed -> SetFillStyle(3001);
            h_bkgoffsetsummed -> SetMarkerSize(2);
            h_bkgoffsetsummed -> SetMarkerStyle(21);
            h_bkgoffsetsummed -> SetMarkerColor(kGreen);


            h_bkgoffsetsummed_up->SetFillColor(kGreen);
            h_bkgoffsetsummed_up->SetFillStyle(3001);
            h_bkgoffsetsummed_do->SetFillColor(kGreen);
            h_bkgoffsetsummed_do->SetFillStyle(3001);

            h_dataoffsetsigma->SetMarkerSize(2);
            h_dataoffsetsigma->SetFillColor(kRed);
            h_dataoffsetsigma->SetFillStyle(3001);

            h_dataoffset -> SetMarkerSize(2);
            h_dataoffset -> SetMarkerStyle(20);
            h_dataoffset -> SetMarkerColor(kBlack);
            h_dataoffset -> SetLineWidth(2);
            h_dataoffset -> SetLineColor(kBlack);

            h_signaloffset -> SetMarkerSize(2);
            h_signaloffset -> SetMarkerStyle(20);
            h_signaloffset -> SetMarkerColor(kBlack);
            h_signaloffset -> SetLineWidth(2);
            h_signaloffset -> SetLineColor(kBlack);

            h_dummy  -> SetMarkerSize(2);

            g_dataoffset -> SetMarkerSize(2);
            g_dataoffset -> SetMarkerStyle(20);
            g_dataoffset -> SetMarkerColor(kBlue);
            g_dataoffset -> SetLineWidth(2);
            g_dataoffset -> SetLineColor(kBlue);
            g_dataoffset -> SetFillStyle(3001);
            g_dataoffset -> SetFillColor(kBlue);


            TGraphAsymmErrors *bkgoffsetsummed = new TGraphAsymmErrors();        
            TGraphAsymmErrors *dataoffset = new TGraphAsymmErrors();        
            TH1F *data   = GetDataHist();

            bkgoffsetsummed->SetFillColor(kGreen);
            bkgoffsetsummed->SetFillStyle(3001);

            dataoffset -> SetMarkerSize(2);
            dataoffset -> SetMarkerStyle(20);
            dataoffset -> SetMarkerColor(kBlack);
            dataoffset -> SetLineWidth(2);
            dataoffset -> SetLineColor(kBlack);

            for (int iBin = 0; iBin < summed->GetNbinsX(); iBin ++) {

                double YwithSig = (_BandError->GetY()) [iBin];
                double X = (_BandError->GetX()) [iBin];

                double Y = YwithSig - (_vectTHstackSig.at(_vectTHstackSig.size() - 1) -> GetBinContent(iBin+1)); //---- subtract the signal
                double alpha =  Y/YwithSig; //---- scale the error ... first approx! Since TGraphErrors is built onder the sig+bkg hypothesis


                double errXUp      = _BandError->GetErrorXhigh(iBin);
                double errXDown    = _BandError->GetErrorXlow(iBin);
                double errYUp      = alpha * _BandError->GetErrorYhigh(iBin);
                double errYDown    = alpha * _BandError->GetErrorYlow(iBin);

                Y = data->GetBinContent(iBin+1) - Y;

                std::cout << " X = " << X << " YwithSig = " << YwithSig << " Y = " << Y << std::endl;

                dataoffset -> SetPoint      (iBin, X, Y);
                //          double statisticalError = sqrt(data->GetBinContent(iBin+1));
                //          if (statisticalError == 0) statisticalError = 1;
                //          dataoffset -> SetPointError (iBin, errXDown, errXUp, statisticalError, statisticalError);
                //          
                //          bkgoffsetsummed -> SetPoint      (iBin, X, 0);
                //          bkgoffsetsummed -> SetPointError (iBin, errXDown, errXUp, errYDown, errYUp);



                dataoffset -> SetPoint      (iBin, X, Y);
                double statisticalError = sqrt(data->GetBinContent(iBin+1));
                if (statisticalError == 0) statisticalError = 1;
                dataoffset -> SetPointError (iBin, errXDown, errXUp, 0, 0);

                errYUp = sqrt(errYUp*errYUp       + statisticalError*statisticalError);
                errYDown = sqrt(errYDown*errYDown + statisticalError*statisticalError);

                bkgoffsetsummed -> SetPoint      (iBin, X, 0);
                bkgoffsetsummed -> SetPointError (iBin, errXDown, errXUp, errYDown, errYUp);

                if (numRolling != -1) {
                    int ibinX = iBin/numRolling;
                    int ibinY = iBin - ibinX*numRolling;
                    double errY = ( errYDown + errYUp ) / 2.;
                    h_bkgoffsetsummed -> SetBinContent (ibinX+1, ibinY+1, 0);
                    h_bkgoffsetsummed -> SetBinError   (ibinX+1, ibinY+1, errY);

                    g_bkgoffsetsummed -> SetPoint      (iBin, (ibinX+0.5)*(maxX-minX)/nbinX + minX, (ibinY+0.5)*(maxY-minY)/nbinY + minY, errY);
                    g_bkgoffsetsummed -> SetPointError (iBin, 0, 0, 0);

                    g_bkgoffsetsummed_error -> SetPoint      (iBin, (ibinX+0.5)*(maxX-minX)/nbinX + minX, (ibinY+0.5)*(maxY-minY)/nbinY + minY, 0);
                    g_bkgoffsetsummed_error -> SetPointError (iBin, (maxX-minX)/nbinX/2., (maxY-minY)/nbinY/2., errY);
                    //           std::cout << " errY = " << errY << std::endl;

                    h_bkgoffsetsummed_up -> SetBinContent (ibinX+1, ibinY+1, errYUp);
                    h_bkgoffsetsummed_up -> SetBinError   (ibinX+1, ibinY+1, 0);
                    h_bkgoffsetsummed_do -> SetBinContent (ibinX+1, ibinY+1, -errYDown);
                    h_bkgoffsetsummed_do -> SetBinError   (ibinX+1, ibinY+1, 0);

                    h_dataoffset -> SetBinContent (ibinX+1, ibinY+1, Y);
                    h_dataoffset -> SetBinError   (ibinX+1, ibinY+1, errY);

                    h_dummy -> SetBinContent (ibinX+1, ibinY+1, ibinY+ibinX*nbinY+1);

                    if (subrangeX!=-1 && subrangeY!=-1) {
                        if (ibinX<subrangeX && ibinY<subrangeY) {
                            h_dataoffset_zoom -> SetBinContent (ibinX+1, ibinY+1, Y);
                            h_dataoffset_zoom -> SetBinError   (ibinX+1, ibinY+1, errY);
                            h_signaloffset_zoom-> SetBinContent (ibinX+1, ibinY+1, (_vectTHstackSig.at(_vectTHstackSig.size() - 1) -> GetBinContent(iBin+1)));
                        }
                    }


                    h_signaloffset -> SetBinContent (ibinX+1, ibinY+1, (_vectTHstackSig.at(_vectTHstackSig.size() - 1) -> GetBinContent(iBin+1)));
                    //           h_signaloffset -> SetBinError   (ibinX+1, ibinY+1, (_vectTHstackSig.at(_vectTHstackSig.size() - 1) -> GetBinError(iBin+1)));
                    //           
                    //           std::cout << " (_vectTHstackSig.at(_vectTHstackSig.size() - 1) -> GetBinError(iBin+1)) = " << (_vectTHstackSig.at(_vectTHstackSig.size() - 1) -> GetBinError(iBin+1)) << std::endl;

                    //           h_dataoffset -> SetBinError   (ibinX+1, ibinY+1, 0);

                    //           g_dataoffset -> SetPoint      (iBin, (ibinX+0.5)*(maxX-minX)/nbinX + minX, (ibinY+0.5)*(maxY-minY)/nbinY + minY, Y);
                    g_dataoffset -> SetPointError (iBin, (maxX-minX)/nbinX/2., (maxY-minY)/nbinY/2., 0);


                    double numsigma = 0;
                    if (errY != 0) {
                        if (Y>0) numsigma = Y/errYUp;
                        if (Y<0) numsigma = Y/errYDown;
                    }
                    else numsigma = 0;
                    //           double errnumsigma;
                    //           if (errY != 0) errnumsigma = statisticalError/errY;
                    //           else errnumsigma = 0;


                    //           std::cout << " numsigma = " << numsigma << std::endl;
                    h_dataoffsetsigma -> SetBinContent (ibinX+1, ibinY+1, numsigma);
                    // h_dataoffsetsigma -> SetBinError   (ibinX+1, ibinY+1, errnumsigma);
                    g_dataoffset -> SetPoint      (iBin, (ibinX+0.5)*(maxX-minX)/nbinX + minX, (ibinY+0.5)*(maxY-minY)/nbinY + minY, numsigma);

                }


            }




            if (numRolling != -1) {
                h_bkgoffsetsummed_up->GetXaxis()->SetTitle(nameX);
                h_bkgoffsetsummed_up->GetYaxis()->SetTitle(nameY);
                h_bkgoffsetsummed_do->GetXaxis()->SetTitle(nameX);
                h_bkgoffsetsummed_do->GetYaxis()->SetTitle(nameY);


                h_dummy->GetXaxis()->SetTitle(nameX);
                h_dummy->GetYaxis()->SetTitle(nameY);

                g_dataoffset->GetXaxis()->SetTitle(nameX);
                g_dataoffset->GetYaxis()->SetTitle(nameY);
                g_dataoffset->GetZaxis()->SetTitle("number of #sigma");
                g_dataoffset->SetTitle ("number of #sigma");

                h_dataoffset->GetXaxis()->SetTitle(nameX);
                h_dataoffset->GetYaxis()->SetTitle(nameY);
                h_dataoffset->GetZaxis()->SetTitle("excess of events");
                h_dataoffset->SetTitle ("number of events over background");
                h_dataoffset->SetTitle ("");

                h_dataoffsetsigma->GetXaxis()->SetTitle(nameX);
                h_dataoffsetsigma->GetYaxis()->SetTitle(nameY);
                h_dataoffsetsigma->GetZaxis()->SetTitle("number of #sigma");
                h_dataoffsetsigma->SetTitle ("number of #sigma");
                h_dataoffsetsigma->SetTitle ("");         


                h_signaloffset->GetXaxis()->SetTitle(nameX);
                h_signaloffset->GetYaxis()->SetTitle(nameY);
                h_signaloffset->GetZaxis()->SetTitle("number of signal events");
                h_signaloffset->SetTitle ("number of signal events");
                h_signaloffset->SetTitle ("");



                //          h_bkgoffsetsummed_up->RebinX(2);
                //          h_bkgoffsetsummed_up->RebinY(2);
                // 
                //          h_bkgoffsetsummed_do->RebinX(2);
                //          h_bkgoffsetsummed_do->RebinY(2);
                // 
                //          h_dataoffsetsigma->RebinX(2);

                //          h_dataoffset->RebinX(2);
                //          h_dataoffset->RebinY(2);

                //          h_dataoffset->GetXaxis()->SetTitle(nameX);
                //          h_dataoffset->GetYaxis()->SetTitle(nameY);
                //          h_dataoffset->SetMarkerSize(1.0);
                //          h_dataoffset->GetZaxis()->SetTitle("excess events");
                //          h_dataoffset->Draw ("colZtextE");


                //          h_dataoffset      -> Draw ("EP");
                //          h_bkgoffsetsummed -> Draw ("EPsame");

                //          h_dataoffset      -> Draw ("EP");
                //          g_bkgoffsetsummed_error -> Draw ("Err p same");

                //          g_bkgoffsetsummed -> Draw ("surf1");
                //          g_dataoffset      -> Draw ("err p0");
                //          g_dataoffset      -> Draw ("p");
                //          g_dataoffset -> Draw ("surf2");
                //          g_dataoffset -> Draw ("lego");
                //          g_dataoffset -> Draw ("contsame");
                //          g_dataoffset -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                //          g_dataoffset -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                //          g_dataoffset -> GetZaxis() -> SetRangeUser (-4,4);


                //          h_dataoffsetsigma -> Draw ("surf3");
                //          h_dataoffsetsigma -> Draw ("lego1");
                //          h_dataoffsetsigma -> Draw ("COLZ");
                //          h_dataoffsetsigma -> Draw ("textsame");
                //          h_dataoffsetsigma -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                //          h_dataoffsetsigma -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                //          h_dataoffsetsigma -> GetZaxis() -> SetRangeUser (-4,4);


                //          g_bkgoffsetsummed -> Draw ("surf1same");
                //          h_dataoffset      -> Draw ("EPsame");

                //          h_bkgoffsetsummed_up -> Draw ("LEGO1");
                //          h_bkgoffsetsummed_do -> Draw ("LEGO1same");

                //          h_bkgoffsetsummed_up -> Draw ("surf2");
                //          h_bkgoffsetsummed_up -> Draw ("bar2");
                //          h_bkgoffsetsummed_up -> Draw ("surf2");
                //          h_bkgoffsetsummed_up -> Draw ("cont1 same");
                //          h_bkgoffsetsummed_do -> Draw ("lego1 0");
                //          h_dataoffset      -> Draw ("Esame");


                //          h_dataoffsetsigma->GetXaxis()->SetTitle(nameX);
                //          h_dataoffsetsigma->GetYaxis()->SetTitle(nameY);
                //          h_dataoffsetsigma->GetZaxis()->SetTitle("number of #sigma");
                //          h_dataoffsetsigma->GetZaxis() -> SetRangeUser (-5,5);
                //          h_dataoffsetsigma->Draw("COLZ");
                //          h_dataoffsetsigma->Draw("textsame");

                TExec *ex6 = new TExec("ex4","gStyle->SetPaintTextFormat(\"4.1f\");");

                //          gStyle->SetPaintTextFormat("4.1f");

                //          TExec *ex1 = new TExec("ex1","gStyle->SetPaintTextFormat(\"4.1f\");");
                //          ex1->Draw();




                if (subrangeX == -1 && subrangeY == -1) {
                    c1 -> Divide(2,2);

                    c1 -> cd (1);
                    TH1F* h_frame = gPad->DrawFrame(minX,minY,maxX,maxY);
                    ex6->Draw();
                    h_frame->GetXaxis()->SetTitle(nameX);
                    h_frame->GetYaxis()->SetTitle(nameY);



                    h_dataoffsetsigma -> Draw ("COLZ SAME");
                    h_dataoffsetsigma -> Draw ("textsame");
                    h_dataoffsetsigma -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                    h_dataoffsetsigma -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                    h_dataoffsetsigma -> GetZaxis() -> SetRangeUser (-4,4);
                    gPad -> SetRightMargin(0.2);


                    c1 -> cd (2);
                    TH1F* h_frame2 = gPad->DrawFrame(minX,minY,maxX,maxY);
                    h_frame2->GetXaxis()->SetTitle(nameX);
                    h_frame2->GetYaxis()->SetTitle(nameY);
                    h_dataoffset -> Draw ("COLZ SAME");
                    h_dataoffset -> Draw ("Etextsame");
                    h_dataoffset -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                    h_dataoffset -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                    //           h_dataoffset -> GetZaxis() -> SetRangeUser (-4,4);
                    gPad -> SetRightMargin(0.2);



                    c1 -> cd (3);
                    TH1F* h_frame3 = gPad->DrawFrame(minX,minY,maxX,maxY);
                    TExec *ex5 = new TExec("ex4","gStyle->SetPaintTextFormat(\".0f\");");
                    ex5->Draw();
                    h_frame3->GetXaxis()->SetTitle(nameX);
                    h_frame3->GetYaxis()->SetTitle(nameY);


                    //           h_dummy->SetPaintTextFormat(".0f");
                    h_dummy -> Draw ("TEXT SAME");
                    h_dummy->GetXaxis() -> SetNdivisions (nbinX);
                    h_dummy->GetYaxis() -> SetNdivisions (nbinY);
                    //           h_dummy -> Draw ("TEXT");
                    gPad -> SetRightMargin(0.2);
                    //           gPad -> SetGrid();
                    //           gStyle->SetPaintTextFormat("4.1f");          
                    ex6->Draw();


                    c1 -> cd (4);
                    TH1F* h_frame4 = gPad->DrawFrame(minX,minY,maxX,maxY);
                    h_frame4->GetXaxis()->SetTitle(nameX);
                    h_frame4->GetYaxis()->SetTitle(nameY);

                    h_signaloffset -> Draw ("COLZ SAME");
                    h_signaloffset -> Draw ("textsame");
                    //          h_signaloffset -> Draw ("Etextsame");
                    h_signaloffset -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                    h_signaloffset -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                    gPad -> SetRightMargin(0.2);







                    TCanvas* ccSigma = new TCanvas ("ccSigma","ccSigma",400,400);
                    ccSigma->cd();
                    //           gPad -> SetRightMargin(0.15);
                    //           gPad -> SetLeftMargin(0.15);
                    //           gPad -> SetTopMargin(0.15);
                    //           gPad -> SetBottomMargin(0.15);

                    TH1F* h_Sigma = gPad->DrawFrame(minX,minY,maxX,maxY);
                    h_Sigma->GetXaxis()->SetTitle(nameX);
                    h_Sigma->GetYaxis()->SetTitle(nameY);

                    h_dataoffsetsigma -> Draw ("COLZ SAME");
                    h_dataoffsetsigma -> Draw ("textsame");
                    h_dataoffsetsigma -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                    h_dataoffsetsigma -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                    h_dataoffsetsigma -> GetZaxis() -> SetRangeUser (-4,4);
                    gPad -> SetRightMargin(0.2);
                    ccSigma->SaveAs("ccSigma.png");
                    ccSigma->SaveAs("ccSigma.pdf");


                    TCanvas* ccOffset = new TCanvas ("ccOffset","ccOffset",400,400);
                    ccOffset->cd();
                    //           gPad -> SetRightMargin(0.15);
                    //           gPad -> SetLeftMargin(0.15);
                    //           gPad -> SetTopMargin(0.15);
                    //           gPad -> SetBottomMargin(0.15);

                    TH1F* h_Offset = gPad->DrawFrame(minX,minY,maxX,maxY);
                    h_Offset->GetXaxis()->SetTitle(nameX);
                    h_Offset->GetYaxis()->SetTitle(nameY);

                    h_dataoffset -> Draw ("COLZ SAME");
                    h_dataoffset -> Draw ("Etextsame");
                    h_dataoffset -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                    h_dataoffset -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                    //           h_dataoffset -> GetZaxis() -> SetRangeUser (-4,4);
                    gPad -> SetRightMargin(0.2);
                    ccOffset->SaveAs("ccOffset.png");
                    ccOffset->SaveAs("ccOffset.pdf");







                    TCanvas* ccSignal = new TCanvas ("ccSignal","ccSignal",400,400);
                    ccSignal->cd();
                    //           gPad -> SetRightMargin(0.15);
                    //           gPad -> SetLeftMargin(0.15);
                    //           gPad -> SetTopMargin(0.15);
                    //           gPad -> SetBottomMargin(0.15);

                    TH1F* h_frameSig = gPad->DrawFrame(minX,minY,maxX,maxY);
                    h_frameSig->GetXaxis()->SetTitle(nameX);
                    h_frameSig->GetYaxis()->SetTitle(nameY);

                    h_signaloffset -> Draw ("COLZ SAME");
                    h_signaloffset -> Draw ("textsame");
                    //          h_signaloffset -> Draw ("Etextsame");
                    h_signaloffset -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                    h_signaloffset -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                    gPad -> SetRightMargin(0.2);
                    ccSignal->SaveAs("ccSignal.png");
                    ccSignal->SaveAs("ccSignal.pdf");




                    TCanvas* ccMap = new TCanvas ("ccMap","ccMap",400,400);
                    ccMap->cd();
                    gPad -> SetRightMargin(0.15);
                    gPad -> SetLeftMargin(0.15);
                    gPad -> SetTopMargin(0.15);
                    gPad -> SetBottomMargin(0.15);
                    TH1F* h_frame5 = gPad->DrawFrame(minX,minY,maxX,maxY);
                    TExec *ex4 = new TExec("ex4","gStyle->SetPaintTextFormat(\".0f\");");
                    ex4->Draw();
                    h_frame5->GetXaxis()->SetTitle(nameX);
                    h_frame5->GetYaxis()->SetTitle(nameY);
                    h_dummy -> Draw ("TEXT SAME");    
                    //           h_dummy -> Draw ("COLZ SAME");    
                    //           gStyle->SetPaintTextFormat(".0f");
                    //           h_dummy -> Draw ("TEXT");
                    //           gPad -> SetGrid();
                    ccMap -> Update();
                    ccMap->SaveAs("ccMap.png");
                    ccMap->SaveAs("ccMap.pdf");




                }
                else {
                    c1 -> Divide(2,2);

                    c1 -> cd (1);

                    h_dataoffsetsigma -> Draw ("COLZ");
                    h_dataoffsetsigma -> Draw ("textsame");
                    h_dataoffsetsigma -> GetXaxis() -> SetRangeUser (minX+(0.5)*(maxX-minX)/nbinX,maxX-(0.5)*(maxX-minX)/nbinX);
                    h_dataoffsetsigma -> GetYaxis() -> SetRangeUser (minY+(0.5)*(maxY-minY)/nbinY,maxY-(0.5)*(maxY-minY)/nbinY);
                    h_dataoffsetsigma -> GetZaxis() -> SetRangeUser (-4,4);
                    gPad -> SetRightMargin(0.2);


                    c1 -> cd (2);          
                    h_dataoffset_zoom -> Draw ("COLZ");
                    h_dataoffset_zoom -> Draw ("Etextsame");
                    gPad -> SetRightMargin(0.2);


                    c1 -> cd (3);
                    h_dataoffset -> Draw ("COLZ");
                    h_dataoffset -> Draw ("Etextsame");
                    gPad -> SetRightMargin(0.2);



                    c1 -> cd (4);
                    h_signaloffset_zoom -> Draw ("COLZ");
                    h_signaloffset_zoom -> Draw ("textsame");
                    gPad -> SetRightMargin(0.2);
                }
            }

            else {
                dataoffset->Draw("AP");
                dataoffset->GetXaxis()->SetTitle(_xLabel);
                dataoffset->GetYaxis()->SetTitle("data-background");
                bkgoffsetsummed->Draw("E2");
            }

        }


        //---- draw only background -> normalized to 1! ----

        void DrawNormalized(const int &rebin=1) {
            DrawNormalized(new TCanvas(),rebin);
        }

        void DrawNormalized(TCanvas *c1, const int &rebin=1) {
            int rebin2 = rebin; //---> just not to have warning :)
            rebin2+=0; 

            gStyle->SetOptStat(0);
            c1->cd();
            c1->Clear();

            TPad *pad1;
            _globalYoffset = 0.85;
            pad1 = new TPad("pad1","pad1",0,0,1,1);
            pad1->Draw();
            pad1->cd();


            if (c1->GetLogy()) gPad->SetLogy();

            _max = 1.1;
            _min = 0;

            _maxLog = 10.5;
            _minLog = 0.001;

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

            THStack *hstack = GetStack(c1->GetLogy());

            for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
                if (iBkg == 0) {
                    _vectTHBkg.at(iBkg)->SetLabelSize(0.00,"X");
                    _vectTHBkg.at(iBkg)->SetLabelSize(0.06,"Y");
                    _vectTHBkg.at(iBkg)->SetTitleSize(0.06,"XY");  
                    _vectTHBkg.at(iBkg)->DrawNormalized("L");
                    AxisFonts(_vectTHBkg.at(iBkg)->GetXaxis(), "x", hstack->GetXaxis()->GetTitle());
                    AxisFonts(_vectTHBkg.at(iBkg)->GetYaxis(), "y", "a.u.");
                    std::cout << " miny,maxy = " << miny << " , "  << maxy << std::endl;
                    //           _vectTHBkg.at(iBkg)->GetYaxis()->SetRangeUser(miny, maxy);
                    _vectTHBkg.at(iBkg)->SetTitle("");
                    gPad->SetGrid();
                    //           _vectTHBkg.at(iBkg)->SetMaximum(5);
                    TH1F* tempOfHisto = (TH1F*) _vectTHBkg.at(iBkg)->Clone();
                    double tempint = tempOfHisto->Integral();
                    tempOfHisto->Scale(1./tempint);
                    tempOfHisto->GetYaxis()->SetRangeUser(miny, maxy);
                    tempOfHisto->Draw("L");
                }
                else {
                    _vectTHBkg.at(iBkg) -> DrawNormalized("Lsame");
                }
            }

            for (unsigned int iSig = 0; iSig<_vectTHstackSig.size(); iSig++) {
                if (_mergeSignal == 0) {
                    _vectTHSig.at(iSig) -> DrawNormalized("L,same");
                } 
                else {
                    if (_mergeSignal == 1 && iSig == (_vectTHstackSig.size()-1)) {
                        _vectTHstackSig.at(iSig) -> SetLineColor (kRed);
                        _vectTHstackSig.at(iSig) -> DrawNormalized("L,same");
                    }
                }
            }


            DrawLabels(false); // do not plot data!
            pad1->GetFrame()->DrawClone();
        }




        //---- draw ----

        void Draw(const int &rebin=1,const bool &div=false,  const bool &shadow=true) {
            Draw(new TCanvas(),rebin,div, shadow);
        }

        void Draw(TCanvas *c1, const int &rebin=1, const bool &div=false, const bool &shadow=true, TCanvas *cAdditional=0) {
            //      std::cout << " rebin = " << rebin << std::endl; 
            int rebin2 = rebin; //---> just not to have warning :)
            rebin2+=0; 



            ///---- transform histograms/TGraphErrors to deal with correct edges (begin) ----
            if (_vEdges.size() != 0) {
                double Xedge[1000];
                for (uint iEdg = 0; iEdg < _vEdges.size(); iEdg++) {
                    Xedge[iEdg] = _vEdges.at(iEdg);
                }
                std::vector<TH1F*> tempo_vectTHBkg;
                for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
                    TString name = Form("edge_%s",_vectTHBkg.at(iBkg)->GetName());
                    TH1F* tempoHisto = new TH1F(name, _vectTHBkg.at(iBkg)->GetTitle(), _vectTHBkg.at(iBkg)->GetNbinsX(), Xedge);
                    for (int iBin = 0; iBin < _vectTHBkg.at(iBkg)->GetNbinsX(); iBin ++) {
                        tempoHisto->SetBinContent (iBin+1, _vectTHBkg.at(iBkg)->GetBinContent(iBin+1));
                        tempoHisto->SetBinError   (iBin+1, _vectTHBkg.at(iBkg)->GetBinError(iBin+1)  );
                    }
                    std::swap(_vectTHBkg.at(iBkg), tempoHisto);
                }

                std::vector<TH1F*> tempo_vectTHSig;
                for (unsigned int iSig = 0; iSig<_vectTHSig.size(); iSig++) {
                    TString name = Form("edge_%s",_vectTHSig.at(iSig)->GetName());
                    TH1F* tempoHisto = new TH1F(name, _vectTHSig.at(iSig)->GetTitle(), _vectTHSig.at(iSig)->GetNbinsX(), Xedge);
                    for (int iBin = 0; iBin < _vectTHSig.at(iSig)->GetNbinsX(); iBin ++) {
                        tempoHisto->SetBinContent (iBin+1, _vectTHSig.at(iSig)->GetBinContent(iBin+1));
                        tempoHisto->SetBinError   (iBin+1, _vectTHSig.at(iSig)->GetBinError(iBin+1)  );
                    }
                    std::swap(_vectTHSig.at(iSig), tempoHisto);
                }

                std::vector<TH1F*> tempo_vectTHstackSig;
                for (unsigned int istackSig = 0; istackSig<_vectTHstackSig.size(); istackSig++) {
                    std::cout << " istackSig = " << istackSig << " :: " << _vectTHstackSig.size() << std::endl;
                    TString name = Form("edge_%s",_vectTHstackSig.at(istackSig)->GetName());
                    TH1F* tempoHisto = new TH1F(name, _vectTHstackSig.at(istackSig)->GetTitle(), _vectTHstackSig.at(istackSig)->GetNbinsX(), Xedge);
                    for (int iBin = 0; iBin < _vectTHstackSig.at(istackSig)->GetNbinsX(); iBin ++) {
                        tempoHisto->SetBinContent (iBin+1, _vectTHstackSig.at(istackSig)->GetBinContent(iBin+1));
                        tempoHisto->SetBinError   (iBin+1, _vectTHstackSig.at(istackSig)->GetBinError(iBin+1)  );
                    }
                    std::swap(_vectTHstackSig.at(istackSig), tempoHisto);
                }

                if (_data) {
                    TString name = Form("edge_%s",_data->GetName());
                    TH1F* tempoHisto = new TH1F(name, _data->GetTitle(), _data->GetNbinsX(), Xedge);
                    for (int iBin = 0; iBin < _data->GetNbinsX(); iBin ++) {
                        tempoHisto->SetBinContent (iBin+1, _data->GetBinContent(iBin+1));
                        tempoHisto->SetBinError   (iBin+1, _data->GetBinError(iBin+1)  );
                    }
                    std::swap(_data, tempoHisto);
                }

                if (_doBandError) {
                    TGraphAsymmErrors* tempoGr = new TGraphAsymmErrors();
                    for (int iBin = 0; iBin < _BandError->GetN(); iBin ++) {
                        double xx;
                        double yy;
                        _BandError->GetPoint(iBin, xx, yy);
                        double err_y_up = _BandError->GetErrorYhigh(iBin);
                        double err_y_lo = _BandError->GetErrorYlow(iBin);
                        xx = (_vEdges.at(iBin) + _vEdges.at(iBin+1) ) / 2.;
                        double err_x = (_vEdges.at(iBin+1) - _vEdges.at(iBin) ) / 2.;
                        tempoGr->SetPoint      (iBin, xx, yy);
                        tempoGr->SetPointError (iBin, err_x, err_x, err_y_lo, err_y_up);
                        std::cout << " iBin = " << iBin << " eY = " << err_y_lo << " - " << err_y_up << " eX = " << err_x << " - " << err_x << std::endl;
                        std::cout << "                  Y = " << yy << std::endl;

                    }
                    std::swap(_BandError, tempoGr);
                }

            }
            ///---- transform histograms/TGraphErrors to deal with correct edges (end) ----



            gStyle->SetOptStat(0);
            c1->cd();
            c1->Clear();

            TPad *pad1;
            if(div) {
                pad1 = new TPad("pad1","pad1",0,1-0.714609572,1,1);
                pad1->SetTopMargin(0.0983606557);
                pad1->SetBottomMargin(0.025);
            } else {
                _globalYoffset = 0.85;
                pad1 = new TPad("pad1","pad1",0,0,1,1);
            }
            pad1->Draw();
            pad1->cd();

            //      std::cout << " GetStack" << std::endl;
            THStack *hstack = GetStack(c1->GetLogy());
            //      std::cout << " GetData" << std::endl;
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

            if (_doBandError) {
                double allTG = 0;
                for (int iBin = 0; iBin < summed->GetNbinsX(); iBin ++) {
                    std::cout << " iBin = " << iBin << " :: " << summed->GetNbinsX();
                    std::cout << " => " << (_BandError->GetY()) [iBin] << " / " << summed->GetBinContent(iBin+1) << " = ";
                    std::cout << " ( X = " << (_BandError->GetX()) [iBin] << " ) ";
                    if (summed->GetBinContent(iBin+1) != 0) std::cout << (_BandError->GetY()) [iBin] / summed->GetBinContent(iBin+1) << std::endl;
                    else std::cout << std::endl;

                    if ((_BandError->GetY()) [iBin]) {
                        allTG += (_BandError->GetY()) [iBin];
                        double alpha =  summed->GetBinContent(iBin+1) / (_BandError->GetY()) [iBin];

                        double Y = (_BandError->GetY()) [iBin];
                        double X = (_BandError->GetX()) [iBin];
                        double errXUp      = _BandError->GetErrorXhigh(iBin);
                        double errXDown    = _BandError->GetErrorXlow(iBin);
                        double errYUp      = _BandError->GetErrorYhigh(iBin);
                        double errYDown    = _BandError->GetErrorYlow(iBin);

                        _BandError->SetPoint(iBin, X, alpha*Y);
                        _BandError->SetPointError(iBin, errXDown, errXUp, errYDown * alpha, errYUp * alpha);

                    }
                }
                //              summed->Draw("same");
                if (shadow) {
                    _BandError -> SetFillStyle (3345);
                    _BandError -> Draw("E2same");
                }
                std::cout << " allTG = " << allTG << std::endl;
            }
            else {
                if (shadow) {
                    summed->Draw("sameE2");
                }
                else {
                    summed->Draw("same");
                }
            }

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
                TGraphAsymmErrors *rref = new TGraphAsymmErrors();
                rref -> SetName ("rref");
                for (int i = 0, n = summed->GetNbinsX(); i < n; ++i) {
                    //                  std::cout << "  n+1 = " << n+1 << std::endl;
                    rref->SetPoint      (i,summed->GetBinCenter(i+1), summed->GetBinContent(i+1));
                    rref->SetPointError (i,summed->GetBinWidth(i+1) , summed->GetBinWidth(i+1)  , 0, 0);
                }
                rref->SetTitle("");
                rref->SetLineWidth(0);
                rref->SetFillColor(kGray+1);
                rref->SetFillStyle(1001);
                double absmax = 0;
                for (int i = 0, n = summed->GetNbinsX(); i < n; ++i) {
                    double scale = (rref->GetY())[i];
                    if (scale == 0) {
                        rdat->SetBinContent(i+1, 0);
                        rref->SetPoint     (i,summed->GetBinCenter(i+1), 1);
                        //                         rref->SetPoint     (i,summed->GetBinCenter(i+1) - summed->GetBinWidth(i+1)/2., 0);
                        rdat->SetBinError(i, 0);
                        rref->SetPointError (i,summed->GetBinWidth(i+1)/2.  , summed->GetBinWidth(i+1)/2.  , 0, 0);
                        std::cout << " I'm doing bin = " << i << " with scale = 0    and binXerror = " << summed->GetBinWidth(i+1)/2. << " and binCenter = " << summed->GetBinCenter(i+1) << std::endl;
                    }
                    else {
                        std::cout << " I'm doing bin = " << i << " and binXerror = " << summed->GetBinWidth(i+1)/2. << " and binCenter = " << summed->GetBinCenter(i+1) << std::endl;
                        rdat->SetBinContent(i+1, rdat->GetBinContent(i+1)/scale);
                        //                         rref->SetPoint      (i,summed->GetBinCenter(i+1) - summed->GetBinWidth(i+1)/2., summed->GetBinContent(i+1)/scale);
                        //                         rref->SetPoint      (i,summed->GetBinCenter(i+1), summed->GetBinContent(i+1)/scale);
                        rdat->SetBinError(i+1, rdat->GetBinError(i+1)/scale);

                        double xx = summed->GetBinCenter(i+1);
                        double yy = summed->GetBinContent(i+1)/scale;

                        double errXlo = summed->GetBinWidth(i+1) / 2.;
                        double errXup = summed->GetBinWidth(i+1) / 2.;

                        double errYlo = 0;
                        double errYup = 0;

                        if (_vEdges.size() != 0) {
                            int iEdg = i;
                            errXlo = (_vEdges.at(iEdg+1) - _vEdges.at(iEdg) ) / 2.;
                            errXup = (_vEdges.at(iEdg+1) - _vEdges.at(iEdg) ) / 2.;
                            xx =     (_vEdges.at(iEdg+1) + _vEdges.at(iEdg) ) / 2.;
                        }
                        rref->SetPoint      (i,xx, yy);


                        if (!_doBandError) {
                            errYup = summed->GetBinError(i+1);
                            errYlo = summed->GetBinError(i+1);
                        }
                        else {
                            std::cout << " >>>>>>>>>>>>>>>>>>>>>>>>>> " << summed->GetBinWidth(i+1) << std::endl;

                            errYlo = _BandError->GetErrorYlow(i);
                            errYup = _BandError->GetErrorYhigh(i);

                            errYlo = errYlo/scale;
                            errYup = errYup/scale;

                            //                          if (i!=0 && i!=n+1) {
                            //                           errYup = _BandError->GetErrorYhigh(i-1);  //---- no under/overflow bin!
                            //                           errYlo = _BandError->GetErrorYlow(i-1);  //---- no under/overflow bin!
                            //                          }
                            //                          
                            //                          rref->SetPointEYhigh (i, errYup/scale);
                            //                          rref->SetPointEYlow  (i, errYlo/scale);
                            //                          rref->SetPointEXhigh (i, errXup);
                            //                          rref->SetPointEXlow  (i, errXlo);
                            //                          
                            //                          std::cout << " ~~~~~~~~~~~~~~~~~~~ " << std::endl;
                            //                          std::cout << " errYup/scale = " << errYup/scale ;
                            //                          std::cout << " errYlo/scale = " << errYlo/scale ;
                            //                          double tempx, tempy;
                            //                          rref->GetPoint(i, tempx, tempy);
                            //                          std::cout << " X      = " << tempx;
                            //                          std::cout << " errXup = " << errXup ;
                            //                          std::cout << " errXlo = " << errXlo ;
                            //                          std::cout << std::endl;
                            //                          std::cout << " summed->GetBinWidth(" << i+1 << ") = " << summed->GetBinWidth(i+1) << std::endl;

                        }
                        rref->SetPointError (i,errXlo, errXup, errYlo, errYup); 
                        double mymax = TMath::Max(1.2*fabs(rdat->GetBinContent(i+1)-1)+1.4*rdat->GetBinError(i+1), 2.0*rref->GetErrorYhigh(i));
                        absmax = TMath::Max(mymax, absmax);
                    }
                    if (rdat->GetBinContent(i+1) == 0) {
                        rdat->SetBinContent(i+1, -1);
                    }
                }

                c1->cd();
                TPad *pad2 = new TPad("pad2","pad2",0,0,1,1-0.714609572);
                pad2->SetTopMargin(0.0261437908);
                pad2->SetBottomMargin(0.392156863);
                pad2->Draw();
                pad2->cd();

                std::cout << "  rref->GetXaxis()->GetXmax() = " <<  rref->GetXaxis()->GetXmax() << std::endl;
                std::cout << "  rref->GetXaxis()->GetXmin() = " <<  rref->GetXaxis()->GetXmin() << std::endl;


                //      rref->GetYaxis()->SetRangeUser(TMath::Max(0.,1.-absmax), absmax+1.);
                //      rref->GetYaxis()->SetRangeUser(TMath::Max(0.,1.-absmax), TMath::Min(10.,absmax+1.));
                rref->GetYaxis()->SetRangeUser(0., 3.);
                //                 rref->GetYaxis()->SetRangeUser(0., 2.);
                //                 rref->GetYaxis()->SetRangeUser(0., 4.);
                //                 rref->GetYaxis()->SetRangeUser(0., 5.);

                //                 AxisFonts(rref->GetYaxis(), "y", "ratio");
                AxisFonts(rref->GetXaxis(), "x", hstack->GetXaxis()->GetTitle());
                rref->GetXaxis()->SetRangeUser(summed->GetXaxis()->GetBinLowEdge(1), summed->GetXaxis()->GetBinLowEdge(_nbins+1));
                std::cout << "==========================================================" << std::endl;
                std::cout << " summed->GetXaxis()->GetBinLowEdge(1) = " << summed->GetXaxis()->GetBinLowEdge(1)  << "  , summed->GetXaxis()->GetBinLowEdge(_nbins+1)) = " << summed->GetXaxis()->GetBinLowEdge(_nbins+1) << std::endl;
                std::cout << "==========================================================" << std::endl;
                rref->GetYaxis()->SetTitle("data / sim");
                rref->GetYaxis()->SetLabelSize(0.09);
                rref->GetYaxis()->SetTitleSize(0.09);
                rref->GetYaxis()->SetTitleOffset(1.02);
                rref->GetXaxis()->SetLabelSize(0.09);
                rref->GetXaxis()->SetTitleSize(0.09);
                rref->GetXaxis()->SetTitleOffset(1.5);
                rref->Draw("AE2"); 
                //                 rref->Draw("APE2"); 
                rref->GetXaxis()->SetRangeUser(summed->GetXaxis()->GetBinLowEdge(1), summed->GetXaxis()->GetBinLowEdge(_nbins+1));

                //                 TLine *line = new TLine(rref->GetXaxis()->GetXmin(), 1.0, rref->GetXaxis()->GetXmax(), 1.0);
                TLine *line = new TLine(summed->GetXaxis()->GetBinLowEdge(1), 1.0, summed->GetXaxis()->GetBinLowEdge(_nbins+1), 1.0);
                line->SetLineColor(kBlack);
                line->SetLineWidth(1);
                line->SetLineStyle(1);

                std::cout << " rref->GetN() = " << rref->GetN() << std::endl;
                if (_doLabelNumber) {   
                    TText t;
                    t.SetTextAngle(0);
                    t.SetTextSize(0.08);
                    t.SetTextAlign(33);
                    for (int iBin=0;iBin<summed->GetNbinsX();iBin++) {
                        TString labels = Form ("%d",iBin+1);
                        double X = (rref->GetX()) [iBin];
                        std::cout << " X = " << X << std::endl;
                        t.DrawText(X+summed->GetBinWidth(iBin+1)/3,-0.1,labels.Data());
                    }
                    rref->GetXaxis()->SetLabelOffset(10);
                }

                rdat->SetMarkerStyle(20);
                rdat->Draw("E0 SAME p");
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
            //      int totnumbers;
            std::cout << " ~~~~~~ " << std::endl;      
            //      totnumbers = last->Integral();
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


            //---- plot "peak like" background subtracted
            if (cAdditional) {
                cAdditional->cd();
                /*              TH1F *excessDat = (TH1F*) data->Clone("excessDat");    */

                if(gROOT->FindObject("rrefData")) {
                    gROOT->FindObject("rrefData")->Delete();
                }
                TGraphAsymmErrors *rrefData = new TGraphAsymmErrors();
                rrefData -> SetName ("rrefData");

                if(gROOT->FindObject("rrefDataStat")) {
                    gROOT->FindObject("rrefDataStat")->Delete();
                }
                TGraphAsymmErrors *rrefDataStat = new TGraphAsymmErrors();
                rrefDataStat -> SetName ("rrefDataStat");

                if(gROOT->FindObject("rrefBkgSub")) {
                    gROOT->FindObject("rrefBkgSub")->Delete();
                }
                TGraphAsymmErrors *rrefBkgSub = new TGraphAsymmErrors();
                rrefBkgSub -> SetName ("rrefBkgSub");

                std::vector<TH1F*> temp_vectTHstackSig;
                for (uint iSig = 0; iSig<_vectTHstackSig.size(); iSig++) {
                    temp_vectTHstackSig.push_back( (TH1F*) (_vectTHstackSig.at(iSig)->Clone()));
                }  


                double minY = 0;
                double maxY = 0;

                for (int i = 0, n = summed->GetNbinsX(); i < n; ++i) {
                    //                  std::cout << "  n+1 = " << n+1 << std::endl;

                    double SigPlusBkg    = summed->GetBinContent(i+1);
                    double errSigPlusBkg = summed->GetBinError(i+1);

                    double OnlySig    = temp_vectTHstackSig.at(temp_vectTHstackSig.size()-1) -> GetBinContent(i+1);
                    double OnlyBkg    = SigPlusBkg - OnlySig;                      

                    double DataMinusBkg = 0;

                    double errYupDataMinusBkg_Syst = errSigPlusBkg;
                    double errYloDataMinusBkg_Syst = errSigPlusBkg;

                    double errYupDataMinusBkg = errSigPlusBkg;
                    double errYloDataMinusBkg = errSigPlusBkg;

                    double errYupDataMinusBkg_Stat = 0;
                    double errYloDataMinusBkg_Stat = 0;

                    if (_doBandError) {
                        errYloDataMinusBkg = _BandError->GetErrorYlow(i);
                        errYupDataMinusBkg = _BandError->GetErrorYhigh(i);

                        errYloDataMinusBkg_Syst = _BandError->GetErrorYlow(i);
                        errYupDataMinusBkg_Syst = _BandError->GetErrorYhigh(i);

                        //                std::cout << " errYloDataMinusBkg = " << errYloDataMinusBkg << std::endl;
                        //                std::cout << " errYupDataMinusBkg = " << errYupDataMinusBkg << std::endl;
                        //                std::cout << " ==== " << std::endl;
                    }
                    if (data) {
                        DataMinusBkg = data->GetBinContent(i+1) - OnlyBkg;
                        errYloDataMinusBkg = sqrt(errYloDataMinusBkg_Syst*errYloDataMinusBkg_Syst + data->GetBinContent(i+1)); //---- poissonian
                        errYupDataMinusBkg = sqrt(errYupDataMinusBkg_Syst*errYupDataMinusBkg_Syst + data->GetBinContent(i+1)); //---- poissonian
                        errYloDataMinusBkg_Stat = sqrt(data->GetBinContent(i+1));
                        errYupDataMinusBkg_Stat = sqrt(data->GetBinContent(i+1));

                        //                std::cout << " errYloDataMinusBkg_Stat = " << errYloDataMinusBkg_Stat << std::endl;
                        //                std::cout << " errYupDataMinusBkg_Stat = " << errYupDataMinusBkg_Stat << std::endl;
                        //                std::cout << "   >>  errYloDataMinusBkg = " << errYloDataMinusBkg << std::endl;
                        //                std::cout << "   >>  errYupDataMinusBkg = " << errYupDataMinusBkg << std::endl;
                        //                std::cout << " ==== " << std::endl;

                    }

                    rrefData->SetPoint      (i,summed->GetBinCenter(i+1), DataMinusBkg);
                    rrefData->SetPointError (i,summed->GetBinWidth(i+1)/2. , summed->GetBinWidth(i+1)/2.  , errYloDataMinusBkg, errYupDataMinusBkg);

                    rrefDataStat->SetPoint      (i,summed->GetBinCenter(i+1), DataMinusBkg);
                    rrefDataStat->SetPointError (i,summed->GetBinWidth(i+1)/2. , summed->GetBinWidth(i+1)/2.  , errYloDataMinusBkg_Stat, errYupDataMinusBkg_Stat);

                    rrefBkgSub->SetPoint      (i,summed->GetBinCenter(i+1), 0);
                    rrefBkgSub->SetPointError (i,summed->GetBinWidth(i+1)/2. , summed->GetBinWidth(i+1)/2.  , errYloDataMinusBkg_Syst, errYupDataMinusBkg_Syst);




                    if ((DataMinusBkg - errYloDataMinusBkg) < minY) minY = (DataMinusBkg - errYloDataMinusBkg);
                    if ((DataMinusBkg + errYupDataMinusBkg) > maxY) maxY = (DataMinusBkg + errYupDataMinusBkg);
                }


                for (int iSig = (temp_vectTHstackSig.size()-1); iSig>=0; iSig--) {
                    //               std::cout << " iSig = " << iSig << "  temp_vectTHstackSig.size() = " << temp_vectTHstackSig.size() << std::endl;
                    if (_mergeSignal == 0 ||  iSig == (temp_vectTHstackSig.size()-1)) {
                        if (_mergeSignal == 1) {
                            temp_vectTHstackSig.at(iSig) -> SetLineColor (kRed);
                        }
                        temp_vectTHstackSig.at(iSig) -> SetFillStyle (3004);
                        temp_vectTHstackSig.at(iSig) -> SetFillColor (temp_vectTHstackSig.at(iSig) -> GetLineColor());
                        if (iSig == (temp_vectTHstackSig.size()-1)) {
                            temp_vectTHstackSig.at(iSig) -> SetTitle ("");
                            temp_vectTHstackSig.at(iSig) -> Draw();
                            AxisFonts(temp_vectTHstackSig.at(iSig)->GetXaxis(), "x", hstack->GetXaxis()->GetTitle());
                            AxisFonts(temp_vectTHstackSig.at(iSig)->GetYaxis(), "y", "data - background");
                            if (data) {
                                temp_vectTHstackSig.at(iSig) ->GetYaxis () -> SetRangeUser(minY - 10 ,maxY*1.5 + 20);
                            }
                            else {
                                temp_vectTHstackSig.at(iSig) ->GetYaxis () -> SetRangeUser(0 ,temp_vectTHstackSig.at(temp_vectTHstackSig.size()-1)->GetMaximum() * 1.5 + 5);
                            }
                        }                
                        else {
                            temp_vectTHstackSig.at(iSig) -> Draw("same");
                        }
                        //                if (iSig == 0) temp_vectTHstackSig.at(iSig) -> Draw("hist");
                        //                else           temp_vectTHstackSig.at(iSig) -> Draw("hist,same");
                    }
                }


                rrefData->SetTitle("");
                rrefData -> SetLineWidth (2);
                rrefData -> SetMarkerSize (1);
                rrefData -> SetMarkerStyle(20);
                rrefData -> SetLineColor (kBlack);
                rrefData -> SetMarkerColor (kBlack);

                rrefDataStat->SetTitle("");
                rrefDataStat -> SetLineWidth (4);
                //              rrefDataStat -> SetLineStyle (2);
                rrefDataStat -> SetMarkerSize (1);
                rrefDataStat -> SetMarkerStyle(21);
                rrefDataStat -> SetLineColor (kBlue);
                rrefDataStat -> SetMarkerColor (kBlue);

                TLine *line2 = new TLine(summed->GetXaxis()->GetBinLowEdge(1), 0.0, summed->GetXaxis()->GetBinLowEdge(_nbins+1), 0.0);
                line2->SetLineColor(kBlack);
                line2->SetLineWidth(1);
                line2->SetLineStyle(1);
                line2->Draw("SAME"); 

                //              rrefData->Draw("EP");
                //              rrefDataStat->Draw("EP");

                rrefBkgSub->SetLineWidth(0);
                rrefBkgSub->SetFillColor(kGray+1);
                rrefBkgSub->SetLineColor(kGray+1);
                rrefBkgSub->SetFillStyle(3001);
                rrefBkgSub->Draw("E2");

                rrefDataStat->SetTitle("");
                rrefDataStat -> SetLineWidth (2);
                rrefDataStat -> SetMarkerSize (1);
                rrefDataStat -> SetMarkerStyle(20);
                rrefDataStat -> SetLineColor (kBlack);
                rrefDataStat -> SetMarkerColor (kBlack);
                rrefDataStat->Draw("EP");

                std::cout << " x1 = " << summed->GetXaxis()->GetBinLowEdge(1) + (summed->GetXaxis()->GetBinLowEdge(_nbins+1) - summed->GetXaxis()->GetBinLowEdge(1)) * 1. / 3. << std::endl;
                std::cout << " y1 = " << maxY+5 << std::endl;
                std::cout << " x2 = " << summed->GetXaxis()->GetBinLowEdge(1) + (summed->GetXaxis()->GetBinLowEdge(_nbins+1) - summed->GetXaxis()->GetBinLowEdge(1)) * 2. / 3. << std::endl;
                std::cout << " y2 = " << maxY+15 << std::endl;

                //              TLegend* legendSigMinusBkg = new TLegend(summed->GetXaxis()->GetBinLowEdge(1) + (summed->GetXaxis()->GetBinLowEdge(_nbins+1) - summed->GetXaxis()->GetBinLowEdge(1)) * 1. / 3. , maxY+5, summed->GetXaxis()->GetBinLowEdge(1) + (summed->GetXaxis()->GetBinLowEdge(_nbins+1) - summed->GetXaxis()->GetBinLowEdge(1)) * 2. / 3. ,  maxY+15);
                TLegend* legendSigMinusBkg = new TLegend(0.3, 0.7, 0.7, 1.0);

                legendSigMinusBkg->SetBorderSize(     0);
                legendSigMinusBkg->SetFillColor (     0);
                legendSigMinusBkg->SetTextAlign (    12);
                legendSigMinusBkg->SetTextFont  (_labelFont);
                legendSigMinusBkg->SetTextSize  (_legendTextSize);
                //              legendSigMinusBkg->AddEntry(rrefData,     "data (stat + syst)", "PL");
                //              legendSigMinusBkg->AddEntry(rrefDataStat, "data (stat)", "PL");

                legendSigMinusBkg->AddEntry(rrefDataStat, "data", "PL");
                legendSigMinusBkg->AddEntry(rrefBkgSub,   "bkg ", "F" );

                for (uint iSig = 0; iSig<temp_vectTHstackSig.size(); iSig++) {
                    if (_mergeSignal == 0) {
                        legendSigMinusBkg->AddEntry(temp_vectTHstackSig.at(iSig), _vectNameSig.at(iSig).c_str(), "PL");
                    }
                    else if ((_mergeSignal == 1) && (iSig == (temp_vectTHstackSig.size()-1))) {
                        if (_mass == -1) {
                            legendSigMinusBkg->AddEntry(temp_vectTHstackSig.at(iSig), "Higgs", "PL");
                        }
                        else {
                            TString name4Legend = Form ("Higgs %d GeV", _mass);
                            legendSigMinusBkg->AddEntry(temp_vectTHstackSig.at(iSig), name4Legend.Data(), "PL");
                        }
                    }
                }
                legendSigMinusBkg->Draw();

                cAdditional->Update();

            }
            c1->cd();
            c1->Update();
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

            if(gROOT->FindObject("hMC")) {
                gROOT->FindObject("hMC")->Delete();
            }
            TH1F* hMC;
            if (_vEdges.size() != 0) {
                double Xedge[1000];
                for (uint iEdg = 0; iEdg < _vEdges.size(); iEdg++) {
                    Xedge[iEdg] = _vEdges.at(iEdg);
                }
                hMC= new TH1F("hMC","hMC",_nbins, Xedge);
            }
            else {
                hMC = new TH1F("hMC","hMC",_nbins,_low,_high);
            }
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
                //       binWidth = _vectTHBkg.at (iBkg) -> GetBinWidth(1);
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

        void DrawLabels(bool plotData=true) {

            // total mess to get it nice, should be redone
            size_t j=0;

            float *pos,*off;
            int sampCount = GetSampCount();
            if(sampCount == 12 || sampCount == 15) { pos = xPosA; off = yOffA; }
            else if(sampCount == 11 )              { pos = xPosB; off = yOffB; }
            else                                   { pos = xPos;  off = yOff;  }
            float x0=0.22; float wx=0.19;
            if(_data   && plotData     ) { 
                DrawLegend(x0+pos[j]*wx, _globalYoffset - off[j]*_yoffset, _data,                  " data",                "lp");
                j++; 
            }
            else {
                //              if (plotData == false) j++;
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

            if (plotData == false) j++;

            for (unsigned int iBkg = 0; iBkg<_vectTHBkg.size(); iBkg++) {
                DrawLegend(x0+pos[j]*wx, _globalYoffset - off[j]*_yoffset, _vectTHBkg.at(iBkg)         , _vectNameBkg.at(iBkg) ,           "f" );
                j++; 
            }


            if (plotData) {
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
            }
            //      if(_extraLabel) _extraLabel->Draw("same");
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

        std::vector<double>      _vEdges ;

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

        bool    _doBandError    ;
        TGraphAsymmErrors*    _BandError      ;

        bool    _doLabelNumber  ;

};


