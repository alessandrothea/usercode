#include <map>
#include <string>
#include <TH1D.h>

#include "HWWAnalysis/Misc/interface/RootUtils.h"
#include "CommonTools/Utils/interface/TFileDirectory.h"

namespace hww {
//_____________________________________________________________________________
TH1D* makeLabelHistogram( const std::string& name, const std::string& title, std::map<int,std::string> labels) {
    int xmin = labels.begin()->first;
    int xmax = labels.begin()->first;

    std::map<int, std::string>::iterator it;
    for( it = labels.begin(); it != labels.end(); ++it ) {
        xmin = it->first < xmin ? it->first : xmin;
        xmax = it->first > xmax ? it->first : xmax;
    }

    ++xmax;
    int nbins = xmax-xmin;

    TH1D* h = new TH1D(name.c_str(), title.c_str(), nbins, xmin, xmax);
    for( it = labels.begin(); it != labels.end(); ++it ) {
        int bin = h->GetXaxis()->FindBin(it->first);
        h->GetXaxis()->SetBinLabel(bin, it->second.c_str());
    }

    return h;
}

//_____________________________________________________________________________
TH1D* makeLabelHistogram( TFileDirectory* fd, const std::string& name, const std::string& title, std::map<int,std::string> labels) {
    int xmin = labels.begin()->first;
    int xmax = labels.begin()->first;

    std::map<int, std::string>::iterator it;
    for( it = labels.begin(); it != labels.end(); ++it ) {
        xmin = it->first < xmin ? it->first : xmin;
        xmax = it->first > xmax ? it->first : xmax;
    }

    ++xmax;
    int nbins = xmax-xmin;

    TH1D* h = fd->make<TH1D>(name.c_str(), title.c_str(), nbins, xmin, xmax);
    for( it = labels.begin(); it != labels.end(); ++it ) {
        int bin = h->GetXaxis()->FindBin(it->first);
        h->GetXaxis()->SetBinLabel(bin, it->second.c_str());
    }

    return h;
}

}
